import time
import keyboard
import pyautogui
import cv2
import numpy as np
import mouse
from mss import mss

'''
TUNABLE PARAMETERS
'''
# button used to select region and stop program
start_button = "p"

# For Google Game
color = (153, 153, 153)

# https://www.crazygames.com/game/atari-breakout
# color = (255, 255, 255)

# https://scratch.mit.edu/projects/33459194/
# color = (255, 90, 74)

# how close in size a contour has to be to the largest one
# to still be considered a ball (used if multiple balls in game)
contour_tolerance = 0.9

# change to True if your game can have multiple balls
multiple_balls = False
'''
END TUNABLE PARAMETERS
'''

# function uses screenshot to move the mouse correctly
def follow_ball(scrot):
    # identify places where we see the ball based on its color
    mask = cv2.inRange(scrot, color, color)
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    
    # handle multiple balls (follow lowest one)
    if len(contours) > 0:
        if multiple_balls:
            biggest_size = cv2.contourArea(contours[0])
            eligible_contours = []
            
            # find all contours that are close to the size of the biggest one
            # we assume all these are also balls
            for contour in contours:
                if cv2.contourArea(contour) >= contour_tolerance * biggest_size:
                    eligible_contours.append(contour)
            
            # find ball that is closest to hitting ground and track it
            lowest_contour = None
            lowest_y = 0
            for contour in eligible_contours:
                (x_min, y_min, box_width, box_height) = cv2.boundingRect(contour)
                if y_min > lowest_y:
                    lowest_contour = contour
                    lowest_y = y_min
                
            if lowest_contour is not None:
                (x_min, y_min, box_width, box_height) = cv2.boundingRect(lowest_contour)
                mouse.move(coords[0] + x_min + box_width // 2, coords[1] + HEIGHT * 4 // 5, absolute = True)
        else:
            # if a single ball, just follow biggest contour
            (x_min, y_min, box_width, box_height) = cv2.boundingRect(contours[0])
            mouse.move(coords[0] + x_min + box_width // 2, coords[1] + HEIGHT * 4 // 5, absolute = True)
  
# record position of one corner of the game when start_button is clicked
while True:
    if keyboard.is_pressed(start_button):
        mousePos1 = pyautogui.position()
        break
    
time.sleep(0.2)

# record position of second corner of the game when start_button is clicked
while True:
    if keyboard.is_pressed(start_button):
        mousePos2 = pyautogui.position()
        break
    
time.sleep(0.2)

# use recorded positions to calculate window width and height
WIDTH = mousePos2.x - mousePos1.x
HEIGHT = mousePos2.y - mousePos1.y
coords = (mousePos1.x, mousePos1.y, mousePos2.x, mousePos2.y)

times = []
while True:
    # pressing start_button exits the game
    if keyboard.is_pressed(start_button):
        break
    
    # used for FPS calculation
    tic = time.perf_counter()
    
    # slightly slower way of getting screenshot
    # scrot = np.array(pyautogui.screenshot(region = (mousePos1.x, mousePos1.y, WIDTH, HEIGHT)))
    
    # faster way of getting screenshot
    with mss() as sct:
        monitor = {"top": mousePos1.y, "left": mousePos1.x, "width": WIDTH, "height": HEIGHT}
        scrot = sct.grab(monitor)
        scrot = np.array(scrot, dtype=np.uint8)
        scrot = np.flip(scrot[:, :, :3], 2)
        
    # call follow ball function that moves the mouse
    follow_ball(scrot)
    times.append(time.perf_counter() - tic)
  
# calculate and print average FPS
mean_time = sum(times) / len(times)
print(f"FPS: {1 / mean_time}")
