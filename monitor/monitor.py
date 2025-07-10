# serial_debugger.py
import os
import sys
import time
from threading import Thread
from typing import Optional
from dotenv import load_dotenv
from colorama import Fore, Back, Style, init

from .connection import ReadingTimeoutError
from .serial_connection import SerialConnection


# Load environment variables

class SerialMonitor:
    def __init__(self, port: str, baud: int):
        self.conn: Optional[SerialConnection] = None
        self.port = port
        self.baud = baud
        self.running = False

    def connect(self):
        try:
            print(Fore.GREEN + Style.BRIGHT + f"Connecting to {self.port} at {self.baud} baud...")
            self.conn = SerialConnection(port=self.port, baudrate=self.baud)
            print(Fore.GREEN + Style.BRIGHT + "Connected.")
        except Exception as e:
            print(Fore.RED + Style.BRIGHT + f"Connection failed: {e}")
            sys.exit(1)

    def read_loop(self):
        while self.running:
            try:
                data = self.conn.read_all()
                if data:
                    print(data.decode("utf-8", errors="replace"), end="")
            except Exception as e:
                print(Fore.RED + Style.BRIGHT + f"Read error: {e}")
                break

    def write_loop(self):
        while self.running:
            try:
                line = input()
                self.conn.write(line.encode("utf-8") + b"\r\n")
            except KeyboardInterrupt:
                self.stop()
            except Exception as e:
                print(Fore.RED + Style.BRIGHT + f"Write error: {e}")
                break

    def start(self):
        self.running = True
        read_thread = Thread(target=self.read_loop, daemon=True)
        read_thread.start()

        try:
            self.write_loop()
        finally:
            self.stop()

    def stop(self):
        self.running = False
        if self.conn:
            self.conn.close()
        print(Fore.GREEN + Style.BRIGHT + "Connection closed.")
