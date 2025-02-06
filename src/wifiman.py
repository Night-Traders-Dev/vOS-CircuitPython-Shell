import wifi
from dmesg import dmesg_log

SSID = ""
PASSWORD = ""
radio = None
ipaddr = None


def disconnect():
    if wifi.radio.enabled:
        print("Disconnecting wifi...\n")
        wifi.radio.enabled = False
        dmesg_log("Wifi Disconnected")
    else:
        print("Wifi already disconnected...\n")

def get_wifi_status():
    """Return the current Wi-Fi radio and IP address."""
    return radio, ipaddr
def wifi_stats():
    """Print current Wi-Fi stats."""
    if radio and ipaddr:
        print(f"Connected to: {SSID}")
        print(f"IP Address: {ipaddr}")
    else:
        print("Not connected to Wi-Fi.")

def connect():
    """Connect to Wi-Fi and store connection details."""
    global radio, ipaddr, SSID
    wifi.radio.enabled = False
    try:
        if not wifi.radio.enabled:
            wifi.radio.enabled = True
            dmesg_log("Wi-Fi radio enabled.")
        dmesg_log("Connecting to Wi-Fi...")
        wifi.radio.connect(SSID, PASSWORD, timeout=10.0)  # Increased timeout for more connection time
        dmesg_log("Connected to Wi-Fi.")
        # Store the connection details
        radio = wifi.radio
        ipaddr = wifi.radio.ipv4_address
        dmesg_log(f"IP Address: {ipaddr}")  # Debug: Check IP after connection

    except Exception as e:
        print(f"Wi-Fi connection failed: {e}")
        # Debug: Print available Wi-Fi networks
        print("Available networks:", wifi.radio.scan())
        print("Wi-Fi connection error details:", e)


