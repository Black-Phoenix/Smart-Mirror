import datetime
import os

import pygame
from pygame.locals import *
import pygame.gfxdraw
import news
from threading import Thread
import calender
import weather
import sprite
import time
from point import Point


def on_cleanup():
    pygame.quit()


def roundline(srf, color, start, end, radius=1):
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    distance = max(abs(dx), abs(dy))
    for i in range(distance):
        x = int(start[0] + float(i) / distance * dx)
        y = int(start[1] + float(i) / distance * dy)
        pygame.draw.circle(srf, color, (x, y), radius)


def blurSurf(surface, amt):
    """
    Blur the given surface by the given 'amount'.  Only values 1 and greater
    are valid.  Value 1 = no blur.
    """
    if amt < 1.0:
        raise ValueError("Arg 'amt' must be greater than 1.0, passed in value is %s" % amt)
    scale = 1.0 / float(amt)
    surf_size = surface.get_size()
    scale_size = (int(surf_size[0] * scale), int(surf_size[1] * scale))
    surf = pygame.transform.smoothscale(surface, scale_size)
    surf = pygame.transform.smoothscale(surf, surf_size)
    return surf


class GUI:
    def __init__(self):
        self._running = True
        self._display_surf = None
        self.red = (255, 0, 0)
        self.green = (0, 255, 0)
        self.blue = (0, 0, 255)
        self.darkBlue = (0, 0, 128)
        self.white = (255, 255, 255)
        self.gray = (125, 125, 125)
        self.black = (0, 0, 0)
        self.pink = (255, 200, 200)
        self.pos_touch = (0, 0)
        self.clicked = False
        self.swipe_up = False
        self.news_object = news.News()
        self.loading_gif = sprite.Sprite()
        self.bottom_timeline_pos = -1
        self.last_pos = [0, 0]
        self.reminder_radius = 6
        self.mouse_move = False
        self.new_reminder = False

        self.users = open("Conf/users.conf", 'r').read().splitlines()

    def on_init(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        infoObject = pygame.display.Info()
        self.size = self.weight, self.height = [640, 400]#[infoObject.current_w, infoObject.current_h]
        # objects
        self.weather_object = weather.Weather(int(0.8 / 12.0 * self.size[1]))
        self.calender_object = calender.Calender(1)  # todo not hardcoded

        self.ratio_outsize = 12.0 / 14.0
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.size[0] = int(self.size[0] * self.ratio_outsize)
        self._running = True
        self.font_cs_50 = pygame.font.SysFont("commicsans", int(0.1 / 12.0 * self.size[0]))
        self.font_cs_75 = pygame.font.SysFont("commicsans", int(0.125 / 12.0 * self.size[0]))
        self.font_cs_100 = pygame.font.SysFont("commicsans", int(0.15 / 12.0 * self.size[0]))
        self.font_cs_150 = pygame.font.SysFont("commicsans", int(0.175 / 12.0 * self.size[0]))
        self.font_cs_200 = pygame.font.SysFont("commicsans", int(0.2 / 12.0 * self.size[0]))
        self.font_cs_400 = pygame.font.SysFont("commicsans", int(0.4 / 12.0 * self.size[0]))
        self.font_cs_850 = pygame.font.SysFont("commicsans", int(0.85 / 12.0 * self.size[0]))
        thread = Thread(target=self.news_object.update_news, args=())
        thread.start()
        # drawing surface
        self.reminder_surface = pygame.Surface([11.0 / 12.0 * self.size[0], 11.0 / 12.0 * self.size[1]],
                                               pygame.SRCALPHA, 32)
        self.reminder_surface = self.reminder_surface.convert_alpha()

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.clicked = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.clicked = False
            self.mouse_move = False
        if event.type == pygame.MOUSEMOTION:
            self.mouse_move = True
            self.last_pos = self.pos_touch
        else:
            self.mouse_move = False
        if event.type is KEYDOWN and event.key == K_f:
            if self._display_surf.get_flags() & FULLSCREEN:
                pygame.display.set_mode([int(self.size[0] / self.ratio_outsize), self.size[1]])
            else:
                pygame.display.set_mode([int(self.size[0] / self.ratio_outsize), self.size[1]], FULLSCREEN)

    def draw_text(self, text, color, rect, font, aa=True, bkg=None):
        rect = Rect(rect)
        y = rect.top
        lineSpacing = -2

        # get the height of the font
        fontHeight = font.size("Tg")[1]

        while text:
            i = 1

            # determine if the row of text will be outside our area
            if y + fontHeight > rect.bottom:
                break

            # determine maximum width of line
            while font.size(text[:i])[0] < rect.width and i < len(text) and text[i] != '\n':
                i += 1

            # if we've wrapped the text, then adjust the wrap to the last word
            if i != len(text) and text[i] == '\n':
                text = text[:i] + text[(i + 1):]
            elif i < len(text):
                i = text.rfind(" ", 0, i) + 1

            # render the line and blit it to the surface
            if bkg:
                image = font.render(text[:i], aa, color, bkg)
                image.set_colorkey(bkg)
            else:
                image = font.render(text[:i], aa, color)
            self._display_surf.blit(image, (rect.left, y))
            y += fontHeight + lineSpacing

            # remove the text we just blitted
            text = text[i:]

        return text

    def news_events_draw(self):
        if self.news_object.size == 0:
            # noinspection PyTypeChecker
            self.draw_text("Updating News Feed", self.white, (
                12.3 / 12.0 * self.size[0], 3.24 / 12.0 * self.size[1], 2.0 / 12.0 * self.size[0],
                0.90 / 12.0 * self.size[1]), self.font_cs_200)
            return
        x = 3.0  # 3rd position
        pygame.gfxdraw.box(self._display_surf, pygame.Rect(12.1 / 12.0 * self.size[0],
                                                           x / 12.0 * self.size[1] + (x - 1) * 0.01 * self.size[1],
                                                           2.0 / 12.0 * self.size[0],
                                                           0.8 / 12.0 * self.size[1]),
                           (255, 255, 255, min(40, int(self.news_object.curr_alpha))))
        # noinspection PyTypeChecker
        self.draw_text(self.news_object.news_headings[self.news_object.curr_news_item],
                       (
                           min(255, 60 + int(self.news_object.curr_alpha)),
                           min(255, 60 + int(self.news_object.curr_alpha)),
                           min(255, 60 + int(self.news_object.curr_alpha))),
                       (12.15 / 12.0 * self.size[0], x / 12.0 * self.size[1] + (x - 0.85) * 0.01 * self.size[1],
                        1.80 / 12.0 * self.size[0], 0.8 / 12.0 * self.size[1]), self.font_cs_150)
        #click circle
        pygame.gfxdraw.aacircle(self._display_surf, int(11.75 / 12.0 * self.size[0]),
                                int((x + 0.5 + (x - 0.85) * 0.01) / 12.0 * self.size[1]),
                                int(0.2/ 12.0 * self.size[0]), self.white)

        if int(11.5 / 12.0 * self.size[0]) <= self.pos_touch[0] <= int(12.0 / 12.0 * self.size[0]) and \
                                                (x + (x - 0.85) * 0.01) / 12.0 * self.size[1] <= \
                self.pos_touch[1] <= int((0.7915 + x * 1.01) / 12.0 * self.size[1]) and self.clicked:
            self.news_object.expanded_news = True
        elif self.clicked:
            self.news_object.expanded_news = False
        if not self.news_object.expanded_news:
            self.news_object.curr_alpha -= 0.3
            if self.news_object.curr_alpha <= 0:
                self.news_object.curr_alpha = 225 * 2.0
                self.news_object.curr_news_item = (self.news_object.curr_news_item + 1) % self.news_object.size
        else:
            # noinspection PyTypeChecker
            self.draw_text(self.news_object.news_bodies[self.news_object.curr_news_item],
                           (255, 255, 255),
                           (3.05 / 12.0 * self.size[0], 2.05 / 12.0 * self.size[1], 7.0 / 12.0 * self.size[0],
                            6.0 / 12.0 * self.size[1]), self.font_cs_200)

    def reminder(self):
        if not self.swipe_up and self.clicked and 0.5 / 12.0 * self.size[0] <= self.pos_touch[0] <= int(
                                10.05 / 12.0 * self.size[0]) \
                and 1.05 / 12.0 * self.size[1] <= self.pos_touch[1] <= int(6.05 / 12.0 * self.size[0]) \
                and not self.news_object.expanded_news:
            pygame.draw.circle(self.reminder_surface, self.white, [int(self.pos_touch[0]), int(self.pos_touch[1])],
                               self.reminder_radius)
            if self.mouse_move:
                roundline(self.reminder_surface, self.white, [int(self.pos_touch[0]), int(self.pos_touch[1])],
                          [int(self.last_pos[0]), int(self.last_pos[1])], self.reminder_radius)
            self.new_reminder = True
        if not self.news_object.expanded_news:
            # draw the save button
            if self.clicked and int(11.0 / 12.0 * self.size[0]) <= self.pos_touch[0] <= int(11.5 / 12.0 * self.size[0]) \
                    and int(2.0 / 12.0 * self.size[0]) <= self.pos_touch[1] <= int(2.1 / 12.0 * self.size[0]):
                self.new_reminder = False
                self.reminder_surface = pygame.Surface([11.0 / 12.0 * self.size[0], 11.0 / 12.0 * self.size[1]],
                                                       pygame.SRCALPHA, 32)
            else:
                for i in enumerate(self.users):
                    if self.clicked and int(11.0 / 12.0 * self.size[0]) <= self.pos_touch[0] <= int(11.5 / 12.0 * self.size[0]) \
                        and int(2.0 / 12.0 * self.size[0]) <= self.pos_touch[1] <= int(2.1 / 12.0 * self.size[0]):

                        self.reminder_surface = self.reminder_surface.convert_alpha()
            if self.new_reminder:
                # noinspection PyTypeChecker
                self.draw_text("Clear", self.white, (
                    11.0 / 12.0 * self.size[0], 3.0 / 12.0 * self.size[1], 0.5 / 12.0 * self.size[0],
                    0.5 / 12.0 * self.size[1]), self.font_cs_150)
                for pos, i in enumerate(self.users):
                    # noinspection PyTypeChecker
                    self.draw_text(i, self.white, (
                        11.0 / 12.0 * self.size[0], float(pos + 4.0) / 12.0 * self.size[1], 1.0 / 12.0 * self.size[0],
                        1.0 / 12.0 * self.size[1]), self.font_cs_100)
            self._display_surf.blit(self.reminder_surface, (0, 0))

    def calender_events_draw(self):
        # todo fix positions
        base_pos = 4
        if len(self.calender_object.events) == 0:
            # noinspection PyTypeChecker
            self.draw_text("No Upcoming Calender Events", self.white, (
                12.3 / 12.0 * self.size[0], (base_pos + 0.24) / 12.0 * self.size[1], 1.9 / 12.0 * self.size[0],
                1.0 / 12.0 * self.size[1]), self.font_cs_200)
            return
        x = 4  # 2nd position

        # click circle
        pygame.gfxdraw.aacircle(self._display_surf, int(11.75 / 12.0 * self.size[0]),
                                int((x + 0.6) / 12.0 * self.size[1]),
                                int(0.2 / 12.0 * self.size[0]), self.white)
        #handel touch
        if int(11.5 / 12.0 * self.size[0]) <= self.pos_touch[0] <= int(12.0 / 12.0 * self.size[0]) and \
                                                (x + (x - 0.85) * 0.01) / 12.0 * self.size[1] <= \
                self.pos_touch[1] <= int((0.7915 + x * 1.01) / 12.0 * self.size[1]) and self.clicked:
            self.calender_object.selected_event = 1

        # event is in focus
        if self.calender_object.selected_event:
            pos = pygame.Rect(12.1 / 12.0 * self.size[0], (x) / 12.0 * self.size[1] + (x - 1) * 0.01 * self.size[
                1],
                              2.0 / 12.0 * self.size[0],
                              1.3 / 12.0 * self.size[1])

            if "location" in self.calender_object.events[self.calender_object.calender_selected_event]:
                location = self.calender_object.events[self.calender_object.calender_selected_event]["location"]
            else:
                location = "No Location Data Associated With Event"
            offset = 2.5
            # noinspection PyTypeChecker
            self.draw_text(location, self.white, (
                12.35 / 12.0 * self.size[0], x / 12.0 * self.size[1] + (x + 3.45 + offset) * 0.01 * self.size[1],
                2.0 / 12.0 * self.size[0], 3.0 / 12.0 * self.size[1]), self.font_cs_75)

            if "description" in self.calender_object.events[self.calender_object.calender_selected_event]:
                description = self.calender_object.events[self.calender_object.calender_selected_event]["description"]
            else:
                description = "No Description Data Associated With Event"
            # noinspection PyTypeChecker
            self.draw_text(description, self.white, (
                12.35 / 12.0 * self.size[0], x / 12.0 * self.size[1] + (x + .9) * 0.01 * self.size[1],
                2.0 / 12.0 * self.size[0], 3.0 / 12.0 * self.size[1]), self.font_cs_75)
        else:
            pos = pygame.Rect(12.1 / 12.0 * self.size[0], x / 12.0 * self.size[1] + (x - 1) * 0.01 * self.size[
                1],
                              2.0 / 12.0 * self.size[0],
                              0.6 / 12.0 * self.size[1])
            offset = 0
        pygame.gfxdraw.box(self._display_surf, pos,
                           (255, 255, 255, 40))
        # noinspection PyTypeChecker
        self.draw_text(self.calender_object.events[self.calender_object.calender_selected_event]["summary"], self.white,
                       (12.15 / 12.0 * self.size[0], x / 12.0 * self.size[1] + (x - 0.85) * 0.01 * self.size[1],
                        2.0 / 12.0 * self.size[0], 1.0 / 12.0 * self.size[1]), self.font_cs_200)
        # noinspection PyTypeChecker
        self.draw_text("- " + str(self.calender_object.events[self.calender_object.calender_selected_event]["end"] -
                                  self.calender_object.events[self.calender_object.calender_selected_event][
                                      "start"]) + " hr", self.white,
                       (12.35 / 12.0 * self.size[0], x / 12.0 * self.size[1] + (x + 1 + offset) * 0.01 * self.size[1],
                        2.0 / 12.0 * self.size[0], 3.0 / 12.0 * self.size[1]), self.font_cs_75)

        if self.calender_object.events[self.calender_object.calender_selected_event]["start"] <= 0:
            text = "Event Already Started"
        else:
            text = "Event Starts in " + str(
                self.calender_object.events[self.calender_object.calender_selected_event]["start"]) + " hrs"
        # noinspection PyTypeChecker
        self.draw_text(text, self.white, ( 12.35 / 12.0 * self.size[0],
                           x / 12.0 * self.size[1] + (x + 2.25 + offset) * 0.01 * self.size[1],
                           2.0 / 12.0 * self.size[0], 3.0 / 12.0 * self.size[1]), self.font_cs_75)

    def day_schedule(self):
        time_temp = 6
        for i in range(12):
            if int(time.strftime("%H")) + i < 21 and int(time.strftime("%H")) > 6:
                pygame.draw.lines(self._display_surf, self.white, False,
                                  [(float(i) / 12.0 * self.size[0], 11.9 / 12.0 * self.size[1]),
                                   (float(i + 1) / 12.0 * self.size[0], 11.9 / 12.0 * self.size[1])],
                                  1)  # redraw the points
                pygame.draw.lines(self._display_surf, self.white, False,
                                  [(float(i) / 12.0 * self.size[0], 11.8 / 12.0 * self.size[1]),
                                   (float(i) / 12.0 * self.size[0], self.size[1])],
                                  1)
                # noinspection PyTypeChecker
                self.draw_text(str(int(time.strftime("%H")) + i), self.white,
                               [float(i) / 12.0 * self.size[0], 11.65 / 12.0 * self.size[1],
                                float(i + 1) / 12.0 * self.size[0], self.size[1]], self.font_cs_75)
            elif int(time.strftime("%H")) + i == 21:
                pygame.draw.lines(self._display_surf, self.white, False,
                                  [(float(i) / 12.0 * self.size[0], 11.9 / 12.0 * self.size[1]),
                                   ((float(i + 0.35)) / 12.0 * self.size[0], 11.9 / 12.0 * self.size[1])],
                                  1)  # redraw the points
                pygame.draw.lines(self._display_surf, self.white, False,
                                  [((float(i + 1)) / 12.0 * self.size[0], 11.9 / 12.0 * self.size[1]),
                                   (float(i + 0.65) / 12.0 * self.size[0], 11.9 / 12.0 * self.size[1])],
                                  1)  # redraw the points

                pygame.draw.lines(self._display_surf, self.white, False,
                                  [(float(i + 0.35) / 12.0 * self.size[0], 11.9 / 12.0 * self.size[1]),
                                   (float(i + 0.45) / 12.0 * self.size[0], 11.8 / 12.0 * self.size[1])],
                                  1)  # redraw the points
                pygame.draw.lines(self._display_surf, self.white, False,
                                  [((float(i + 0.45)) / 12.0 * self.size[0], 11.8 / 12.0 * self.size[1]),
                                   (float(i + 0.55) / 12.0 * self.size[0], 12.0 / 12.0 * self.size[1])],
                                  1)  # redraw the points
                pygame.draw.lines(self._display_surf, self.white, False,
                                  [((float(i + 0.55)) / 12.0 * self.size[0], 12.0 / 12.0 * self.size[1]),
                                   (float(i + 0.65) / 12.0 * self.size[0], 11.9 / 12.0 * self.size[1])],
                                  1)  # redraw the points

                pygame.draw.lines(self._display_surf, self.white, False,
                                  [(float(i) / 12.0 * self.size[0], 11.8 / 12.0 * self.size[1]),
                                   (float(i) / 12.0 * self.size[0], self.size[1])],
                                  1)
                # noinspection PyTypeChecker
                self.draw_text(str(int(time.strftime("%H")) + i), self.white,
                               [float(i) / 12.0 * self.size[0], 11.65 / 12.0 * self.size[1],
                                float(i + 1) / 12.0 * self.size[0], self.size[1]], self.font_cs_75)
            else:
                pygame.draw.lines(self._display_surf, self.white, False,
                                  [(float(i) / 12.0 * self.size[0], 11.9 / 12.0 * self.size[1]),
                                   (float(i + 1) / 12.0 * self.size[0], 11.9 / 12.0 * self.size[1])],
                                  1)  # redraw the points
                pygame.draw.lines(self._display_surf, self.white, False,
                                  [(float(i) / 12.0 * self.size[0], 11.8 / 12.0 * self.size[1]),
                                   (float(i) / 12.0 * self.size[0], self.size[1])],
                                  1)

                # noinspection PyTypeChecker
                self.draw_text(str(time_temp), self.white,
                               [float(i) / 12.0 * self.size[0], 11.65 / 12.0 * self.size[1],
                                float(i + 1) / 12.0 * self.size[0], self.size[1]], self.font_cs_75)
                time_temp += 1

        #update swipeup
        if self.bottom_timeline_pos == int(float(self.pos_touch[0]) / float(self.size[0]) * 12.0):
            self.swipe_up = True
        else:
            self.swipe_up = False

        # time of day thing!!
        if not self.swipe_up and self.mouse_move:
            if self.pos_touch[1] >= int(10.0 / 12.0 * self.size[1]) and self.pos_touch[0] <= self.size[0]:
                # in the correct place
                pygame.draw.lines(self._display_surf, self.green, False,
                                  [(int(float(self.pos_touch[0]) / float(self.size[0]) * 12.0) / 12.0 * self.size[0],
                                    11.8 / 12.0 * self.size[1]),
                                   (int(float(self.pos_touch[0]) / float(self.size[0]) * 12.0) / 12.0 * self.size[0],
                                    self.size[1])],
                                  1)

                self.bottom_timeline_pos = int(float(self.pos_touch[0]) / float(self.size[0]) * 12.0)
                if self.bottom_timeline_pos > 12:
                    self.bottom_timeline_pos = 12
            else:
                self.bottom_timeline_pos = -1
                # current weather

    def print_time(self):
        str_time = datetime.datetime.now().strftime("%H:%M")
        # noinspection PyTypeChecker
        self.draw_text(str_time, self.white, (
            12.4 / 12.0 * self.size[0], 0.0 / 12.0 * self.size[1], 1.5 / 12.0 * self.size[0],
            2.0 / 12.0 * self.size[1]),
                       self.font_cs_850)

        str_date = datetime.datetime.now().strftime("%A, %b-%d")
        # noinspection PyTypeChecker
        self.draw_text(str_date, self.white, (
            12.83 / 12.0 * self.size[0], 1.0 / 12.0 * self.size[1], 1 / 12.0 * self.size[0], 1 / 12.0 * self.size[1]),
                       self.font_cs_150)

    def weather_draw(self):
        # read weather and blit the required one
        self.weather_object.update()

        # graphs
        sun_points = []
        humid_points = []
        timeline_day = 0
        points_ai = 6
        for i in range(13):
            if int(time.strftime("%H")) > 21:
                timeline_day = 1
                points_ai = 6 + i
            elif i + int(time.strftime("%H")) > 21:
                timeline_day = 1
                points_ai = i - 21 + (int(time.strftime("%H"))) + 5
            elif int(time.strftime("%H")) < 6:
                timeline_day = 1
                points_ai = 6 + i
            else:
                points_ai = int(time.strftime("%H")) + i
            sun_points.append((float(i) / 12.0 * self.size[0] - 1,
                               (12.0 - self.weather_object.future_temp[timeline_day][points_ai] / 45) / 12.0 *
                               self.size[1]))
            humid_points.append((float(i) / 12.0 * self.size[0] - 1,
                                 (12.0 - self.weather_object.future_humidity[timeline_day][points_ai] / 100) / 12.0 *
                                 self.size[1]))
        sun_points.append((self.size[0], self.size[1]))
        sun_points.append((0, self.size[1]))
        humid_points.append((self.size[0], self.size[1]))
        humid_points.append((0, self.size[1]))
        pygame.gfxdraw.aapolygon(self._display_surf, sun_points, (253, 180, 19, 200))
        pygame.gfxdraw.aapolygon(self._display_surf, humid_points, (66, 105, 180, 200))

        # icon and disc
        img_size = int(0.8 / 12.0 * self.size[1]) / 2
        if self.bottom_timeline_pos == -1:
            x = sun_points[0][0]
            y = min(sun_points[0][1], humid_points[0][1]) - img_size  # Same as the alternative
            self._display_surf.blit(self.weather_object.curr_icon,
                                    (x, y))
            # temp
            # noinspection PyTypeChecker
            self.draw_text(str(self.weather_object.curr_temp) + " C", self.white,
                           (x + img_size + 0.2 / 12 * self.size[0], y + img_size / 4, 1.0 / 12.0 * self.size[0],
                            1.0 / 12.0 * self.size[1]), self.font_cs_200)
            # disc
            # noinspection PyTypeChecker
            self.draw_text(self.weather_object.curr_disc, self.white,
                           (x + img_size + 0.2 / 12 * self.size[0], y + img_size + 0.1 / 12.0 * self.size[1],
                            1.0 / 12.0 * self.size[0], 1.0 / 12.0 * self.size[1]),
                           self.font_cs_100)
        else:
            timeline_day = 0
            points_ai = 0
            if self.bottom_timeline_pos + int(time.strftime("%H")) > 21 >= int(time.strftime("%H")):
                timeline_day = 1
                points_ai = self.bottom_timeline_pos - 21 + (int(time.strftime("%H"))) + 5
            elif int(time.strftime("%H")) < 6:
                points_ai = 6 + self.bottom_timeline_pos
            elif int(time.strftime("%H")) > 21:
                timeline_day = 1
                points_ai = 6 + self.bottom_timeline_pos
            else:
                points_ai = self.bottom_timeline_pos + int(time.strftime("%H"))

            # where to draw
            x = self.pos_touch[0] - img_size
            y = min(sun_points[self.bottom_timeline_pos][1],
                    humid_points[self.bottom_timeline_pos][1]) - img_size  # Same as the alternative
            self._display_surf.blit(self.weather_object.future_icon[timeline_day][points_ai],
                                    (x, y))
            # temp
            # noinspection PyTypeChecker
            self.draw_text(str(self.weather_object.future_temp[timeline_day][points_ai]) + " C", self.white,
                           (x + img_size + 0.2 / 12 * self.size[0], y + img_size / 4, 1.0 / 12.0 * self.size[0],
                            1.0 / 12.0 * self.size[1]), self.font_cs_200)
            # disc
            # noinspection PyTypeChecker
            self.draw_text(self.weather_object.future_disc[timeline_day][points_ai], self.white,
                           (x + img_size + 0.2 / 12 * self.size[0], y + img_size + 0.1 / 12.0 * self.size[1],
                            1.0 / 12.0 * self.size[0], 1.0 / 12.0 * self.size[1]),
                           self.font_cs_100)

    def calender_timeline_draw(self):
        if not self.calender_object.updating:
            thread = Thread(target=self.calender_object.update_tasks, args=())
            thread.start()
        if len(self.calender_object.events) == 0:
            self.calender_events_draw()
            return
        for num, i in enumerate(self.calender_object.events):
            if i["start"] > 24:
                continue
            if 21 > (int(time.strftime("%H")) + i["start"]) % 24 > 6:
                if 21 > (int(time.strftime("%H")) + i["end"]) % 24 > 6:
                    if 21 > int(time.strftime("%H")) > 6:  # OK, OK, OK
                        i["pos_start"] = float(i["start"]) / 12.0 * self.size[0]
                        i["pos_end"] = float(i["end"] - i["start"]) / 12.0 * self.size[0]
                    else:  # OK it seems
                        if 21 < int(time.strftime("%H")):
                            i["pos_start"] = float((int(time.strftime("%H")) + i["start"]) % 24 - 6) / 12.0 * self.size[
                                0]
                            i["pos_end"] = float(i["end"] - i["start"]) / 12.0 * self.size[0]
                        else:  # ok it seems
                            i["pos_start"] = float(i["start"] - (6 - int(time.strftime("%H")))) / 12.0 * self.size[0]
                            i["pos_end"] = float(i["end"] - i["start"]) / 12.0 * self.size[0]
                else:
                    i["pos_start"] = float(i["start"]) / 12.0 * self.size[0]
                    i["pos_end"] = (21.0 - float(time.strftime("%H")) + 0.3) / 12.0 * self.size[0]
            else:
                if 21 > (int(time.strftime("%H")) + i["end"]) % 24 > 6:
                    if 6 > int(time.strftime("%H")) or int(time.strftime("%H")) > 21:
                        i["pos_start"] = 0.0 / 12.0 * self.size[0]
                        i["pos_end"] = (float(int(time.strftime("%H")) + i["end"]) % 24 - 6) / 12.0 * self.size[0]
                    else:
                        i["pos_start"] = (21.0 - float(time.strftime("%H")) + 0.6) / 12.0 * self.size[0]
                        i["pos_end"] = (float(i["end"]) - 8.0 + 0.1) / 12.0 * self.size[0]
                else:
                    if 6 > int(time.strftime("%H")) or int(time.strftime("%H")) > 21:  # maybe ok
                        i["pos_start"] = 0.0 / 12.0 * self.size[0]
                        i["pos_end"] = 0.50 / 12.0 * self.size[0]
                    else:  # to test still
                        i["pos_start"] = (21.0 - float(time.strftime("%H"))) / 12.0 * self.size[0]
                        i["pos_end"] = 1.0 / 12.0 * self.size[0]
            if i["pos_start"] <= self.pos_touch[0] <= i["pos_start"] + i["pos_end"] and self.pos_touch[1] >= int(
                                    10.0 / 12.0 * self.size[1]) and self.pos_touch[0] <= self.size[0]:
                self.calender_object.calender_selected_event = num
            else:
                self.calender_object.calender_selected_event = 0

            if not self.clicked:
                self.swipe_up = False

            if (i["pos_start"] <= self.pos_touch[0] <= i["pos_start"] + i["pos_end"] and self.pos_touch[0] <= self.size[
                0] and self.pos_touch[1] <= int(10.9 / 12.0 * self.size[
                1]) and self.swipe_up) or self.calender_object.selected_event == True:
                self.calender_object.selected_event = True
            if self.clicked and self.pos_touch[1] <= int(10.0 / 12.0 * self.size[1]) and not self.swipe_up:
                self.calender_object.selected_event = False
            pygame.gfxdraw.box(self._display_surf,
                               (i["pos_start"], 11.85 / 12.0 * self.size[1], i["pos_end"], 0.1 / 12.0 * self.size[1]),
                               (175, 175, 175, 175))

            # add the box to the right of the screen
        self.calender_events_draw()

    def draw_boundaries(self, width=1, dash_length=10):
        origin = Point([self.size[0], self.size[1]])
        target = Point([self.size[0], 0])
        displacement = target - origin
        length = len(displacement)
        slope = displacement / length

        for index in range(0, length / dash_length, 2):
            start = origin + (slope * index * dash_length)
            end = origin + (slope * (index + 1) * dash_length)
            pygame.draw.line(self._display_surf, self.white, start.get(), end.get(), width)

    def on_loop(self):
        # bottom time line
        self.weather_draw()
        self.day_schedule()
        self.print_time()
        # populating news
        self.calender_timeline_draw()
        self.draw_boundaries()
        self.news_events_draw()
        self.reminder()
        pygame.display.update()

    def on_execute(self):
        if self.on_init() == False:
            self._running = False

        while self._running:
            self._display_surf.fill(self.black)
            for event in pygame.event.get():
                self.on_event(event)
            self.pos_touch = [pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]]
            # correction for touch

            #self.pos_touch[0] *= 15.6/18.5
            #self.pos_touch[1] = self.size[1] - 15.6/18.5 * (self.size[1] - self.pos_touch[1])
            self.on_loop()
            self.clock.tick(60)

        on_cleanup()


if __name__ == "__main__":
    theApp = GUI()
    theApp.on_execute()
    os._exit(1)
