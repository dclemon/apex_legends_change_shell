# -*- coding: UTF-8 -*-
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit
import keyboard
from jd_config import read_ini
from pynput.mouse import Button, Controller as c_mouse
import cv2
import numpy as np
import time
from PIL import ImageGrab
from PyQt5.QtCore import Qt
import ctypes
import os
import winsound



def compare_images(image1, image2):
    return cv2.norm(image1, image2, cv2.NORM_L2)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.text_edit = QTextEdit(self)
        self.setCentralWidget(self.text_edit)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setWindowOpacity(0.8)
        self.mouse = c_mouse()
        self.shell_locate = read_ini('config', 'shell_location', 'config.ini')
        self.sim_min = float(read_ini('config', 'sim_min', 'config.ini'))
        self.press_delay = float(read_ini('config', 'press_delay', 'config.ini'))
        self.mouse_location = read_ini('config', 'mouse_location', 'config.ini')
        print('1. 想要在游戏前端显示此窗口，请游戏里开无边框模式')
        print('2. 按·可获取当前鼠标坐标并在鼠标附近区域截图')
        self.capture_delay = float(read_ini('config', 'capture_delay', 'config.ini'))
        self.shell_locate = eval(self.shell_locate)
        self.mouse_location = eval(self.mouse_location)
        self.local_image = cv2.cvtColor(cv2.imread("local_image.png"), cv2.COLOR_BGR2GRAY)
        self.x = float(read_ini('config', 'x', 'config.ini'))
        self.y = float(read_ini('config', 'y', 'config.ini'))
        self.width = float(read_ini('config', 'width', 'config.ini'))
        self.height = float(read_ini('config', 'height', 'config.ini'))
        self.save_pic = read_ini('config', 'save_pic', 'config.ini')
        _, self.local_image = cv2.threshold(self.local_image, 127, 255, cv2.THRESH_BINARY_INV)
        keyboard.on_press_key("`", self.on_press_b)
        keyboard.on_press_key("e", self.on_press_e)
        keyboard.on_press_key("+", self.on_press_c)

    def capture_screen(self, x, y, width, height):
        screen = ImageGrab.grab(bbox=[x, y, x + width, y + height])
        if self.save_pic == 'True':
            screen.save("captured_image.png")

        screen = np.array(screen)
        return cv2.cvtColor(screen, cv2.COLOR_BGR2RGB), screen

    def on_press_e(self, e):
        try:
            start_time = time.time()
            local_image = self.local_image
            while True:
                # Check if 'e' key is still pressed
                if not keyboard.is_pressed("e"):
                    break

                # Check if enough time has passed since last capture
                if time.time() - start_time >= self.capture_delay:
                    # Capture the image on the screen (x, y, width, height)
                    _, captured_image = self.capture_screen(self.x, self.y, self.width, self.height)
                    # Screenshot of binary processing
                    captured_image = cv2.cvtColor(captured_image, cv2.COLOR_BGR2GRAY)
                    _, captured_image = cv2.threshold(captured_image, 127, 255, cv2.THRESH_BINARY_INV)
                    # Calculate similarity
                    similarity = compare_images(captured_image, local_image)
                    similarity_percentage = (100 - similarity / 100) / 100
                    print("Similarity:" + str(
                        similarity_percentage))
                    if similarity_percentage >= self.sim_min:
                        print('背包已开启，开始换甲')
                        for x in self.shell_locate:
                            self.mouse.position = x
                            time.sleep(self.press_delay)
                            self.mouse.click(Button.left)
                            # Logitech.mouse.click(1)
                        # Restore mouse position
                        self.mouse.position = self.mouse_location[0]
                        winsound.Beep(800, 200)
                        time.sleep(1)
                    else:
                        print('背包未开启，请重试')
                        # Update start time for next capture
                        start_time = time.time()
                    continue
        except Exception as e:
            # Handle the error and raise a new exception to indicate that an error occurred
            print("An error occurred: ", e)
            raise Exception("An error occurred during the on_press_e method.")

    def on_press_b(self, e):
        print('当前坐标是：' + str(self.mouse.position[0]) + ',' + str(
            self.mouse.position[1]))

    def on_press_c(self, e):
        x = float(read_ini('config', 'x', 'config.ini'))
        y = float(read_ini('config', 'y', 'config.ini'))
        width = float(read_ini('config', 'width', 'config.ini'))
        height = float(read_ini('config', 'height', 'config.ini'))
        print('从该位置截图：' + str(x) + ',' + str(y))
        print('截图长度：' + str(width) + ',高度' + str(height))
        self.capture_screen(self.x, self.y, self.width, self.height)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.text_edit.document().setMaximumBlockCount(5);
    sys.exit(app.exec_())
