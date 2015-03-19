#!/usr/bin/python3
import os
import shutil
import re
import sys

importLineMatcher = re.compile("(^[ \t]*from )([^\.][^ ]+)( import.*$)")

def determinRelativeImport(importBasePath, fileName, importPath):
	absModulePath = os.path.join(importBasePath, importPath.replace(".", "/"))
	if os.path.exists(absModulePath) or os.path.exists(absModulePath + ".py"):
		relPath = os.path.relpath(absModulePath, os.path.dirname(fileName))
		if (relPath != "." and relPath != ".."):
			relImport = "."
			for part in relPath.split("/"):
				if (part == ".."):
					relImport += "."
				else:
					if (not relImport.endswith(".")): relImport += "."
					relImport += part
		else:
			relImport = relPath

		print("  Converted {0} to {1}".format(importPath, relImport))
		return relImport
	else:
		return importPath

def processLine(importBasePath, fileName, line):
	importLine = importLineMatcher.match(line)
	if (importLine != None):
		newImportLinePart = determinRelativeImport(importBasePath, fileName, importLine.group(2))
		newImportLine = importLine.group(1) + newImportLinePart + importLine.group(3) + "\n"
		return newImportLine
	else:
		return line

def convertFile(importBasePath, fileName):
	print("Processing {0}...".format(fileName))
	with open(fileName) as inFile:
		with open(fileName + ".new", "w") as outFile:
			for line in inFile.readlines():
				outFile.write(processLine(importBasePath, fileName, line))

	shutil.move(fileName + ".new", fileName)


def absToRelative(importBasePath, path):
	for dirName, subdirs, files in os.walk(path):
		for file in files:
			if (file.endswith(".py")):
				convertFile(importBasePath, os.path.join(dirName, file))

if (len(sys.argv) != 2):
	print("Usage:")
	print("abs2rel_import.py <modulePath>")
else:
	modulePath = sys.argv[1]

	absToRelative(os.path.dirname(modulePath), modulePath)