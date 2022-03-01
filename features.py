from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import json
# from main import main_win

# отступ вначале ячейки таблицы
class PaddingDelegate(QStyledItemDelegate):
    def __init__(self, padding=1, parent=None):
        super(PaddingDelegate, self).__init__(parent)
        self._padding = ' ' * max(1, padding)

    def displayText(self, text, locale):
        return self._padding + text

    def createEditor(self, parent, option, indEX):
        editor = super().createEditor(parent, option, indEX)
        margins = editor.textMargins()
        padding = editor.fontMetrics().width(self._padding) + 1
        margins.setLeft(margins.left() + padding)
        editor.setTextMargins(margins)
        return editor


class LineEdit(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        le_style = """
        QLineEdit{
            background-color: #FFF;
            color: #833AE0;
            font-size: 15pt;
            border-radius: 15px;
            padding: 10px;
            }

        """
        self.setStyleSheet(le_style)


class PushButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        button_style = """
        QPushButton{
            background-color: #833AE0;
            color: #FFFFFF;
            font-size: 15pt;
            border-radius: 15px;
            padding: 10px;
            }
        QPushButton:pressed
        {
          border-left: 3px solid #2B2235;
          border-top: 3px solid #2B2235;
        }
        """
        self.setStyleSheet(button_style)



