"""
    1. Запись замечаний в файл
    2. Переделать список достижений в файле в двумерный список для второго элмента - замечаний
    3. Расчет итоговой суммы при вводе данных (исправить)
"""

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import json

achievements_list = ["Посещение",
                     "Пунктуальность",
                     "Ответы на вопросы преподавателя",
                     "Выполнение основных заданий",
                     "Выполнение бонусных заданий",
                     "Выполнение дополнительных заданий",
                     "Помощь нуждающимся"]

groups_list = [
    "СР 17-00 ВП",
    "СР 19-00 ГД",
    "ЧТ 9-30 ВП",
    "ПТ 19-00 ПС2",
    "СБ 10-30 ВП",
    "СБ 12-30 ГД",
    "СБ 14-10 ПС1",
    "СБ 16-00 КГ",
    "СБ 17-40 СС",
    "ВС 10-30 ГД",
    "ВС 12-30 КГ",
    "ВС 15-00 СС",
    "ВС 17-00 ГД",
    "ВС 19-00 ПС2"
]

dates = {
    "СР": None,
    "ЧТ": None,
    "ПТ": None,
    "СБ": None,
    "ВС": None
}

# формирование словаря дат по дням
start_day = QDate(2021, 1, 27)
for d in dates.keys():
    days = []
    _day = start_day
    while _day.month() < 6:
        days.append(_day.toString("dd MMM"))
        _day = _day.addDays(7)
    dates[d] = days
    start_day = start_day.addDays(1)


class PaddingDelegate(QStyledItemDelegate):  # отступ вначале ячейки таблицы
    def __init__(self, padding=1, parent=None):
        super(PaddingDelegate, self).__init__(parent)
        self._padding = ' ' * max(1, padding)

    def displayText(self, text, locale):
        return self._padding + text

    def createEditor(self, parent, option, index):
        editor = super().createEditor(parent, option, index)
        margins = editor.textMargins()
        padding = editor.fontMetrics().width(self._padding) + 1
        margins.setLeft(margins.left() + padding)
        editor.setTextMargins(margins)
        return editor


