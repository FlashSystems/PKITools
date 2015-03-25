from .decorators import UseFor
from ..pyasn1.type import base, tag, constraint, namedtype, namedval, tagmap, univ, char
from .. import decoder
#from ..pyasn1.codec.der import decoder

from ..pyasn1_modules import rfc5280

# This translator class convertes ASN1-Structures into new
# parse trees to dive deeper into classes of the type Any.
class Asn1Translators:
    @UseFor(univ.Any)
    def translateAny(self, record):
        # Parse the content of the Any-Tag if there is any content and return the result
        if (record):            
            return decoder.decode(record)[0]
        else:
            return None

class X509Translators:
    ceOIDClassMap = {
        rfc5280.id_ce_authorityKeyIdentifier: rfc5280.AuthorityKeyIdentifier,
        rfc5280.id_ce_basicConstraints: rfc5280.BasicConstraints,
        rfc5280.id_ce_certificateIssuer: rfc5280.CertificateIssuer,
        rfc5280.id_ce_certificatePolicies: rfc5280.CertificatePolicies,
        rfc5280.id_ce_cRLDistributionPoints: rfc5280.CRLDistPointsSyntax,
        #rfc5280.id_ce_cRLNumber - Handled by auto value decoding feature. Decoding the integer directly fails.
        rfc5280.id_ce_cRLReasons: rfc5280.CRLReason,
        rfc5280.id_ce_extKeyUsage: rfc5280.ExtKeyUsageSyntax,
        rfc5280.id_ce_freshestCRL: rfc5280.FreshestCRL,
        rfc5280.id_ce_holdInstructionCode: rfc5280.HoldInstructionCode,
        rfc5280.id_ce_invalidityDate: rfc5280.InvalidityDate,
        rfc5280.id_ce_issuerAltName: rfc5280.IssuerAltName,
        rfc5280.id_ce_issuingDistributionPoint: rfc5280.IssuingDistributionPoint,
        rfc5280.id_ce_keyUsage: rfc5280.KeyUsage,
        rfc5280.id_ce_nameConstraints: rfc5280.NameConstraints,
        rfc5280.id_ce_policyConstraints: rfc5280.PolicyConstraints,
        rfc5280.id_ce_policyMappings: rfc5280.PolicyMappings,
        rfc5280.id_ce_privateKeyUsagePeriod: rfc5280.PrivateKeyUsagePeriod,
        rfc5280.id_ce_subjectAltName: rfc5280.SubjectAltName,
        rfc5280.id_ce_subjectDirectoryAttributes: rfc5280.SubjectDirectoryAttributes,
        rfc5280.id_ce_subjectKeyIdentifier: rfc5280.SubjectKeyIdentifier,
        rfc5280.id_pe_authorityInfoAccess: rfc5280.AuthorityInfoAccessSyntax
    }

    @UseFor(rfc5280.Extension)
    def translateExtension(self, record):
        extensionOID = record["extnID"]

        # The extension is stored as an instance of the class any.
        # This instance must be decoded first to get the internal structure of the extension
        extensionValue = decoder.decode(record["extnValue"].asOctets())[0]

        # Iterate over all registered Extensions and decode the subelements.
        for oidClassMapEntry in self.ceOIDClassMap:
            if (extensionOID == oidClassMapEntry):
                try:
                    record["extnValue"].override = decoder.decode(extensionValue, asn1Spec=self.ceOIDClassMap[oidClassMapEntry]())[0]
                    return record;
                except:
                    pass

        # Start a universal decoding try on the extensionValue if it was not found within the list.
        # This is called: Auto value decoding
        try:
            record["extnValue"].override = decoder.decode(extensionValue)[0]
            return record
        except:
            pass

        # Just retorn the internaly decoded any.
        record["extnValue"].override = extensionValue
        return record
