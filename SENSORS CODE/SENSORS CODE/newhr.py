from gpiozero import MCP3008
import time
from datetime import datetime
import json
import boto3
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Initialize MCP3008
adc = MCP3008(channel=0)  # Assuming the pulse sensor is connected to channel 0

# AWS IoT Core endpoint
AWS_ENDPOINT = "a16iuxf1b2w7n8-ats.iot.us-east-1.amazonaws.com"

# Initialize AWS IoT client
iot_client = boto3.client('iot-data')

# MQTT topic to publish sensor data
TOPIC = "heartrate"

# Email configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_ADDRESS = 'panotiislive@gmail.com'
EMAIL_PASSWORD = 'pdqp dwkk axjg vxfe'
RECIPIENT_EMAIL = 'pv092435@gmail.com'

# Initialize variables
heartbeat_count = 0
start_time = time.time()  # Initialize start time here

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

try:
    while True:
        # Read analog value from pulse sensor
        pulse_value = adc.value
        
        # Check if pulse value exceeds threshold
        if pulse_value > 0.5:
            heartbeat_count += 1
        
        # Check if 5 seconds have passed
        if time.time() - start_time >= 5:
            # Calculate heart rate
            heart_rate = heartbeat_count * 12  # Adjusted for 5-second interval
            print(f"Heart rate: {heart_rate:.2f} beats per minute")
            
            # Create sensor data dictionary including heart rate
            sensor_data = {
                "heart_rate": heart_rate
            }
            
            # Create JSON structure with sensor data
            json_data = {
                "sensor_data": sensor_data
            }
            
            # Convert output data to JSON format
            message_body = json.dumps(json_data)
            
            # Create final message format
            message = {
                "body": message_body
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
            
            # Get current date and time
            now = datetime.now()
            date_string = now.strftime("%Y-%m-%d")
            time_string = now.strftime("%H:%M:%S")
            day_string = now.strftime("%A")
            week_string = now.strftime("%U")
            month_string = now.strftime("%B")
            year_string = now.strftime("%Y")
            
            # Send email if heartbeat count is 0
            if heart_rate == 0:
                subject = "Alert: No Heartbeat Detected"
                body = "No heartbeat detected in the last interval."
                send_email(subject, body)
            
            # Reset variables
            heartbeat_count = 0
            start_time = time.time()  # Update start time
        
        time.sleep(0.1)  # Adjust the sleep time as needed
        
except KeyboardInterrupt:
    print("\nExiting program...")
