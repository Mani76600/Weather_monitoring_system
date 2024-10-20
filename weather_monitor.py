import requests
import time
import sqlite3
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from collections import Counter
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Configuration
API_KEY = os.getenv("OPENWEATHERMAP_API_KEY", "8af0831ff2980237d816c0de0e6872f8")
CITY_IDS = {
    "Delhi": 1273294,
    "Mumbai": 1275339,
    "Chennai": 1264527,
    "Bangalore": 1277333,
    "Kolkata": 1275004,
    "Hyderabad": 1269843
}
INTERVAL = 300  # 5 minutes
TEMPERATURE_THRESHOLD = 35  # Celsius
CONSECUTIVE_ALERTS = 2
DB_NAME = "weather_data.db"

# Database setup
def setup_database():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS weather_data
                 (city TEXT, timestamp INTEGER, temp REAL, feels_like REAL, main TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS daily_summaries
                 (city TEXT, date TEXT, avg_temp REAL, max_temp REAL, min_temp REAL, dominant_weather TEXT)''')
    conn.commit()
    conn.close()
    print("Database setup complete.")

# API call function
def get_weather_data(city, city_id):
    url = f"http://api.openweathermap.org/data/2.5/weather?id={city_id}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            'city': city,
            'timestamp': data['dt'],
            'temp': data['main']['temp'],
            'feels_like': data['main']['feels_like'],
            'main': data['weather'][0]['main']
        }
    else:
        print(f"Error fetching data for {city}: {response.status_code}")
        return None

# Store weather data
def store_weather_data(data):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO weather_data VALUES (?, ?, ?, ?, ?)",
              (data['city'], data['timestamp'], data['temp'], data['feels_like'], data['main']))
    conn.commit()
    conn.close()
    print(f"Stored data for {data['city']}: Temp: {data['temp']}°C, Feels like: {data['feels_like']}°C, Weather: {data['main']}")

# Calculate daily summary
def calculate_daily_summary():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    yesterday = datetime.now().date() - timedelta(days=1)
    start_of_day = int(datetime(yesterday.year, yesterday.month, yesterday.day).timestamp())
    end_of_day = start_of_day + 86400

    summaries = []
    for city in CITY_IDS.keys():
        c.execute("""SELECT AVG(temp), MAX(temp), MIN(temp), main
                     FROM weather_data
                     WHERE city = ? AND timestamp BETWEEN ? AND ?
                     GROUP BY city""", (city, start_of_day, end_of_day))
        result = c.fetchone()
        if result:
            avg_temp, max_temp, min_temp, _ = result
            c.execute("""SELECT main FROM weather_data
                         WHERE city = ? AND timestamp BETWEEN ? AND ?""", (city, start_of_day, end_of_day))
            weather_conditions = [row[0] for row in c.fetchall()]
            dominant_weather = Counter(weather_conditions).most_common(1)[0][0]

            c.execute("""INSERT INTO daily_summaries
                         VALUES (?, ?, ?, ?, ?, ?)""",
                      (city, yesterday.isoformat(), avg_temp, max_temp, min_temp, dominant_weather))
            
            summaries.append({
                'city': city,
                'date': yesterday.isoformat(),
                'avg_temp': avg_temp,
                'max_temp': max_temp,
                'min_temp': min_temp,
                'dominant_weather': dominant_weather
            })

    conn.commit()
    conn.close()
    return summaries

# Alert system
def check_alert_threshold(city, temp):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""SELECT temp FROM weather_data
                 WHERE city = ? ORDER BY timestamp DESC LIMIT ?""", (city, CONSECUTIVE_ALERTS))
    recent_temps = [row[0] for row in c.fetchall()]
    conn.close()

    if len(recent_temps) == CONSECUTIVE_ALERTS and all(t >= TEMPERATURE_THRESHOLD for t in recent_temps):
        print_and_send_alert(city, temp)

def print_and_send_alert(city, temp):
    subject = f"Weather Alert: High temperature in {city}"
    body = f"The temperature in {city} has exceeded {TEMPERATURE_THRESHOLD}°C for {CONSECUTIVE_ALERTS} consecutive readings. Current temperature: {temp}°C"
    
    # Print alert to terminal
    print("\n" + "="*50)
    print("WEATHER ALERT")
    print("="*50)
    print(subject)
    print(body)
    print("="*50 + "\n")

    # Flush the output to ensure it's displayed immediately
    import sys
    sys.stdout.flush()

    send_email_alert(city, subject, body)

def send_email_alert(city, subject, body):
    sender_email = "manichennakesava@gmail.com"
    receiver_email = "manichennakesavareddy@gmail.com"
    password = "buoa cmfq zxhb xlba"

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print(f"Email alert sent for {city}")
    except Exception as e:
        print(f"Failed to send email alert: {e}")

# Visualization
def create_visualizations():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    for city in CITY_IDS.keys():
        # First, try to get data from daily_summaries
        c.execute("""SELECT date, avg_temp, max_temp, min_temp
                     FROM daily_summaries
                     WHERE city = ? ORDER BY date DESC LIMIT 7""", (city,))
        data = c.fetchall()
        
        if not data:
            # If no daily summary data, use today's weather_data
            today = datetime.now().date()
            start_of_day = int(datetime(today.year, today.month, today.day).timestamp())
            c.execute("""SELECT timestamp, temp, temp, temp
                         FROM weather_data
                         WHERE city = ? AND timestamp >= ?
                         ORDER BY timestamp""", (city, start_of_day))
            data = c.fetchall()

        if not data:
            print(f"No data available for {city}")
            continue

        dates = [datetime.fromtimestamp(row[0]).strftime('%Y-%m-%d %H:%M') if isinstance(row[0], int) else row[0] for row in data]
        avg_temps = [row[1] for row in data]
        max_temps = [row[2] for row in data]
        min_temps = [row[3] for row in data]

        plt.figure(figsize=(12, 6))
        plt.plot(dates, avg_temps, label='Average/Current', marker='o')
        if data[0][1] != data[0][2]:  # Check if we're using daily summary data
            plt.plot(dates, max_temps, label='Max', marker='s')
            plt.plot(dates, min_temps, label='Min', marker='^')
        plt.title(f'{city} - Temperature Trend')
        plt.xlabel('Date/Time')
        plt.ylabel('Temperature (°C)')
        plt.legend()
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(f'{city}_temperature_trend.png')
        plt.close()

        print(f"Visualization created for {city}")

    conn.close()

# Main function
def main():
    setup_database()
    print("Fetching initial weather data...")
    for city, city_id in CITY_IDS.items():
        data = get_weather_data(city, city_id)
        if data:
            store_weather_data(data)
            check_alert_threshold(city, data['temp'])

    print("\nCreating initial visualizations...")
    create_visualizations()

    print("\nEntering continuous monitoring mode...")
    last_summary_time = datetime.now()

    while True:
        current_time = datetime.now()

        for city, city_id in CITY_IDS.items():
            data = get_weather_data(city, city_id)
            if data:
                store_weather_data(data)
                check_alert_threshold(city, data['temp'])
        
        # Calculate daily summary and create visualizations at midnight
        if current_time.hour == 0 and (current_time - last_summary_time).days >= 1:
            print("\nCalculating daily summary and updating visualizations...")
            summaries = calculate_daily_summary()
            for summary in summaries:
                print(f"{summary['city']} - Date: {summary['date']}, Avg Temp: {summary['avg_temp']:.2f}°C, "
                      f"Max Temp: {summary['max_temp']:.2f}°C, Min Temp: {summary['min_temp']:.2f}°C, "
                      f"Dominant Weather: {summary['dominant_weather']}")
            create_visualizations()
            last_summary_time = current_time
        
        # Update visualizations every hour
        elif current_time.minute == 0:
            print("\nUpdating visualizations with latest data...")
            create_visualizations()

        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()