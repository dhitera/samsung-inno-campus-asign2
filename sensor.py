import network
import time
import urequests
import ujson
from machine import Pin
import dht
from umqtt.simple import MQTTClient

#inisialisasi wifi
SSID = "capnal"
PASSWORD = "capnal123"

#inisialisasi ubidots
UBIDOTS_DEVICE_LABEL = "esp-32_sic6"
UBIDOTS_TOKEN = "BBUS-EDEsI39lXmYaGC6iiCP1wwV6zoPupN"
UBIDOTS_BROKER = "industrial.api.ubidots.com"
UBIDOTS_TOPIC = b"/v1.6/devices/" + UBIDOTS_DEVICE_LABEL.encode()
MQTT_CLIENT_ID = "esp32-weather-logger"

#inisialisasi flask endpoint
SERVER_URL = "http://192.168.51.234:5000/upload"

#inisialisasi sensor
DHT_PIN = 15  # DHT11 on GPIO15
PIR_PIN = 14   # HC-SR501 on GPIO4
led = Pin(4, Pin.OUT)

dht_sensor = dht.DHT11(Pin(DHT_PIN))
pir_sensor = Pin(PIR_PIN, Pin.IN)

#koneksi ke wifi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

while not wlan.isconnected():
    print("Connecting to Wi-Fi...")
    time.sleep(1)

print("Connected, IP address:", wlan.ifconfig()[0])

#koneksi ke ubidots
print("Connecting to Ubidots MQTT server...", end="")
client = MQTTClient(MQTT_CLIENT_ID, UBIDOTS_BROKER, user=UBIDOTS_TOKEN, password="")
client.connect()
print(" Connected!")

prev_data = ""
motion_count = 0

while True:
    try:
        print("Mengukur sensor data...", end="")

        #baca dht
        dht_sensor.measure()
        temperature = dht_sensor.temperature()
        humidity = dht_sensor.humidity()

        #baca PIR
        motion_state = pir_sensor.value()

        if motion_state == 1:
            motion_count += 1
            print(f"Pergerakan Terdeteksi! Count: {motion_count}")
            led(1)
            time.sleep(2)
            led(0)
            
        #masukkan kedalam bentuk json
        data = {
            "temperature": temperature,
            "humidity": humidity,
            "motion": motion_count
        }
        
        message = ujson.dumps(data)

        #kirim data ke ubidots
        if message != prev_data:
            print(" Updated!")
            print("Publishing to Ubidots:", message)
            client.publish(UBIDOTS_TOPIC, message)
            prev_data = message
        else:
            print(" No change")

        #kirim data ke API
        try:
            headers = {"Content-Type": "application/json"}
            response = urequests.post(SERVER_URL, json=data, headers=headers)
            print("Sent to Flask API! Response:", response.text)
            response.close()
        except Exception as e:
            print("Error sending to Flask:", str(e))

    except Exception as e:
        print("Error reading sensors:", str(e))

    time.sleep(5)  # update setiap 5 detik

