#Copyrigth 2017 by Thanh LE DINH
#VNU University of Engineering and Technology

import abc
from util import *
import pickle

class Model(dict):
	@abc.abstractmethod
	def isNormal(self, req, wr, threshold):
		pass

	@abc.abstractmethod
	def execute(self, req, wr):
		pass

	@abc.abstractmethod
	def commit(self):
		pass

class CST(Model):
	def __init__(self):
		super(Model, self).__init__()
		self.traindata = dict()

	# training phase
	def execute(self, req, wr):
		key = req.get_method() + req.get_path()
		
		if not key in self.traindata:
			self.traindata[key] = dict()
		di = self.traindata[key]
		
		header = req.get_headers()
		body = parse_params(req.recv_body())
		query = parse_params(req.get_query_string())
		for k in header:
			if not k in di:
				di[k] = []
			di[k].append(char_distribution(header[k]))
		for k in body:
			if not k in di:
				di[k] = []
			di[k].append(char_distribution(body[k]))
		for k in query:
			if not k in di:
				di[k] = []
			di[k].append(char_distribution(query[k]))
	
	# generate model
	def commit(self):
		for key in self.traindata:
			di = self.traindata[key]
			self[key] = dict()
			m = self[key]
			for field in di:
				values = di[field]
				m[field] = dict()
				if len(values) == 0:
					continue
				res = [0] * 256
				for v in values:
					for i in range(256):
						res[i] += v[i]
				f_len = sum(res)
				for i in range(256):
					res[i] = res[i] * 1.0 / f_len
				# icd = idealized character distribution
				m[field]['icd'] = to_6bin(res)

	def isNormal(self, req, wr, threshold):
		key = req.get_method() + req.get_path()
	
		if not key in self:
			return False
		
		# compute character frequency of observed request
		header = req.get_headers()
		body = parse_params(req.recv_body())
		query = parse_params(req.get_query_string())
		di = {}
		for k in header:
			di[k] = char_freq(header[k])
		for k in body:
			di[k] = char_freq(body[k])
		for k in query:
			di[k] = char_freq(query[k])
		m = self[key]
		for k in di:
			if not k in m:
				return False
			icd = m[k]['icd']
			f_len = sum(di[k])
			di[k] = to_6bin(di[k])
			ss = 0
			value = 0
			# expect = idealized character distribution * length
			# chisquare = sum( (obs_i - expect_i) ^ 2 / expect_i )
			# i = 0..5 (1..6 if index from 1)
			# if expect_i = 0 and obs != 0
			#	(obs_i - expect_i) ^ 2 / expect_i = infinity
			#	then chisquare distribution = 0
			for i in range(6):
				expect = icd[i] * f_len
				obs = di[k][i]
				if expect != 0:
					value += ((obs - expect) ** 2) * 1.0 / expect
				elif obs != 0:
					return False
			# the degree of freedom is 5 (= (2 - 1) * (6 - 1))
			p = chisquare_distribution(value, 5)
			#print p
			if p < threshold:
				return False
		return True


