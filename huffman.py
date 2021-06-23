#!/usr/local/bin/python3
import sys
import argparse
import shutil
from collections import defaultdict
import json

class Node:
	def __init__(self, char, number, left=None, right=None):
		self.left = left
		self.right = right
		self.character = char
		self.numberOfTimes = number

charCodes = {}
frequencyChar = {}
nodesDict = {}

def countChars(filePath):
	with open(filePath, 'r') as file:
		data = file.read()
		for char in data:
			if char in frequencyChar:
				frequencyChar[char] += 1
			else:
				frequencyChar[char] = 1
	frequencyChar["EOF"] = 1
	# print(frequencyChar)

def char_encodings(root, enc = "", lr = "0"):
	newEnc = enc + lr
	if(root.left):
		char_encodings(root.left, newEnc, "0")
	if(root.right):
		char_encodings(root.right, newEnc, "1")
	if(not root.left and not root.right):
		charCodes[root.character] = newEnc[1:]
	
def data_8bit(data):
	num_of_zeros = 8 - (len(data) % 8)
	for i in range(num_of_zeros):
		data += '0'
	char = ''
	for i in range(0, len(data), 8):
		char += chr(int(data[i:i+8], 2))
	return char

def encode(input_file, output_file):
	print("encoding ", input_file, output_file)
	countChars(input_file)
	nodesList = [Node(i, frequencyChar[i]) for i in frequencyChar.keys()]
	
	# print(nodesList)
	# nodesList = sorted(nodesList, key = lambda x: x.numberOfTimes)
	# for i in nodesList: print(i.numberOfTimes)
	# exit()

	while len(nodesList) != 1:
		nodesList = sorted(nodesList, key = lambda x: x.numberOfTimes)
		left = nodesList[0]
		right = nodesList[1]
		newNode = Node(left.character+right.character, left.numberOfTimes+right.numberOfTimes, left, right)
		nodesList.remove(left)
		nodesList.remove(right)
		nodesList.append(newNode)
	char_encodings(nodesList[0])
	# print(charCodes)
	out_data = ""
	with open(input_file, 'r') as file:
		data = file.read()
		for i in data: out_data += charCodes[i]
	out_data += charCodes["EOF"]
	# num_of_zeros = 8 - (len(out_data) % 8)
	# for i in range(num_of_zeros):
	# 	out_data += '0'
	# print(out_data)
	# print(charCodes)

	data_to_file = data_8bit(out_data)
	with open(output_file, 'w') as out_file:
		out_file.write(data_to_file)
	with open("encodings.json", 'w') as file:  
		json.dump(charCodes, file, indent = 6)

def decimalToBinary(n):
	return bin(n).replace("0b", "")

def decode(input_file, output_file):
	print("decoding ", input_file, output_file)
	with open(input_file, 'r') as file:
		data = file.read()
	# print("------------------", decimalToBinary(int(data)))
	with open("encodings.json", 'r') as file:
		charCodes = json.load(file)
	codes = charCodes.values()

	decoded_bin = ""
	bit_string = ''
	for i in range(len(data)):
		cint = ord(data[i])
		bin = decimalToBinary(cint)
		bin_r = bin[::-1] 
		while len(bin_r) < 8:
			bin_r += '0'
		char_bin = bin_r[::-1]
		decoded_bin += str(char_bin)
	
	decodedChar = ""
	decoded = ""
	# print(charCodes)
	# print(decoded_bin)
	for i in decoded_bin:
		decoded += i
		if decoded in codes:
			for (k, v) in charCodes.items():
				if v == decoded:
					if k == "EOF":break
					decodedChar += str(k)  
					decoded = ""
	# print(decodedChar)
	with open(output_file, 'w') as out_file:
		out_file.write(decodedChar)


def get_options(args=sys.argv[1:]):
	parser = argparse.ArgumentParser(description="Huffman compression.")
	groups = parser.add_mutually_exclusive_group(required=True)
	groups.add_argument("-e", type=str, help="Encode files")
	groups.add_argument("-d", type=str, help="Decode files")
	parser.add_argument("-o", type=str, help="Write encoded/decoded file", required=True)
	options = parser.parse_args()
	return options


if __name__ == "__main__":
	options = get_options()
	if options.e is not None:
		encode(options.e, options.o)
	if options.d is not None:
		decode(options.d, options.o)
