import time

# List to store log messages
dmesg_logs = []

# Function to log messages with timestamp
def dmesg_log(message):
    t = time.localtime()
    timestamp = f"{t[0]}-{t[1]:02d}-{t[2]:02d} {t[3]:02d}:{t[4]:02d}:{t[5]:02d}"
    log_entry = f"{timestamp} - {message}"
    dmesg_logs.append(log_entry)

# Function to print all logged messages
def dmesg_print():
    if not dmesg_logs:
        print("No messages logged.")
    else:
        for log in dmesg_logs:
            print(log)
