import sys
import re
import os
import argparse

defines = [] # Stores all the constants have been defined
# Pattern that finds magic numbers
pattern = "(?<![a-zA-Z_])([-+]?\d*\.\d+|\d+)(?![a-zA-Z_])"
script_path = os.path.abspath(__file__)
script_dir = os.path.split(script_path)[0]

def firstPass(file):
	"""
	Passes over the file to store any constants that are defined.
	This does not take into consideration local constants. They will be considered
	global.
	
	All constants are stored in the list ''defines'' as tuples. Each tuple has two elements:
	the first element is the name of the constant, the second is the value of the constant.

	Args:
		file (str) the filename of the file we want to process.
	"""
	del defines[:]
	for line in file:
		line = line.strip()
		words = line.split()
		if len(words) > 0:
			if words[0].lower() == "#define":
				defTuple = (words[1], words[2])
				defines.append(defTuple)

def find_all_header_files(file):
	"""
	Given a source file, the function will loop through all the lines in the file
	and store all header files. It is assumed that the file is already open. 

	Args:
		file (str) the filename of the file that contains header files

	Return:
		List (str) for all the header files found in the input file
	"""
	header_files = []
	file.seek(0, 0)
	for line in file:
		line = line.strip()
		tokens = line.split()
		if len(tokens) > 0:
			if tokens[0].strip().lower() == "#include" and tokens[1][0] == "\"" :
				header_files.append(tokens[1][1:-1])

	return header_files


def process(file, args):
	"""
	Reads input file line by line to check if there are numbers in the line.
	The function does not assume that the file is already open.

	Args:
		file (str) path/filename for the input file
		args (ArgumentParser) that contains all user-specified flags
	"""
	print ("===========", file, "===========")
	lineNum = 1
	for line in file:
		line = line.rstrip()
		find_magic_number_in_line(line, lineNum, args)
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
			

def find_magic_number_in_line(line, lineNum, args):
	"""
	Given an input string the function will check if it contains any numbers.
	If any other numbers than 0 and 1 occur, the linenumber, the line itself
	and the magic number will be printed. The function will suggest possible replacements
	for the magic number, if one has been defined.

	Args:
		line (str) a string containing a line from the input file
		lineNum (int) the linenumber of the line
		args (ArgumentParser) that contains all user-specified flags
	"""
	matches = re.findall(pattern, line)
	if matches and not isConstant(line):
		removeAllValidValues(matches)
		for num in matches:
			if args["print"]:
				print(str(lineNum) + ":\t\"", line.strip(), "\", ", num)
			else:
				print(str(lineNum) + ":\t", num)

			if args["suggestions"] == True:
				for const in defines:
					if num in const:
						print( "\tConsider replacing with ", const[0])


def is_file_extension_valid(filename):
	"""
	Checks if a filename is of a valid type. At the time of writing only ''.c'' files
	are supported. The function only checks the file extension to see if it is valid.

	Args:
		filename (str) the path/filename of the inputted file.

	Return:
		True (boolean) when the file suffix (read: file type) is supported
		False (boolean) when the file suffix (read: file type) is not supported
	"""
	ret = False;
	name, extension = os.path.splitext(filename)
	if extension.lower() == ".c": #or extension.lower() == ".txt"):
		ret = True
	elif extension.lower() == ".h":
		ret = True
	else:
		ret = False
	return ret

def find_magic_number_in_file(filename, args):
	"""
	Determines all the constants before checking if magic numbers exist in
	the file.

	Args:
		filename (str) the path/filename of the file
		args (ArgumentParser) that contains all user-specified flags
	"""
	file = open(filename)
	if args["suggestions"] == True:
		firstPass(file)
		file.seek(0, 0)
	
	process(file, args)
	file.close()
				

