#!/usr/bin/env python3
"""
Serial Monitor for MicroPython using pyboard

This module provides a serial monitor that can connect to MicroPython devices
and display real-time output with features like:
- Real-time output display
- Command input capability
- Automatic reconnection
- Colored output
- Timestamp logging
- Raw REPL mode support
"""

import sys
import time
import threading
import os
from datetime import datetime
from pyboard import Pyboard, PyboardError
from dotenv import load_dotenv

try:
    from colorama import init, Fore, Back, Style
    init()
    COLOR_SUPPORT = True
except ImportError:
    COLOR_SUPPORT = False
    # Fallback color definitions
    class Fore:
        RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = RESET = ""
    class Back:
        RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = RESET = ""
    class Style:
        BRIGHT = DIM = NORMAL = RESET_ALL = ""

# Load environment variables
load_dotenv()

class SerialMonitor:
    def __init__(self,
                 show_timestamps=True, auto_reconnect=True, raw_repl=False):
        """
        Initialize the Serial Monitor

        Args:
            device: Serial device path (e.g., /dev/ttyUSB0, COM3)
            baudrate: Baud rate for serial communication
            user: Username for telnet connections
            password: Password for telnet connections
            show_timestamps: Whether to show timestamps for each line
            auto_reconnect: Whether to automatically reconnect on disconnect
            raw_repl: Start in raw REPL mode
        """
        self.device = os.getenv('DEVICE')
        self.baud = os.getenv('BAUD')
        self.show_timestamps = show_timestamps
        self.auto_reconnect = auto_reconnect
        self.raw_repl = raw_repl

        self.pyboard = None
        self.running = False
        self.input_thread = None
        self.monitor_thread = None

        # Statistics
        self.bytes_received = 0
        self.bytes_sent = 0
        self.start_time = None
        self.reconnect_count = 0

    def connect(self):
        """Connect to the MicroPython device"""
        try:
            self.print_status(f"Connecting to {self.device} at {self.baud} baud...")

            self.pyboard = Pyboard(
                device=self.device,
                baudrate=self.baud,
                wait=2,
                exclusive=True
            )

            if self.raw_repl:
                self.pyboard.enter_raw_repl(soft_reset=False)
                self.print_status("Entered RAW REPL mode")

            self.print_status(f"Connected to {self.device}")
            return True

        except PyboardError as e:
            self.print_error(f"Failed to connect: {e}")
            return False
        except Exception as e:
            self.print_error(f"Connection error: {e}")
            return False

    def disconnect(self):
        """Disconnect from the device"""
        if self.pyboard:
            try:
                if self.raw_repl:
                    self.pyboard.exit_raw_repl()
                self.pyboard.close()
                self.print_status("Disconnected")
            except:
                pass
            finally:
                self.pyboard = None

    def print_status(self, message):
        """Print a status message with color and timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S") if self.show_timestamps else ""
        prefix = f"[{timestamp}] " if timestamp else ""

        if COLOR_SUPPORT:
            print(f"{Fore.CYAN}{prefix}[MONITOR] {message}{Style.RESET_ALL}")
        else:
            print(f"{prefix}[MONITOR] {message}")

    def print_error(self, message):
        """Print an error message with color"""
        timestamp = datetime.now().strftime("%H:%M:%S") if self.show_timestamps else ""
        prefix = f"[{timestamp}] " if timestamp else ""

        if COLOR_SUPPORT:
            print(f"{Fore.RED}{prefix}[ERROR] {message}{Style.RESET_ALL}")
        else:
            print(f"{prefix}[ERROR] {message}")

    def print_data(self, data):
        """Print received data with timestamp"""
        if not data:
            return

        try:
            # Try to decode as UTF-8
            text = data.decode('utf-8', errors='replace')

            # Split into lines but preserve line endings
            lines = text.splitlines(keepends=True)

            for line in lines:
                if line.strip():  # Only print non-empty lines
                    timestamp = datetime.now().strftime("%H:%M:%S") if self.show_timestamps else ""
                    prefix = f"[{timestamp}] " if timestamp else ""

                    if COLOR_SUPPORT:
                        print(f"{Fore.WHITE}{prefix}{line.rstrip()}{Style.RESET_ALL}")
                    else:
                        print(f"{prefix}{line.rstrip()}")

            self.bytes_received += len(data)

        except Exception as e:
            self.print_error(f"Error processing data: {e}")

    def send_command(self, command):
        """Send a command to the device"""
        if not self.pyboard:
            self.print_error("Not connected to device")
            return False

        try:
            if self.raw_repl:
                # In raw REPL mode, execute the command
                result, error = self.pyboard.exec_raw(command)
                if result:
                    self.print_data(result)
                if error:
                    self.print_error(error.decode('utf-8', errors='replace'))
            else:
                # In normal mode, send the command directly
                command_bytes = (command + '\r\n').encode('utf-8')
                self.pyboard.serial.write(command_bytes)
                self.bytes_sent += len(command_bytes)

            return True

        except Exception as e:
            self.print_error(f"Error sending command: {e}")
            return False

    def monitor_loop(self):
        """Main monitoring loop"""
        buffer = bytearray()

        while self.running:
            try:
                if not self.pyboard:
                    if self.auto_reconnect:
                        self.print_status("Attempting to reconnect...")
                        if self.connect():
                            self.reconnect_count += 1
                            continue
                        else:
                            time.sleep(2)  # Wait before retry
                            continue
                    else:
                        break

                # Check for incoming data
                if self.pyboard.serial.inWaiting() > 0:
                    try:
                        data = self.pyboard.serial.read(self.pyboard.serial.inWaiting())
                        if data:
                            buffer.extend(data)

                            # Process complete lines
                            while b'\n' in buffer:
                                line_end = buffer.find(b'\n')
                                line = bytes(buffer[:line_end + 1])
                                buffer = buffer[line_end + 1:]
                                self.print_data(line)

                            # If buffer gets too large, flush it
                            if len(buffer) > 1024:
                                self.print_data(bytes(buffer))
                                buffer.clear()

                    except Exception as e:
                        self.print_error(f"Error reading data: {e}")
                        if self.auto_reconnect:
                            self.disconnect()
                            continue
                        else:
                            break
                else:
                    time.sleep(0.01)  # Short sleep to prevent CPU spinning

            except KeyboardInterrupt:
                break
            except Exception as e:
                self.print_error(f"Monitor loop error: {e}")
                if self.auto_reconnect:
                    self.disconnect()
                    time.sleep(1)
                else:
                    break

        # Print any remaining buffer data
        if buffer:
            self.print_data(bytes(buffer))

    def input_loop(self):
        """Handle user input"""
        self.print_status("Enter commands (Ctrl+C to exit, 'help' for commands)")

        while self.running:
            try:
                # Get user input
                user_input = input().strip()

                if not user_input:
                    continue

                # Handle special commands
                if user_input.lower() == 'help':
                    self.show_help()
                elif user_input.lower() == 'stats':
                    self.show_stats()
                elif user_input.lower() == 'reconnect':
                    self.disconnect()
                    self.connect()
                elif user_input.lower() == 'raw':
                    self.toggle_raw_repl()
                elif user_input.lower() in ['exit', 'quit']:
                    self.running = False
                    break
                elif user_input.lower() == 'reset':
                    self.send_reset()
                else:
                    # Send command to device
                    self.send_command(user_input)

            except EOFError:
                break
            except KeyboardInterrupt:
                break

    def show_help(self):
        """Show help information"""
        help_text = """
