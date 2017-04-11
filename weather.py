from urllib2 import urlopen

import pygame
from apixu.client import ApixuClient, ApixuException
import calendar
import time
import io

class Weather:
    def __init__(self, size):
        keys = open("Conf/keys.conf", 'r')
        api_key = keys.readline().splitlines()
        self.client = ApixuClient(api_key)
        self.curr_temp = 0
        self.last_update = 0
        self.curr_disc = ""
        self.curr_icon = []
        self.future_temp = [[], []]
        self.future_disc = [[], []]
        self.future_humidity = [[], []]
        self.future_icon = [[], []]
        self.size = size
        self.update()

    def update(self):
        if abs(self.last_update - calendar.timegm(time.gmtime())) > 3600:
            weather = self.client.getForecastWeather(q='bangalore', days=2)
            self.curr_disc = weather["current"]["condition"]["text"]
            self.curr_icon = pygame.transform.scale(pygame.image.load("./img/weather_icons/" + str(weather["current"]["condition"]["code"]) + "_" + str(int(not weather["current"]["is_day"]) + 1) +".png"), (self.size, self.size))
            self.curr_temp = weather["current"]['temp_c']
            self.last_update = weather["current"]["last_updated_epoch"]
            day = 0
            for j in weather["forecast"]['forecastday']:
                for i in j["hour"]:
                    self.future_temp[day].append(i['temp_c'])
                    self.future_humidity[day].append(float(i['humidity']))
                    self.future_disc[day].append(i["condition"]["text"])
                    self.future_icon[day].append(pygame.transform.scale(pygame.image.load("./img/weather_icons/"+ str(i["condition"]["code"]) + "_" + str(int(not i["is_day"]) + 1) + ".png"), (self.size, self.size)))
                day += 1