class CSTplus(Model):
	def __init__(self):
		super(Model, self).__init__()
		self.traindata = dict()

	# training phase
	def execute(self, req, wr):
		key = req.get_method() + req.get_path()
		
		if not key in self.traindata:
			self.traindata[key] = dict()
		di = self.traindata[key]
		
		header = req.get_headers()
		body = parse_params(req.recv_body())
		query = parse_params(req.get_query_string())
		for k in header:
			if not k in di:
				di[k] = []
			di[k].append(char6_distribution(header[k]))
		for k in body:
			if not k in di:
				di[k] = []
			di[k].append(char6_distribution(body[k]))
		for k in query:
			if not k in di:
				di[k] = []
			di[k].append(char6_distribution(query[k]))
	
	# generate model
	def commit(self):
		for key in self.traindata:
			di = self.traindata[key]
			self[key] = dict()
			m = self[key]
			for field in di:
				values = di[field]
				m[field] = dict()
				if len(values) == 0:
					continue
				res = [0] * 6
				for v in values:
					for i in range(6):
						res[i] += v[i]
				f_len = sum(res)
				for i in range(6):
					res[i] = res[i] * 1.0 / f_len
				# icd = idealized character distribution
				res.sort()
				m[field]['icd'] = res[::-1]

	def isNormal(self, req, wr, threshold):
		key = req.get_method() + req.get_path()
	
		if not key in self:
			return False
		
		# compute character frequency of observed request
		header = req.get_headers()
		body = parse_params(req.recv_body())
		query = parse_params(req.get_query_string())
		di = {}
		for k in header:
			di[k] = char6_freq(header[k])
		for k in body:
			di[k] = char6_freq(body[k])
		for k in query:
			di[k] = char6_freq(query[k])
		m = self[key]
		for k in di:
			if not k in m:
				return False
			icd = m[k]['icd']
			f_len = sum(di[k])
			di[k].sort()
			di[k] = di[k][::-1]
			ss = 0
			value = 0
			# expect = idealized character distribution * length
			# chisquare = sum( (obs_i - expect_i) ^ 2 / expect_i )
			# i = 0..5 (1..6 if index from 1)
			# if expect_i = 0 and obs != 0
			#	(obs_i - expect_i) ^ 2 / expect_i = infinity
			#	then chisquare distribution = 0
			for i in range(6):
				expect = icd[i] * f_len
				obs = di[k][i]
				if expect != 0:
					value += ((obs - expect) ** 2) * 1.0 / expect
				elif obs != 0:
					return False
			# the degree of freedom is 5 (= (2 - 1) * (6 - 1))
			p = chisquare_distribution(value, 5)
			#print p
			if p < threshold:
				return False
		return True



class PAYL(Model):
	def __init__(self):
		super(Model, self).__init__()
		self.traindata = dict()

	def execute(self, req, wr):
		key = req.get_method() + req.get_path()
		if not key in self.traindata:
			self.traindata[key] = dict()
	
		di = self.traindata[key]
		if not 0 in di:
			di[0] = []
		di[0].append(char_distribution(wr))
	
	def commit(self):
		for key in self.traindata:
			di = self.traindata[key]
			self[key] = dict()
			m = self[key]
			for field in di:
				values = di[field]
				m[field] = dict()
				m[field]['mean'] = mean_matrix(values)
				m[field]['deviation'] = standard_deviation(values)

	def isNormal(self, req, wr, threshold):
		key = req.get_method() + req.get_path()
	
		if not key in self:
			#print "key not found: " + key
			return False

		di = {}
		di[0] = char_distribution(wr)
		m = self[key]
		# distance = sum( | obs_i - mean_i | / (deviation_i + alpha))
		# alpha is smooth factor
		# i chose alpha = 0.0001 but it can be any small values
		for k in di:
			if not k in m:
				return False
			mean = m[k]['mean']
			deviation = m[k]['deviation']
			obs = di[k]
			distance = 0
			alpha = 0.0001
			for i in range(256):
				distance += abs(obs[i] - mean[i]) / (deviation[i] + alpha) 
			if distance > threshold:
				return False
		return True

class PAYLplus(Model):
	def __init__(self):
		super(Model, self).__init__()
		self.traindata = dict()

	def execute(self, req, wr):
		key = req.get_method() + req.get_path()
		if not key in self.traindata:
			self.traindata[key] = dict()
	
		di = self.traindata[key]
		if not 0 in di:
			di[0] = []
		di[0].append(char6_distribution(wr))
	
	def commit(self):
		for key in self.traindata:
			di = self.traindata[key]
			self[key] = dict()
			m = self[key]
			for field in di:
				values = di[field]
				m[field] = dict()
				m[field]['mean'] = mean_matrix(values)
				m[field]['deviation'] = standard_deviation(values)

	def isNormal(self, req, wr, threshold):
		key = req.get_method() + req.get_path()
	
		if not key in self:
			return False
	
		di = {}
		di[0] = char6_distribution(wr)
		m = self[key]
		# distance = sum( | obs_i - mean_i | / (deviation_i + alpha))
		# alpha is smooth factor
		# i chose alpha = 0.0001 but it can be any small values
		for k in di:
			if not k in m:
				return False
			mean = m[k]['mean']
			deviation = m[k]['deviation']
			obs = di[k]
			distance = 0
			alpha = 0.0001
			for i in range(6):
				distance += abs(obs[i] - mean[i]) / (deviation[i] + alpha) 
			if distance > threshold:
				return False
		return True