Available commands:
  help        - Show this help message
  stats       - Show connection statistics
  reconnect   - Reconnect to device
  raw         - Toggle raw REPL mode
  reset       - Send soft reset (Ctrl+D)
  exit/quit   - Exit monitor
  
Any other input will be sent to the device.
Use Ctrl+C to exit.
        """
        print(help_text)

    def show_stats(self):
        """Show connection statistics"""
        if self.start_time:
            uptime = time.time() - self.start_time
            uptime_str = f"{int(uptime // 3600):02d}:{int((uptime % 3600) // 60):02d}:{int(uptime % 60):02d}"
        else:
            uptime_str = "00:00:00"

        stats = f"""
Connection Statistics:
  Device: {self.device}
  Baud Rate: {self.baud}
  Uptime: {uptime_str}
  Bytes Received: {self.bytes_received}
  Bytes Sent: {self.bytes_sent}
  Reconnections: {self.reconnect_count}
  Raw REPL Mode: {'Yes' if self.raw_repl else 'No'}
        """
        print(stats)

    def toggle_raw_repl(self):
        """Toggle raw REPL mode"""
        if not self.pyboard:
            self.print_error("Not connected to device")
            return

        try:
            if self.raw_repl:
                self.pyboard.exit_raw_repl()
                self.raw_repl = False
                self.print_status("Exited RAW REPL mode")
            else:
                self.pyboard.enter_raw_repl()
                self.raw_repl = True
                self.print_status("Entered RAW REPL mode")
        except Exception as e:
            self.print_error(f"Error toggling RAW REPL: {e}")

    def send_reset(self):
        """Send soft reset command"""
        if not self.pyboard:
            self.print_error("Not connected to device")
            return

        try:
            self.print_status("Sending soft reset...")
            self.pyboard.serial.write(b'\x04')  # Ctrl+D
            self.bytes_sent += 1
        except Exception as e:
            self.print_error(f"Error sending reset: {e}")

    def start(self):
        """Start the serial monitor"""
        self.print_status("Starting Serial Monitor...")
        self.print_status(f"Device: {self.device}, Baud: {self.baud}")

        if not self.connect():
            return False

        self.running = True
        self.start_time = time.time()

        # Start monitor thread
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()

        # Start input thread
        self.input_thread = threading.Thread(target=self.input_loop, daemon=True)
        self.input_thread.start()

        try:
            # Wait for threads to complete
            self.input_thread.join()
        except KeyboardInterrupt:
            self.print_status("Interrupted by user")
        finally:
            self.stop()

        return True

    def stop(self):
        """Stop the serial monitor"""
        self.running = False
        self.disconnect()

        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1)

        self.print_status("Serial monitor stopped")


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description='MicroPython Serial Monitor')
    parser.add_argument('--no-timestamps',
                        action='store_true',
                        help='Disable timestamp display')
    parser.add_argument('--no-reconnect',
                        action='store_true',
                        help='Disable automatic reconnection')
    parser.add_argument('--raw-repl',
                        action='store_true',
                        help='Start in raw REPL mode')

    args = parser.parse_args()

    # Create and start monitor
    monitor = SerialMonitor(
        show_timestamps=not args.no_timestamps,
        auto_reconnect=not args.no_reconnect,
        raw_repl=args.raw_repl
    )

    try:
        monitor.start()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())