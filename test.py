import time
from smbus2 import SMBus

# I²C bus and sensor address
I2C_BUS = 1
SENSOR_ADDR = 0x6C  # 7-bit address

# Command to start measurement (0x8B93)
START_MEASUREMENT_CMD = [0x8B, 0x93]

# Register addresses for pressure and temperature data
PRESSURE_REG = 0x00  # Replace with actual register address
TEMPERATURE_REG = 0x02  # Replace with actual register address

def initialize_sensor():
    """Initialize the sensor by sending the start measurement command."""
    with SMBus(I2C_BUS) as bus:
        bus.write_i2c_block_data(SENSOR_ADDR, 0x22, START_MEASUREMENT_CMD)
        print("Measurement started.")

def read_sensor_data():
    """Read pressure and temperature data from the sensor."""
    with SMBus(I2C_BUS) as bus:
        # Read 4 bytes of data (2 bytes for pressure and 2 for temperature)
        data = bus.read_i2c_block_data(SENSOR_ADDR, PRESSURE_REG, 4)
        
        # Process the data (assuming 16-bit unsigned integers)
        pressure = (data[0] << 8) | data[1]
        temperature = (data[2] << 8) | data[3]
        
        # Convert raw data to meaningful units (example: pressure in bar, temperature in °C)
        pressure_value = pressure * 0.01  # Adjust conversion factor as per sensor specs
        temperature_value = temperature * 0.1  # Adjust conversion factor as per sensor specs
        
        return pressure_value, temperature_value

def main():
    """Main function to initialize sensor and read data."""
    initialize_sensor()
    time.sleep(0.1)  # Wait for measurement to complete
    pressure, temperature = read_sensor_data()
    print(f"Pressure: {pressure} bar")
    print(f"Temperature: {temperature} °C")

if __name__ == "__main__":
    main()
