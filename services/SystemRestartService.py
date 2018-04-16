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

class SystemRestartService(Service):

    SERVICE_UUID = '997A'
    SERVICE_NAME = "SystemRestartService"

    def __init__(self, bus, index,logger):
        Service.__init__(self, bus, index, self.SERVICE_UUID, True)
        self.add_characteristic(SystemRestartValueCharacteristic(bus, 0, self, logger))
        self.add_characteristic(SystemRestartGroupCharacteristic(bus, 1, self))
        self.add_characteristic(SystemRestartNameCharacteristic(bus, 2, self))
        self.add_characteristic(SystemRestartTypeCharacteristic(bus, 3, self))

class SystemRestartValueCharacteristic(Characteristic):

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
            #osc = OsControl(self.logger)
            #self.logger.info(self.service.SERVICE_NAME + " - Restarting System")

            data = [{"value": ""}]
            self.value = array.array('B', json.dumps(data))
            self.value = self.value.tolist()        
            return dbus.Array(self.value)

        except:
            self.logger.info("Error")

    def WriteValue(self, value):

        try:
            self.logger.info(self.service.SERVICE_NAME + " - Restarting System")
            osc = OsControl(self.logger)
            osc.restart()
        except:
            self.logger.info("Error")

class SystemRestartGroupCharacteristic(Characteristic):

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

class SystemRestartNameCharacteristic(Characteristic):

    CHARACS_UUID = '900C'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index,
            self.CHARACS_UUID,
            ['read'],
            service)

    def ReadValue(self):

        data = [{"name": "Restart Server"}]
        self.value = array.array('B', json.dumps(data))
        self.value = self.value.tolist()        
        return dbus.Array(self.value)

class SystemRestartTypeCharacteristic(Characteristic):

    CHARACS_UUID = '900D'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index,
            self.CHARACS_UUID,
            ['read'],
            service)

    def ReadValue(self):

        data = [{"type": "button"}]
        self.value = array.array('B', json.dumps(data))
        self.value = self.value.tolist()        
        return dbus.Array(self.value)
