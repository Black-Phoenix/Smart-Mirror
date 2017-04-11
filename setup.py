import pygame
from pygame.locals import *
from apixu.client import ApixuClient, ApixuException


def main():
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))

    api_key = 'e54f45f8d4ce450fa49182858171803'
    client = ApixuClient(api_key)
    weather = client.getForecastWeather(q='bangalore', days=2)
    day = 0
    control_points = []
    for i in weather["forecast"]['forecastday'][0]["hour"]:
            if i["is_day"] == 0:
                print(i["time"])
            else:
                control_points.append([day, 768 - i['temp_c']])
                day += 70
    ### Control points that are later used to calculate the curve

    ### The currently selected point
    selected = None

    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type in (QUIT, KEYDOWN):
                running = False

        ### Draw stuff
        screen.fill((0, 0, 0))

        ### Draw control points
        for p in range(len(control_points) - 1):
            pygame.draw.line(screen, (255, 255, 0), (int(control_points[p][0]), int(control_points[p][1])), (int(control_points[p+1][0]), int(control_points[p +1][1])), 4)

        ### Flip screen
        pygame.display.flip()
        clock.tick(100)
        #print clock.get_fps()

if __name__ == '__main__':
    main()
