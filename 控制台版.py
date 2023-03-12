# -*- coding: UTF-8 -*-
import hashlib
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
import keyboard
from jd_config import read_ini
from pynput.mouse import Button, Controller as c_mouse
import cv2
import numpy as np
import time
from PIL import ImageGrab
import winsound
import os
import ctypes


def compare_images(image1, image2):
    return cv2.norm(image1, image2, cv2.NORM_L2)


try:
    root = os.path.abspath(os.path.dirname(__file__))
    driver = ctypes.CDLL(f'{root}/logitech.driver.dll')
    ok = driver.device_open() == 1
    if not ok:
        print('Error, GHUB or LGS driver not found')
except FileNotFoundError:
    print(f'Error, DLL file not found')


class Logitech:
    class mouse:

        """
        code: 1:左键, 2:中键, 3:右键
        """

        @staticmethod
        def press(code):
            if not ok:
                return
            driver.mouse_down(code)

        @staticmethod
        def release(code):
            if not ok:
                return
            driver.mouse_up(code)

        @staticmethod
        def click(code):
            if not ok:
                return
            driver.mouse_down(code)
            driver.mouse_up(code)

        @staticmethod
        def scroll(a):
            """
            a:没搞明白
            """
            if not ok:
                return
            driver.scroll(a)

        @staticmethod
        def move(x, y):
            """
            相对移动, 绝对移动需配合 pywin32 的 win32gui 中的 GetCursorPos 计算位置
            pip install pywin32 -i https://pypi.tuna.tsinghua.edu.cn/simple
            x: 水平移动的方向和距离, 正数向右, 负数向左
            y: 垂直移动的方向和距离
            """
            if not ok:
                return
            if x == 0 and y == 0:
                return
            driver.moveR(x, y, True)

    class keyboard:

        """
        键盘按键函数中，传入的参数采用的是键盘按键对应的键码
        code: 'a'-'z':A键-Z键, '0'-'9':0-9, 其他的没猜出来
        """

        @staticmethod
        def press(code):

            if not ok:
                return
            driver.key_down(code)

        @staticmethod
        def release(code):
            if not ok:
                return
            driver.key_up(code)

        @staticmethod
        def click(code):
            if not ok:
                return
            driver.key_down(code)
            driver.key_up(code)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.shell_locate = read_ini('config', 'shell_location', 'config.ini')
        self.sim_min = float(read_ini('config', 'sim_min', 'config.ini'))
        self.press_delay = float(read_ini('config', 'press_delay', 'config.ini'))
        self.mouse_location = read_ini('config', 'mouse_location', 'config.ini')
        self.capture_delay = float(read_ini('config', 'capture_delay', 'config.ini'))
        self.local_image = cv2.cvtColor(cv2.imread("local_image.png"), cv2.COLOR_BGR2GRAY)
        self.x = float(read_ini('config', 'x', 'config.ini'))
        self.y = float(read_ini('config', 'y', 'config.ini'))
        self.width = float(read_ini('config', 'width', 'config.ini'))
        self.height = float(read_ini('config', 'height', 'config.ini'))
        self.save_pic = read_ini('config', 'save_pic', 'config.ini')
        _, self.local_image = cv2.threshold(self.local_image, 127, 255, cv2.THRESH_BINARY_INV)
        self.shell_locate = eval(self.shell_locate)
        self.mouse_location = eval(self.mouse_location)
        self.mouse = c_mouse()
        keyboard.on_press_key("`", self.on_press_b)
        keyboard.on_press_key("e", self.on_press_e)
        keyboard.on_press_key("+", self.on_press_c)

        print('1. 按~获取当前鼠标坐标')
        print('2. 按+在指定区域截图')
        print('3. 长按E自动换甲')

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
                time.sleep(0.01)
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
                            time.sleep(self.press_delay)
                            Logitech.mouse.click(1)
                        # Restore mouse position
                        self.mouse.position = self.mouse_location[0]
                        winsound.Beep(1000, 200)
                    else:
                        print('背包未开启，请重试')
                        winsound.Beep(200, 200)
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
        print('从该位置截图：' + str(self.x) + ',' + str(self.y))
        print('截图长度：' + str(self.width) + ',高度' + str(self.height))
        self.capture_screen(self.x, self.y, self.width, self.height)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    sys.exit(app.exec_())



