
import json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class MainWidget(QWidget):
    def __init__(self):
        super(MainWidget, self).__init__()
        # переменные
        self.data = None

        # виджеты
        self.tabs = QTabWidget()
        self.table = QTableWidget()

        self.gb_edit = QGroupBox("Редактирование группы")
        self.edit_gr_name = QLineEdit()
        self.edit_gr_name.setPlaceholderText("Название группы")

        # макет
        gb_layout = QVBoxLayout()
        gb_layout.addWidget(self.edit_gr_name, alignment=Qt.AlignTop)

        self.gb_edit.setLayout(gb_layout)
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.tabs)
        main_layout.addWidget(self.gb_edit)

        self.setLayout(main_layout)
        self.setWindowTitle("Редактор групп")
        self.setFont(QFont(None, 20))
        self.showMaximized()

        self.load_from_file()

    def load_from_file(self):
        try:
            with open("data.json", "r", encoding='utf-8') as file:
                self.data = json.load(file)
        except FileNotFoundError as e:
            mb = QMessageBox()
            mb.setWindowTitle("Не удалось загрузить файл")
            mb.setText(str(e))
            mb.show()
            mb.exec_()
        else:
            self.fill_table()

    def fill_table(self):
        self.table.setColumnCount(1)
        for g in self.data:
            self.tab = QWidget()
            self.tabs.addTab(self.tab, g)
            # tabs_layout = QVBoxLayout()
            # tabs_layout.addWidget(self.table)
            # self.tab.setLayout(tabs_layout)
            print(g)




if __name__ == "__main__":
    app = QApplication([])
    groupEditorWin = MainWidget()
    app.exec_()