class PAYLa(Model):
	def __init__(self):
		super(Model, self).__init__()
		self.traindata = dict()

	def execute(self, req, wr):
		key = req.get_method() + req.get_path()
		if not key in self.traindata:
			self.traindata[key] = dict()
	
		di = self.traindata[key]
		header = req.get_headers()
		body = parse_params(req.recv_body())
		query = parse_params(req.get_query_string())
		for k in header:
			if not k in di:
				di[k] = []
			di[k].append(char_distribution(header[k]))
		for k in body:
			if not k in di:
				di[k] = []
			di[k].append(char_distribution(body[k]))
		for k in query:
			if not k in di:
				di[k] = []
			di[k].append(char_distribution(query[k]))
	
	def commit(self):
		for key in self.traindata:
			di = self.traindata[key]
			self[key] = dict()
			m = self[key]
			for field in di:
				values = di[field]
				m[field] = dict()
				m[field]['mean'] = mean_matrix(values)
				m[field]['deviation'] = standard_deviation(values)

	def isNormal(self, req, wr, threshold):
		key = req.get_method() + req.get_path()
	
		if not key in self:
			return False
	
		header = req.get_headers()
		body = parse_params(req.recv_body())
		query = parse_params(req.get_query_string())
		di = {}
		for k in header:
			di[k] = char_distribution(header[k])
		for k in body:
			di[k] = char_distribution(body[k])
		for k in query:
			di[k] = char_distribution(query[k])
		m = self[key]
		# distance = sum( | obs_i - mean_i | / (deviation_i + alpha))
		# alpha is smooth factor
		# i chose alpha = 0.0001 but it can be any small values
		for k in di:
			if not k in m:
				return False
			mean = m[k]['mean']
			deviation = m[k]['deviation']
			obs = di[k]
			distance = 0
			alpha = 0.0001
			for i in range(256):
				distance += abs(obs[i] - mean[i]) / (deviation[i] + alpha) 
			#print distance
			if distance > threshold:
				return False
		return True


class PAYLplusa(Model):
	def __init__(self):
		super(Model, self).__init__()
		self.traindata = dict()

	def execute(self, req, wr):
		key = req.get_method() + req.get_path()
		if not key in self.traindata:
			self.traindata[key] = dict()
	
		di = self.traindata[key]
		header = req.get_headers()
		body = parse_params(req.recv_body())
		query = parse_params(req.get_query_string())
		for k in header:
			if not k in di:
				di[k] = []
			di[k].append(char6_distribution(header[k]))
		for k in body:
			if not k in di:
				di[k] = []
			di[k].append(char6_distribution(body[k]))
		for k in query:
			if not k in di:
				di[k] = []
			di[k].append(char6_distribution(query[k]))
	
	def commit(self):
		for key in self.traindata:
			di = self.traindata[key]
			self[key] = dict()
			m = self[key]
			for field in di:
				values = di[field]
				m[field] = dict()
				m[field]['mean'] = mean_matrix(values)
				m[field]['deviation'] = standard_deviation(values)

	def isNormal(self, req, wr, threshold):
		key = req.get_method() + req.get_path()
	
		if not key in self:
			return False
	
		header = req.get_headers()
		body = parse_params(req.recv_body())
		query = parse_params(req.get_query_string())
		di = {}
		for k in header:
			di[k] = char6_distribution(header[k])
		for k in body:
			di[k] = char6_distribution(body[k])
		for k in query:
			di[k] = char6_distribution(query[k])
		m = self[key]
		# distance = sum( | obs_i - mean_i | / (deviation_i + alpha))
		# alpha is smooth factor
		# i chose alpha = 0.0001 but it can be any small values
		for k in di:
			if not k in m:
				return False
			mean = m[k]['mean']
			deviation = m[k]['deviation']
			obs = di[k]
			distance = 0
			alpha = 0.00001
			for i in range(6):
				distance += abs(obs[i] - mean[i]) / (deviation[i] + alpha) 
			#print distance
			if distance > threshold:
				return False
		return True



