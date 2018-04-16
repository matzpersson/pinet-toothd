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
    """
    Current Disc Usage Service
    """

    SERVICE_UUID = '998A'
    SERVICE_NAME = "SystemGpioService"
    
    def __init__(self, bus, index, logger):
        Service.__init__(self, bus, index, self.SERVICE_UUID, True)
        self.add_characteristic(SystemDiscUsageValueCharacteristic(bus, 0, self, logger))
        self.add_characteristic(SystemDiscUsageGroupCharacteristic(bus, 1, self))
        self.add_characteristic(SystemDiscUsageNameCharacteristic(bus, 2, self))

class SystemGpioValueCharacteristic(Characteristic):

    CHARACS_UUID = '900A'

    def __init__(self, bus, index, service, logger):
        Characteristic.__init__(
            self, bus, index,
            self.CHARACS_UUID,
            ['read'],
            service)


    def ReadValue(self):

        osc = OsControl(self.logger, self.default_scheduler)

        data = [{"value": osc.df() }]
        self.value = array.array('B', json.dumps(data))
        self.value = self.value.tolist()        
        return dbus.Array(self.value)

class SystemGpioGroupCharacteristic(Characteristic):

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

class SystemGpioNameCharacteristic(Characteristic):

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
