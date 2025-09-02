import smbus2
import time

bus = smbus2.SMBus(0)

address = 0x6C

def read_sensor():
    try:
        # Read 4 bytes of data starting from register 0x00
        data = bus.read_i2c_block_data(address, 0x00, 4)
        # Process the data as needed
        print("Sensor Data:", data)
    except Exception as e:
        print("Error reading sensor:", e)

while True:
    read_sensor()
    time.sleep(1)
