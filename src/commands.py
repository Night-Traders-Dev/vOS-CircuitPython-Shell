import neopixel
import busio
import board
import sys
import os
import time
import gc
import wifiman

# Function to clear the screen
def clear():
    print("\033[2J\033[H", end="")  # ANSI escape code to clear screen

# Function to list files
def ls():
    try:
        files = os.listdir()
        for file in files:
            print(file)
    except Exception as e:
        print(f"Error listing files: {e}")

# Function to print the current working directory
def pwd():
    try:
        print(os.getcwd())
    except Exception as e:
        print(f"Error getting current directory: {e}")

# Function to change directory
def cd(path):
    try:
        os.chdir(path)
        print(f"Changed directory to {os.getcwd()}")
    except Exception as e:
        print(f"Error changing directory: {e}")

# Function to display file contents
def cat(filename):
    try:
        with open(filename, "r") as f:
            print(f.read())
    except Exception as e:
        print(f"Error reading {filename}: {e}")

# Function to delete a file
def rm(filename):
    try:
        os.remove(filename)
        print(f"Deleted {filename}")
    except Exception as e:
        print(f"Error deleting {filename}: {e}")

# Function to execute a Python script
def run(script_name):
    try:
        if script_name.endswith('.py') and script_name in os.listdir():
            print(f"Running {script_name}...")
            with open(script_name) as f:
                exec(f.read(), {})
        else:
            print(f"Error: {script_name} not found or invalid file type.")
    except Exception as e:
        print(f"Error running {script_name}: {e}")

# Function to display available commands
def show_help():
    print("Available commands:")
    print("  ls            - List files in the current directory")
    print("  pwd           - Print current working directory")
    print("  cd <dir>      - Change directory")
    print("  cat <file>    - Show contents of a file")
    print("  rm <file>     - Delete a file")
    print("  run <file.py> - Execute a Python script")
    print("  clear         - Clear the screen")
    print("  help          - Show this help message")
    print("  exit          - Exit the shell")


def ifconfig():
    radio, ipaddr = wifiman.get_wifi_status()
    print(f"SSID: {wifiman.SSID}")
    print(f"IP Address: {ipaddr}")
#        print(f"MAC Address: {':'.join(f'{b:02X}' for b in wifi.radio.mac_address)}")

def connect():
    wifiman.connect()

def disconnect():
    wifiman.disconnect()

def memuse():
    gc.collect()  # Run garbage collection to get accurate memory usage
    total_ram = gc.mem_alloc() + gc.mem_free()
    used_ram = gc.mem_alloc()
    free_ram = gc.mem_free()
    usage_percent = (used_ram / total_ram) * 100 if total_ram > 0 else 0

    print(f"Used RAM: {used_ram} bytes")
    print(f"Total RAM: {total_ram} bytes")
    print(f"Free RAM: {free_ram} bytes")
    print(f"Memory Usage: {usage_percent:.2f}%")

def uptime(start_time):
    elapsed = time.monotonic() - start_time
    hours = int(elapsed // 3600)
    minutes = int((elapsed % 3600) // 60)
    seconds = int(elapsed % 60)
    print(f"Uptime: {hours}h {minutes}m {seconds}s")

def exit():
    sys.exit()

def release_hardware():
    global pixels, i2cl, i2c0, display, sht_sensor
    try:
        # Reset neopixel
        pixels.deinit()

        # Reset I2C bus interfaces
        i2cl.deinit()
        i2c0.deinit()

        # If display is using I2C, deinitialize display
        if display:
            display.deinit()

        # If any sensors are using I2C, deinitialize them
        if sht_sensor:
            sht_sensor.deinit()

        print("Hardware released successfully.")
    except Exception as e:
        print(f"Error releasing hardware: {e}")
