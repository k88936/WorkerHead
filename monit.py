#!/usr/bin/env python3
import os

from dotenv import load_dotenv

from monitor.monitor import SerialMonitor

# Initialize colorama
def main():
    # Set up logging to show INFO level messages
    # logging.basicConfig(level=logging.INFO)
    load_dotenv()
    PORT = os.getenv("DEVICE")
    BAUD = int(os.getenv("BAUD", "115200"))
    serial = SerialMonitor(PORT, BAUD)
    serial.connect()
    serial.start()


if __name__ == "__main__":
    main()
