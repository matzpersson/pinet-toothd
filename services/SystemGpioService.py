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

class SystemGpioService(Service):

    SERVICE_UUID = '998A'
    SERVICE_NAME = "SystemGpioService"
    
    def __init__(self, bus, index, logger):
        Service.__init__(self, bus, index, self.SERVICE_UUID, True)
        self.add_characteristic(SystemGpioValueCharacteristic(bus, 0, self, logger))
        self.add_characteristic(SystemGpioGroupCharacteristic(bus, 1, self))
        self.add_characteristic(SystemGpioNameCharacteristic(bus, 2, self))
        self.add_characteristic(SystemGpioTypeCharacteristic(bus, 3, self))

class SystemGpioValueCharacteristic(Characteristic):

    CHARACS_UUID = '900A'

    def __init__(self, bus, index, service, logger):
        Characteristic.__init__(
            self, bus, index,
            self.CHARACS_UUID,
            ['read','write'],
            service)

        self.logger = logger

    def ReadValue(self):

        try:
            dummyGpioPort1Value = "True"

            data = [{"value": dummyGpioPort1Value }]
            self.value = array.array('B', json.dumps(data))
            self.value = self.value.tolist()        
            return dbus.Array(self.value)
        except:
            self.logger.info("Error")

    def WriteValue(self, value):

        try:
            self.logger.info( "Set GPIO Port to: " + bytearray(value).decode())
        except:
            self.logger.info("Error")

class SystemGpioGroupCharacteristic(Characteristic):

    CHARACS_UUID = '900B'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index,
            self.CHARACS_UUID,
            ['read'],
            service)

    def ReadValue(self):

        data = [{"group": "House"}]
        self.value = array.array('B', json.dumps(data))
        self.value = self.value.tolist()        
        return dbus.Array(self.value)

class SystemGpioNameCharacteristic(Characteristic):

    CHARACS_UUID = '900C'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index,
            self.CHARACS_UUID,
            ['read'],
            service)

    def ReadValue(self):

        data = [{"name": "Master Bedroom Light"}]
        self.value = array.array('B', json.dumps(data))
        self.value = self.value.tolist()        
        return dbus.Array(self.value)

class SystemGpioTypeCharacteristic(Characteristic):

    CHARACS_UUID = '900D'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index,
            self.CHARACS_UUID,
            ['read'],
            service)

    def ReadValue(self):

        data = [{"type": "switch"}]
        self.value = array.array('B', json.dumps(data))
        self.value = self.value.tolist()        
        return dbus.Array(self.value)
