import time
import commands
import microcontroller
import wifiman
from picossh import PicoSSH

COMMANDS = {
    "ls": commands.ls,
    "pwd": commands.pwd,
    "clear": commands.clear,
    "help": commands.show_help,
    "wifi.connect": wifiman.connect,
    "wifi.disconnect": commands.disconnect,
    "ifconfig": commands.ifconfig,
    "version": commands.read_vos_version,
    "dmesg": commands.dmesg,
    "exit": lambda: print("Exiting shell.") or commands.exit(),
    "quit": lambda: print("Exiting shell.") or microcontroller.reset(),
}

def shell():
    commands.read_vos_version("dmesg")
    start_time = time.monotonic()
    wifiman.connect()
    commands.clear()  # Auto-clear screen on start
    print("Welcome to vOS Core\n")
    while True:
        try:
            input_str = input("vOS> ").strip()

            # Skip empty input
            if not input_str:
                continue

            # Handle commands with arguments (e.g., cd, run, etc.)
            if input_str.startswith("cd "):
                commands.cd(input_str[3:].strip())
            elif input_str.startswith("run "):
                commands.run(input_str[4:].strip())
            elif input_str.startswith("cat "):
                commands.cat(input_str[4:].strip())
            elif input_str.startswith("rm "):
                commands.rm(input_str[3:].strip())
            elif input_str.startswith("uptime"):
                commands.uptime(start_time)
            elif input_str.startswith("memuse"):
                commands.memuse("print")
            # Handle simple commands (without arguments)
            elif input_str in COMMANDS:
                COMMANDS[input_str]()  # Call the command function with no args

            else:
                print(f"Unknown command: {input_str}")

        except KeyboardInterrupt:
            print("\nShell interrupted. Type 'exit' to quit.")
        except Exception as e:
            print(f"Shell error: {e}")

# Run the shell
shell()
