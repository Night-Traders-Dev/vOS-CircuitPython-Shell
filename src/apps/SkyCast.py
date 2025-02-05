import adafruit_ntp
import adafruit_requests
import board
import busio
import digitalio
import gc
import neopixel
import rtc
import socketpool
import ssl
import time
import wifi
from adafruit_sht31d import SHT31D
from adafruit_ssd1306 import SSD1306_I2C


pixels = neopixel.NeoPixel(board.GP22, 1)
i2cl = busio.I2C(scl=board.GP15, sda=board.GP14)
i2c0 = busio.I2C(scl=board.GP17, sda=board.GP16)
display = SSD1306_I2C(128, 64, i2c0)
sht_sensor = SHT31D(i2cl)

SSID = ""
PASSWORD = ""
API_KEY = ""
latitude = 0.0
longitude = -0.0

try:
    if not wifi.radio.enabled:
        wifi.radio.enabled = True
    print("Connecting to Wi-Fi...")
    wifi.radio.connect(SSID, PASSWORD, timeout=5.0)
    print("Connected")
except Exception as e:
    print(f"Wi-Fi connection failed: {e}")


pool = socketpool.SocketPool(wifi.radio)
ssl_context = ssl.create_default_context()
requests = adafruit_requests.Session(pool, ssl_context)

weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={API_KEY}&units=imperial"

buffer = ""
unsent_messages = {}
retry_limit = 3
MAX_RETRIES = 3
TIMEOUT = 10

def fetch_weather_data_with_retries(requests_session, url, retries=3, delay=2):
    attempt = 0
    gc.collect()
    while attempt < retries:
        try:
            print(f"Attempt {attempt + 1} of {retries} to fetch weather data...")
            response = requests_session.get(url, timeout=10)  # Perform the GET request
            if response.status_code == 200:
                return response.json()  # Return the JSON response if successful
            else:
                print(f"Error: HTTP {response.status_code}")
        except Exception as e:
            print(f"Error occurred: {e}")

        attempt += 1
        if attempt < retries:
            print(f"Retrying in {delay} seconds...")
            wifi.radio.enabled = False
            time.sleep(delay)
            wifi.radio.enabled = True
            wifi.radio.connect(SSID, PASSWORD, timeout=5.0)
        else:
            print("Max retries reached. Failing.")
            raise RuntimeError("Failed to fetch weather data after retries.")


