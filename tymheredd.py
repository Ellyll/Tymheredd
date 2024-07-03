#!/usr/bin/python

#
# based on code from lrvick and LiquidCrystal
# lrvic - https://github.com/lrvick/raspi-hd44780/blob/master/hd44780.py
# LiquidCrystal - https://github.com/arduino/Arduino/blob/master/libraries/LiquidCrystal/LiquidCrystal.cpp
#

from adafruit_charlcd import Adafruit_CharLCD
from datetime import datetime, timezone, date
from time import sleep
import time
import flotilla
import requests
import os
import sys


def set_rainbow(rainbow, brightness):
  r = 192
  g = 64
  b = 0
  for x in range(rainbow.num_pixels):
    rainbow.set_pixel (x, 0, 0, 0)

  if brightness > 100:
    rainbow.set_pixel (0, r, g, b)
  if brightness > 250:
    rainbow.set_pixel (1, r, g, b)
  if brightness > 400:
    rainbow.set_pixel (2, r, g, b)
  if brightness > 550:
    rainbow.set_pixel (3, r, g, b)
  if brightness > 700:
    rainbow.set_pixel (4, r, g, b)

  rainbow.update()


# Main

if __name__ == '__main__':
  # PIN 27 is 21 on Rev1 RPis
  #lcd = Adafruit_CharLCD(pins_db=[23, 17, 21, 22])
  #with Adafruit_CharLCD(pins_db=[23, 17, 21, 22]) as lcd:
  with Adafruit_CharLCD(pins_db=[23, 17, 27, 22]) as lcd:

    def dangos(neges):
      print(neges)
      lcd.clear()
      lcd.message(neges.replace("°", "\xDF"))


    #lcd.clear()
    #lcd.message("Cychwyn...")
    dangos("Cychwyn...")

    dock = flotilla.Client()
    dangos("Cysylltwyd cleient...")

    while not dock.ready:
      pass

    dangos("Darganfod modiwl tywydd...")
    weather = dock.first(flotilla.Weather)
    if weather is None:
      dangos("Methu darganfod modiwl tywydd!")
      dock.stop()
      sys.exit(1)

    dangos("Darganfod modiwl golau...")
    light = dock.first(flotilla.Light)
    if light is None:
      dangos("Methu darganfod modiwl golau!")
      dock.stop()
      sys.exit(1)

    dangos("Darganfod modiwl rhif...")
    number = dock.first(flotilla.Number)
    if number is None:
      dangos("Methu darganfod modiwl rhif!")
      dock.stop()
      sys.exit(1)

    dangos("Darganfod modiwl enfys...")
    rainbow = dock.first(flotilla.Rainbow)
    if rainbow is None:
      dangos("Methu darganfod modiwl enfys!")
      dock.stop()
      sys.exit(1)


    dangos("Rhedeg...")

    def json_serial(obj):
        """JSON serializer for objects not serializable by default json code"""

        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        raise TypeError ("Type %s not serializable" % type(obj))


    def ysgrifennu_api(amser, tymheredd, gwasgedd, golau_light, golau_lux):
        data_dict = {
            "amser": amser.isoformat(),
            "tymheredd": tymheredd,
            "gwasgedd": gwasgedd,
            "golau_light": golau_light,
            "golau_lux": golau_lux
        }
        url = os.environ["URL_API"]
        allwedd = os.environ["ALLWEDD_API"]
        for i in range(1,3):
          try:
            r = requests.post(url, json=data_dict, headers={ "Authorization":"Bearer " + allwedd })
            if r.status_code != 200:
              print(r.status_code, r.reason)
            else:
              break
          except KeyboardInterrupt:
            raise
          except Exception as ex:
            print("POST wedi methu", ex)
            sleep(60)

    try:
      temp = weather.temperature
      pres = weather.pressure
      brightness = int(light.light)
      dangos('{} {}°C\n{:.3f}kPA'.format(time.strftime("%H:%M:%S"), temp, pres/100.0))
      print('Light: {0}\tLux: {1}'.format(light.light, light.lux))
      number.set_brightness(64)
      number.set_number(brightness)
      number.update()
      rwan = datetime.now(timezone.utc)
      ysgrifennu_api(rwan, temp, pres, light.light, light.lux)
      while True:
        if temp != weather.temperature or pres != weather.pressure or brightness != int(light.light):
          temp = weather.temperature
          pres = weather.pressure
          brightness = int(light.light)
          dangos('{} {}°C\n{:.3f}kPA'.format(time.strftime("%H:%M:%S"), temp, pres/100.0))
          print('Light: {0}\tLux: {1}'.format(light.light, light.lux))
          number.set_number(brightness)
          set_rainbow(rainbow, brightness)
          number.update()
          rwan = datetime.now(timezone.utc)

          ysgrifennu_api(rwan, temp, pres, light.light, light.lux)

        time.sleep(60.0)
    except KeyboardInterrupt:
      dangos("Cau Flotilla...")
      dock.stop()
