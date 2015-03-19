#!/usr/bin/python
#
# Read ASN.1/PEM X.509 certificates on stdin, parse each into plain text,
# then build substrate from it
#
from PKITools.asn1formater.pyasn1.codec.der import decoder, encoder
from PKITools.asn1formater.pyasn1_modules import rfc2459, pem
from PKITools.asn1formater.formaters import scalars, translators
from PKITools.asn1formater import oids, dumpFormater
import sys
import re
import os
import base64

class FileOutput():
    indentation = 0

    def __init__(self, fileName):
        self.hFile = open(fileName, "w")

    def __del__(self):
        self.close()

    def close(self):
        if (self.hFile != None): self.hFile.close()
        self.hFile = None

    def writeLine(self, line):
        self.hFile.write(('  ' * self.indentation) + line + "\n")

    def indent(self):
        self.indentation += 1;

    def outdent(self):
        if (self.indentation > 0): self.indentation -= 1

def pemToBinary(base64CertLines):
    inBase64Block = False
    base64Block = ""

    boundryFilter = re.compile("^[ \t]*-+(START|BEGIN|END)([A-Za-z ]*)-+$")

    for line in base64CertLines:
        match = boundryFilter.match(line);
        if (match != None):
            tag = match.group(1).upper()
            inBase64Block = (tag == "START") or (tag == "BEGIN")
        else:
            if (inBase64Block):
                base64Block += line
            else:
                if (len(base64Block) > 0): break

    return base64.b64decode(base64Block.encode("ascii"))

def loadBase64File(file):
    with open(file) as hFile:
        return pemToBinary(hFile.readlines())

def loadBinaryFile(file):
    with open(file, "rb") as hFile:
        return hFile.read()

def runTest(data, outFileName, spec):
    #try:
        oidResolver = oids.OIDResolver("PKITools/dumpasn1.cfg")

        cert, rest = decoder.decode(data, asn1Spec=spec)

        if rest: substrate = substrate[:-len(rest)]

        formater = dumpFormater.DumpFormater()
        formater.addScalarFormater(scalars.ScalarsFormater())
        formater.addScalarFormater(scalars.TimeFormater())
        formater.addScalarFormater(scalars.OIDFormater(oidResolver))
        formater.addTranslator(translators.Asn1Translators())
        formater.addTranslator(translators.X509Translators())
        #formater.enableDebuging()
        formater.format(spec.__class__.__name__, cert, FileOutput(outFileName))
    #except:
    #    print("ERROR")


for dirName, subdirs, files in os.walk('TestData'):
    for file in files:
        inFile = os.path.join(dirName, file)
        outFile = inFile + ".txt"

        if (file.endswith(".cer")):
            runTest(loadBase64File(inFile), outFile, rfc2459.Certificate())
        elif (file.endswith(".crl")):
            runTest(loadBinaryFile(inFile), outFile, rfc2459.CertificateList())
