import sublime, sublime_plugin
from .asn1formater.pyasn1.codec.der import decoder, encoder
from .asn1formater.pyasn1_modules import rfc2459, pem
from .asn1formater.pyasn1 import error
from .asn1formater.formaters import scalars, translators
from .asn1formater import oids
from .asn1formater import dumpFormater
import sys
import re
import os
import base64
import binascii

class ViewOutput():
	indentation = 0

	def __init__(self, outputView):
		# Disable automatic indentation for the output view.
		# We will indent everything by ourselves
		outputView.settings().set("auto_indent", False)

		self.outputView = outputView

	def writeLine(self, line):
		self.outputView.run_command("insert", {"characters": ('  ' * self.indentation)  + line + "\n"})

	def indent(self):
		self.indentation += 1;

	def outdent(self):
		if (self.indentation > 0): self.indentation -= 1

	def showError(self, message):
		# Error messages are never indentet
		self.indentation = 0
		self.writeLine("ERROR: " + message)


class PkiParseCertificateCommand(sublime_plugin.TextCommand):
	encodingHex = re.compile("^(?:0x)?([a-fA-f0-9 \r\n]+)$")
	encodingBase64 = re.compile("^([a-zA-Z0-9+/=\n]+)$")
	encodingPEM = re.compile("---+(?:START|BEGIN)[A-Za-z ]+---+\n([a-zA-Z0-9+/=\n]+)---+END[A-Za-z ]+---+")
	cleanupTranslation = {ord(' '): None, ord('\r'): None, ord('\n'): None}

	def decodeToBinary(self, string):
		# Check if the encoding matches a hex string
		try:
			match = self.encodingHex.match(string)
			if (match != None):
				return binascii.unhexlify(match.group(1).translate(self.cleanupTranslation))
		except:
			# Do Nothing and try the next filter
			pass

		try:
			match = self.encodingBase64.match(string)
			if (match != None):
				return base64.b64decode(match.group(1).translate(self.cleanupTranslation))
		except:
			# Do Nothing and try the next filter
			pass

		try:
			match = self.encodingPEM.match(string)
			if (match != None):
				return base64.b64decode(match.group(1).translate(self.cleanupTranslation))
		except:
			# Do Nothing and try the next filter
			pass

		return None

	def parseAndShow(self, selection, sourceName, view, codec):
		oidResolver = oids.OIDResolver(os.path.join(sublime.packages_path(), "PKITools", "dumpasn1.cfg"))


		if (codec == "rfc2459-cert"):
			codec = rfc2459.Certificate()
			codecName = "X509 certificate"
		else:
			codec = None
			codecName = "ASN.1"

		view.set_name(sourceName + " (" + codecName + ")")

		formater = dumpFormater.DumpFormater()
		formater.addScalarFormater(scalars.ScalarsFormater())
		formater.addScalarFormater(scalars.TimeFormater())
		formater.addScalarFormater(scalars.OIDFormater(oidResolver))
		formater.addTranslator(translators.Asn1Translators())
		formater.addTranslator(translators.X509Translators())

		viewOutput = ViewOutput(view)

		substrate = self.decodeToBinary(selection)
		if (substrate == None):
			viewOutput.showError("Unkown input encoding. Only hex, base64 and PEM are supported.")
			return

		try:
			cert, rest = decoder.decode(substrate, asn1Spec=codec)

			if rest: substrate = substrate[:-len(rest)]

			#formater.enableDebuging()
			formater.format("Certificate", cert, viewOutput)
		except error.SubstrateUnderrunError:
			viewOutput.showError("Premature end of imput stream.")
		except error.ValueConstraintError:
			viewOutput.showError("Valuce constraint violated in input data.")
		except:
			e = sys.exc_info()[0]
			viewOutput.showError(str(e))

	def run(self, edit, codec="asn1"):
		newView = self.view.window().new_file()
		newView.set_scratch(True)

		selection = self.view.sel() # get selection coords
		if (selection[0].size() > 0):
			selection = self.view.substr( selection[0] ) # get selected text
		else:
			selection = self.view.substr( sublime.Region(0, self.view.size()) )

		# Use the name of the buffer if set.
		# If there is no name use the basename of the file to construct the name of the new view.
		bufferName = self.view.name()
		if ((bufferName == None) or (len(bufferName.strip()) == 0)): bufferName = os.path.basename(self.view.file_name())

		self.parseAndShow(selection, bufferName, newView, codec)

		newView.set_syntax_file("Packages/PKITools/pkitools.hidden-tmLanguage")
		newView.set_read_only(True)
