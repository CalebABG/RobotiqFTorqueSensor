import struct
import serial
import time

# Project relies on PySerial
# Run this command in CMD or terminal to install package
# pip install pyserial
# https://pypi.org/project/pyserial/

# Check on Arduino IDE for the COM port
# The other com will be for the Force Torque Sensor
# Check Device Manager under 'Ports' to find ports to find both if unsure


csvFile = None

try:
    csvFile = open('FTSensorData.csv', 'w')
except() as e:
    print(e)

running = True

pressureSenSerial = serial.Serial(port='COM7', baudrate=19200)

# set timeout to none to make blocking call (wait for data)
arduinoSerial = serial.Serial(port='COM6', baudrate=115200, timeout=None)
time.sleep(2)

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
                # read 14 bytes: 2bytes for end crc
                incoming = pressureSenSerial.read(14)

                # only want the 12bytes of data
                incoming = incoming[:-2]

                # unpack the data from little-endian 2byte (high,low)
                data = struct.unpack('<6h', incoming)

                # send capital A to Arduino when data is received
                arduinoSerial.write(b'A')

                arduinoData = arduinoSerial.read_until(b':')[:-1].decode().split(',')

                # data package of sensor data and arduino response
                FTorqueData = [data[0] / 100.0, data[1] / 100.0, data[2] / 100.0,
                               data[3] / 1000.0, data[4] / 1000.0, data[5] / 1000.0]

                csvData = arduinoData + FTorqueData

                # write to csv
                csvFile.write("{},{},{},{},{},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f}\n".format(*csvData))
                print("{},{},{},{},{},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f}\n".format(*csvData))

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

    if csvFile is not None:
        csvFile.close()

except() as e:
    print(e)

finally:
    print("Exiting Script")
