import neopixel
import busio
import board
import storage
import sys
import os
import time
import gc
import wifiman
from dmesg import dmesg_print, dmesg_log

def storage_init():
    storage.remount("/", readonly=False)


def dmesg():
    dmesg_print()

# Function to clear the screen
def clear():
    print("\033[2J\033[H", end="")  # ANSI escape code to clear screen


# Function to format file permissions
def format_permissions(mode):
    perms = ['d' if mode & 0x4000 else '-']
    for i in range(3):
        perms.append('r' if mode & (0o400 >> (i * 3)) else '-')
        perms.append('w' if mode & (0o200 >> (i * 3)) else '-')
        perms.append('x' if mode & (0o100 >> (i * 3)) else '-')
    return ''.join(perms)

# Function to manually format the timestamp
def format_time(modified_time):
    return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
        modified_time.tm_year, modified_time.tm_mon, modified_time.tm_mday,
        modified_time.tm_hour, modified_time.tm_min, modified_time.tm_sec
    )

# Function to list files with timestamps, color coding, and permissions
def ls():
    try:
        files = os.listdir()
        print(f"{'Permissions':<12} {'Name':<20} {'Type':<10} {'Size (bytes)':>12} {'Last Modified':>20}")
        print("-" * 80)

        for file in files:
            stats = os.stat(file)
            size = stats[6]  # File size in bytes
            modified_time = time.localtime(stats[7])  # Last modified timestamp
            formatted_time = format_time(modified_time)

            # Check if it's a directory
            if stats[0] & 0x4000:
                file_type = "\033[94mDirectory\033[0m"  # Blue for directories
                file_name = f"\033[94m{file}\033[0m"
            else:
                file_type = "\033[92mFile\033[0m"  # Green for files
                file_name = f"\033[92m{file}\033[0m"

            permissions = format_permissions(stats[0])

            # Display the file with formatting
            print(f"{permissions:<12} {file_name:<20} {file_type:<10} {size:>12} {formatted_time:>20}")

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
            dmesg_log(f"Running {script_name}...")
            memuse("dmesg")
            with open(script_name) as f:
                exec(f.read(), {})
            memuse("dmesg")
        else:
            print(f"Error: {script_name} not found or invalid file type.")
    except Exception as e:
        dmesg_log(f"Error running {script_name}: {e}")

# Function to display available commands
def show_help():
    print("Available commands:")
    print("  ls            - List files in the current directory")
    print("  pwd           - Print current working directory")
    print("  cd <dir>      - Change directory")
    print("  cat <file>    - Show contents of a file")
    print("  rm <file>     - Delete a file")
    print("  run <file.py> - Execute a Python script")
    print("  touch <file>  - Create a new empty file")
    print("  mkdir <dir>   - Create a new directory")
    print("  rmdir <dir>   - Remove an empty directory")
    print("  mv <src> <dst>- Move or rename a file or directory")
    print("  cp <src> <dst>- Copy a file")
    print("  echo <text>   - Display text or write to a file")
    print("  df            - Show disk space usage")
    print("  whoami        - Display current user")
    print("  memuse        - Display memory usage")
    print("  uptime        - Show system uptime")
    print("  dmesg         - Display system messages")
    print("  clear         - Clear the screen")
    print("  help          - Show this help message")
    print("  exit          - Exit the shell")
    print("  quit          - Reboot the system")


def ifconfig():
    radio, ipaddr = wifiman.get_wifi_status()
    print(f"SSID: {wifiman.SSID}")
    print(f"IP Address: {ipaddr}")
#        print(f"MAC Address: {':'.join(f'{b:02X}' for b in wifi.radio.mac_address)}")

def connect():
    wifiman.connect()

def disconnect():
    wifiman.disconnect()

def memuse(call):
    gc.collect()  # Run garbage collection to get accurate memory usage
    total_ram = gc.mem_alloc() + gc.mem_free()
    used_ram = gc.mem_alloc()
    free_ram = gc.mem_free()
    usage_percent = (used_ram / total_ram) * 100 if total_ram > 0 else 0

    usedmsg = (f"Used RAM: {used_ram:,} bytes")
    totalmsg = (f"Total RAM: {total_ram:,} bytes")
    freemsg  = (f"Free RAM: {free_ram:,} bytes")
    percmsg = (f"Memory Usage: {usage_percent:.2f}%")
    msg_list = [usedmsg, totalmsg, freemsg, percmsg]
    for msg in msg_list:
        if call == "print":
            print(msg)
        dmesg_log(msg)

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


def read_vos_version(call):
    try:
        # Open the file in read mode
        with open("/vos.info", "r") as file:
            # Read the first line (version)
            version = file.readline().strip()  # Remove any extra spaces or newlines
            msg = (f"vOS version: {version}")
            if call == "dmesg":
                dmesg_log(msg)
            print(msg)
    except FileNotFoundError:
        print("Error: vos.info file not found.")
    except Exception as e:
        print(f"Error reading vos.info: {e}")


def head(filename, n=10):
    try:
        with open(filename, 'r') as file:
            for i in range(n):
                line = file.readline()
                if not line:
                    break
                print(line, end='')
    except Exception as e:
        print(f"Error reading {filename}: {e}")


def tail(filename, n=10):
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
            for line in lines[-n:]:
                print(line, end='')
    except Exception as e:
        print(f"Error reading {filename}: {e}")



def echo(text, filename=None):
    try:
        if filename:
            with open(filename, 'w') as file:
                file.write(text)
            print(f"Text written to {filename}")
        else:
            print(text)
    except Exception as e:
        print(f"Error with echo command: {e}")



def df():
    try:
        fs_stat = os.statvfs('/')
        total = fs_stat[0] * fs_stat[2]
        free = fs_stat[0] * fs_stat[3]
        used = total - free
        print(f"Total: {total} bytes, Used: {used} bytes, Free: {free} bytes")
    except Exception as e:
        print(f"Error fetching disk usage: {e}")


def rmdir(dirname):
    try:
        os.rmdir(dirname)
        print(f"Directory {dirname} removed.")
    except Exception as e:
        print(f"Error removing directory {dirname}: {e}")




def mkdir(dirname):
    try:
        os.mkdir(dirname)
        print(f"Directory {dirname} created.")
    except Exception as e:
        print(f"Error creating directory {dirname}: {e}")


def touch(filename):
    try:
        with open(filename, 'a'):
            os.utime(filename, None)
        print(f"{filename} created/updated.")
    except Exception as e:
        print(f"Error creating/updating {filename}: {e}")

def mv(source, destination):
    try:
        os.rename(source, destination)
        print(f"{source} moved/renamed to {destination}.")
    except Exception as e:
        print(f"Error moving/renaming {source}: {e}")


def cp(source, destination):
    try:
        with open(source, 'rb') as src_file:
            with open(destination, 'wb') as dest_file:
                dest_file.write(src_file.read())
        print(f"{source} copied to {destination}.")
    except Exception as e:
        print(f"Error copying {source}: {e}")



def whoami():
    print("vos")
