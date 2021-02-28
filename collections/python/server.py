import os
import sys
import logging
import threading
import time
from jsonlogging import *
from metrics import MetricsClient

sys.path.append('./services')
# from diarization import Diarization
# from enhancedTranscript import EnhancedTranscript
# from premiumEnsemble import Premium_Ensemble
# from voiceaEnsemble import Voicea_Ensemble 
# from tmSegment import TM_Segment 
# from enhancedHighlight import EnhancedHighlight
# from activeMeetings import ActiveMeetings
# from forLambda import ForLambda
# from forOptimus import ForOptimus
# from example import Example

# metricsClient = MetricsClient()

class sharderThread(name, threading.Thread):
	def __init__(self, metric):
		threading.Thread.__init__(self)
		self.metric = metric
		self.metricName = metric.getMetricName()
		self.metricInterval = metric.getMetricInterval()
		try:
			metricsClient.createMetric(self.metricName)
		except Exception as e:
			LOG.error({"message":"Could not create, ensure metric does not already exist", "Exception":str(e)})
	
	def run(self):
		LOG.info({"message":"Starting: " + self.metric.getMetricName()})
		while True:
			metricValue = self.metric.getMetricValue()
			metricsClient.writeMetric(self.metricName, metricValue)
			time.sleep(self.metricInterval)			

def main():	
	# serviceObjects = [Diarization(), Example(), EnhancedTranscript(), 
	# 	   Voicea_Ensemble(), Premium_Ensemble(), 
	#        EnhancedHighlight(), ActiveMeetings(), 
	# 	   ForLambda(), ForOptimus(), TM_Segment()]
	TOTAL_THREAD = 3
	threadLock = threading.Lock()
	threads = []
	for ti in range(TOTAL_THREAD):
		#create new thread
		thread = sharderThead(ti)
		thread.start()
		threads.append(thread)
	
	# for serviceObject in serviceObjects:
	# 	# Create new thread
	# 	thread = metricThread(serviceObject)
	# 	# Start new Thread
	# 	thread.start()
	# 	# Add thread to thread list
	# 	threads.append(thread)

	# Wait for all threads to complete
	for t in threads:
		t.join()

	LOG.info({"message":"Exiting main thread"})

if __name__=='__main__':
	main()
