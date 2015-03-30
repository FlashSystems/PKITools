# Raised if a simple type with indefinite length is detected.
# The decoder can't continue in this case.
class Saa1IndefiniteSimpleException(Exception): pass
class Saa1EndOfStreamException(Exception): pass
class Saa1ParentSizeExceededException(Exception): pass