import re
from datetime import datetime, timedelta, timezone
import time

class Boolean:
	def __init__(self, data):
		self._value = (data[0] > 0)

	def __str__(self):
		if (self._value):
			return "TRUE"		 
		else:
			return "FALSE"

class Integer:
	def __init__(self, data):
		self._value = 0

		for i in data:
			self._value = (self._value << 8) | i

	def __int__(self):
		return self._value

	def __str__(self):
		return str(self._value)

class Enum(Integer):
	pass

class ObjectIdentifier:
	_oidString = ""

	def __init__(self, data):		
		currentSubidentifier = 0
		for i in data:
			# Add the data to the subidentifier
			currentSubidentifier = (currentSubidentifier << 7) | ( i & 0x7F)

			# If this is the last octet, output the value and reset the subIdentifier accumulator
			if (i & 0x80 == 0):
				# The first two items of the OID are packed together and must be decoded.
				if (len(self._oidString) == 0):
					y = currentSubidentifier % 40
					x = (currentSubidentifier - y) // 40
					self._oidString = "{0}.{1}".format(x, y)
				else:
					self._oidString = "{0}.{1}".format(self._oidString, currentSubidentifier)

				currentSubidentifier = 0

	def __str__(self):
		return self._oidString

class Null:
	def __init__(self, data):
		pass

	def __str__(self):
		return "NULL"

class BaseTime:
	def __init__(self, data, slicer):
		self._value = data.decode("ascii")
		self._dt = self._convertTime(data, slicer)

	def _convertTime(self, data, slicer):
		timeParts = re.compile(slicer).match(data.decode("ascii"))
		if (timeParts is None): return None
		timeParts = timeParts.groups()

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

		# Process a two digit year according to RFC5280
		if (year < 100):
			if (year >=50):
				year += 1900
			else:
				year += 2000

		return datetime(year, month, day, hours, minutes, seconds, microseconds, timezone(tz))

	def __str__(self):
		return self._value

	def getTime(self):
		return self._dt		

class UTCTime(BaseTime):
	def __init__(self, data):
		super(UTCTime, self).__init__(data, "(\d{2})(\d{2})(\d{2})(\d{2})((?:\d{2})?)((?:\d{2})?)((?:\.\d+)?)([Z+-]\d*)")

class GeneralizedTime(BaseTime):
	def __init__(self, data):
		super(UTCTime, self).__init__(data, "(\d{4})(\d{2})(\d{2})(\d{2})((?:\d{2})?)((?:\d{2})?)((?:\.\d+)?)([Z+-]\d*)")
