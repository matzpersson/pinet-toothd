import datetime
import time
import Tools as tools

import os
import subprocess
import json
import uuid

class OsControl():
	def __init__(self, logger):
		self.logger = logger
		self.prefix = "OS Control - "

	def health(self):

		health = [{'diskusage': self.df, 'uptime': self.uptime() }]
		return health

	def uptime(self):

		return 0

	def df(self):

		cmd = 'df -m | grep /dev/root | cut -c 41-45'
		ps = subprocess.Popen(cmd , shell=True, stdout=subprocess.PIPE)
		lines = ps.stdout.read()

		return lines.replace(' ','').replace('\n','')

	def restart(self):

		self.logger.info(self.prefix + 'Restart Server by API')
		cmd = "shutdown -r now"
		os.system(cmd)

		return json.dumps("")

	def orientation(self, orientation):

		options = {"normal": 0, "left": 3, "right": 1, "180": 2}

		filename = "/boot/config.txt"
		f = open(filename, 'w')

		f.write('dtparam=audio=on\n')
		f.write('gpu_mem=128\n')
		f.write("display_rotate=" + str(options[orientation]) + '\n')
		f.close()
		
		self.logger.info(self.prefix + 'Display rotated to ' + orientation + '. Requires reboot!')

		return json.dumps([{'rotate': orientation}])

	def networkEthDhcp(self):

		filename = "/etc/network/interfaces"
		f = open(filename, 'w')

		f.write('auto lo\n')
		f.write('iface lo inet loopback\n\n')

		f.write('auto eth0\n')
		f.write('iface eth0 inet dhcp\n')

		f.close()

		## -- Disable hostapd and dnsmasq. Requires restart
		filename = '/etc/init.d/dnsmasq'
		if os.path.isfile(filename):
			os.rename(filename, filename + ".off")

		filename = '/etc/init.d/hostapd'
		if os.path.isfile(filename):
			os.rename(filename, filename + ".off")

		self.logger.info(self.prefix + 'Configured Ethernet DHCP!')

		return json.dumps([{'network': "ethernet (DHCP)"}])

	def networkWifiDhcp(self, ssid, psk):

		## -- Configure hotspot
		if not ssid or not psk:
			return json.dumps([{'failure': "Must pass both SSID and PSK"}])

		filename = "/etc/wpa_supplicant/wpa_supplicant.conf"
		f = open(filename, 'w')
		f.write('network={\n')
		f.write('   ssid="' + ssid + '"\n')
		f.write('   psk="' + psk + '"\n')
		f.write('}\n')

		f.close()

		## -- Configure Wifi
		filename = "/etc/network/interfaces"
		f = open(filename, 'w')

		f.write('auto lo\n')
		f.write('iface lo inet loopback\n\n')

		f.write('auto wlan\n')
		f.write('allow-hotplug wlan0\n')
		f.write('iface wlan0 inet manual\n')
		f.write('    wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf\n')

		f.close()

		self.logger.info(self.prefix + 'Configured Wifi DHCP!')

		return json.dumps([{'network': "wifi (DHCP)"}])

	def getApList(self, iface = 'wlan0'):

		cmd = 'iwlist ' + iface + ' scan | grep ESSID'
		ps = subprocess.Popen(cmd , shell=True, stdout=subprocess.PIPE)
		lines = ps.stdout.read()

		## -- Yikes...
		return lines.replace(' ','').replace('ESSID:', '').replace('"','')[:-1].split('\n')

	def getCurrentAp(self):

		cmd = 'iwconfig wlan0 | grep ESSID | cut -c 30-100'

		ps = subprocess.Popen(cmd , shell=True, stdout=subprocess.PIPE)
		lines = ps.stdout.read()

		return lines.replace('"','').replace('\n','').replace(' ','')

	def networkHotspot(self):

		## -- Configure Hotspot
		filename = "/etc/network/interfaces"
		f = open(filename, 'w')

		f.write('auto lo\n')
		f.write('iface lo inet loopback\n\n')

		f.write('auto wlan\n')
		f.write('allow-hotplug wlan0\n')
		f.write('iface wlan0 inet static\n')
		f.write('    address 192.168.50.1\n')

		f.close()

		## -- Enable hostapd and dnsmasq. Requires restart
		filename = '/etc/init.d/dnsmasq'
		if os.path.isfile(filename+".off"):
			os.rename(filename+".off", filename)

		filename = '/etc/init.d/hostapd'
		if os.path.isfile(filename+".off"):
			os.rename(filename+".off", filename)

		self.logger.info(self.prefix + 'Configured Hotspot!')

		return json.dumps([{'network': "Hostspot, requires restart"}])

	def getNetwork(self):

		return {'ip': tools.getIp(), 'hostname': tools.getHostname()}

