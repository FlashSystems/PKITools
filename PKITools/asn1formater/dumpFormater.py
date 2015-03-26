from .pyasn1.type import base, tag, constraint, namedtype, namedval, tagmap, univ, char
from .pyasn1.codec.der import decoder
from .formaters import scalars

class DumpFormater:
    scalarFormaters = []
    translators = []

    # For complex type the positional arguments are:
    # Name
    # Type of complex class
    # Class name (for debuging) - Added by enableDebuging
    complexTypeFormatString = "{0}{1}"

    # For simple types the positional arguments are:
    # Name Prefix (depending on tag class)
    # Name
    # Value
    simpleTypeFormatString = "{0}{1}: {2}"


    def addScalarFormater(self, formaterInstance):
        self.scalarFormaters.append(formaterInstance)

    def addTranslator(self, translatorInstance):
        self.translators.append(translatorInstance)

    def enableDebuging(self):
        # To enable debuging the complexTypeFormatString is extended by positional
        # parameter 2 that includes the class name of the record.
        self.complexTypeFormatString += "{{{2}}}"

    def callMethodUnderstandingClass(self, insanceList, record, *args):
        # Search for the method that understands the type of record and call it.
        # Return the result.
        for formaterInstance in insanceList:
            # First the exact class matches are checked. Then the isinstance matches.
            for method in formaterInstance.__class__.__dict__.values():
                if (callable(method) and not getattr(method, "understoodClasses", None) is None):
                    for understoodClass in method.understoodClasses:
                        if (type(record) == understoodClass):
                            return method(formaterInstance, record, *args)

        for formaterInstance in insanceList:
            for method in formaterInstance.__class__.__dict__.values():
                if (callable(method) and not getattr(method, "understoodClasses", None) is None):
                    for understoodClass in method.understoodClasses:
                        if (isinstance(record, understoodClass)):
                            return method(formaterInstance, record, *args)

        return None

    def nameAndTypeString(self, name, asn1construct):
        if ((name is None) or (len(name) == 0)):
            name = ""
            spacer = ""
        else:
            spacer = " "

        return "{0}{1}({2})".format(name, spacer, asn1construct)


    def format(self, name, record, out):
        # Indent one step because this recursion is one level deepr than the one before
        out.indent()

        # None is output as a NULL on a single line.
        if (record is None):
            out.writeLine(self.nameAndTypeString(name, "NULL"))
            out.outdent()
            return

        # If there is a registered translator, call it now and process the translators
        # result as a replacement for the original value.
        newRecord = self.callMethodUnderstandingClass(self.translators, record)
        if (not newRecord is None): record = newRecord

        # Now determinif the tag has the class CONTEXT.
        # If that's the case, we should prefix the name with
        # the index of the instance.
        namePrefix = ""
        tags = record.getTagSet()
        if (isinstance(tags, tag.TagSet) and len(tags) > 0):
            cls, fmt, nr = tags[-1]
            if (cls is tag.tagClassContext):
                namePrefix = "[" + str(nr) + "] "
        if (isinstance(record, univ.Choice)):
            self.format(name, record.getComponent(), out)

        elif (isinstance(record, univ.SetOf) or isinstance(record, univ.SequenceOf) or isinstance(record, univ.SequenceAndSetBase)):
            if (isinstance(record, univ.SequenceOf) or isinstance(record, univ.Sequence)):
                asn1construct = "sequence"
            elif (isinstance(record, univ.SetOf) or isinstance(record, univ.Set)):
                asn1construct = "set"
            else:
                asn1construct = "?"

            out.writeLine(self.complexTypeFormatString.format(namePrefix, self.nameAndTypeString(name, asn1construct), record.__class__.__name__))

            for i in range(len(record)):
                component = record.getComponentByPosition(i)
                component = getattr(component, "override", component)

                self.format(record.getNameByPosition(i) if (not getattr(record, "getNameByPosition", None) is None) else component.__class__.__name__, component, out)

        else:
            if (name is None): name = "?"

            # Ok, it's non of the understood complex types.
            # Call the scalar formater to format it as a simple type.
            # The result can be a string (str) or a list. The list is output
            # with the second and all follwoing elements indented below the first
            formatedResult = self.callMethodUnderstandingClass(self.scalarFormaters, record)

            # If the formated result is None. Then no formater was found. Output the
            # class and a ?
            if (formatedResult is None):
                out.writeLine("? ({0})".format(record.__class__.__name__))
            else:
                # The result can
                if (isinstance(formatedResult, str)):
                    out.writeLine(self.simpleTypeFormatString.format(namePrefix, name, formatedResult))
                else:
                    out.writeLine(self.simpleTypeFormatString.format(namePrefix, name, formatedResult.pop(0)))
                    out.indent()
                    for line in formatedResult:
                        out.writeLine(line)
                    out.outdent()

        out.outdent()
