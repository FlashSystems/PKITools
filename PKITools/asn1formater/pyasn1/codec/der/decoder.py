# DER decoder
from ..cer import decoder

tagMap = decoder.tagMap
typeMap = decoder.typeMap
Decoder = decoder.Decoder

decode = Decoder(tagMap, typeMap)
