import Tools as tools
import datetime
import os, sys, shutil
import time
from Tools import Thread

import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service

import array
#import gobject
from gi.repository import GObject as gobject

from random import randint

mainloop = None

BLUEZ_SERVICE_NAME = 'org.bluez'
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
DBUS_OM_IFACE = 'org.freedesktop.DBus.ObjectManager'
DBUS_PROP_IFACE = 'org.freedesktop.DBus.Properties'

LE_ADVERTISEMENT_IFACE = 'org.bluez.LEAdvertisement1'

## -- Main Thread
class Advert(Thread):
    def __init__(self, logger):

        self.logger = logger
        self.keepGoing = True

    def Run(self):

        #while self.keepGoing:

        #    self.logger.info('a log')
        #    time.sleep(5)
        self.main()

    def Stop(self):
        self.logger.info('Shutting down Advertisement')
        mainloop.quit()

    def register_ad_cb(self):
        self.logger.info('Toothd Advertisement registered')


    def register_ad_error_cb(self, error):
        self.logger.info('Failed to register advertisement: ' + str(error))
        mainloop.quit()


    def find_adapter(self, bus):
        remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'),
                                   DBUS_OM_IFACE)
        objects = remote_om.GetManagedObjects()

        for o, props in objects.iteritems():
            if LE_ADVERTISING_MANAGER_IFACE in props:
                return o

        return None


    def main(self):
        global mainloop

        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

        bus = dbus.SystemBus()

        adapter = self.find_adapter(bus)
        if not adapter:
            print 'LEAdvertisingManager1 interface not found'
            return

        adapter_props = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter),
                                       "org.freedesktop.DBus.Properties");

        adapter_props.Set("org.bluez.Adapter1", "Powered", dbus.Boolean(1))

        ad_manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter),
                                    LE_ADVERTISING_MANAGER_IFACE)

        toothd_advertisement = TootdAdvertisement(bus, 0)

        mainloop = gobject.MainLoop()

        ad_manager.RegisterAdvertisement(toothd_advertisement.get_path(), {},
                                         reply_handler=self.register_ad_cb,
                                         error_handler=self.register_ad_error_cb)

        #mythread = threading.Thread(target=mainloop.run)
        mainloop.run()

class InvalidArgsException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.freedesktop.DBus.Error.InvalidArgs'


class NotSupportedException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.bluez.Error.NotSupported'


class NotPermittedException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.bluez.Error.NotPermitted'


class InvalidValueLengthException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.bluez.Error.InvalidValueLength'


class FailedException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.bluez.Error.Failed'


class Advertisement(dbus.service.Object):
    PATH_BASE = '/org/bluez/toothd/advertisement'

    def __init__(self, bus, index, advertising_type):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        self.ad_type = advertising_type
        self.service_uuids = None
        self.manufacturer_data = None
        self.solicit_uuids = None
        self.service_data = None
        self.include_tx_power = None
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        properties = dict()
        properties['Type'] = self.ad_type
        if self.service_uuids is not None:
            properties['ServiceUUIDs'] = dbus.Array(self.service_uuids,
                                                    signature='s')
        if self.solicit_uuids is not None:
            properties['SolicitUUIDs'] = dbus.Array(self.solicit_uuids,
                                                    signature='s')
        if self.manufacturer_data is not None:
            properties['ManufacturerData'] = dbus.Dictionary(
                self.manufacturer_data, signature='qay')
        if self.service_data is not None:
            properties['ServiceData'] = dbus.Dictionary(self.service_data,
                                                        signature='say')
        if self.include_tx_power is not None:
            properties['IncludeTxPower'] = dbus.Boolean(self.include_tx_power)
        return {LE_ADVERTISEMENT_IFACE: properties}

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_service_uuid(self, uuid):
        if not self.service_uuids:
            self.service_uuids = []
        self.service_uuids.append(uuid)

    def add_solicit_uuid(self, uuid):
        if not self.solicit_uuids:
            self.solicit_uuids = []
        self.solicit_uuids.append(uuid)

    def add_manufacturer_data(self, manuf_code, data):
        if not self.manufacturer_data:
            self.manufacturer_data = dict()
        self.manufacturer_data[manuf_code] = data

    def add_service_data(self, uuid, data):
        if not self.service_data:
            self.service_data = dict()
        self.service_data[uuid] = data

    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):

        if interface != LE_ADVERTISEMENT_IFACE:
            raise InvalidArgsException()

        return self.get_properties()[LE_ADVERTISEMENT_IFACE]

    @dbus.service.method(LE_ADVERTISEMENT_IFACE,
                         in_signature='',
                         out_signature='')
    def Release(self):
        print '%s: Released!' % self.path


class TootdAdvertisement(Advertisement):

    def __init__(self, bus, index):
        Advertisement.__init__(self, bus, index, 'peripheral')
        self.add_service_uuid('180A')
        self.add_service_uuid('999A')
        self.add_manufacturer_data(0xffff, [0x05, 0x06, 0x02, 0x03, 0x04])
        self.add_service_data('9999', [0x00, 0x01, 0x02, 0x03, 0x04])
        self.include_tx_power = True

