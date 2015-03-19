

class OIDResolver:
    oids = {}

    def __init__(self, fileName):
        lastOID = None

        with open(fileName) as hFile:
            for line in hFile.readlines():
                line = line.strip()
                parts = line.split("=", 2)
                if (len(parts) == 2):
                    name = parts[0].strip()
                    value = parts[1].strip()
                    if (name == "OID"): lastOID = value.replace(" ", ".")
                    if (name == "Description" and lastOID != None):
                        self.oids[lastOID] = value

    def getNameForOID(self, oid):
        return self.oids.get(oid, None)
