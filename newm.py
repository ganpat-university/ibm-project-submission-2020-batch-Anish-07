import time
import json
import boto3
from gpiozero import LED, MotionSensor
import csv
from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# AWS IoT Core endpoint
AWS_ENDPOINT = "a16iuxf1b2w7n8-ats.iot.us-east-1.amazonaws.com"

# Path to your device certificate, private key, and root CA certificate
CERT_PATH = "/home/vedant/Desktop/connectAWS/raspberrypi_sensors.cert.pem"
KEY_PATH = "/home/vedant/Desktop/connectAWS/raspberrypi_sensors.private.key"
ROOT_CA_PATH = "/home/vedant/Desktop/connectAWS/root-CA.crt"

# Initialize AWS IoT client
iot_client = boto3.client('iot-data')

# MQTT topic to publish sensor data
TOPIC = "motion"

# Initialize motion sensor
pir = MotionSensor(4)  # Replace 4 with the GPIO pin connected to your PIR motion sensor

# Initialize LEDs
green_led = LED(17)  # Replace 17 with the GPIO pin connected to your LED
buzzer = LED(18)  # Replace 18 with the GPIO pin connected to your buzzer

# CSV file for motion detection log
csv_file = 'motion_detection_log.csv'

# Email configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_ADDRESS = 'panotiislive@gmail.com'
EMAIL_PASSWORD = 'pdqp dwkk axjg vxfe'
RECIPIENT_EMAIL = 'pv092435@gmail.com'

def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    text = msg.as_string()
    server.sendmail(EMAIL_ADDRESS, RECIPIENT_EMAIL, text)
    server.quit()

# Initialize variables
last_motion_time = datetime.now()

try:
    while True:
        # Check motion sensor
        if pir.motion_detected:
            last_motion_time = datetime.now()  # Update last motion time
            sensor_data = {
                "motion": "detected",
                "time": last_motion_time.strftime("%Y-%m-%d %H:%M:%S"),
                "device_id": "raspberrypi",  # Assuming this is the device ID
                "location": "living_room"  # Assuming this is the location of the sensor
            }
            green_led.on()  # Turn on the green LED
            buzzer.on()  # Turn on the buzzer
        else:
            sensor_data = {
                "motion": "not detected",
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "device_id": "raspberrypi",  # Assuming this is the device ID
                "location": "living_room"  # Assuming this is the location of the sensor
            }

        # Create JSON structure
        output_data = {
            "body": json.dumps({"sensor_data": sensor_data})
        }
        
        # Convert output data to JSON format
        message = json.dumps(output_data)

        # Publish message to AWS IoT Core
        response = iot_client.publish(
            topic=TOPIC,
            qos=1,
            payload=message,
        )
        print("Message published. Response:", response)

        # Check if no motion for a long time
        if datetime.now() - last_motion_time > timedelta(minutes=30):  # Adjust the time threshold as needed
            # Send email notification
            subject = "No Motion Detected"
            body = "No motion has been detected for a long time."
            send_email(subject, body)

            # Update last motion time to prevent repeated notifications
            last_motion_time = datetime.now()

        time.sleep(1)

except KeyboardInterrupt:
    pass

finally:
    green_led.off()  # Ensure the green LED is turned off on program exit
    buzzer.off()  # Ensure the buzzer is turned off on program exit

