import re

class StringType:
	def isValid(self):
		return True

class OctetString(StringType):
	def __init__(self, data):				
		self._value = data

	def __len__(self):
		return len(self._value)

	def __getitem__(self, key):
		return self._value[key]

	def __str__(self):
		return "%(byteLength)i bytes" % { "byteLength": len(self._value) }

	def getAllBytes(self):
		return self._value

class BitString(StringType):
	def __init__(self, data):	
		self._bits = len(data) * 8 - data[0]
		self._value = data[1:]

	def __len__(self):
		return self._bits

	def __getitem__(self, key):
		mask = 2 ^ (key % 8)
		return ((self._value[key // 8] & mask) == mask)

	def __str__(self):
		return "%(bitLength)i bits" % { "bitLength": self._bits }

	def getAllBytes(self):
		# TODO: Ist das so gut? Oder lieber eine Exception
		if ((self._bits % 8) > 0):
			return None

		return self._value

class RestrictedString(StringType):
	def __init__(self, data):
		self._value = data.decode(self._encoding)

	def isValid(self):
		if (self._allowedCharsRegex is None):
			return True
		else:
			return (re.compile(self._allowedCharsRegex).search("^" + self._allowedCharsRegex + "+$") != None)

	def __str__(self):
		return self._value

class UTF8String(RestrictedString):
	_encoding = "utf-8"
	_allowedCharsRegex = None

class NumericString(RestrictedString):
	_encoding = "ascii"
	_allowedCharsRegex = "[0-9 ]"

class PrintableString(RestrictedString):
	_encoding = "ascii"
	_allowedCharsRegex = "[A-Za-z0-9 '()+,-./:=?]"

class GraphicString(RestrictedString):
	_encoding = "ascii"
	_allowedCharsRegex = None

class GraphicString(RestrictedString):
	_encoding = "ascii"
	_allowedCharsRegex = None

class TeletexString(RestrictedString):
	_encoding = "ascii"
	_allowedCharsRegex = None
	
class VideotexString(RestrictedString):
	_encoding = "ascii"
	_allowedCharsRegex = None

class IA5String(RestrictedString):
	_encoding = "ascii"
	_allowedCharsRegex = None

class GeneralString(RestrictedString):
	_encoding = "ascii"
	_allowedCharsRegex = None

class UniversalString(RestrictedString):
	_encoding = "utf-16"
	_allowedCharsRegex = None	

class BMPString(RestrictedString):
	_encoding = "utf-16"
	_allowedCharsRegex = None	
