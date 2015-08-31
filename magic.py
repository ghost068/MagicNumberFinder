import sys
import re
import os
import argparse

defines = []
pattern = "(?<![a-zA-Z_])([-+]?\d*\.\d+|\d+)(?![a-zA-Z_])"

def firstPass(file):
	"""
	Passes over the file to store any constants that are defined.
	This does not take into consideration local constants. They will be considered
	global at the time of writing.
	
	All constants are stored in the list ''defines'' as tuples. Each tuple has two elements:
	the first element is the name of the constant, the second is the value of the constant.

	Args:
		file (str) the filename of the file we want to process.
	"""
	with open(file) as f:
		del defines[:]
		for line in f:
			line = line.strip()
			words = line.split()
			if len(words) > 0:
				if words[0].lower() == "#define":
					defTuple = (words[1], words[2])
					defines.append(defTuple)


def process(file):
	"""
	Opens the input file and reads it line by line to check if there are numbers in the line.
	The function does not assume that the file is already open.

	Args:
		file (str) path/filename for the input file
	"""
	print ("===========", file, "===========")
	with open(file) as openFile:
		lineNum = 1
		for line in openFile:
			line = line.rstrip()
			checkLine(line, lineNum)
			lineNum += 1
	print()


def isConstant(string):
	"""
	Checks if a string declares a constant. It is assumed that the first token in the string
	is ''#define''.

	Args:
		string (str) a string that we want to check if is a define statement

	Return:
		True (boolean) when the string starts with ''#define''
		False (boolean) when the string does not start with ''#define''
	"""
	tokens = string.strip().split()
	if len(tokens) > 0 and tokens[0].lower() == "#define":
		return True
	else:
		return False


def removeAllValidValues(list):
	"""
	Removes all occurences of ''0'', ''1'', and ''0'' ''1.0'' in ''list''.
	It is assumes that the list stores the numbers as strings.

	Args:
		list (str[]) a list of numbers
	"""
	while "0" in list:
		list.remove("0")
	while "1" in list:
		list.remove("1")
	while "1.0" in list:
		list.remove("1.0")
	while "0.0" in list:
		list.remove("0.0")
			

def checkLine(line, lineNum):
	"""
	Given an input string the function will check if it contains any numbers.
	If any other numbers than 0 and 1 occur, the linenumber, the line itself
	and the magic number will be printed. The function will suggest possible replacements
	for the magic number, if one has been defined.

	Args:
		line (str) a string containing a line from the input file
		lineNum (int) the linenumber of the line
	"""
	matches = re.findall(pattern, line)
	if matches and not isConstant(line):
		removeAllValidValues(matches)
		for num in matches:
			print(str(lineNum) + ":\t\"", line.strip(), "\", ", num)
			for const in defines:
				if num in const:
					print( "\tConsider replacing with ", const[0])


def checkFileExtension(filename):
	"""
	Checks if a filename is of a valid type. At the time of writing only ''.c'' files
	are supported. The function only checks the file extension to see if it is valid.

	Args:
		filename (str) the path/filename of the inputted file.

	Return:
		True (boolean) when the file suffix (read: file type) is supported
		False (boolean) when the file suffix (read: file type) is not supported
	"""
	name, extension = os.path.splitext(filename)
	if extension.lower() == ".c": #or extension.lower() == ".txt"):
		return True
	else:
		return False

def processFile(filename):
	"""
	Determines all the constants before checking if magic numbers exist in
	the file.

	Args:
		filename (str) the path/filename of the file
	"""
	firstPass(filename)
	process(filename)
				

def traverse(rootDir):
	"""
	Processes all files in the current directory and all sub-directories.

	Args:
		rootDir (str) the path to the root of the directory we want to traverse
	"""
	print(rootDir)
	processAllFiles(rootDir)
	dirs = [d for d in os.listdir(rootDir) if os.path.isdir(os.path.join(rootDir, d))]
	for directory in dirs:
		print("=== ", directory, " ===")
		traverse(os.path.join(rootDir, directory))

def processAllFiles(directory):
	for dirent in os.listdir(directory):
		path = os.path.join(directory, dirent)
		if os.path.isfile(path):
			if checkFileExtension(dirent) == True:
				processFile(path)

def main():
	parser = argparse.ArgumentParser(description="Find magic numbers in CLANG files.")
	parser.add_argument("-r", "--recursively", 
		help = "Recursively search any sub-directories", required = False, action = "store_true")
	parser.add_argument("dirent", help = "File or directory to be searched")
	args = vars(parser.parse_args())

	if args["recursively"] == True:
		traverse(args["dirent"])
	else:
		if os.path.isfile(args["dirent"]):
			processFile(args["dirent"])
		else:
			processAllFiles(args["dirent"])


if __name__ == "__main__":
	main()

