#Copyrigth 2017 by Thanh LE DINH
#VNU University of Engineering and Technology

from scipy.stats import chi2
import numpy as np
from numpy.linalg import pinv
import math
import time
import string

##--------------------------------------------------------------
# Parse query/body message
#	Ex:
#		id=100&sort=day
#		=> {"id": "100", "sort": "day"}
#---------------------------------------------------------------
def parse_params(q):
	if q == '':
		return {}
	# by convention query and body delimiter often be `&`
	# sometime it is `;` but our dataset only has `&`
	q = q.split('&')
	result = dict()
	for p in q:
		# param often in form `key=value`
		info = p.split('=')
		if len(info) != 2:
			continue
		key = info[0]
		value = info[1]
		result[key] = value
	return result

##--------------------------------------------------------------
# Calculate frequency of each character (in range 0 - 255)
#	Ex:
#		String is "hello",
#		the freq of `h`, `e`, `o` is 1, `l` is 2, others is 0
##--------------------------------------------------------------
def char_freq(s):
	res = [0] * 256
	for ch in s:
		res[ord(ch)] += 1
	return res

##--------------------------------------------------------------
# Calculate the left area of chisquare distribution at `value`
# the sum of the left and right distribution is 1.0
# the value of the right side is value of cumulative distribution
# function, so the value for the left is: 1.0 - cdf	
##--------------------------------------------------------------
def chisquare_distribution(value, degree_of_freedom):
	return 1.0 - chi2.cdf(value, degree_of_freedom)

##--------------------------------------------------------------
# Current time in timestamp format
##--------------------------------------------------------------
def get_time():
	return time.time()

##--------------------------------------------------------------
# Keruegel vingna 6-bin
# 	The sorted arr in descending order is splited into 6 segments
#		0, 1-3, 4-6, 7-11, 12-15, 16-255
#	
##--------------------------------------------------------------
def to_6bin(a):
	res = [0]* 6
	a.sort()
	a = a[::-1]
	res[0] = a[0]
	res[1] = sum(a[1:4])
	res[2] = sum(a[4:7])
	res[3] = sum(a[7:12])
	res[4] = sum(a[12:16])
	res[5] = sum(a[16:])
	return res

##-----------------------------------------------------------------
# Calculate relative frequency
#	Ex:
#		String "hello"
#		=>	`h`, `e`, `o` : 0.20;
#			`l`: 0.40
#
##-----------------------------------------------------------------
def char_distribution(s):
	res = char_freq(s)
	total = len(s)
	res = [freq * 1.0 / total for freq in res]
	return res
##-----------------------------------------------------------------
#
#
##-----------------------------------------------------------------
def char6_distribution(s):
	res = char6_freq(s)
	res = [cnt * 1.0 / len(s) for cnt in res]
	return res


def char6_freq(s):
	res = [0] * 6
	for ch in s:
		o = ord(ch)
		if o < 9 or (o > 13 and o < 32):
			res[0] += 1
		elif ch in string.digits:
			res[1] += 1
		elif ch in string.letters:
			res[2] += 1
		elif ch in '*=<>/\\.()\'"':
			res[3] += 1
		elif ch in string.punctuation:
			res[3] += 1
		elif ch in string.whitespace:
			res[4] += 1
		else:
			res[5] += 1
	return res
##-----------------------------------------------------------------
#	Matrix A:	[a11 a12 .. a1n]
#				[a21 a22 .. a2n]
#						...
#				[am1 am2 .. amn]
# => mean matrix of A:
#				[x1  x2  .. xn ]
#	xi = (a1i + a2i + .. + ami) / m
##-----------------------------------------------------------------
def mean_matrix(a):
	res = [0] * len(a[0])
	for row in a:
		for i in range(len(row)):
			res[i] += row[i]
	res = np.true_divide(res, len(a))
	return res

##-----------------------------------------------------------------
#	Matrix A:	[a11 a12 .. a1n]
#				[a21 a22 .. a2n]
#						...
#				[am1 am2 .. amn]
#   Mean matrix: [x1 x2  .. xn]
# => centre matrix of A:
#				[C11 C12 .. C1n]
#				[C21 C22 .. C2n]
#						...
#				[Cm1 Cm2 .. Cmn]]
#	Cij = aij - xi
##-----------------------------------------------------------------
def centre_matrix(a, m):
	res = np.subtract(a, m)
	return res

##-----------------------------------------------------------------
#	Covariance matrix = 1/n . (C^T . C)
#		C is center matrix
#
##-----------------------------------------------------------------
def covariance(a):
	m = mean_matrix(a)
	c = centre_matrix(a, m)
	C = np.array(c)
	res = np.dot(C.T, C)
	res = np.true_divide(res, len(a))
	return res

##-----------------------------------------------------------------
#
#
##-----------------------------------------------------------------
def standard_deviation(a):
	return np.std(a, axis=0)

##-----------------------------------------------------------------
#	Subtract 2 matrix
#
##-----------------------------------------------------------------	
def subtract(a, b):
	return np.subtract(a, b)

##-----------------------------------------------------------------
#	multiply 2 matrix
#
##-----------------------------------------------------------------
def multiply(a, b):
	return np.dot(a, b)

##-----------------------------------------------------------------
#
#
##-----------------------------------------------------------------
def isZero_matrix(a):
	n, m = a.shape
	for i in range(n):
		for j in range(m):
			if abs(a[i][j]) > 0.0001:
				 return False
	return True

def squareroot(a):
	return math.sqrt(a)

def pseudoinverse(a):
	return pinv(a)
