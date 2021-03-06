


import json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class MainWidget(QWidget):
    def __init__(self):
        super(MainWidget, self).__init__()
        # переменные
        self.data = None
        self.groups_list = []

        # виджеты
        # self.tabs = QTabWidget()
        self.gb_groups = QGroupBox("Группы")

        self.table = QTableWidget()
        self.table.setColumnCount(1)
        self.table.horizontalHeader().setStretchLastSection(True)

        self.gb_edit = QGroupBox("Редактирование группы")
        self.edit_gr_name = QLineEdit()
        self.edit_gr_name.setPlaceholderText("Название группы")
        self.rename_group_btn = QPushButton("Переименовать группу")
        self.rename_group_btn.setEnabled(False)
        self.add_group_btn = QPushButton("➕")
        self.total_pupils_amount = QSpinBox()
        self.total_pupils_amount.setValue(9)
        self.table.setRowCount(self.total_pupils_amount.value())
        self.save_group = QPushButton("Сохранить")
        self.remove_group_btn = QPushButton("🗑")

        # макет
        self.groups_layout = QVBoxLayout()
        gb_edit_layout = QVBoxLayout()
        group_name_layout = QHBoxLayout()
        group_name_layout.addWidget(self.edit_gr_name)
        group_name_layout.addWidget(self.rename_group_btn)
        group_name_layout.addWidget(self.add_group_btn)
        # gb_edit_layout.setAlignment(Qt.AlignAbsolute)
        gb_edit_layout.addLayout(group_name_layout)
        pupils_amount_layout = QHBoxLayout()
        pupils_amount_layout.addWidget(QLabel("Максимальное количество учеников"))
        pupils_amount_layout.addWidget(self.total_pupils_amount)
        gb_edit_layout.addLayout(pupils_amount_layout)
        buttons = QHBoxLayout()
        buttons.addWidget(self.save_group, stretch=9)
        buttons.addWidget(self.remove_group_btn, stretch=1)
        gb_edit_layout.addLayout(buttons)

        self.gb_edit.setLayout(gb_edit_layout)
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.gb_groups, stretch=1)
        main_layout.addWidget(self.table, stretch=1)
        main_layout.addWidget(self.gb_edit, stretch=2)

        self.setLayout(main_layout)
        self.setWindowTitle("Редактор групп")
        self.setFont(QFont(None, 20))

        self.load_from_file()
        self.edit_gr_name.textChanged.connect(self.enabled_rename_button)
        self.rename_group_btn.clicked.connect(self.rename_group)
        self.add_group_btn.clicked.connect(self.add_group)
        self.remove_group_btn.clicked.connect(self.remove_group)

        self.showMaximized()


    def load_from_file(self):
        filename = "data_test.json"
        try:
            with open(filename, "r") as file:
                self.data = json.load(file)
                print(self.data)
        except FileNotFoundError as e:
            try:
                with open(filename, "w") as file:
                    json.dump({}, file)
            except:
                pass
                mb = QMessageBox()
                mb.setWindowTitle("Не удалось сохранить файл")
                mb.setText("К сожалению в папке с программой не удалось создать необходимый файл для работы с БД")
                mb.show()
                mb.exec_()
            else:
                mb = QMessageBox()
                mb.setWindowTitle("Не удалось загрузить файл")
                mb.setText("Был создан файл " + filename)
                mb.show()
                mb.exec_()
        else:
            self.fill_group_names()
        finally:
            for rb in self.groups_list:
                rb.clicked.connect(self.fill_table)

    def fill_group_names(self):
        groups_box = QButtonGroup()
        # очистка макета от всех кнопок для выбора сегодняшних групп
        while self.groups_layout.count():
            child = self.groups_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # for i in reversed(range(groups_layout.count())):
            # groups_layout.itemAt(i).widget().setParent(None)

        for g in self.data:
            for _ in g.keys(): # не сработало обновление списка кнопок при добавлении новой группы
                _group_name = QRadioButton(_)
                self.groups_list.append(_group_name)
                groups_box.addButton(_group_name)
                self.groups_layout.addWidget(_group_name)
        self.gb_groups.setLayout(self.groups_layout)
        groups_box.setExclusive(False)
        self.groups_list[0].setChecked(True)
        groups_box.setExclusive(True)
        self.fill_table()

    def fill_table(self):
        for g in self.groups_list: ###############
            if g.isChecked():
                self.current_group_name = g
                self.table.clear()
                self.table.setHorizontalHeaderLabels(["Фамилия Имя"])
                row = 0
                for p in self.data:
                    if g.text() in p:
                        for _ in p[g.text()]:
                            self.table.setItem(row, 0, QTableWidgetItem(_)) # self.data[q.getText()]
                            row += 1
                self.edit_gr_name.setText(g.text())
                return
            else:
                continue

    def enabled_rename_button(self):
        if self.edit_gr_name.text() == self.current_group_name.text():
            self.rename_group_btn.setEnabled(False)
        else:
            self.rename_group_btn.setEnabled(True)

    def rename_group(self):
        for dic in self.data:
            if self.current_group_name.text() in dic:
                dic[self.edit_gr_name.text()] = dic[self.current_group_name.text()]
                del dic[self.current_group_name.text()]
                self.current_group_name.setText(self.edit_gr_name.text())
        self.enabled_rename_button()
        with open("data_test.json", "w") as file:
            json.dump(self.data, file, ensure_ascii=False)
        self.fill_group_names()

    def add_group(self):
        num, ok = QInputDialog.getText(self, "Куда добавить группу?", "Уажите номер группы по порядку, начиная с 1:")
        if ok and num != "":
            try:
                num = int(num)
            except:
                print("Номер группы должен быть целым числом")
            else:
                self.data.insert(num-1,{self.edit_gr_name.text():[]})
                self.table.clear()
                with open("data_test.json", "w") as file:
                    json.dump(self.data, file, ensure_ascii=False)
                self.fill_group_names()

    def remove_group(self):############## что-то не так при удалении группы второй раз, не закрывая программы
        # возможно надо очищать список self.group_list
        for dic in self.data:
            if self.edit_gr_name.text() in dic:
                # self.groups_list.remove(self.edit_gr_name.text())
                self.data.remove(dic)
                # del dic[self.current_group_name.text()]
        self.enabled_rename_button()
        with open("data_test.json", "w") as file:
            json.dump(self.data, file, ensure_ascii=False)
        self.fill_group_names()


if __name__ == "__main__":
    app = QApplication([])
    groupEditorWin = MainWidget()
    app.exec_()
