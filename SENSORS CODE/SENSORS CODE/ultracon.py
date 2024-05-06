import time
import json
import boto3
import random
import csv
import RPi.GPIO as GPIO
from gpiozero import DistanceSensor

GPIO.setmode(GPIO.BCM)

GPIO_TRIG = 5
GPIO_ECHO = 24
BUZZER_PIN = 17

GPIO.setwarnings(False)
GPIO.setup(GPIO_TRIG, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# AWS IoT Core endpoint
AWS_ENDPOINT = "a16iuxf1b2w7n8-ats.iot.us-east-1.amazonaws.com"

# Path to your device certificate, private key, and root CA certificate
CERT_PATH = "/home/vedant/Desktop/connectAWS/raspberrypi_sensors.cert.pem"
KEY_PATH = "/home/vedant/Desktop/connectAWS/raspberrypi_sensors.private.key"
ROOT_CA_PATH = "/home/vedant/Desktop/connectAWS/root-CA.crt"

# Initialize AWS IoT client
iot_client = boto3.client('iot-data')

# MQTT topic to publish sensor data
TOPIC = "ultra"

def measure_distance():
    GPIO.output(GPIO_TRIG, GPIO.LOW)
    time.sleep(2)

    GPIO.output(GPIO_TRIG, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIG, GPIO.LOW)

    start_time = time.time()
    bounce_back_time = time.time()

    while GPIO.input(GPIO_ECHO) == 0:
        start_time = time.time()

    while GPIO.input(GPIO_ECHO) == 1:
        bounce_back_time = time.time()

    pulse_duration = bounce_back_time - start_time
    distance = round(pulse_duration * 17150, 2)
    return distance

def generate_buzzer_signal():
    GPIO.output(BUZZER_PIN, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(BUZZER_PIN, GPIO.LOW)

try:
    while True:
        distance = measure_distance()
        print(f"Distance: {distance} cm")

        MINIMUM_DISTANCE_THRESHOLD = 10

        if distance < MINIMUM_DISTANCE_THRESHOLD:
            generate_buzzer_signal()
            print("Distance below threshold. Activating buzzer.")

        # Publish message to AWS IoT Core
        sensor_data = {
            "distance": distance
        }
        message = json.dumps(sensor_data)
        response = iot_client.publish(
            topic=TOPIC,
            qos=1,
            payload=message,
        )
        print("Message published. Response:", response)

        # Log data to CSV file
        csv_file_path = "distance_data.csv"
        with open(csv_file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([time.strftime('%Y-%m-%d %H:%M:%S'), distance])

        time.sleep(5)

except KeyboardInterrupt:
    pass

finally:
    GPIO.cleanup()
