#Copyrigth 2017 by Thanh LE DINH
#VNU University of Engineering and Technology

from dataParser import DataParser
from model import *
import logging
import time
import gc

logging.basicConfig(level=logging.INFO)

def testModel(mn, threshold_min, threshold_step):
	print mn
	model = None
	if mn == "CST":
		model = CST()
	elif mn == "CSTplus":
		model = CSTplus()
	elif mn == "CSTr":
		model = CSTr()
	elif mn == "CSTplusr":
		model = CSTplusr()
	elif mn == "PAYL":
		model = PAYL()
	elif mn == "PAYLplus":
		model = PAYLplus()
	elif mn == "PAYLa":
		model = PAYLa()
	elif mn == "PAYLplusa":
		model = PAYLplusa()
	else:
		print "Model not found"
		return
	
	#Learning = Building the model
	data = DataParser('dataset/normalTrafficTraining.txt')
	cntTraining = 0
	while data.hasNextReq():
		[req, wr] = data.getNextReq()
		if req:
			cntTraining += 1
			model.execute(req, wr)
	model.commit()
	for i in range(2000):
		#Detection
		intervalPos = 0.0
		intervalNeg = 0.0
		
		#normal requests
		data = DataParser('dataset/normalTrafficTest.txt')
		cntNormal = 0
		wrong = 0
		while data.hasNextReq():
			[req, wr] = data.getNextReq()
			if req:
				cntNormal += 1
				tstart = time.clock()
				isPos = not model.isNormal(req, wr, threshold_min + i*threshold_step)
				tend = time.clock()
				if isPos:
					wrong += 1
					intervalPos = intervalPos + tend - tstart
				else:
					intervalNeg = intervalNeg + tend - tstart
		
		#anomalous requests
		data = DataParser('dataset/anomalousTrafficTest.txt')
		cntAnomalous = 0
		right = 0
		while data.hasNextReq():
			[req, wr] = data.getNextReq()
			if req:
				cntAnomalous += 1
				tstart = time.clock()
				isPos = not model.isNormal(req, wr, threshold_min + i*threshold_step)
				tend = time.clock()
				if isPos:
					right += 1
					intervalPos = intervalPos + tend - tstart
				else:
					intervalNeg = intervalNeg + tend - tstart
 
		
		#FalsePositiveRate (%) TruePositiveRate(%) ProcessingTimePerPositivePacket(ms) ProcessingTimePerNegativePacket(ms)
		if cntNormal+cntAnomalous-wrong-right > 0 and wrong+right > 0:
			print (wrong*100.0/cntNormal), (right*100.0/cntAnomalous), (intervalPos*1000/(wrong+right)), (intervalNeg*1000/(cntNormal+cntAnomalous-wrong-right)) 
		
		data = None
		gc.collect()



#testModel("CST", 0.0001, 0.0001)
#testModel("CSTplus", 0.0000001, 0.0000001)
#testModel("CSTplus", 0.0000201, 0.0000005)
#testModel("CSTplus", 0.0000241, 0.000001)
#testModel("CSTplus", 0.0003241, 0.00005)
#testModel("CSTplus", 0.0032882, 0.00000001)
#testModel("CSTr", 0.83, 0.005)
#testModel("CSTplusr", 0.0000000001, 0.0000000001)

#testModel("PAYL", 63.5, 0.1)
#testModel("PAYLplus", 6.00, 0.02)
#testModel("PAYLa", 50, 1)
testModel("PAYLplusa", 8.5, 0.01)