class CSTr(Model):
	def __init__(self):
		super(Model, self).__init__()
		self.traindata = dict()

	# training phase
	def execute(self, req, wr):
		key = req.get_method() + req.get_path()
		
		if not key in self.traindata:
			self.traindata[key] = dict()
		di = self.traindata[key]
		
		if not 0 in di:
			di[0] = []
		di[0].append(char_distribution(wr))
		
	# generate model
	def commit(self):
		for key in self.traindata:
			di = self.traindata[key]
			self[key] = dict()
			m = self[key]
			for field in di:
				values = di[field]
				m[field] = dict()
				if len(values) == 0:
					continue
				res = [0] * 256
				for v in values:
					for i in range(256):
						res[i] += v[i]
				f_len = sum(res)
				for i in range(256):
					res[i] = res[i] * 1.0 / f_len
				# icd = idealized character distribution
				m[field]['icd'] = to_6bin(res)

	def isNormal(self, req, wr, threshold):
		key = req.get_method() + req.get_path()
	
		if not key in self:
			return False
		
		# compute character frequency of observed request
		di = {}
		di[0] = char_freq(wr)
		m = self[key]
		#print "new request"
		for k in di:
			if not k in m:
				return False
			icd = m[k]['icd']
			f_len = sum(di[k])
			di[k] = to_6bin(di[k])
			ss = 0
			value = 0
			# expect = idealized character distribution * length
			# chisquare = sum( (obs_i - expect_i) ^ 2 / expect_i )
			# i = 0..5 (1..6 if index from 1)
			# if expect_i = 0 and obs != 0
			#	(obs_i - expect_i) ^ 2 / expect_i = infinity
			#	then chisquare distribution = 0
			for i in range(6):
				expect = icd[i] * f_len
				obs = di[k][i]
				if expect != 0:
					value += ((obs - expect) ** 2) * 1.0 / expect
				elif obs != 0:
					return False
			# the degree of freedom is 5 (= (2 - 1) * (6 - 1))
			p = chisquare_distribution(value, 5)
			#print p
			if p < threshold:
				return False
		return True




class CSTplusr(Model):
	def __init__(self):
		super(Model, self).__init__()
		self.traindata = dict()

	# training phase
	def execute(self, req, wr):
		key = req.get_method() + req.get_path()
		
		if not key in self.traindata:
			self.traindata[key] = dict()
		di = self.traindata[key]
		
		if not 0 in di:
			di[0] = []
		di[0].append(char6_distribution(wr))
		
	# generate model
	def commit(self):
		for key in self.traindata:
			di = self.traindata[key]
			self[key] = dict()
			m = self[key]
			for field in di:
				values = di[field]
				m[field] = dict()
				if len(values) == 0:
					continue
				res = [0] * 6
				for v in values:
					for i in range(6):
						res[i] += v[i]
				f_len = sum(res)
				for i in range(6):
					res[i] = res[i] * 1.0 / f_len
				# icd = idealized character distribution
				res.sort()
				m[field]['icd'] = res[::-1]

	def isNormal(self, req, wr, threshold):
		key = req.get_method() + req.get_path()
	
		if not key in self:
			return False
		
		# compute character frequency of observed request
		di = {}
		di[0] = char6_freq(wr)
		m = self[key]
		#print "new request"
		for k in di:
			if not k in m:
				return False
			icd = m[k]['icd']
			f_len = sum(di[k])
			di[k].sort()
			di[k] = di[k][::-1]
			ss = 0
			value = 0
			# expect = idealized character distribution * length
			# chisquare = sum( (obs_i - expect_i) ^ 2 / expect_i )
			# i = 0..5 (1..6 if index from 1)
			# if expect_i = 0 and obs != 0
			#	(obs_i - expect_i) ^ 2 / expect_i = infinity
			#	then chisquare distribution = 0
			for i in range(6):
				expect = icd[i] * f_len
				obs = di[k][i]
				if expect != 0:
					value += ((obs - expect) ** 2) * 1.0 / expect
				elif obs != 0:
					return False
			# the degree of freedom is 5 (= (2 - 1) * (6 - 1))
			p = chisquare_distribution(value, 5)
			#print p
			if p < threshold:
				return False
		return True



