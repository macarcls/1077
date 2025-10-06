from PyQt6.QtWidgets import QApplication, QMainWindow
from qt_material import apply_stylesheet
import asyncio
from qasync import QEventLoop
from UI_Funct.UI_Buttons_Functions import UI_func

app = QApplication([])
loop = QEventLoop(app)
asyncio.set_event_loop(loop)
win = UI_func()
apply_stylesheet(app, theme='dark_teal.xml')
win.show()
with loop:
    loop.run_forever()