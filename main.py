import requests
import smtplib
from email.mime.text import MIMEText
import schedule
import time
import os # Import os module to access environment variables

# 1. Get weather data using Open-Meteo API
def get_weather():
    # Coordinates for Bangalore
    latitude = 12.9716
    longitude = 77.5946

    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={latitude}&longitude={longitude}"
        f"&current_weather=true&timezone=auto"
    )

    try:
        response = requests.get(url)
        response.raise_for_status() # Raise an exception for HTTP errors
        data = response.json()

        weather_code = data['current_weather']['weathercode']
        condition = weather_code_to_description(weather_code)
        print(f"Weather condition: {condition}")
        return condition.lower()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return ""
    except KeyError as e:
        print(f"Error parsing weather data (missing key): {e}")
        print(f"Full response data: {data}") # Print full data for debugging
        return ""
    except Exception as e:
        print(f"An unexpected error occurred in get_weather: {e}")
        return ""

# 2. Convert Open-Meteo weather code to readable condition
def weather_code_to_description(code):
    code_map = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        56: "Light freezing drizzle",
        57: "Dense freezing drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        66: "Light freezing rain",
        67: "Heavy freezing rain",
        71: "Slight snow fall",
        73: "Moderate snow fall",
        75: "Heavy snow fall",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers"
    }
    return code_map.get(code, "Unknown")

# 3. Send email via Outlook (using Gmail SMTP)
def send_email_via_outlook():
    sender_email = os.getenv("SENDER_EMAIL", "your_email@gmail.com") # Get from environment variable
    sender_password = os.getenv("SENDER_PASSWORD") # Get from environment variable
    recipient_email = os.getenv("RECIPIENT_EMAIL", "your_email@gmail.com") # Get from environment variable

    if not sender_password:
        print("Error: SENDER_PASSWORD environment variable not set. Cannot send email.")
        return

    subject = "Umbrella Reminder"
    body = "Hey! The weather looks rainy or cloudy today. Don't forget your umbrella! ☔"

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print("Email sent successfully!")
    except smtplib.SMTPAuthenticationError:
        print("Failed to send email: Authentication Error. Check your email and app password.")
        print("For Gmail, you might need to generate an 'App password' if you have 2-Factor Authentication enabled.")
    except Exception as e:
        print(f"Failed to send email: {e}")

# 4. Main scheduled job
def job():
    print("Running weather check job...")
    weather = get_weather()
    #print(weather)
    if "rain" in weather or "cloud" in weather:
        send_email_via_outlook()
    else:
        print("No rain or clouds. No need for umbrella today.")

# 5. Schedule the job
# schedule.every().day.at("06:57").do(job) # Uncomment and set your preferred time (24hr format)
schedule.every(1).minutes.do(job) # Runs every 1 minute for testing. Change for production.
job() # Run immediately for quick test

print("Scheduler started. Waiting for the next run...")

while True:
    schedule.run_pending()
    time.sleep(1) # Sleep for 1 second to reduce CPU usage, schedule checks every minute
