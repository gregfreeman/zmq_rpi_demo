#!/usr/bin/python

from __future__ import print_function
from Adafruit_I2C import Adafruit_I2C
import struct

class Adafruit_L3GD20(Adafruit_I2C):

    L3GD20_ADDRESS             =    (0x6B)       #  1101011
    L3GD20_POLL_TIMEOUT        =    (100)        #  Maximum number of read attempts
    L3GD20_ID                  =    0xD4
    L3GD20H_ID                 =    0xD7
 
    L3GD20_SENSITIVITY_250DPS  = (0.00875)      # Roughly 22/256 for fixed point match
    L3GD20_SENSITIVITY_500DPS  = (0.0175)       # Roughly 45/256
    L3GD20_SENSITIVITY_2000DPS = (0.070)        # Roughly 18/256
    L3GD20_DPS_TO_RADS         = (0.017453293)  # degress/s to rad/s multiplier

    L3GD20_REGISTER_WHO_AM_I            = 0x0F  # 11010100   r
    L3GD20_REGISTER_CTRL_REG1           = 0x20  # 00000111   rw
    L3GD20_REGISTER_CTRL_REG2           = 0x21  # 00000000   rw
    L3GD20_REGISTER_CTRL_REG3           = 0x22  # 00000000   rw
    L3GD20_REGISTER_CTRL_REG4           = 0x23  # 00000000   rw
    L3GD20_REGISTER_CTRL_REG5           = 0x24  # 00000000   rw
    L3GD20_REGISTER_REFERENCE           = 0x25  # 00000000   rw
    L3GD20_REGISTER_OUT_TEMP            = 0x26  #            r
    L3GD20_REGISTER_STATUS_REG          = 0x27  #            r
    L3GD20_REGISTER_OUT_X_L             = 0x28  #            r
    L3GD20_REGISTER_OUT_X_H             = 0x29  #            r
    L3GD20_REGISTER_OUT_Y_L             = 0x2A  #            r
    L3GD20_REGISTER_OUT_Y_H             = 0x2B  #            r
    L3GD20_REGISTER_OUT_Z_L             = 0x2C  #            r
    L3GD20_REGISTER_OUT_Z_H             = 0x2D  #            r
    L3GD20_REGISTER_FIFO_CTRL_REG       = 0x2E  # 00000000   rw
    L3GD20_REGISTER_FIFO_SRC_REG        = 0x2F  #            r
    L3GD20_REGISTER_INT1_CFG            = 0x30  # 00000000   rw
    L3GD20_REGISTER_INT1_SRC            = 0x31  #            r
    L3GD20_REGISTER_TSH_XH              = 0x32  # 00000000   rw
    L3GD20_REGISTER_TSH_XL              = 0x33  # 00000000   rw
    L3GD20_REGISTER_TSH_YH              = 0x34  # 00000000   rw
    L3GD20_REGISTER_TSH_YL              = 0x35  # 00000000   rw
    L3GD20_REGISTER_TSH_ZH              = 0x36  # 00000000   rw
    L3GD20_REGISTER_TSH_ZL              = 0x37  # 00000000   rw
    L3GD20_REGISTER_INT1_DURATION       = 0x38  # 00000000   rw

    def __init__(self, busnum=-1, debug=False, res='250DPS'):

        # Accelerometer and magnetometer are at different I2C
        # addresses, so invoke a separate I2C instance for each
        self.i2c = Adafruit_I2C(self.L3GD20_ADDRESS, busnum, debug)

        id = self.i2c.readU8(self.L3GD20_REGISTER_WHO_AM_I)
        if ((id != self.L3GD20_ID) and (id != self.L3GD20H_ID)):
            raise Exception('gyro no identified')

        # Switch to normal mode and enable all three channels
        self.i2c.write8(self.L3GD20_REGISTER_CTRL_REG1, 0x0F)

        # L3DS20_RANGE_2000DPS
        if res == '2000DPS':
            self.i2c.write8(self.L3GD20_REGISTER_CTRL_REG4, 0x20)
            self.SC = self.L3GD20_SENSITIVITY_2000DPS
        elif res == '500DPS':
            self.i2c.write8(self.L3GD20_REGISTER_CTRL_REG4, 0x10)
            self.SC = self.L3GD20_SENSITIVITY_500DPS
        else:
            self.i2c.write8(self.L3GD20_REGISTER_CTRL_REG4, 0x00)
            self.SC = self.L3GD20_SENSITIVITY_250DPS

    def int16(self, low, high):
        # struct.unpack('hhh',list)
        n = low | (high << 8)   # High, low bytes
        return n if n < 32768 else n - 65536  # 2's complement signed

    def read(self):
        # Read the gyro -
        result = []
        for i in range(3):
            low = self.i2c.readU8(self.L3GD20_REGISTER_OUT_X_L+i*2)
            high = self.i2c.readU8(self.L3GD20_REGISTER_OUT_X_H+i*2)
            result.append(self.int16(low, high) * self.SC)
        return result

    # Interpret signed 16-bit inst
    # def int16(self, list, idx):
    #     # struct.unpack('hhh',list)
    #     n = (list[idx]) | (list[idx+1] << 8)   # High, low bytes
    #     return n if n < 32768 else n - 65536  # 2's complement signed

    # why is block read not working. getting 6 copies of byte 0.
    # def read(self):
    #     # Read the gyro
    #     b = self.i2c.readList(self.L3GD20_REGISTER_OUT_X_L, 6)
    #     for i in range(6):
    #         print '%x' % self.i2c.readU8(self.L3GD20_REGISTER_OUT_X_L+i)
    #     print self.i2c.bus.read_i2c_block_data(0x6B, 0x28, 6)
    #     print ['%x' % bi for bi in b]
    #     b2 = struct.pack('bbbbbb', *b)
    #     x = struct.unpack_from('<hhh', b2)
    #     print x
    #     return x[0] * self.SC, x[1] * self.SC, x[2] * self.SC

        # print len(b)
        # return (self.int16(b, 0) * self.SC,
        #         self.int16(b, 2) * self.SC,
        #         self.int16(b, 4) * self.SC)


# Simple example prints accel/mag data once per second:
if __name__ == '__main__':

    from time import sleep

    gyr = Adafruit_L3GD20()

    print('(Gyro X, Y, Z)')
    while True:
        r = gyr.read()
        print('%09.3f %09.3f %09.3f' % (r[0], r[1], r[2]))
        sleep(0.1)  # Output is fun to watch if this is commented out
