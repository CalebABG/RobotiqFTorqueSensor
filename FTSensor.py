import struct
import serial

# Project relies on PySerial
# https://pypi.org/project/pyserial/

running = True

pressureSenSerial = serial.Serial(port='COM17', baudrate=19200)

# 11 bytes
init_msg_data = [9, 16, 1, 154, 0, 1, 2, 2, 0, 205, 202]

# *list grabs all the data and spills it into individual pieces
init_msg = struct.pack('11B', *init_msg_data)

# write init message to serial to start data flow
pressureSenSerial.write(init_msg)

while running:
    try:
        msg1 = pressureSenSerial.read()

        if ord(msg1) == 0x20:
            msg2 = pressureSenSerial.read()

            if ord(msg2) == 0x4e:
                # read 16 bytes: 2bytes for start , 2bytes for end crc
                incoming = pressureSenSerial.read(14)

                # only want the 12bytes of data
                incoming = incoming[:-2]

                # unpack the data from little-endian 2byte (high,low)
                data = struct.unpack('<6h', incoming)

                print (data[0] / 100.0, data[1] / 100.0, data[2] / 100.0,
                       data[3] / 1000.0, data[4] / 1000.0, data[5] / 1000.0)

    except KeyboardInterrupt as keyboardInterruptExc:
        running = False
        print(keyboardInterruptExc)

    # handle generic exception
    except() as e:
        running = False
        print(e)


# at end free up port if not null
try:
    if pressureSenSerial is not None:
        pressureSenSerial.close()

    print("Closed Serial Port!")
except() as e:
    print(e)

finally:
    print("Exiting Script")

