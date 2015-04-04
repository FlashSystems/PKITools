# SAA.1 Simple API for ASN.1 (DER) parsing.

from .primitives import other, strings, datetime
from .exceptions import *

class ByteStream:	
	_position = 0	

	def __init__(self, data):
		self._data = data

	def __len__(self):
		return len(self._data)

	def getBytes(self, length):
		self._position += length

		if (self._position > len(self._data)):
			raise Saa1EndOfStreamException()

		return self._data[self._position - length:self._position]

	def getByte(self):
		if (self._position >= len(self._data)):
			raise Saa1EndOfStreamException()

		byte = self._data[self._position]
		self._position += 1
		return byte

	def getRemainingBytes(self):
		return len(self._data) - self._position

	def isEmpty(self):
		return len(self._data) <= self._position	

class PartOfByteStream:
	_length = 0
	_backStream = None

	def __init__(self, backingStream, length):	
		if (length > backingStream.getRemainingBytes()):
			length = backingStream.getRemainingBytes()

		self._length = length
		self._backStream = backingStream

	def __len__(self):
		return self._length

	def getBytes(self, length):
		# IF the length is exhausted
		if (length > self._length):
			# Consume the remaining length to allow continuing after the exception was catched
			self._backStream.getBytes(self._length)
			raise Saa1ParentSizeExceededException()

		self._length -= length

		return self._backStream.getBytes(length)

	def getByte(self):
		if (self._length > 0):
			self._length -= 1
			return self._backStream.getByte()
		else:
			raise Saa1ParentSizeExceededException()

	def getRemainingBytes(self):
		return self._length

	def isEmpty(self):
		return (self._length <= 0)

class Tag:
	def __init__(self, stream):
		identifier = stream.getByte()

		self._cls = identifier >> 6
		self._constructed = bool((identifier & 0x20) >> 5)
		self._tag = identifier & 0x1F

		# Tag number is greater than 31
		if (self._tag == 0x1F):
			while True:
				value = stream.getByte()
				self._tag = (self._tag << 7) | (value & 0x7F)
				if (not (value & 0x80)): break

	def isEoo(self):
		return (self._cls == 0) and (not self._constructed) and (self._tag == 0)

	def isConstructed(self):
		return self._constructed

	def getClass(self):
		return self._cls

	def getTag(self):
		return self._tag

class Length(int):	
	def __new__(cls, stream):
		lengthOctet = stream.getByte()

		# Multiple length octets or undefined length
		if (lengthOctet & 0x80):			
			if (lengthOctet == 0x80):
				# Undefined length
				return None
			else:
				# Multiple length octets
				length = 0
				for i in range(0, lengthOctet & 0x7F):
					length = (length << 8) | stream.getByte()

				return length
		else:
			# Normal length encoding
			return lengthOctet

class Class:
	UNIVERSAL = 0x00
	APPLICATION = 0x01
	CONTEXT = 0x02
	PRIVATE = 0x03

