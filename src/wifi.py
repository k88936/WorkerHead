import network
import time
import urequests

# Replace with your network name (SSID) and password
ssid = 'k88936_mobile'
password = 'k8893666'

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print('Connecting to network...')
        wlan.connect(ssid, password)

        # Wait for connection (timeout in 10 seconds)
        timeout = 10
        while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1

    if wlan.isconnected():
        url = "http://httpbin.org/post"
        data = '{"name": "ESP32", "value": 42}'
        headers = {'Content-Type': 'application/json'}

        response = urequests.post(url, data=data, headers=headers)
        print(response.text)
        response.close()
        print('Connected!')
        print('Network config:', wlan.ifconfig())
    else:
        print('Failed to connect.')