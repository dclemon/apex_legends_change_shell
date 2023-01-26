from pynput.keyboard import Key, Listener, KeyCode, Controller
from pynput.mouse import Button,Controller as c_mouse
import jd_config
import gevent

control = Controller()
mouse = c_mouse()


shell_loacte = jd_config.read_ini('config', 'shell_location', 'config.ini')
print('读取到护甲坐标：'+ shell_loacte)

shell_loacte = eval(shell_loacte)

def show(key):

    #if key == Key.alt_l:
    if key == KeyCode.from_char('`') or key == KeyCode.from_char('~'):

        control.release('w')
        control.release('a')
        control.release('s')
        control.release('d')

        control.press('e')
        gevent.sleep(0.5)
        control.release('e')

        for x in shell_loacte:
            mouse.position = x
            mouse.click(Button.left)
            #点击左键

        control.press(Key.tab)
        control.release(Key.tab)
        print('换甲完成')

    if key == KeyCode.from_char('1'):
        print('当前坐标是：'+str(mouse.position[0])+','+str(mouse.position[1]))

# Collect all event until released
with Listener(on_press = show) as listener:
    listener.join()