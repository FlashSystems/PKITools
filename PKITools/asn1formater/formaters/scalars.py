from .decorators import UseFor
from ..pyasn1.type import base, tag, constraint, namedtype, namedval, tagmap, univ, char, useful
import re
from datetime import datetime, timedelta, timezone, tzinfo
import time

class LocalTimezone(tzinfo):
    stdOffset = timedelta(seconds = -time.timezone)
    if time.daylight:
        dstOffset = timedelta(seconds = -time.altzone)
    else:
        dstOffset = stdOffset

    dstDiff = dstOffset - stdOffset

    def utcoffset(self, dt):
        if self._isdst(dt):
            return self.dstOffset
        else:
            return self.stdOffset

    def dst(self, dt):
        if self._isdst(dt):
            return self.dstDiff
        else:
            return timedelta(0)

    def tzname(self, dt):
        return time.tzname[self._isdst(dt)]

    def _isdst(self, dt):
        tt = (dt.year, dt.month, dt.day,
              dt.hour, dt.minute, dt.second,
              dt.weekday(), 0, 0)
        stamp = time.mktime(tt)
        tt = time.localtime(stamp)
        return tt.tm_isdst > 0

class OIDFormater:
    def __init__(self, oidResolver):
        self.oidResolver = oidResolver

    @UseFor(univ.ObjectIdentifier)
    def fmtObjectIdentifier(self, record):
        resolvedName = self.oidResolver.getNameForOID(str(record))
        if (not resolvedName is None):
            return ".{1} ({0})".format(str(record), resolvedName)
        else:
            return "OID {0}".format(str(record))

class TimeFormater:
    tzLocal = LocalTimezone()

    def __init__(self):
        self.utcTimeSlicer = re.compile("(\d{2})(\d{2})(\d{2})(\d{2})((?:\d{2})?)((?:\d{2})?)((?:\.\d+)?)([Z+-]\d*)")
        self.generalizedTimeSlicer = re.compile("(\d{4})(\d{2})(\d{2})(\d{2})((?:\d{2})?)((?:\d{2})?)((?:\.\d+)?)([Z+-]\d*)")

    def formatTime(self, timeType, timeParts):
        year = int(timeParts[0])
        month = int(timeParts[1])
        day = int(timeParts[2])
        hours = int(timeParts[3])
        minutes = int(timeParts[4]) if timeParts[4].isdigit() else 0
        seconds = int(timeParts[5]) if timeParts[5].isdigit() else 0
        microseconds = int(timeParts[6]) if timeParts[6].isdigit() else 0
        tz = timeParts[7]

        # Convert the time zone offset into a timedelta between the given time and UTC
        if (tz == "Z"):
            tz = timedelta(hours = 0)
        else:
            tz = timedelta(hours = int(tz.strip(" +")))


        # Now convert the hours by the time zone offset.
        # Negative hours are handles well by datetime.
        #hours -= tz

        # Process a two digit year according to RFC5280
        if (year < 100):
            if (year >=50):
                year += 1900
            else:
                year += 2000

        dt = datetime(year, month, day, hours, minutes, seconds, microseconds, timezone(tz))

        return [
            "({0})".format(timeType),
            "stored time: {0}".format(dt.strftime("%Y-%m-%d %H:%M:%S.%f %z")),
            "local time: {0}".format(dt.astimezone(self.tzLocal).strftime("%Y-%m-%d %H:%M:%S.%f %z"))
            ]

    @UseFor(useful.GeneralizedTime)
    def fmtGeneralizedTime(self, record):
        matches = self.generalizedTimeSlicer.match(str(record));
        if (matches is None):
            return str(record)
        else:
            return self.formatTime("GeneralizedTime", matches.groups())

    @UseFor(useful.UTCTime)
    def fmtGeneralizedTime(self, record):
        matches = self.utcTimeSlicer.match(str(record))
        if (matches is None):
            return str(record)
        else:
            return self.formatTime("UTCTime", matches.groups())

class ScalarsFormater:
    def bitstringToHex(self, bitstring):
        hexValue = ""

        for i in range(0, len(bitstring), 8):
            value = 0
            for bit in bitstring[i:i+7]:
                value <<= 1;
                value |= int(bit)

            hexValue += "%02X" % value

        return hexValue

    @UseFor(univ.Null)
    def fmtNull(self, record):
        return "NULL"

    @UseFor(univ.Boolean)
    def fmtBoolean(self, record):
        if (int(record)>0):
            return "TRUE"
        else:
            return "FALSE"

    @UseFor(univ.Integer)
    @UseFor(univ.Enumerated)
    def fmtIntegerOrEnum(self, record):
        namedValueSuffix = ""

        if (len(record.namedValues) > 0):
            # If there are namedValues, decode them
            valueName = record.namedValues.getName(int(record))
            if (valueName is None): valueName = "?"

            namedValueSuffix = " ({0})".format(valueName)

        return str(record) + namedValueSuffix

    @UseFor(univ.Real)
    def fmtReal(self, record):
        return str(record)

    @UseFor(univ.BitString)
    def fmtBitString(self, record):
        # If the Bit-String is used as a bitfield decode the names,
        # if set.
        bitFieldElements = []
        if (len(record.namedValues) > 0):
            for bitPos in range(0, len(record)):
                if (record[bitPos]):
                    flagName = record.namedValues.getName(bitPos)
                    if (flagName is None): flagName = "?"
                    bitFieldElements.append("- " + flagName)

        return [
            "({0} bits)".format(len(record)),
            "0x" + self.bitstringToHex(record)
            ] + bitFieldElements

    @UseFor(char.NumericString)
    @UseFor(char.PrintableString)
    @UseFor(char.TeletexString)
    @UseFor(char.T61String)
    @UseFor(char.VideotexString)
    @UseFor(char.IA5String)
    @UseFor(char.GraphicString)
    @UseFor(char.VisibleString)
    @UseFor(char.ISO646String)
    @UseFor(char.GeneralString)
    @UseFor(char.UniversalString)
    @UseFor(char.BMPString)
    @UseFor(char.UTF8String)
    def fmtStringType(self, record):
        return [
            "(" + record.__class__.__name__ + ")",
            '"' + str(record) + '"'
            ]

    @UseFor(univ.OctetString)
    def fmtOctedString(self, record):
        numbers = tuple(record)
        if all(x >= 32 and x <= 126 for x in numbers):
            bracket = '"'
            return '"' + str(record) + '"'
        else:
            return [
                "({0} octets)".format(len(record)),
                '0x' + ''.join(( '%02X' % x for x in numbers ))
                ]
