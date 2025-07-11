#!/usr/bin/env python3

import os
import sys
import time
import argparse
import hashlib
import dotenv
from pathlib import Path
from colorama import Fore, Back, Style, init

# Initialize colorama
init(autoreset=True)

# Import pyboard module from local path
from pyboard import Pyboard, PyboardError


def get_file_hash(file_path):
    """Calculate MD5 hash of a file"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def save_uploaded_file_hash(file_path, file_hash):
    """Save hash of uploaded file"""
    os.makedirs(".uploaded", exist_ok=True)
    with open(os.path.join(".uploaded", os.path.basename(file_path) + ".md5"), "w") as f:
        f.write(file_hash)


def get_uploaded_file_hash(file_path):
    """Get saved hash of uploaded file"""
    hash_file = os.path.join(".uploaded", os.path.basename(file_path) + ".md5")
    if os.path.exists(hash_file):
        with open(hash_file, "r") as f:
            return f.read().strip()
    return None


def has_file_changed(file_path):
    """Check if file has changed since last upload"""
    current_hash = get_file_hash(file_path)
    saved_hash = get_uploaded_file_hash(file_path)
    return saved_hash != current_hash


def upload_file(pyb, src_path, dest_path):
    """Upload a file to the pyboard"""
    print(Fore.CYAN + f"Uploading {src_path} to {dest_path}")
    try:
        # Check if directory exists, create if not
        dir_path = os.path.dirname(dest_path)
        if dir_path:
            try:
                pyb.fs_stat(dir_path)
            except PyboardError:
                print(Fore.YELLOW + f"Creating directory {dir_path}")
                pyb.fs_mkdir(dir_path)

        # Upload file
        pyb.fs_put(src_path, dest_path)

        # Save hash after successful upload
        save_uploaded_file_hash(src_path, get_file_hash(src_path))
        return True
    except Exception as e:
        print(Fore.RED + Style.BRIGHT + f"Error uploading {src_path}: {e}")
        return False


def upload_changed_files(src_dir="./src", all_files=False):
    """Upload changed files from src_dir to pyboard"""
    try:
        dotenv.load_dotenv()
        DEVICE = os.environ.get("DEVICE")
        # Connect to the pyboard
        print(Fore.GREEN + Style.BRIGHT + f"Connecting to pyboard at {DEVICE}...")
        pyb = Pyboard(DEVICE)
        pyb.enter_raw_repl(soft_reset=False)
        print(Fore.GREEN + "Raw REPL mode entered")

        # Get list of Python files in src_dir
        py_files = []
        print(Fore.CYAN + f"Scanning {src_dir} for Python files...")
        for root, _, files in os.walk(src_dir):
            for file in files:
                if file.endswith(".py"):
                    py_files.append(os.path.join(root, file))

        if not py_files:
            print(Fore.YELLOW + Style.BRIGHT + f"No Python files found in {src_dir}")
            return

        # Track upload statistics
        uploaded = 0
        skipped = 0
        failed = 0

        # Process each file
        for src_file in py_files:
            # Calculate destination path (map ./src to root of pyboard)
            rel_path = os.path.relpath(src_file, src_dir)
            dest_file = "/" + rel_path.replace(os.path.sep, "/")

            # Check if file has changed or we're uploading all files
            if all_files or has_file_changed(src_file):
                if upload_file(pyb, src_file, dest_file):
                    uploaded += 1
                else:
                    failed += 1
            else:
                print(Fore.BLUE + f"Skipping unchanged file: {src_file}")
                skipped += 1

        # Print summary
        print(Style.BRIGHT + f"\nUpload summary:")
        print(Fore.GREEN + f"  Uploaded: {uploaded}")
        print(Fore.BLUE + f"  Skipped:  {skipped}")
        print(Fore.RED + f"  Failed:   {failed}")

        # Exit raw REPL mode
        pyb.exit_raw_repl()
        pyb.serial.write(b"\x04")  # ctrl-D: soft reset
        pyb.close()

    except Exception as e:
        print(Fore.RED + Style.BRIGHT + f"Error: {e}")
        sys.exit(1)


def main():
    # Load environment variables
    dotenv.load_dotenv()

    # Display banner
    print(Style.BRIGHT + Fore.CYAN + "="*60)
    print(Style.BRIGHT + Fore.CYAN + "         MicroPython File Uploader")
    print(Style.BRIGHT + Fore.CYAN + "="*60)

    # Get device from environment or use default
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Upload Python files to pyboard")
    parser.add_argument("--all", action="store_true", help="Upload all files, not just changed ones")
    args = parser.parse_args()

    if args.all:
        print(Fore.YELLOW + "Mode: Uploading ALL files")
    else:
        print(Fore.YELLOW + "Mode: Uploading only CHANGED files")

    upload_changed_files(all_files=args.all)


if __name__ == "__main__":
    main()