class TableWidget(QTableWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        table_style = """
            QTableWidget:item {font-size: 12px}
        """
        self.setStyleSheet(table_style)
        self.setFont(QFont(None, 15))
        # добавление отступа вначале ячейки
        self.delegate = PaddingDelegate()
        self.setItemDelegate(self.delegate)

    def contextMenuEvent(self, event):
        context_menu = QMenu(self)
        del_row_menu = context_menu.addAction("Удалить строку")
        action = context_menu.exec_(self.mapToGlobal(event.pos()))

        if action == del_row_menu:
            current_row_index = self.currentRow()
            del main_win.pupil[self.item(current_row_index, 0).text()]
            self.removeRow(current_row_index)
            self.setRowCount(10)

    # def mousePressEvent(self, event):
    #     table = event.button()
    #     if table == Qt.RightButton:
    #         print("Right button click!")
    #     elif table == Qt.LeftButton:
    #         print("Left button click!")
    #     return QTableWidget.mousePressEvent(self, event)


class MainWidget(QWidget):
    def __init__(self):
        super().__init__()

        # переменные
        self.groups_btn_list = []  # список кнопок выбора текущей группы сегодня
        self.achievement_chb_list = []  # список чекбоксов для выбора достижения

        # виджеты
        self.groups_list_layout = QHBoxLayout()
        self.setFont(QFont("Times", 12))
        self.prev_btn = QPushButton("◀")
        self.next_btn = QPushButton("▶")
        self.group_name_lbl = QLabel("Группа")
        self.group_name_lbl.setAlignment(Qt.AlignCenter)
        self.table = TableWidget(10, 1)
        self.add_table_col_btn = QPushButton("Добавить столбец")
        self.achievements_gb = QGroupBox("Достижения")
        self.reprimands_amount = QLineEdit()
        self.reprimands_amount.setReadOnly(True)
        self.reprimands_amount.setText("0")
        self.reprimands_amount.setAlignment(Qt.AlignCenter)
        self.inc_repr_btn = QPushButton("▲")
        self.dec_repr_btn = QPushButton("▼")
        self.save_btn = QPushButton("Сохранить")
        self.note_field = QTextEdit()
        self.groups_list_btn_gb = QGroupBox("Список групп сегодня")
        self.calendar = QCalendarWidget()
        self.calendar.setFont(QFont("Times", 12))

        # словарь вида: ФИ : {дата : [список достижений за занятие]}
        self.pupil = dict()
        self.resize(1366, 768)
        self.choose_day()
        self.widgets_location()
        self.connects()
        self.showMaximized()

    def widgets_location(self):
        nav_layout = QHBoxLayout()
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.group_name_lbl)
        nav_layout.addWidget(self.next_btn)

        # динамическое добавление виджетов checkbox
        achievements_layout = QVBoxLayout()
        achievement_style_sheet = '''
                QCheckBox {
                    spacing: 20px;
                    font-size:18pt;     
                }

                QCheckBox::indicator {
                    width:  40px;
                    height: 40px;
                }
                '''
        for _ in range(len(achievements_list)):
            chb = QCheckBox(achievements_list[_])
            chb.setStyleSheet(achievement_style_sheet)
            self.achievement_chb_list.append(chb)
            achievements_layout.addWidget(self.achievement_chb_list[_])

        reprimand_layout = QHBoxLayout()
        reprimand_layout.addWidget(QLabel("Количество замечаний:"))
        reprimand_layout.addWidget(self.reprimands_amount)
        reprimand_layout.addWidget(self.inc_repr_btn)
        reprimand_layout.addWidget(self.dec_repr_btn)
        achievements_layout.addLayout(reprimand_layout)
        self.achievements_gb.setLayout(achievements_layout)

        table_layout = QVBoxLayout()
        table_layout.addLayout(nav_layout)
        table_layout.addWidget(self.table)
        table_layout.addWidget(self.save_btn)

        top_layout = QHBoxLayout()
        top_layout.addLayout(table_layout, stretch=2)
        top_layout.addWidget(self.achievements_gb, stretch=1)

        comment_layout = QVBoxLayout()
        comment_layout.addWidget(self.note_field)
        comment_layout.addWidget(self.groups_list_btn_gb)

        bottom_layout = QHBoxLayout()
        bottom_layout.addLayout(comment_layout, stretch=2)
        bottom_layout.addWidget(self.calendar, stretch=1)

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addLayout(bottom_layout)
        self.setLayout(main_layout)

    def choose_day(self):
        try:
            current_day = self.calendar.selectedDate()
            weekday_name = current_day.shortDayName(current_day.dayOfWeek())

            groups_list_today = []  # список групп СЕГОДНЯ
            for group_name in groups_list:
                if weekday_name.lower() in group_name.lower():
                    groups_list_today.append(group_name)
            self.group_name_lbl.setText(groups_list_today[0])

            # очистка макета от всех кнопок для выбора сегодняшних групп
            while self.groups_list_layout.count():
                child = self.groups_list_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            self.groups_btn_list.clear()
            # создание переключателей для выбора текущей группы
            for i in range(len(groups_list_today)):
                self.groups_btn_list.append(QRadioButton(groups_list_today[i]))
                self.groups_list_layout.addWidget(self.groups_btn_list[i])
            self.groups_btn_list[0].setChecked(1)
            self.groups_list_btn_gb.setLayout(self.groups_list_layout)
            self.button_click()
        except:
            print("Не срабтала функция choose_day")
        else:
            # т.к. кнопки создаются всякий раз при выборе дня, то и клики обрабатывать нужно всегдя по новой
            for self.b in self.groups_btn_list:
                self.b.clicked.connect(self.button_click)
        finally:
            for chb in self.achievement_chb_list:
                chb.setCheckState(0)
            self.reprimands_amount.setText("0")

    def button_click(self):
        for b in self.groups_btn_list:
            if b.isChecked():
                self.group_name_lbl.setText(b.text())
                self.open_table()

    def pupils_load(self):
        # group = {None: []}
        # filename = str(self.group_name_lbl.text()) + ".json"
        with open("data.json", 'r', encoding="utf-8") as file:
            group = json.load(file)
        row = 0
        for p in group[str(self.group_name_lbl.text())]:
            if self.table.item(row, 0) is not None:
                return
            else:
                self.table.setItem(row, 0, QTableWidgetItem(p))
            row += 1

    def save_table_to_file(self):
        try:
            if len(self.pupil) > 0:
                filename = str(self.group_name_lbl.text()) + ".json"
                with open(filename, 'w') as file:
                    json.dump(self.pupil, file, sort_keys=True, ensure_ascii=False)
        except:
            print("Ошибка при сохранении файла")

    def open_file(self):
        try:
            self.pupil.clear()
            filename = str(self.group_name_lbl.text()) + ".json"
            file = open(filename, 'r')
        except:
            pass
        else:
            self.pupil = json.load(file)
        finally:
            file.close()

    def add_col(self):
        self.table.setColumnCount(int(self.table.columnCount()) + 1)
        self.table.setColumnWidth(self.table.columnCount() - 1, 100)

    def open_table(self):
        # при открытии таблицы создается 1 столбец для ученика
        try:
            self.table.clear()
            self.table.setColumnCount(1)
            self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
            for d in dates.keys():
                if self.calendar.selectedDate().shortDayName(
                        self.calendar.selectedDate().dayOfWeek()).lower() == d.lower():
                    for i in dates[d]:
                        self.add_col()
                    break
            group_dates = [str(_) for _ in dates[d]]
            group_dates.insert(0, "Фамилия Имя")
            group_dates.append("ИТОГО")
            self.add_col()
            self.table.setHorizontalHeaderLabels(group_dates)
        except:
            print("Что-то не так при создании шаблона страницы")
        else:
            try:
                self.open_file()
                row = 0
                for pup in self.pupil:
                    self.table.setItem(row, 0, QTableWidgetItem(pup))
                    sum = 0
                    for col in range(1, self.table.columnCount()-1):
                        if self.table.horizontalHeaderItem(col).text() in self.pupil[pup]:
                            value = self.pupil[pup][str(self.table.horizontalHeaderItem(col).text())]
                            self.table.setItem(row, col, QTableWidgetItem(str(len(value) * 10)))
                            sum += len(value) * 10
                    self.table.setItem(row, col+1, QTableWidgetItem(str(sum)))  # последний столбец для общей суммы
                    row += 1
            except:
                print("Опять что-то не так, но уже при загрузке данных из файла")
            finally:
                self.pupils_load()

    def cell_fill(self):
        # обработка нажатия на каждый чекбокс
        if self.table.currentColumn() != 0:
            try:
                points = 0
                key = self.table.item(self.table.currentRow(), 0).text()
                value = self.table.horizontalHeaderItem(self.table.currentColumn()).text()
                _ach_lst = []
                for chb in self.achievement_chb_list:
                    if chb.checkState():
                        points += 1
                        _ach_lst.append(chb.text())
                        # self.pupil[key][value].append(chb.text())
                if key not in self.pupil:
                    self.pupil[key] = {value: None}
                self.pupil[key][value] = _ach_lst
                self.table.setItem(self.table.currentRow(), self.table.currentColumn(), QTableWidgetItem(str(points * 10)))
                self.pupil[key]["Замечания"] = int(self.reprimands_amount.text())
            except:
                print("Нужно выбрать ячейку")

    def cell_select(self):
        self.reprimands_amount.setText("0")
        for chb in self.achievement_chb_list:
            chb.setCheckState(0)
        try:
            t = self.table
            if t.item(t.currentRow(), t.currentColumn()) is not None:
                key = self.table.item(self.table.currentRow(), 0).text()
                value = self.table.horizontalHeaderItem(self.table.currentColumn()).text()
                for chb in self.achievement_chb_list:
                    if chb.text() in self.pupil[key][value]:
                        chb.setCheckState(1)
                    else:
                        chb.setCheckState(0)
        except:
            pass

    def inc_repr(self):
        count = int(self.reprimands_amount.text()) + 1
        self.reprimands_amount.setText(str(count))
        if self.table.currentItem() is not None:
            key = self.table.item(self.table.currentRow(), 0).text()
            value = self.table.horizontalHeaderItem(self.table.currentColumn()).text()
            current_value = len(self.pupil[key][value])*10
            current_value -= count * 10
            self.table.currentItem().setText(str(current_value))
        # self.pupil[key][value].append(count)
        self.calculate_sum()

    def dec_repr(self):
        count = int(self.reprimands_amount.text())
        if count > 0:
            count -= 1
            self.reprimands_amount.setText(str(count))
        if self.table.currentItem() is not None:
            key = self.table.item(self.table.currentRow(), 0).text()
            value = self.table.horizontalHeaderItem(self.table.currentColumn()).text()
            current_value = int(self.table.currentItem().text())
            current_value = len(self.pupil[key][value]) * 10
            current_value -= count * 10
            self.table.currentItem().setText(str(current_value))
        # self.pupil[key][value].append(count)
        self.calculate_sum()

    def calculate_sum(self):
        self.table.setFocus()
        for row in range(self.table.rowCount()):
            if self.table.item(row, 0) is not None:
                total_sum = 0
                for col in range(1, self.table.columnCount()-1):
                    if self.table.item(row, col) is not None:
                        total_sum += int(self.table.item(row, col).text())
                self.table.setItem(row, col+1, QTableWidgetItem(str(total_sum)))  # последний столбец для общей суммы
            else:
                return

    def test(self):
        pass

    def connects(self):
        self.calendar.selectionChanged.connect(self.choose_day)
        self.add_table_col_btn.clicked.connect(self.test)
        for chb in self.achievement_chb_list:
            chb.clicked.connect(self.cell_fill)
        self.table.clicked.connect(self.cell_select)
        self.save_btn.clicked.connect(self.save_table_to_file)
        self.inc_repr_btn.clicked.connect(self.inc_repr)
        self.dec_repr_btn.clicked.connect(self.dec_repr)


if __name__ == "__main__":
    app = QApplication([])
    main_win = MainWidget()
    app.exec_()
