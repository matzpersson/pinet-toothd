import logging
from logging.handlers import TimedRotatingFileHandler
import os
import datetime
import time
import thread
import socket
import sys

def initLogging(logfile_prefix, level_name, log_name):

	datefmt='%Y-%m-%d %H:%M:%S'
	formatter = logging.Formatter(
		'%(asctime)s - %(message)s',
		datefmt
	)

	logger = logging.getLogger(log_name)
	logger.setLevel(logging.DEBUG)

	if logfile_prefix:
		LOG_FILENAME = 'logs/' + logfile_prefix + '.log'
	else:
		LOG_FILENAME = None

	logger.info('INIT')
	
	if (LOG_FILENAME):
		roll = TimedRotatingFileHandler(
			filename=LOG_FILENAME,
			when='midnight',
			interval=1,
			backupCount=30
		)
		roll.setFormatter(formatter)
		roll.suffix = '%Y-%m-%d'
		logger.addHandler(roll)
	else:
		logging.basicConfig(
			format='%(asctime)s - %(message)s',
			datefmt=datefmt,
			filename=LOG_FILENAME
		)
	        
	return logger 

def getHostname():
    return socket.gethostname()
    
def getIp():
    return [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]

class Thread:
    def __init__(self):
        self.logger = logger
        self.session = session
        self.running = False

    def Start(self):
        self.keepGoing = self.running = True
        thread.start_new_thread(self.Run, ())
        #self.logger.info('STARTED Thread')

    def Stop(self):
        self.keepGoing = False
        self.running = False
        #self.logger.info('STOPPED Thread')

    def Restart(self):
    	self.Stop()
    	self.Start()

    def IsRunning(self):
        if hasattr(self,'running'):
            return self.running
        else:
            return False
