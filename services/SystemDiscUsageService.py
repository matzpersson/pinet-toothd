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

class SystemDiscUsageService(Service):

    SERVICE_UUID = '998A'
    SERVICE_NAME = "SystemDiscUsageService"

    def __init__(self, bus, index, logger):
        Service.__init__(self, bus, index, self.SERVICE_UUID, True)

        self.name = "SystemDiscUsageService"
        self.add_characteristic(SystemDiscUsageValueCharacteristic(bus, 0, self, logger))
        self.add_characteristic(SystemDiscUsageGroupCharacteristic(bus, 1, self))
        self.add_characteristic(SystemDiscUsageNameCharacteristic(bus, 2, self))
        self.add_characteristic(SystemDiscUsageTypeCharacteristic(bus, 3, self))

class SystemDiscUsageValueCharacteristic(Characteristic):

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
            self.logger.info(self.service.SERVICE_NAME + " - Reading Disk Usage")

            data = [{"value": osc.df() }]
            self.value = array.array('B', json.dumps(data))
            self.value = self.value.tolist()        
            return dbus.Array(self.value)

        except:
            self.logger.info("Error")

class SystemDiscUsageGroupCharacteristic(Characteristic):

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

class SystemDiscUsageNameCharacteristic(Characteristic):

    CHARACS_UUID = '900C'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index,
            self.CHARACS_UUID,
            ['read'],
            service)

    def ReadValue(self):

        data = [{"name": "Current Disk Usage"}]
        self.value = array.array('B', json.dumps(data))
        self.value = self.value.tolist()        
        return dbus.Array(self.value)

class SystemDiscUsageTypeCharacteristic(Characteristic):

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