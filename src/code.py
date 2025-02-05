import os
import sys
import time
import board
import digitalio

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

# Function to simulate a basic shell loop with Ctrl+C handling
def shell():
    clear()  # Auto-clear screen on start
    print("Welcome to vOS Core\n")

    while True:
        try:
            input_str = input("vOS> ").strip()

            if input_str == "ls":
                ls()
            elif input_str == "pwd":
                pwd()
            elif input_str.startswith("cd "):
                cd(input_str[3:].strip())
            elif input_str.startswith("run "):
                run(input_str[4:].strip())
            elif input_str.startswith("cat "):
                cat(input_str[4:].strip())
            elif input_str.startswith("rm "):
                rm(input_str[3:].strip())
            elif input_str == "clear":
                clear()
            elif input_str == "help":
                show_help()
            elif input_str in ["exit", "quit"]:
                print("Exiting shell.")
                break
            else:
                print(f"Unknown command: {input_str}")
        except KeyboardInterrupt:
            print("\nShell interrupted. Type 'exit' to quit.")
        except Exception as e:
            print(f"Shell error: {e}")

# Run the shell
shell()
