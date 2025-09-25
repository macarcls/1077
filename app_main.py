from PyQt6.QtWidgets import QApplication, QMainWindow
from qt_material import apply_stylesheet
from UI_Funct.UI_Buttons_Functions import UI_func

app = QApplication([])
win = UI_func()
apply_stylesheet(app, theme='dark_teal.xml')
win.show()
app.exec()
win.show()