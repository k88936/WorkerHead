#!/usr/bin/env python3

import upload, monit
def main():
    upload.upload_changed_files()
    monit.main()
if __name__ == '__main__':
    main()