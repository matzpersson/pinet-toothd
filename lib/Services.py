import Tools as tools
import datetime
import os, sys, shutil
import time
from Tools import Thread
import json

import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service
import array
from gi.repository import GObject as gobject

from random import randint

from GattServer import Service
from GattServer import Characteristic
from GattServer import Descriptor

from services.SystemDiscUsageService import *
from services.SystemNetworkInfoService import *
from services.SystemRestartService import *
from services.SystemWifiService import *
from services.SystemGpioService import *

BLUEZ_SERVICE_NAME = 'org.bluez'
GATT_MANAGER_IFACE = 'org.bluez.GattManager1'
DBUS_OM_IFACE =      'org.freedesktop.DBus.ObjectManager'
DBUS_PROP_IFACE =    'org.freedesktop.DBus.Properties'

GATT_SERVICE_IFACE = 'org.bluez.GattService1'
GATT_CHRC_IFACE =    'org.bluez.GattCharacteristic1'
GATT_DESC_IFACE =    'org.bluez.GattDescriptor1'

mainloop = None
global_logger = None

class Services(Thread):
    def __init__(self, logger):

        self.logger = logger

        global global_logger 
        global_logger = self.logger

    def Run(self):

        self.logger.info('Starting Toothd Services')
        self.main()

    def Stop(self):
        self.logger.info('Shutting down Services')
        mainloop.quit()

    def register_service_cb(self):
        self.logger.info('Registered GATT Service')


    def register_service_error_cb(self, error):
        self.logger.info('Failed to register service: ' + str(error))
        mainloop.quit()


    def find_adapter(self, bus):
        remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'),
                                   DBUS_OM_IFACE)
        objects = remote_om.GetManagedObjects()

        for o, props in objects.iteritems():
            if props.has_key(GATT_MANAGER_IFACE):
                return o

        return None

    def main(self):
        global mainloop

        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

        bus = dbus.SystemBus()

        adapter = self.find_adapter(bus)
        if not adapter:
            print('GattManager1 interface not found')
            return

        service_manager = dbus.Interface(
                bus.get_object(BLUEZ_SERVICE_NAME, adapter),
                GATT_MANAGER_IFACE)

        #bat_service = BatteryService(bus, 0)
        #translation_service = TranslationService(bus, 1)
        discusage_service = SystemDiscUsageService(bus, 2, global_logger)
        networkinfo_service = SystemNetworkInfoService(bus, 3, global_logger)
        restart_service = SystemRestartService(bus, 4, global_logger)
        wifi_service = SystemWifiService(bus, 5, global_logger)
        gpio_service = SystemGpioService(bus, 6, global_logger)

        mainloop = gobject.MainLoop()

        #service_manager.RegisterService(bat_service.get_path(), {},
        #                                reply_handler=self.register_service_cb,
        #                                error_handler=self.register_service_error_cb)

        ##service_manager.RegisterService(translation_service.get_path(), {},
        ##                                reply_handler=self.register_service_cb,
        ##                                error_handler=self.register_service_error_cb)

        service_manager.RegisterService(gpio_service.get_path(), {},
                                        reply_handler=self.register_service_cb,
                                        error_handler=self.register_service_error_cb)

        service_manager.RegisterService(discusage_service.get_path(), {},
                                        reply_handler=self.register_service_cb,
                                        error_handler=self.register_service_error_cb)

        service_manager.RegisterService(networkinfo_service.get_path(), {},
                                        reply_handler=self.register_service_cb,
                                        error_handler=self.register_service_error_cb)   

        service_manager.RegisterService(restart_service.get_path(), {},
                                        reply_handler=self.register_service_cb,
                                        error_handler=self.register_service_error_cb) 

        service_manager.RegisterService(wifi_service.get_path(), {},
                                        reply_handler=self.register_service_cb,
                                        error_handler=self.register_service_error_cb) 
        
        mainloop.run()

