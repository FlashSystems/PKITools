import re
from datetime import datetime, timedelta, timezone
import time

class DateTimeBase:
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
		if (len(timeParts) > 3):
			hours = int(timeParts[3])
			minutes = int(timeParts[4]) if timeParts[4].isdigit() else 0
			seconds = int(timeParts[5]) if timeParts[5].isdigit() else 0
			microseconds = int(timeParts[6]) if timeParts[6].isdigit() else 0
		else:
			hours = 0
			minutes = 0
			seconds = 0
			microseconds = 0
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

class UTCTime(DateTimeBase):
	def __init__(self, data):
		super(UTCTime, self).__init__(data, "(\d{2})(\d{2})(\d{2})(\d{2})((?:\d{2})?)((?:\d{2})?)((?:\.\d+)?)([Z+-]\d*)")

class GeneralizedTime(DateTimeBase):
	def __init__(self, data):
		super(UTCTime, self).__init__(data, "(\d{4})(\d{2})(\d{2})(\d{2})((?:\d{2})?)((?:\d{2})?)((?:\.\d+)?)([Z+-]\d*)")

class Date(DateTimeBase):
	def __init__(self, data):
		super(UTCTime, self).__init__(data, "(\d{4})(\d{2})(\d{2})")