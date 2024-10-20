# Real-Time Weather Monitoring System

## Project Overview

This project implements a real-time data processing system for weather monitoring, utilizing the OpenWeatherMap API. It provides summarized insights using rollups and aggregates for multiple cities in India.

## Features

- Real-time weather data retrieval for six major Indian cities
- Daily weather summaries with rollups and aggregates
- Temperature-based alerting system
- Visualization of 7-day temperature trends(and also provides daily data visualizations)
- Data storage using SQLite database

## Dependencies

To run this project, you'll need:

- Python 3.7 or higher
- pip (Python package manager)
- Docker (optional, for containerization)
  (Here i did not used docker)
Python libraries:
- requests
- matplotlib
- sqlite3 (comes with Python standard library)

## Setup and Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-username/weather-monitoring-system.git
   cd weather-monitoring-system
   ```

2. Set up a virtual environment (optional but recommended):
   ```
   python -m venv venv
   # On mac ,use source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Sign up for a free API key at [OpenWeatherMap](https://openweathermap.org/api).

5. Replace `"YOUR_OPENWEATHERMAP_API_KEY"` in `weather_monitor.py` with your actual API key.

6. For the sending and receiving the email alerts , you have to give the sender mail and app password(should be created by you navigate to the google account/security and the search for app passwords there generate password then use that password in the alert function).

## Running the Application

To start the weather monitoring system:

```
python weather_monitor.py
```

The script will run continuously, fetching weather data every 5 minutes (configurable).

## Docker Support(optional)

To run the application in a Docker container:

1. Build the Docker image:
   ```
   docker build -t weather-monitoring-system .
   ```

2. Run the container:
   ```
   docker run -d --name weather-monitor weather-monitoring-system
   ```

## Visualizations

- Visualizations are created daily at midnight.
- 7-day temperature trend charts are generated for each city after receiving the 7-day temperature data.
- Now the visualizations are created only fo the data received after running.
- Overall day visualizations will get at midnight.
- PNG files are saved in the project directory with names like `Hyderabad_temperature_trend.png`.



1. Run the script and monitor the console output for any errors in data retrieval or processing.
2. Check the SQLite database (`weather_data.db`) for stored weather data and daily summaries.
3. Temporarily lower the `TEMPERATURE_THRESHOLD` in the script to trigger alerts more easily.
4. Review generated visualization files for accuracy.

## Bonus Features

- The system supports multiple cities, demonstrating scalability.
- Visualization of weather data trends is implemented using matplotlib.
- The code structure allows easy extension to include additional weather parameters.

## Project Structure

```
weather-monitoring-system/
│
├── weather_monitor.py    # Main script
├── requirements.txt      # Python dependencies
├── Dockerfile            # For Docker support
├── README.md             # This file
├── weather_data.db       # SQLite database (created when script runs)
└── [City]_temperature_trend.png    # Generated visualizations
```
System Architecture Diagram:

![weather_monitor_flowchart](https://github.com/user-attachments/assets/39297f47-990c-417f-bb76-7f5c722d2ec8)



**Result:
**
   
![result1 weather monitor](https://github.com/user-attachments/assets/84847c78-0bf8-4aca-b0a2-e7aa3309d40d)
The above image is the output occured in terminal after running the application. 

![showing alert for weather monitor](https://github.com/user-attachments/assets/3b0e0325-b5b5-4a01-ac5a-e23a8dc6521c)
The above image is the output occured in terminal , that alert sent and displaying the same in terminal.
Note: To check weather the alerts are receiving or not adjuct the threshold temperature to the less value and check.

![received mail alert weather monitor](https://github.com/user-attachments/assets/1002cd77-bfc2-4488-83d6-8923ec7b8d60)
The above image is alert received through the mail.


## Contributing

Contributions to improve the project are welcome. Please follow these steps:

1. Fork the repository
2. Create a new branch (`git checkout -b feature-branch`)
3. Make your changes and commit (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature-branch`)
5. Create a new Pull Request