class TranslationService(Service):
    """
    Fake Battery service that emulates a draining battery.

    """
    TRANSLATION_UUID = '999A'

    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.TRANSLATION_UUID, True)
        self.add_characteristic(TranslationCharacteristic(bus, 0, self))


class TranslationCharacteristic(Characteristic):

    TRANSLATION_UUID = '999B'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.TRANSLATION_UUID,
                ['read'],
                service)


    def ReadValue(self):

        serviceTranslations = [{
            "998A": "System",
            "180A": "The Battery Service",
            "999C": "House Lights",
        }]

        lth = len(json.dumps(serviceTranslations).encode('utf-8'))
        global_logger.info("Translation Service string length is " + str(lth) + " bytes.")
        if lth > 510:
            global_logger.info("... WARNING - Translation Service is too long for Bluetooth.")

        self.value = array.array('B', json.dumps(serviceTranslations))
        self.value = self.value.tolist()        
        return dbus.Array(self.value)





class BatteryService(Service):
    """
    Fake Battery service that emulates a draining battery.

    """
    BATTERY_UUID = '180A'

    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.BATTERY_UUID, True)
        self.add_characteristic(BatteryLevelCharacteristic(bus, 0, self))
 

class BatteryLevelCharacteristic(Characteristic):
    """
    Fake Battery Level characteristic. The battery level is drained by 2 points
    every 5 seconds.

    """
    BATTERY_LVL_UUID = '888a'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.BATTERY_LVL_UUID,
                ['read', 'notify'],
                service)
        ##self.add_descriptor(BatteryLevelDescriptor(bus, 0, self))
        self.notifying = True
        self.battery_lvl = 100
        gobject.timeout_add(5000, self.drain_battery)

    def notify_battery_level(self):
        if not self.notifying:
            return

        self.PropertiesChanged(
                GATT_CHRC_IFACE,
                { 'Value': [dbus.Byte(self.battery_lvl)] }, [])

        #self.PropertiesChanged(
        #        GATT_CHRC_IFACE,
        #        { 'Value': [dbus.Byte(14),dbus.Byte(2)] }, [])

    def drain_battery(self):
        if self.battery_lvl > 0:
            self.battery_lvl -= 2
            if self.battery_lvl < 0:
                self.battery_lvl = 0


        global_logger.info('Battery Level drained: ' + repr(self.battery_lvl))

        self.notify_battery_level()
        return True

    def ReadValue(self):

        """
        meta_record = {
            "id": "asdf", 
            "description": "", 
            "size": 2, 
            "type":'vadasf', 
            "original_filename": 'asdf.mp', 
            "directory": '..', 
            "filename": "full.mp4",
            "status": "uploaded",
            "origin": "Local Upload",
            "updated": datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
            "duration": ""
        }

        self.value = array.array('B', json.dumps(meta_record))
        self.value = self.value.tolist()        
        print (self.value)
        return dbus.Array(self.value)
        """

        print('Battery Level read: ' + repr(self.battery_lvl))
        return [dbus.Byte(self.battery_lvl)]
        

    def StartNotify(self):
        if self.notifying:
            print('Already notifying, nothing to do')
            return

        self.notifying = True
        self.notify_battery_level()

    def StopNotify(self):
        if not self.notifying:
            print('Not notifying, nothing to do')
            return

        self.notifying = False

class BatteryLevelDescriptor(Descriptor):
    """
    Dummy test descriptor. Returns a static value.

    """
    TEST_DESC_UUID = '12345678-1234-5678-1234-56789abcdef2'

    def __init__(self, bus, index, characteristic):
        Descriptor.__init__(
                self, bus, index,
                self.TEST_DESC_UUID,
                ['read'],
                characteristic)

    def ReadValue(self):
        return [
                dbus.Byte('T'), dbus.Byte('e'), dbus.Byte('s'), dbus.Byte('t')
        ]
