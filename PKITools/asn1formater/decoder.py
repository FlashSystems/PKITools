from .pyasn1.codec.der import decoder as derDecoder
from .pyasn1.codec.ber import decoder as berDecoder
from .pyasn1.type import univ
from .pyasn1.type import error
import traceback

class Decoder(derDecoder.Decoder):
	def __init__(self, tagMap, typeMap={}):
		super(Decoder, self).__init__(tagMap, typeMap)

		self.defaultErrorState =  berDecoder.stDumpRawValue

	def __call__(self, substrate, asn1Spec=None, tagSet=None, length=None, state=berDecoder.stDecodeTag, recursiveFlag=1, substrateFun=None):
		try:
			return super(Decoder, self).__call__(substrate, asn1Spec, tagSet, length, state, recursiveFlag, substrateFun)
		except error.ValueConstraintError:
			return super(Decoder, self).__call__(substrate, None, None, length, state, recursiveFlag, substrateFun)

tagMap = derDecoder.tagMap
typeMap = derDecoder.typeMap

decode = Decoder(tagMap, typeMap)