def find_magic_numbers_recursively(rootDir, args):
	"""
	Processes all files in the current directory and all sub-directories.

	Args:
		rootDir (str) the path to the root of the directory we want to process
		args (ArgumentParser) that contains all user-specified flags
	"""
	print(rootDir)
	find_magic_numbers_in_directory(rootDir)
	dirs = [d for d in os.listdir(rootDir) if os.path.isdir(os.path.join(rootDir, d))]
	for directory in dirs:
		print("=== ", directory, " ===")
		find_magic_numbers_recursively(os.path.join(rootDir, directory))

def find_magic_numbers_in_directory(directory, args):
	"""
	Finds all the magic numbers for all the source files in the ''directory''.

	Args:
		directory (str) path to the directory 
		args (ArgumentParser) that contains all user-specified flags
	"""
	for dirent in os.listdir(directory):
		path = os.path.join(directory, dirent)
		if os.path.isfile(path):
			if is_file_extension_valid(dirent) == True:
				find_magic_number_in_file(path, args)

def createArgParser():
	"""
	Creates and returns an argument parser for the program. All arugments are 
	added and helper strings are provided.
	"""
	parser = argparse.ArgumentParser(description="Find magic numbers in CLANG files.")
	# parser.add_argument("-t", "--test", required=False, action="store_true")
	parser.add_argument("-r", "--recursively", 
		help = "Recursively search any sub-directories", required = False, action = "store_true")
	parser.add_argument("dirent", help = "File or directory to be searched")
	parser.add_argument("-p", "--print",
		help = "Print the line where a magic number occurs", required = False, action = "store_true")
	parser.add_argument("-s", "--suggestions",
		help = "Pre-processes the file(s) to suggest replacing magic numbers with any constants",
		required = False, action = "store_true")
	parser.add_argument("-d", "--derive",
		help = "Derive constants from include statements in the source files",
		required = False, action = "store_true")
	return parser

def find_magic_numbers_in_file_derive_constants(path, args):
	"""
	Takes a file and finds all maigc numbers in it. Based on the header files
	specified in the source file, all constants are defined. When all constants
	have been defined all magic numbers will be found.

	Args:
		path (str) to the source file
		args (ArgumentParser) that contains all user-specified flags
	"""
	directory = os.path.split(path)[0]
	file = open(os.path.join(script_dir, path))
	headers = find_all_header_files(file)
	for s in headers:
		full_path = os.path.join(directory, s)
		with open(full_path) as header_file:
			store_all_constants(header_file)

	file.seek(0, 0)
	process(file, args)
	file.close()
	del defines[:]

def store_all_constants(file):
	"""
	Finds and stores all constants - all non-zero and non-one values - that are 
	defined in ''file''. All constants are stored in the global ''defines''.

	Args:
		file (momdule) The open header file
	"""
	for line in file:
		line = line.strip()
		words = line.split()
		if len(words) > 0:
			if words[0].lower() == "#define":
				defTuple = (words[1], words[2])
				if defTuple not in defines:
					defines.append(defTuple)

def find_magic_numbers_in_directory_derive_constants(directory, args):
	"""
	Finds all magic numbers in the source files stored in ''directory''.

	Args:
		directory (str) path to directory containing source files
		args (ArgumentParser) that contains all user-specified flags
	"""
	for dirent in os.listdir(directory):
		if os.path.isfile(os.path.join(directory, dirent)):
			filename, extension = os.path.splitext(dirent)
			if extension.lower() == ".c":
				find_magic_numbers_in_file_derive_constants(os.path.join(directory, dirent), args)

def main():
	parser = createArgParser()
	args = vars(parser.parse_args())
	if args["derive"]:
		if os.path.isfile(args["dirent"]):
			find_magic_numbers_in_file_derive_constants(args["dirent"], args)
		else:
			find_magic_numbers_in_directory_derive_constants(args["dirent"], args)
	elif args["recursively"] == True:
		find_magic_numbers_recursively(args["dirent"], args)
	else:
		if os.path.isfile(args["dirent"]):
			find_magic_number_in_file(args["dirent"], args)
		else:
			find_magic_numbers_in_directory(args["dirent"], args)

if __name__ == "__main__":
	main()