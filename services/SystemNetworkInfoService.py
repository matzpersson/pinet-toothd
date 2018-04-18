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

class SystemNetworkInfoService(Service):

    SERVICE_UUID = '995A'
    SERVICE_NAME = "SystemNetworkInfoService"

    def __init__(self, bus, index, logger):
        Service.__init__(self, bus, index, self.SERVICE_UUID, True)
        self.add_characteristic(SystemNetworkInfoValueCharacteristic(bus, 0, self, logger))
        self.add_characteristic(SystemNetworkInfoGroupCharacteristic(bus, 1, self))
        self.add_characteristic(SystemNetworkInfoNameCharacteristic(bus, 2, self))
        self.add_characteristic(SystemNetworkInfoTypeCharacteristic(bus, 3, self))

class SystemNetworkInfoValueCharacteristic(Characteristic):

    CHARACS_UUID = '900A'

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
            self.logger.info(self.service.SERVICE_NAME + " - Get Ip Address")

            network = osc.getNetwork()

            data = [{"value": network['ip']}]
            self.value = array.array('B', json.dumps(data))
            self.value = self.value.tolist()        
            return dbus.Array(self.value)

        except:
            self.logger.info("Error")

class SystemNetworkInfoGroupCharacteristic(Characteristic):

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

class SystemNetworkInfoNameCharacteristic(Characteristic):

    CHARACS_UUID = '900C'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index,
            self.CHARACS_UUID,
            ['read'],
            service)

    def ReadValue(self):

        data = [{"name": "IP Address"}]
        self.value = array.array('B', json.dumps(data))
        self.value = self.value.tolist()        
        return dbus.Array(self.value)

class SystemNetworkInfoTypeCharacteristic(Characteristic):

    CHARACS_UUID = '900D'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index,
            self.CHARACS_UUID,
            ['read'],
            service)

    def ReadValue(self):

        data = [{"type": "label"}]
        self.value = array.array('B', json.dumps(data))
        self.value = self.value.tolist()        
        return dbus.Array(self.value)
