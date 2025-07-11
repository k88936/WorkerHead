#!/usr/bin/env python3

import upload, monitor
def main():
    upload.upload_changed_files()
    monitor.main()
if __name__ == '__main__':
    main()