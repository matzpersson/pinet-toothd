import os
import sys
import datetime
import logging
import time

sys.path.append('./lib/')

import Tools as tools
from Advertisement import Advert
from Services import Services

#logfile_prefix = "signd"
logfile_prefix = None
## -- If logprefix is null, output is to console otherwise into todays log file
#logfile_prefix = config.get('local', 'logfile_prefix')

level_name = 'info'
logger = tools.initLogging(logfile_prefix, level_name, 'toothd')

logger.info('## --------------------------------- ##') 
logger.info('## ---- Running Toothd Daemon  ---- ##') 
logger.info('## --------------------------------- ##') 

logger.info("Node Ip Address: " + tools.getIp() ) 
logger.info("Node Hostname: " + tools.getHostname() ) 

advert = Advert(logger)
advert.Start()

services = Services(logger)
services.Start()

while True:

	i = raw_input()
	if i == 'q':
		
		advert.Stop()
		services.Stop()

		logger.info("Bye...")
		sys.exit()
