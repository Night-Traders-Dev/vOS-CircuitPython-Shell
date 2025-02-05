# vOS-CircuitPython-Shell

Welcome to **vOS-CircuitPython-Shell**, a lightweight and flexible virtual operating system (vOS) shell for CircuitPython. This project allows you to execute commands, manage Wi-Fi connectivity, interact with hardware components, and more, all within a minimalistic shell environment on your Raspberry Pi Pico or similar CircuitPython-compatible devices.

---

## Features

- **Command Line Interface (CLI):** A simple, interactive shell that lets you run commands like `ls`, `cd`, `pwd`, and more.
- **Wi-Fi Management:** Connect to Wi-Fi networks, check connection status, and view IP address information.
- **Hardware Interaction:** Control and manage hardware components like neopixels, I2C sensors, displays, and more.
- **Remote Access:** Enable SSH to allow remote shell access for other users to interact with the vOS system.
- **System Monitoring:** Display system information such as RAM usage, uptime, and memory statistics.
- **Extensible Commands:** Add custom commands to interact with your specific hardware or system features.

---

## Installation

To get started with `vOS-CircuitPython-Shell`, you'll need:

- A Raspberry Pi Pico or other CircuitPython-compatible device.
- A compatible microcontroller (e.g., ESP32, ESP8266) for Wi-Fi connectivity.

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-username/vOS-CircuitPython-Shell.git
   ```

2. **Install CircuitPython:**
   Follow the [CircuitPython installation guide](https://circuitpython.org/board/raspberry_pi_pico/) to install CircuitPython on your device.

3. **Upload to Device:**
   Copy the `vOS-CircuitPython-Shell` files to the root of your CircuitPython device.

4. **Connect to Wi-Fi:**
   Ensure you have a valid Wi-Fi network setup for the device to connect to.

---

## Usage

### Starting the Shell

To start the shell, run `code.py` or execute it from the REPL:

```bash
python code.py
```

This will initiate the shell, where you can enter various commands.

### Available Commands

- **`ls`**: List the files and directories in the current directory.
- **`pwd`**: Print the current working directory.
- **`cd <directory>`**: Change the current working directory.
- **`run <script>`**: Run a specified Python script.
- **`cat <file>`**: Display the contents of a file.
- **`rm <file>`**: Remove a file.
- **`help`**: Show help information for available commands.
- **`uptime`**: Display system uptime.
- **`clear`**: Clear the screen.

### Wi-Fi Management

- **`wifi.connect`**: Connect to a Wi-Fi network using predefined SSID and password.
- **`ifconfig`**: Display network information (e.g., SSID and IP address).

### SSH Access

To enable remote shell access via SSH, make sure to run the `PicoSSH` server, and then you can connect to your device over SSH.

---

## Configuration

The `vOS-CircuitPython-Shell` is highly configurable. Some key settings can be adjusted in the `settings.toml` file, including Wi-Fi credentials, IP address, and SSH configurations.

### Example `settings.toml`:

```toml
[Wi-Fi]
SSID = "Your_SSID"
Password = "Your_Password"

[SSH]
Enabled = true
Port = 22
```

---

## Hardware Support

This shell can interact with various hardware components, including but not limited to:

- **Neopixels**: Control LEDs connected to a GPIO pin.
- **I2C Devices**: Interact with I2C sensors and displays.
- **Buttons, switches, and more**: Customize and add support for other devices.

---

## Troubleshooting

### Common Issues

- **Wi-Fi Connection Issues:** Ensure your Wi-Fi network is correctly configured in `settings.toml`. You may need to reset the Wi-Fi connection if it fails.
- **GPIO Pin Conflicts:** If you encounter errors related to GPIO pins being in use (e.g., neopixels), ensure that hardware resources are properly released by calling the `deinit()` method on peripherals.

### Errors during script execution:
If a script gives an error related to hardware (e.g., "GPIO pin already in use"), ensure that you call the `deinit()` method for any peripherals before re-running the script.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contributing

Contributions are welcome! Please feel free to open issues, submit pull requests, or provide suggestions for improvements.

---

## Acknowledgments

- **CircuitPython**: For providing an easy-to-use platform for microcontroller development.
- **Raspberry Pi Foundation**: For the Raspberry Pi Pico and related hardware.
- **ESP32/ESP8266**: For enabling Wi-Fi connectivity on microcontrollers.

---