def get_cardinal_direction(degrees: float) -> str:
    """Return the cardinal direction (N, NE, E, SE, S, SW, W, NW) for given wind direction degrees."""
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    degrees = degrees % 360
    index = int((degrees + 22.5) // 45) % 8
    return directions[index]

# Function to convert Celsius to Fahrenheit
def c_to_f(temp):
    return (temp * 9/5) + 32

# Function to map temperature to RGB color
def temperature_to_color(temp_f):
    # Define temperature ranges and corresponding RGB colors
    color_map = [
        (0, (0, 0, 255)),    # Blue for freezing
        (10, (0, 128, 255)), # Light blue
        (20, (0, 255, 255)), # Cyan
        (30, (0, 255, 128)), # Aqua-green
        (40, (0, 255, 0)),   # Green
        (50, (128, 255, 0)), # Yellow-green
        (60, (255, 255, 0)), # Yellow
        (70, (255, 128, 0)), # Orange
        (80, (255, 0, 0)),   # Red
        (90, (128, 0, 128)), # Purple
        (100, (255, 0, 255)) # Magenta
    ]

    # Find the closest temperature range
    for i in range(len(color_map) - 1):
        if color_map[i][0] <= temp_f < color_map[i + 1][0]:
            # Linear interpolation between colors
            t1, c1 = color_map[i]
            t2, c2 = color_map[i + 1]
            ratio = (temp_f - t1) / (t2 - t1)
            r = int(c1[0] + ratio * (c2[0] - c1[0]))
            g = int(c1[1] + ratio * (c2[1] - c1[1]))
            b = int(c1[2] + ratio * (c2[2] - c1[2]))
            return (r, g, b)

    # If the temperature is out of range, return the nearest color
    if temp_f < color_map[0][0]:
        return color_map[0][1]
    elif temp_f > color_map[-1][0]:
        return color_map[-1][1]


def display_text(str, line):
    display.text(str, 0, (line % 8) * 8, 1, font_name="/lib/font5x8.bin")


def get_ram():
    free_memory = gc.mem_free()
    allocated_memory = gc.mem_alloc()
    total_memory = free_memory + allocated_memory
    used_memory_percentage = (allocated_memory / total_memory) * 100
    ram_usage = f"Used: {allocated_memory // 1024} KB"
    ram_free = f"Free: {free_memory // 1024} KB"
    ram_total = f"Total: {total_memory // 1024} KB"
    ram_percent = f"Usage: {used_memory_percentage:.2f}%"
    ram_display = f"Ram: {allocated_memory // 1024}/{total_memory // 1024} KB({used_memory_percentage:.2f})%"
    return ram_usage, ram_free, ram_total, ram_percent, ram_display

def get_time_with_retry():
    retries = 0
    while retries < MAX_RETRIES:
        try:
            start_time = time.monotonic()
            ntp = adafruit_ntp.NTP(pool, tz_offset=-5)
            rtc.RTC().datetime = ntp.datetime
            now = time.localtime()

            # If it reaches here, it means it succeeded
            return now

        except Exception as e:
            retries += 1
            elapsed_time = time.monotonic() - start_time
            if elapsed_time >= TIMEOUT:
                raise TimeoutError("NTP request timed out.")
            elif retries >= MAX_RETRIES:
                raise Exception("Max retries reached. Failed to get NTP time.")
            else:
                print(f"Retry {retries}/{MAX_RETRIES} after error: {e}")
                time.sleep(2 ** retries)  # Exponential backoff before retrying


# Main loop
while True:
    try:
        weather_data = fetch_weather_data_with_retries(requests, weather_url, retries=5, delay=3)
        print("Weather data fetched successfully:")
    except Exception as e:
        print(f"Failed to fetch weather data: {e}")

    # Extract current weather data
    temperature = weather_data['main']['temp']            # °F (units=imperial)
    windspeed = weather_data['wind']['speed']             # mph
    winddirec = weather_data['wind']['deg']               # degrees
    humidity = weather_data['main']['humidity']           # %
    condition = weather_data['weather'][0]['description'] # textual condition
    # Check for rain/snow keys in the current weather data
    precip = 0
    if 'rain' in weather_data and '1h' in weather_data['rain']:
        precip = weather_data['rain']['1h']  # mm in last hour
    elif 'rain' in weather_data and '3h' in weather_data['rain']:
        precip = weather_data['rain']['3h']  # mm in last 3 hours

    if 'snow' in weather_data and '1h' in weather_data['snow']:
        precip = weather_data['snow']['1h']  # mm in last hour
    elif 'snow' in weather_data and '3h' in weather_data['snow']:
         precip = weather_data['snow']['3h']  # mm in last 3 hours

    weather_info = [
        f"Temp: {temperature}°F",
        f"Windspeed: {windspeed} mph",
        f"Winddirection: {get_cardinal_direction(winddirec)}",
        f"Condition: {condition}",
        f"Humidity: {humidity}%",
        f"Precipitation: {precip}mm"
    ]

    display.fill(0)
    temp_c = sht_sensor.temperature
    humi = sht_sensor.relative_humidity

    # Convert temperature to Fahrenheit
    temp_f = c_to_f(temp_c)

    # Get color based on temperature
    color = temperature_to_color(temp_f)

    # Update NeoPixel color
    pixels[0] = color

    # Print temperature, humidity, and color
    display_text(f"Temp: {temp_f:.2f}/{temperature:.2f}F", 0)
    display_text(f"Humidity: {humi:.2f}/{humidity:.2f}%", 2)
    display_text(f"IP: {wifi.radio.ipv4_address}", 6)
    print("Weather Metrics and Sensors Displayed...\n")

    # Delay
    display.show()
    time.sleep(15)
    display.fill(0)
    ram_usage, ram_free, ram_total, ram_percent, ram_display = get_ram()
    display_text(ram_free, 0)
    display_text(ram_total, 2)
    display_text(ram_percent, 4)
    now = get_time_with_retry()
    display_text("{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
    now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec
    ), 6)
    print("Ram and Time Info Displayed...\n")
    display.show()
    time.sleep(5)
