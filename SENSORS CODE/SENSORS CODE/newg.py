import time
import json
import boto3
import csv
from datetime import datetime
import RPi.GPIO as GPIO

# AWS IoT Core endpoint
AWS_ENDPOINT = "a16iuxf1b2w7n8-ats.iot.us-east-1.amazonaws.com"

# Path to your device certificate, private key, and root CA certificate
CERT_PATH = "/home/vedant/Desktop/connectAWS/raspberrypi_sensors.cert.pem"
KEY_PATH = "/home/vedant/Desktop/connectAWS/raspberrypi_sensors.private.key"
ROOT_CA_PATH = "/home/vedant/Desktop/connectAWS/root-CA.crt"

# Initialize AWS IoT client
iot_client = boto3.client('iot-data')

# MQTT topic to publish sensor data
TOPIC = "gas"

# Set GPIO mode
GPIO.setmode(GPIO.BOARD)

# Define the GPIO pin connected to the analog output of the gas sensor
ANALOG_PIN = 7  # Change this to match your actual GPIO pin

# Function to read analog voltage from gas sensor
def read_gas_sensor(pin):
    # To read analog values, you need to use GPIO setup for output and input
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)
    time.sleep(0.1)  # Delay to discharge capacitor
    GPIO.setup(pin, GPIO.IN)
    
    # Measure time until capacitor charges
    start_time = time.time()
    while GPIO.input(pin) == GPIO.LOW:
        pass
    end_time = time.time()
    
    # Calculate the time difference
    duration = end_time - start_time
    
    # Convert time to a voltage value
    # You may need to calibrate this conversion based on your sensor's characteristics
    voltage = duration * 1000  # Assuming 5V supply, convert to millivolts
    
    return voltage

# Function to write data to CSV file
def write_to_csv(data):
    with open('gas_data.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data)

try:
    while True:
        # Read analog voltage from gas sensor
        gas_value = read_gas_sensor(ANALOG_PIN)
        print(f"Gas Value: {gas_value}")

        # Create sensor data dictionary for gas sensor
        gas_sensor_data = {
            "gas_value": gas_value,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Create JSON structure
        output_data = {
            "body": json.dumps({"sensor_data": gas_sensor_data})
        }
        
        # Convert output data to JSON format
        message = json.dumps(output_data)

        # Publish message to AWS IoT Core for gas sensor
        gas_response = iot_client.publish(
            topic=TOPIC,
            qos=1,
            payload=message,
        )
        print("Gas Message published. Response:", gas_response)
        
        # Log data to CSV file for gas sensor
        gas_data_to_write = [gas_sensor_data["timestamp"], gas_sensor_data["gas_value"]]
        write_to_csv(gas_data_to_write)
        
        time.sleep(5)  # Publish data every 5 seconds

except KeyboardInterrupt:
    # Cleanup GPIO settings
    GPIO.cleanup()

