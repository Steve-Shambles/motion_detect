"""
Motion detect and save v2
By Steve Shambles
Original code Dec 2019, updated may 2023

Tested on Win7

pip install opencv-python
pip install numpy

Based on intel detection algo, found here:
https://software.intel.com/en-us/node/754940
"""
import os
import time
from tkinter import messagebox, Tk
import webbrowser

import cv2
import numpy as np

root = Tk()
motion_detect = 0
md_switch = 'OFF'

# check for folder.
my_dir = ('detected-images')
check_folder = os.path.isdir(my_dir)
# If folder doesn't exist, then create it.
if not check_folder:
    os.makedirs(my_dir)
# Make that folder current dir.
os.chdir(my_dir)

# Change sdthresh (sensitivty) to suit camera and conditions,
# 10-15 is usually within the threshold range.
sdThresh = 15

# Used to count individualy named frames as jpgs.
img_index = 0

# Use this cv2 font.
font = cv2.FONT_HERSHEY_SIMPLEX


def open_folder():
    """open systems file browser to view images folder."""
    cwd = os.getcwd()
    webbrowser.open(cwd)


def distMap(frame1, frame2):
    """outputs pythagorean distance between two frames."""
    frame1_32 = np.float32(frame1)
    frame2_32 = np.float32(frame2)
    diff32 = frame1_32 - frame2_32
    norm32 = np.sqrt(diff32[:, :, 0]**2 + diff32[:, :, 1]**2 + diff32[:, :, 2]
                     ** 2)/np.sqrt(255**2 + 255**2 + 255**2)
    dist = np.uint8(norm32*255)
    return dist


def print_date_time():
    """Updates current date and time and keys info on to video."""
    current_time = time.asctime()
    cv2.putText(frame2, str(current_time), (280, 24),
                font, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
    cv2.putText(frame2, '   Press h for options : Sensitivity = '
                + str(sdThresh) + ' : Save detected images is: '
                + str(md_switch),
                (10, 470), font, 0.5, (255, 255, 255), 1)


# Capture video stream.
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # added cv2.CAP_DSHOW fix cv.
ret, frame1 = cap.read()  # added ret, to fix update in cv2 module.
ret, frame2 = cap.read()  # added ret, to fix update in cv2 module.

# Main loop.
while True:
    ret, frame3 = cap.read()  # added ret, to fix update in cv2 module.

    # Report error if camera not found.
    try:
        rows, cols, _ = np.shape(frame3)
    except ValueError as ve:
        print("Webcam not found or no data from camera error")
        exit(0)

    dist = distMap(frame1, frame3)
    frame1 = frame2
    frame2 = frame3
    keyPress = cv2.waitKey(20)

    # Apply Gaussian smoothing.
    mod = cv2.GaussianBlur(dist, (9, 9), 0)
    # Apply thresholding.
    thresh = cv2.threshold(mod, 100, 255, 0)
    # Calculate st dev test.
    mean, stDev = cv2.meanStdDev(mod)
    # If motion is dectected.  some changes made in next few lines by claude+
    # damned if i can recall but it fixed cv2 update.
    if stDev > sdThresh:
        # Motion is detected.
        cv2.putText(frame2, 'MD '+str(img_index),
                    (0, 20), font, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
        print_date_time()

        # Save a timestamped jpg if motion detected.
        if motion_detect == 1:
            frame_name = (str(img_index)+str('.jpg'))
            cv2.imwrite(frame_name, frame2)
            img_index += 1

    print_date_time()
    cv2.imshow('Live video', frame2)

    # Enter key pauses video stream.
    if keyPress & 0xFF == 13:
        cv2.putText(frame2, 'PAUSED', (210, 260), font, 2,
                    (0, 255, 0), 8, cv2.LINE_AA)
        cv2.imshow('Live video', frame2)
        cv2.waitKey(0)

    # q key to quit program.
    if keyPress & 0xFF == ord('q'):
        root.withdraw()
        ask_yn = messagebox.askyesno('Quit Motion Detector?',
                                     'Are you sure?')
        if ask_yn:
            break
        root.update_idletasks()

    # Motion detect off. s key.
    if keyPress & 0xFF == ord('s'):
        motion_detect = 0
        md_switch = 'OFF'

    # Motion detect on. m key.
    if keyPress & 0xFF == ord('m'):
        motion_detect = 1
        md_switch = 'ON'

    # Camera sensitivity + key.
    if keyPress & 0xFF == ord('+'):
        sdThresh += 1

    # Camera sensitivity - key.
    if keyPress & 0xFF == ord('-'):
        sdThresh -= 1

    # View images folder v key.
    if keyPress & 0xFF == ord('v'):
        open_folder()

    # Snapshot x key.
    if keyPress & 0xFF == ord('x'):
        frame_name = (str(img_index)+str('-snapshot.jpg'))
        cv2.imwrite(frame_name, frame2)
        img_index += 1

    # Help keys msg box.
    if keyPress & 0xFF == ord('h'):
        root.withdraw()
        messagebox.showinfo('Motion Detector help - Keys',
                            'H ~ This menu\n\n'
                            'M ~ Start motion dectect\n\n'
                            'S ~ Stop motion detect\n\n'
                            'X ~ Take a single snaphot\n\n'
                            'V ~ View images folder\n\n'
                            '+ ~ Camera sensitivity increase\n\n'
                            '- ~ Camera sensitivity deccrease\n\n'
                            'Q ~ Quit\n\n'
                            'ENTER - Pause video stream\n\n'
                            'Motion Detector V2 is Freeware.\n'
                            'By Steve Shambles, May 2023.\n\n'
                            'Tip: Make sure video window is selected\n'
                            'for key presses to work.\n'
                            )

# Close down.
cap.release()
cv2.destroyAllWindows()

root.mainloop()
