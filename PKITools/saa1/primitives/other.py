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
