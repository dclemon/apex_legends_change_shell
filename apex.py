import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit
import keyboard
import jd_config
from pynput.mouse import Button,Controller as c_mouse
import cv2
import numpy as np
import time
import os
import winsound
from PIL import ImageGrab
from PyQt5.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.text_edit = QTextEdit(self)
        self.setCentralWidget(self.text_edit)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setWindowOpacity(0.8)
        self.mouse = c_mouse()
        self.shell_locate = jd_config.read_ini('config', 'shell_location', 'config.ini')
        self.sim_min = float(jd_config.read_ini('config', '相似度阈值', 'config.ini'))
        self.text_edit.append('想要在游戏前端显示此窗口，请游戏里开无边框模式(会导致帧数降低，全屏模式后台运行一样有效)')
        self.text_edit.append('按·可获取当前鼠标坐标并在鼠标附近区域截图')
        self.text_edit.append('读取到护甲坐标：' + self.shell_locate)
        self.shell_locate = eval(self.shell_locate)

        keyboard.on_press_key("`", self.on_press_b)
        keyboard.on_press_key("e", self.on_press_e)

    def on_press_e(self, e):
        start_time = time.time()
        while keyboard.is_pressed("e"):
            if time.time() - start_time >= 0.47:
                x = 119
                y = 113
                width = 100
                height = 35
                # 捕获屏幕上 (x, y, width, height) 的图像
                self.capture_screen(x, y, width, height)
                captured_image = cv2.imread("captured_image.png")
                # 二值化处理截图
                _, captured_image = cv2.threshold(captured_image, 128, 255, cv2.THRESH_BINARY)
                # 二值化处理标准图片
                local_image = cv2.imread("local_image.png")
                _, local_image = cv2.threshold(local_image, 128, 255, cv2.THRESH_BINARY)
                # 计算相似度
                similarity = self.compare_images(captured_image, local_image)
                similarity_percentage = (100 - similarity / 100) / 100
                self.text_edit.append("Similarity: " + str(similarity_percentage))
                if similarity_percentage >= self.sim_min:
                    self.text_edit.append('背包已打开，自动换甲')
                    for x in self.shell_locate:
                        time.sleep(0.002)
                        self.mouse.position = x
                        time.sleep(0.002)
                        self.mouse.click(Button.left)
                        # 点击左键
                    self.text_edit.append('换甲完成')
                    # 恢复鼠标位置
                    self.mouse.position = (960, 540)
                    winsound.Beep(800, 200)
                    os.remove("captured_image.png")
                else:
                    self.text_edit.append('背包未开启，请对准死亡之箱重试')
                break
        return False

    def on_press_b(self, e):
        self.text_edit.append('当前坐标是：'+str(self.mouse.position[0])+','+str(self.mouse.position[1]))
        x = self.mouse.position[0]
        y = self.mouse.position[1]
        width = 100
        height = 35
        self.capture_screen(x, y, width, height)

    def capture_screen(self, x, y, width, height):
        screen = ImageGrab.grab(bbox=(x, y, x + width, y + height))
        screen.save("captured_image.png")
        screen = np.array(screen)
        return cv2.cvtColor(screen, cv2.COLOR_BGR2RGB)

    def compare_images(self, image1, image2):
        return cv2.norm(image1, image2, cv2.NORM_L2)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
