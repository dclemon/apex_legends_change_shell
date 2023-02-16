import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit
import keyboard
from jd_config import read_ini
from pynput.mouse import Button, Controller as c_mouse
import cv2
import numpy as np
import time
import winsound
from PIL import ImageGrab
from PyQt5.QtCore import Qt


def capture_screen(x, y, width, height):
    screen = ImageGrab.grab(bbox=[x, y, x + width, y + height])
    screen.save("captured_image.png")
    screen = np.array(screen)
    return cv2.cvtColor(screen, cv2.COLOR_BGR2RGB)


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
        self.mouse_location = read_ini('config', 'mouse_location', 'config.ini')
        self.text_edit.append('<font color=\"#32CD99\">1. 想要在游戏前端显示此窗口，请游戏里开无边框模式</font>')
        self.text_edit.append('<font color=\"#32CD99\">2. 按·可获取当前鼠标坐标并在鼠标附近区域截图</font>')
        # self.text_edit.append('<font color=\"#32CD99\">读取到护甲坐标：</font>' + self.shell_locate)
        self.shell_locate = eval(self.shell_locate)
        self.mouse_location = eval(self.mouse_location)

        keyboard.on_press_key("`", self.on_press_b)
        keyboard.on_press_key("e", self.on_press_e)
        keyboard.on_press_key("+", self.on_press_c)

    def on_press_e(self, e):
        start_time = time.time()
        while keyboard.is_pressed("e"):
            if time.time() - start_time >= 0.47:
                x = float(read_ini('config', 'x', 'config.ini'))
                y = float(read_ini('config', 'y', 'config.ini'))
                width = float(read_ini('config', 'width', 'config.ini'))
                height = float(read_ini('config', 'height', 'config.ini'))
                # 捕获屏幕上 (x, y, width, height) 的图像
                capture_screen(x, y, width, height)
                captured_image = cv2.imread("captured_image.png")
                # 二值化处理截图
                captured_image = cv2.cvtColor(captured_image, cv2.COLOR_BGR2GRAY)
                _, captured_image = cv2.threshold(captured_image, 127, 255, cv2.THRESH_BINARY_INV)
                cv2.imwrite('./pic/captured_image_2.png', captured_image)

                # 二值化处理标准图片
                local_image = cv2.imread("local_image.png")
                local_image = cv2.cvtColor(local_image, cv2.COLOR_BGR2GRAY)
                _, local_image = cv2.threshold(local_image, 127, 255, cv2.THRESH_BINARY_INV)
                cv2.imwrite('./pic/local_image_2.png', local_image)
                # 计算相似度
                similarity = compare_images(captured_image, local_image)
                similarity_percentage = (100 - similarity / 100) / 100
                self.text_edit.append("<font color=\"#32CD99\">Similarity: </font><font color=\"#32CD99\">" + str(
                    similarity_percentage) + '</font>')
                if similarity_percentage >= self.sim_min:
                    self.text_edit.append('<font color=\"#32CD99\">背包已打开，自动换甲</font>')
                    for x in self.shell_locate:
                        time.sleep(0.002)
                        self.mouse.position = x
                        time.sleep(0.002)
                        self.mouse.click(Button.left)
                        # 点击左键
                        time.sleep(0.002)
                        self.mouse.click(Button.left)
                        # 连续两次防止换到空甲
                    self.text_edit.append('<font color=\"#32CD99\">换甲完成</font>')
                    # 恢复鼠标位置
                    self.mouse.position = self.mouse_location[0]
                    winsound.Beep(800, 200)
                else:
                    self.text_edit.append('<font color=\"#FF0000\">背包未开启，请对准死亡之箱重试</font>')
                break
        return False

    def on_press_b(self, e):
        self.text_edit.append('<font color=\"#6B238E\">当前坐标是：</font>' + str(self.mouse.position[0]) + ',' + str(
            self.mouse.position[1]))

    def on_press_c(self, e):

        x = float(read_ini('config', 'x', 'config.ini'))
        y = float(read_ini('config', 'y', 'config.ini'))
        width = float(read_ini('config', 'width', 'config.ini'))
        height = float(read_ini('config', 'height', 'config.ini'))
        self.text_edit.append('<font color=\"#6B238E\">从该位置截图：</font>' + str(x) + ',' + str(
            y))
        self.text_edit.append('<font color=\"#6B238E\">截图长度：</font>' + str(width) + ',高度' + str(
            height))
        capture_screen(x, y, width, height)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
