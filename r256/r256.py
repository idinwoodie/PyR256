import time
import serial
from . import protocol


class Driver:

    def __init__(self, address, port, baud):
        """Initialize communication parameters."""
        self.address = self.assign(address)
        self.con = serial.Serial(port, baud)

    def assign(self, address):
        """Determine the identification string for the controller."""
        if address in protocol.ADDRESS:
            return protocol.ADDRESS[address]
        try:
            tag = int(address)
            if (tag < 1) or (tag > 9):
                raise Exception('Out of bounds')
            return tag
        except:
            print("Error: invalid address " + address)
            exit()

    def open(self):
        """Establish a connection to the controller."""
        self.con.open()
        if not self.con.isOpen():
            print("Error: %d failed to open" %self.con.port)
            exit()

    def move(self, steps):
        """Send an actuation command to the controller."""
        if steps >= 0:
            move_select = P.CMD_FORWARD
        else:
            move_select = P.CMD_BACKWARD
        self.con.write((P.CMD_START + self.address + move_select + str(steps)
                        + P.CMD_RUN + P.CMD_END).encode())
        bytesToRead = self.con.inWaiting()
        status = self.con.read(bytesToRead)
        status = self.page()
        while status != '0':
            status = self.page()
            print(status)
        return status

    def page(self):
        """Ping the controller for a status update."""
        self.con.write((P.CMD_START + self.address + P.CMD_STS
                        + P.CMD_END).encode())
        time.sleep(0.1)
        bytesToRead = self.con.inWaiting()
        status = self.con.read().decode('utf-8')
        self.con.read(bytesToRead-1)
        return status

    def io(self, state):
        """Send a command to the on-board controller relays."""
        self.con.write((P.CMD_START + self.address + P.CMD_IO + str(state)
                        + P.CMD_END).encode())
        time.sleep(0.1)
        bytesToRead = self.con.inWaiting()
        status = (self.con.read(bytesToRead)).decode('utf-8')
        return status

    def cancel(self):
        """Terminate controller activity."""
        self.con.write((P.CMD_START + self.address + P.TERMINATE).encode())

    def close(self):
        """ Closing communication with the controller."""
        while self.con.isOpen() == True:
            self.con.close()

