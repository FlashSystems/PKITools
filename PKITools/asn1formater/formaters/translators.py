from .decorators import UseFor
from ..pyasn1.type import base, tag, constraint, namedtype, namedval, tagmap, univ, char
from ..pyasn1.codec.der import decoder

from ..pyasn1_modules import rfc2459

# This translator class convertes ASN1-Structures into new
# parse trees to dive deeper into classes of the type Any.
class Asn1Translators:
    @UseFor(univ.Any)
    def translateAny(self, record):
        # Parse the content of the Any-Tag and return the result
        return decoder.decode(record)[0]

class X509Translators:
    ceOIDClassMap = {
        rfc2459.id_ce_authorityKeyIdentifier: rfc2459.AuthorityKeyIdentifier,
        rfc2459.id_ce_basicConstraints: rfc2459.BasicConstraints,
        rfc2459.id_ce_certificateIssuer: rfc2459.CertificateIssuer,
        rfc2459.id_ce_certificatePolicies: rfc2459.CertificatePolicies,
        rfc2459.id_ce_cRLDistributionPoints: rfc2459.CRLDistPointsSyntax,
        #rfc2459.id_ce_cRLNumber - Handled by auto value decoding feature. Decoding the integer directly fails.
        rfc2459.id_ce_cRLReasons: rfc2459.CRLReason,
        rfc2459.id_ce_extKeyUsage: rfc2459.ExtKeyUsageSyntax,
        rfc2459.id_ce_holdInstructionCode: rfc2459.HoldInstructionCode,
        rfc2459.id_ce_invalidityDate: rfc2459.InvalidityDate,
        rfc2459.id_ce_issuerAltName: rfc2459.IssuerAltName,
        rfc2459.id_ce_issuingDistributionPoint: rfc2459.IssuingDistributionPoint,
        rfc2459.id_ce_keyUsage: rfc2459.KeyUsage,
        rfc2459.id_ce_nameConstraints: rfc2459.NameConstraints,
        rfc2459.id_ce_policyConstraints: rfc2459.PolicyConstraints,
        rfc2459.id_ce_policyMappings: rfc2459.PolicyMappings,
        rfc2459.id_ce_privateKeyUsagePeriod: rfc2459.PrivateKeyUsagePeriod,
        rfc2459.id_ce_subjectAltName: rfc2459.SubjectAltName,
        rfc2459.id_ce_subjectDirectoryAttributes: rfc2459.SubjectDirectoryAttributes,
        rfc2459.id_ce_subjectKeyIdentifier: rfc2459.SubjectKeyIdentifier,
        rfc2459.id_pe_authorityInfoAccess: rfc2459.AuthorityInfoAccessSyntax
    }

    @UseFor(rfc2459.Extension)
    def translateExtension(self, record):
        extensionOID = record["extnID"]

        # The extension is stored as an instance of the class any.
        # This instance must be decoded first to get the internal structure of the extension
        extensionValue = decoder.decode(record["extnValue"].asOctets())[0]

        # Iterate over all registered Extensions and decode the subelements.
        for oidClassMapEntry in self.ceOIDClassMap:
            if (extensionOID == oidClassMapEntry):
                record["extnValue"].override = decoder.decode(extensionValue, asn1Spec=self.ceOIDClassMap[oidClassMapEntry]())[0]
                return record;

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
