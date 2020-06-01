import os, pty
import threading
from vedirect import VEDirect
from vedirect import VEDirectDeviceEmulator
import unittest


def store_packet(packet, packetlist=None):
    packetlist.append(packet)


class TestVEDirect(unittest.TestCase):

    def cb_function(self, data):
        self.data = data

    def test_v_mppt(self):
        """ Test with an MPPT emulator on a fake serial port """
        master, slave = pty.openpty()  # open the pseudoterminal
        s_name = os.ttyname(slave)  # translate the slave fd to a filename

        # Set up the slave (IoT device client) to listen for data from the (master) device
        vedir = VEDirect(s_name)
        thread_slave = threading.Thread(target=vedir.read_data_single_callback, args=[self.cb_function])
        thread_slave.start()

        # Create a separate device emulator thread that connects to the master port
        vede = VEDirectDeviceEmulator(master, model='MPPT')
        thread_master = threading.Thread(target=vede.send_packet)
        thread_master.start()

        # Wait a maximum of 5 seconds for the IoT device client to finish (it getting one packet)
        thread_slave.join(timeout=5)

        self.assertDictEqual(self.data, VEDirect.typecast(VEDirectDeviceEmulator.data['MPPT']))

    def test_typecast(self):
        """ Test with an MPPT emulator on a fake serial port """
        original = {'V': '12800', 'LOAD': 'ON'}
        new = VEDirect.typecast(original)
        self.assertDictEqual(new, {'V': 12800.0, 'LOAD': 'ON'})

    def test_emulate(self):
        """ Test in emulation mode (no port access) """
        v = VEDirect(emulate='MPPT')
        onepacket=v.read_data_single()
        self.assertEqual(VEDirect.typecast(VEDirectDeviceEmulator.data['MPPT']), onepacket)

    def test_emulate2(self):
        """ Test in emulation mode (no port access) """
        packets = []
        v = VEDirect(emulate='MPPT')
        v.read_data_callback(store_packet, n=2, packetlist=packets)
        self.assertEqual(VEDirect.typecast(VEDirectDeviceEmulator.data['MPPT']), packets[0])
        self.assertEqual(VEDirect.typecast(VEDirectDeviceEmulator.data['MPPT']), packets[1])


if __name__ == '__main__':
    unittest.main()
