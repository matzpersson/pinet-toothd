from GattServer import Service
from GattServer import Characteristic
from GattServer import Descriptor

from OSControl import OsControl

class SystemNetworkInfoService(Service):
    """
    Current Disc Usage Service
    """

    SERVICE_UUID = '995A'

    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.SERVICE_UUID, True)
        self.add_characteristic(SystemNetworkInfoValueCharacteristic(bus, 0, self))
        self.add_characteristic(SystemNetworkInfoGroupCharacteristic(bus, 1, self))
        self.add_characteristic(SystemNetworkInfoNameCharacteristic(bus, 2, self))

class SystemNetworkInfoValueCharacteristic(Characteristic):

    CHARACS_UUID = '900A'

    def __init__(self, bus, index, service):
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

        data = [{"name": "Current Disk Usage"}]
        self.value = array.array('B', json.dumps(data))
        self.value = self.value.tolist()        
        return dbus.Array(self.value)