class Decoder:
	primitiveTagMap = {
		(Class.UNIVERSAL, 0x01): other.Boolean,
		(Class.UNIVERSAL, 0x02): other.Integer,
		(Class.UNIVERSAL, 0x03): strings.BitString,
		(Class.UNIVERSAL, 0x04): strings.OctetString,
		(Class.UNIVERSAL, 0x05): other.Null,
		(Class.UNIVERSAL, 0x06): other.ObjectIdentifier,
		#(Class.UNIVERSAL, 0x07): other.ObjectDescriptor,
		#(Class.UNIVERSAL, 0x08): other.ExternalType,
		#(Class.UNIVERSAL, 0x09): other.Real,
		(Class.UNIVERSAL, 0x0A): other.Enum,
		#(Class.UNIVERSAL, 0x0B): other.EmbeddedBDV,		
		(Class.UNIVERSAL, 0x0C): strings.UTF8String,
		#(Class.UNIVERSAL, 0x0D): other.RelativeObjectIdentifier,
		#(Class.UNIVERSAL, 0x0E): other.Time,
		#(Class.UNIVERSAL, 0x10): other.Sequence,
		#(Class.UNIVERSAL), 0x11): other.SequenceOf,
		(Class.UNIVERSAL, 0x12): strings.NumericString,
		(Class.UNIVERSAL, 0x13): strings.PrintableString,
		(Class.UNIVERSAL, 0x14): strings.TeletexString,
		(Class.UNIVERSAL, 0x15): strings.VideotexString,
		(Class.UNIVERSAL, 0x16): strings.IA5String,
		(Class.UNIVERSAL, 0x17): datetime.UTCTime,
		(Class.UNIVERSAL, 0x18): datetime.GeneralizedTime,
		(Class.UNIVERSAL, 0x19): strings.GraphicString,
		(Class.UNIVERSAL, 0x1A): strings.VisibleString,
		(Class.UNIVERSAL, 0x1B): strings.GeneralString,
		(Class.UNIVERSAL, 0x1C): strings.UniversalString,
		#(Class.UNIVERSAL, 0x1D): strings.UnrestrictedCharacterStringType,
		(Class.UNIVERSAL, 0x1E): strings.BMPString,
		(Class.UNIVERSAL, 0x1F): datetime.Date,
		#(Class.UNIVERSAL, 0x20): other.TimeOfDay,
		#(Class.UNIVERSAL, 0x21): other.DateTime,
		#(Class.UNIVERSAL, 0x22): other.Duration,
		#(Class.UNIVERSAL, 0x23): other.InternationalOID,
		#(Class.UNIVERSAL, 0x24): other.RelativeInternationalOID
	}

	# A list of Tags that may contain embedded ASN.1
	embeddedTagList = (
		(Class.UNIVERSAL, 0x03),	# BitString
		(Class.UNIVERSAL, 0x04),	# OctetString
	)

	def _isEncodedASN1(self, stream):
		try:
			while (not stream.isEmpty()):
				tag = Tag(stream)
				length = Length(stream)

				# Skip the length if it's not indefinite
				if (not length is None):
					if (length > stream.getRemainingBytes()):
						return False
					else:
						stream.getBytes(length)

		except:
			return False

		return True

	def _decodeFromStream(self, stream):
		while (not stream.isEmpty()):
			tag = Tag(stream)
			length = Length(stream)

			# Check if the decoded length fits into this part of the stream
			if (length > len(stream)):
				raise Saa1ParentSizeExceededException()

			# If this is an End Of Octets Tag, leave this decoder.
			if (tag.isEoo()):
				return

			# Decompose constructed tags
			if (tag.isConstructed()):
				self._out.beginConstructed(tag)

				try:
					if (length is None):
						self._decodeFromStream(stream)
					else:
						self._decodeFromStream(PartOfByteStream(stream, length))
				except Saa1ParentSizeExceededException:
					self._out.continuableError("Parent size exceeded.")

				self._out.endConstructed(tag)
			else:
				if (length is None):
					raise Saa1IndefiniteSimpleException()

				idTuple = (tag.getClass(), tag.getTag())
				if (idTuple in self.primitiveTagMap):
					primitiveDecoderClass = self.primitiveTagMap[idTuple]
					primitiveOctets = stream.getBytes(length)
					try:
						decodedValue = primitiveDecoderClass(primitiveOctets)

						# Some ASN.1 simple types can contain ebedded ASN.1.
						# The classes for these types implement getAllBytes().
						# We try some subdecoding here!
						processed = False
						if (idTuple in self.embeddedTagList):
							# Check if the Byte-Stream contains embedded ASN.1
							# If that's the case, call back to query if it should be automatically expanded
							embeddedOctets = decodedValue.getAllBytes()
							if ((not embeddedOctets is None) and self._isEncodedASN1(ByteStream(embeddedOctets)) and self._out.shouldExpandEmbedded(tag)):
								self._out.beginEmbedded(tag)
								self._decodeFromStream(ByteStream(embeddedOctets))
								self._out.endEmbedded(tag)
								processed = True

						# If the value was not processed by the subelement decoder.
						# Just go end 
						if (not processed):
							self._out.primitive(decodedValue)

					except Exception as e:
						self._out.primitiveDecodingError(tag, str(e), primitiveOctets)
				else:
					self._out.unkownPrimitive(tag)

					# Skip the unkown primitive and try decoding the next one
					stream.getBytes(length)

	def decode(self, data, out):
		self._out = out
		self._decodeFromStream(ByteStream(data))
