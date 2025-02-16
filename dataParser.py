#Copyrigth 2016 by Tien PHAN XUAN and Thanh LE DINH
#VNU University of Engineering and Technology

try:
    from http_parser.parser import HttpParser
except ImportError:
    from http_parser.pyparser import HttpParser

class DataParser(object):
	def __init__(self, path_to_data):
		self.data = [] # each element is one line in data
		self.idx = 0 # current line
		self.length = 0 # number of lines
		self.cnt = 0 # number of requests
		
		with open(path_to_data, 'r') as f:
			# split file content by newline
			# since newline in file content is mixed by \r\n and \n
			# we should replace \r\n by \n first
			lines = f.read().replace('\r\n', '\n').split('\n')
		# concat each line with \r\n to reconstruct them
		self.data = [line + '\r\n' for line in lines]
		# number of lines
		self.length = len(self.data)
	
	def getNextReq(self):
		p = HttpParser()
		wr = ""
		
		# loop until getting a complete request
		while not p.is_message_complete():
			line = self.data[self.idx]
			wr = wr + line
			
			p.execute(line, len(line))
			self.idx += 1
			# Oops, reach the end of the file but this request is 
			# not completed, so return None here
			if self.idx >= self.length:
				return [None,None]
		self.cnt += 1 # increase the number of requests
		self.idx += 1 # skip empty line between 2 requests
		return [p,wr]
	
	def hasNextReq(self):
		return self.idx < self.length
