import time
import json
import boto3
import random
import Adafruit_DHT

# AWS IoT Core endpoint
AWS_ENDPOINT = "a16iuxf1b2w7n8-ats.iot.us-east-1.amazonaws.com"

# Initialize AWS IoT client
iot_client = boto3.client('iot-data')

# MQTT topic to publish sensor data
TOPIC = "sensors"

# Thresholds for temperature alert
TEMP_HIGH_THRESHOLD = 40.0  # Example high temperature threshold in Celsius
TEMP_LOW_THRESHOLD = 20.0   # Example low temperature threshold in Celsius

# Function to publish sensor data to AWS IoT Core
def publish_sensor_data(temperature, humidity):
    sensor_data = {
        "temperature": temperature,
        "humidity": humidity
    }
    message = {
        "body": json.dumps({"sensor_data": sensor_data})
    }
    
    # Convert message to JSON format
    message_json = json.dumps(message)
    
    # Publish message to AWS IoT Core
    response = iot_client.publish(
        topic=TOPIC,
        qos=1,
        payload=message_json,
    )
    print("Message published. Response:", response)

# Main loop
while True:
    # Read temperature and humidity from DHT11 sensor
    humidity, temperature = Adafruit_DHT.read_retry(11, 4)

    if humidity is not None and temperature is not None:
        print('Temp: {0:0.1f} C  Humidity: {1:0.1f} %'.format(temperature, humidity))
        
        # Publish sensor data to AWS IoT Core
        publish_sensor_data(temperature, humidity)

        # Check for temperature threshold alert
        if temperature > TEMP_HIGH_THRESHOLD:
            print("Alert: Temperature is too hot!")
            # Add code here to trigger an alert, send a notification, etc.
        elif temperature < TEMP_LOW_THRESHOLD:
            print("Alert: Temperature is too cold!")
            # Add code here to trigger an alert, send a notification, etc.

    else:
        print('Failed to get reading. Try again!')

    time.sleep(5)  # Publish data every 5 seconds
