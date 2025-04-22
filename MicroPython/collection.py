from machine import Pin, I2C, ADC
from time import sleep
import dht
import json
import network
from umqtt.robust import MQTTClient
from config import WIFI_SSID, WIFI_PASS, MQTT_BROKER, MQTT_USER, MQTT_PASS

TOPIC = 'b6610546312/plant_sensors'

led_wifi = Pin(2, Pin.OUT)
led_wifi.value(1)  # turn the red led off
led_iot = Pin(12, Pin.OUT)
led_iot.value(1)  # turn the green led off

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(WIFI_SSID, WIFI_PASS)
while not wlan.isconnected():
    sleep(0.5)
led_wifi.value(0)  # turn the red led on

mqtt = MQTTClient(client_id="",
                  server=MQTT_BROKER,
                  user=MQTT_USER,
                  password=MQTT_PASS)
mqtt.connect()
led_iot.value(0)  # turn the green led on


def res_to_lux(resistance):
    return 562.3413 / (resistance * 0.001) ** 1.25


t_sensor = I2C(1, sda=Pin(4), scl=Pin(5))
t_sensor.writeto(77, bytearray([0x04, 0b01100000]))
t_sensor.writeto(77, bytearray([0]))
h_sensor = dht.DHT11(Pin(32))
l_sensor = ADC(Pin(36))
l_sensor.width(ADC.WIDTH_12BIT)
s_sensor = ADC(Pin(34))
s_sensor.width(ADC.WIDTH_12BIT)  # set 12 bit return values (returned range 0-4095)

while True:
    try:
        sleep(1)

        h_sensor.measure()

        # temperature
        temp = t_sensor.readfrom(77, 2)
        temp_c = (256 * temp[0] + temp[1]) / 128
        print('Temperature: %3.1f C' % temp_c)

        # humidity
        hum = h_sensor.humidity()
        print('Humidity: %3.1f %%' % hum)

        # light
        R_1 = 33000
        V_S = 3.3
        V_a = (l_sensor.read_uv() / 1000000)
        R_LDR = (V_a * R_1) / (V_S - V_a)
        light = res_to_lux(R_LDR)
        print('Light: %3.1f lux' % light)
        print('LDR: %3.1f' % l_sensor.read())

        # soil
        soil = s_sensor.read()
        if soil >= 4059:
            soil_wet = False  # Not wet
        else:
            soil_wet = True  # Wet

        print('Soil: %3.1f' % soil_wet)

        print()

        data = {
            'temp': temp_c,
            'humidity': hum,
            'light': light,
            'ldr': l_sensor.read(),
            'soil': soil_wet,
        }
        mqtt.publish(TOPIC, json.dumps(data))

    except OSError as e:
        print('Failed to read sensor.')