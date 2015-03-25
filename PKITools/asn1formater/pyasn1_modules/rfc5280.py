#
# Extensions to X.509 from RFC 5280
#
# ASN.1 source from:
# http://www.ietf.org/rfc/rfc5280.txt
#
# Sample captures from:
# http://wiki.wireshark.org/SampleCaptures/
#

from ..pyasn1.type import tag, namedtype, namedval, univ, constraint
from .rfc2459 import *

id_ce_freshestCRL = univ.ObjectIdentifier('2.5.29.46')

class FreshestCRL(univ.SequenceOf):
    componentType = DistributionPoint()
    subtypeSpec = univ.SequenceOf.subtypeSpec + constraint.ValueSizeConstraint(1, constraint.MAX)
