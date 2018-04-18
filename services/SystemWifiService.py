import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service
import array

from GattServer import Service
from GattServer import Characteristic
from GattServer import Descriptor

from OSControl import OsControl
import json

class SystemWifiService(Service):

    SERVICE_UUID = '996A'
    SERVICE_NAME = "SystemWifiService"

    def __init__(self, bus, index, logger):
        Service.__init__(self, bus, index, self.SERVICE_UUID, True)
        self.add_characteristic(SystemWifiValueCharacteristic(bus, 0, self, logger))
        self.add_characteristic(SystemWifiGroupCharacteristic(bus, 1, self))
        self.add_characteristic(SystemWifiNameCharacteristic(bus, 2, self))
        self.add_characteristic(SystemWifiTypeCharacteristic(bus, 3, self))
        self.add_characteristic(SystemWifiListCharacteristic(bus, 4, self, logger))

class SystemWifiValueCharacteristic(Characteristic):

    CHARACS_UUID = '900A'

    def __init__(self, bus, index, service, logger):
        Characteristic.__init__(
            self, bus, index,
            self.CHARACS_UUID,
            ['read', 'write'],
            service)

        self.logger = logger

    def ReadValue(self):

        try:
            osc = OsControl(self.logger)
            self.logger.info(self.service.SERVICE_NAME + " - Getting current ESSID")

            data = [{"value": osc.getCurrentAp() }]
            self.value = array.array('B', json.dumps(data))
            self.value = self.value.tolist()        
            return dbus.Array(self.value)

        except:
            self.logger.info("Error")

    def WriteValue(self, value):

        try:

            self.logger.info( "Set accesspoint to: " + bytearray(value).decode())

            ## -- Uncomment to actually set wifi point
            ##osc = OsControl(self.logger)
            ##osc.networkWifiDhcp()

        except:
            self.logger.info("Error")

class SystemWifiGroupCharacteristic(Characteristic):

    CHARACS_UUID = '900B'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index,
            self.CHARACS_UUID,
            ['read'],
            service)

    def ReadValue(self):

        data = [{"group": "System"}]
        self.value = array.array('B', json.dumps(data))
        self.value = self.value.tolist()        
        return dbus.Array(self.value)

class SystemWifiNameCharacteristic(Characteristic):

    CHARACS_UUID = '900C'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index,
            self.CHARACS_UUID,
            ['read'],
            service)

    def ReadValue(self):

        data = [{"name": "Current Wifi Access Point"}]
        self.value = array.array('B', json.dumps(data))
        self.value = self.value.tolist()        
        return dbus.Array(self.value)

class SystemWifiTypeCharacteristic(Characteristic):

    CHARACS_UUID = '900D'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index,
            self.CHARACS_UUID,
            ['read'],
            service)

    def ReadValue(self):

        data = [{"type": "lookup"}]
        self.value = array.array('B', json.dumps(data))
        self.value = self.value.tolist()        
        return dbus.Array(self.value)

class SystemWifiListCharacteristic(Characteristic):

    CHARACS_UUID = '900E'

    def __init__(self, bus, index, service, logger):
        Characteristic.__init__(
            self, bus, index,
            self.CHARACS_UUID,
            ['read'],
            service)

        self.logger = logger

    def ReadValue(self):

        try:
            osc = OsControl(self.logger)
            self.logger.info("Scanning for list of Wifi Access Points...")

            data = [{"list": osc.getApList()}]
            self.value = array.array('B', json.dumps(data))
            self.value = self.value.tolist()        
            return dbus.Array(self.value)

        except:
            self.logger.info("Error")

