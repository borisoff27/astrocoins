"""
    1. Что-то не так с замечаниями или рассчётом
    2.
    3.

"""

"""
Структура словаря
pupil = {
    "Фамилия Имя":{
        ДД мес:{
            "achievements": ["ачивка 1", "ачивка 2"],
            "bonus": 0,
            "extra": 0,
            "reprimands": 0,
            "notes": "заметка об ученике в этот день"
        }
    }
}
"""

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import json

# спиок достижений
achievements_list = ["Посещение",
                     "Пунктуальность",
                     "Ответы на вопросы преподавателя",
                     "Выполнение основных заданий",
                     "Помощь нуждающимся"]

bonus_price = 5  # стоимость одного бонустного задания
extra_price = 5  # стоимость одного дополнительного задания
# "Выполнение бонусных заданий",
# "Выполнение дополнительных заданий",

groups_list = [
    "СР 17-00 ВП",
    "СР 19-00 ГД",
    "ЧТ 9-30 ВП",
    "ПТ 17-20 ГД",
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


# отступ вначале ячейки таблицы
class PaddingDelegate(QStyledItemDelegate):
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


class TableWidget(QTableWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
        self.prev_btn = PushButton("◀")
        self.next_btn = PushButton("▶")
        self.group_name_lbl = QLabel("Группа")
        self.group_name_lbl.setAlignment(Qt.AlignCenter)
        self.table = TableWidget(9, 1)
        self.add_table_col_btn = PushButton("Добавить столбец")
        self.achievements_gb = QGroupBox("Достижения")
        self.achievements_gb.setStyleSheet("background-color:#D9BBFF; color: #2B2235")
        self.bonus_ach = LineEdit()
        self.bonus_ach.setFixedWidth(70)
        self.bonus_ach.setAlignment(Qt.AlignCenter)
        self.bonus_ach.setReadOnly(True)
        self.bonus_up_btn = PushButton("▲")
        self.bonus_up_btn.setFixedWidth(70)
        self.bonus_down_btn = PushButton("▼")
        self.bonus_down_btn.setFixedWidth(70)
        self.extra_ach = LineEdit()
        self.extra_ach.setAlignment(Qt.AlignCenter)
        self.extra_ach.setReadOnly(True)
        self.extra_ach.setFixedWidth(70)
        self.extra_up_btn = PushButton("▲")
        self.extra_up_btn.setFixedWidth(70)
        self.extra_down_btn = PushButton("▼")
        self.extra_down_btn.setFixedWidth(70)
        self.reprimands_amount = QLineEdit()
        self.reprimands_amount.setReadOnly(True)
        self.reprimands_amount.setText("0")
        self.reprimands_amount.setAlignment(Qt.AlignCenter)
        self.inc_repr_btn = PushButton("▲")
        self.inc_repr_btn.setFixedWidth(70)
        self.dec_repr_btn = PushButton("▼")
        self.dec_repr_btn.setFixedWidth(70)
        self.save_btn = PushButton("Сохранить")
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
        self.visualisation()
        self.setWindowTitle("✨Астрокойны💰")
        self.showMaximized()

    def visualisation(self):

        # self.setFont(QFont("Times", 12))
        win_style = """
            background-color: #FFEC99;
            color: #2B2235;
        """
        self.setStyleSheet(win_style)
        table_style = """
                    QTableWidget:item {font-size: 12px}
                """
        header_style = """::section{background-color:#D9BBFF;
                                    font-weight: bold;}"""
        self.table.horizontalHeader().setStyleSheet(header_style)
        self.table.verticalHeader().setStyleSheet(header_style)
        # for _ in range(self.columnCount()):
        #     self.horizontalHeaderItem(_).setBackground(QColor(255, 0, 0))
        # self.setStyleSheet(table_style)

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
                    font-size:15pt;     
                }

                QCheckBox::indicator {
                    width:  40px;
                    height: 40px;
                    border-radius: 5px;
                }
                QCheckBox::indicator:unchecked
                {
                    background-color: #FFF;
                }
                QCheckBox::indicator:checked
                {
                    background-color: #833AE0;
                }
                
                
                '''
        chb_names = [
            "😎 Посещение",
            "⏰ Пунктуальность",
            "✋ Ответы на вопросы преподавателя",
            "✅ Выполнение основных заданий",
            "🤝 Помощь нуждающимся",
            "⭐ Выполнение бонусных заданий",
            "🏠 Выполнение дополнительных заданий"]
        for _ in range(len(chb_names)):
            chb = QCheckBox(chb_names[_])
            self.achievement_chb_list.append(chb)

            if _ == len(chb_names) - 2:
                row1 = QHBoxLayout()
                row1.addWidget(self.achievement_chb_list[_])
                # hs = QSpacerItem(20, 20, QSizePolicy.Ignored, QSizePolicy.Minimum)

                # row1.addItem(hs)
                row1.addWidget(self.bonus_ach)
                row1.addWidget(self.bonus_up_btn)
                row1.addWidget(self.bonus_down_btn)
                achievements_layout.addLayout(row1)
            elif _ == len(chb_names) - 1:
                row2 = QHBoxLayout()
                row2.addWidget(self.achievement_chb_list[_])
                row2.addWidget(self.extra_ach)
                row2.addWidget(self.extra_up_btn)
                row2.addWidget(self.extra_down_btn)
                achievements_layout.addLayout(row2)
            else:
                achievements_layout.addWidget(self.achievement_chb_list[_])
            chb.setStyleSheet(achievement_style_sheet)

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

    def reset_flags(self):
        # сброс чекбоксов
        for chb in self.achievement_chb_list:
            chb.setCheckState(Qt.Unchecked)

        # сброс счетчика бонсуных и доп. заданий
        self.bonus_ach.setText("0")
        self.extra_ach.setText("0")

        # обнуление замечаний
        self.reprimands_amount.setText("0")

        # очистка комментариев
        self.note_field.clear()

        self.visualisation()

    # выбор дня в календаре
    def choose_day(self):
        self.reset_flags()
        try:
            self.note_field.clear()
            current_day = self.calendar.selectedDate()
            weekday_name = current_day.shortDayName(current_day.dayOfWeek())

            groups_list_today = []  # список групп СЕГОДНЯ
            for group_name in groups_list:
                if weekday_name.lower() in group_name.lower():
                    groups_list_today.append(group_name)
            self.group_name_lbl.setText(groups_list_today[0])

            # очистка макета от всех кнопок для выбора сегодняшних групп
            # while self.groups_list_layout.count():
            #     child = self.groups_list_layout.takeAt(0)
            #     if child.widget():
            #         child.widget().deleteLater()
            for i in reversed(range(self.groups_list_layout.count())):
                self.groups_list_layout.itemAt(i).widget().setParent(None)

            self.groups_btn_list.clear()
            # создание переключателей для выбора текущей группы
            for i in range(len(groups_list_today)):
                r_btn = QRadioButton(groups_list_today[i])
                self.groups_btn_list.append(r_btn)
                r_btn.setStyleSheet('QRadioButton{font: 12pt None;} QRadioButton::indicator { width: 40px; height: 40px;};')
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
            self.reset_flags()

    # выбор группы (клик по radiobutton)
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
                    json.dump(self.pupil, file, indent=4, sort_keys=True, ensure_ascii=False)
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

        # подгон ширины под размер содержимого
        for _ in range(1, self.table.columnCount()):
            self.table.horizontalHeader().setSectionResizeMode(_, QHeaderView.ResizeToContents)

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
                    for col in range(1, self.table.columnCount() - 1):
                        if self.table.horizontalHeaderItem(col).text() in self.pupil[pup]:
                            value = self.pupil[pup][str(self.table.horizontalHeaderItem(col).text())]["achievements"]
                            bon = self.pupil[pup][str(self.table.horizontalHeaderItem(col).text())]["bonus"]
                            ex = self.pupil[pup][str(self.table.horizontalHeaderItem(col).text())]["extra"]
                            rep = self.pupil[pup][str(self.table.horizontalHeaderItem(col).text())]["reprimands"]

                            curr_sum = len(
                                value) * 10 + bon * 5 + ex * 5 - rep * 10  # подсчёт суммы астрокойнов из всех данных
                            sum += curr_sum  # итоговая сумма
                            self.table.setItem(row, col, QTableWidgetItem(str(curr_sum)))
                    self.table.setItem(row, col + 1, QTableWidgetItem(str(sum)))  # последний столбец для общей суммы
                    row += 1
            except:
                print("Опять что-то не так, но уже при загрузке данных из файла")
            finally:
                self.pupils_load()

    def cell_fill(self):
        # обработка нажатия на каждый чекбокс
        if self.table.currentColumn() != 0:
            try:
                points, b, e = 0, 0, 0
                key = self.table.item(self.table.currentRow(), 0).text()  # фамилия
                value = self.table.horizontalHeaderItem(self.table.currentColumn()).text()  # дата
                _ach_lst = []
                for chb in self.achievement_chb_list:
                    if chb.checkState():
                        if chb.text().find("Посещение") != -1:
                            points += 0.5
                        elif chb.text().find("Пунктуальность") != -1:
                            points += 1.5
                        elif chb.text().find("бонус") != -1:
                            b = int(self.bonus_ach.text()) * bonus_price
                        elif chb.text().find("допол") != -1:
                            e = int(self.extra_ach.text()) * extra_price
                        else:
                            points += 1

                        if chb.text().find("бонус") == -1 and chb.text().find("допол") == -1:
                            _ach_lst.append(chb.text()[2:])

                if key not in self.pupil:
                    self.pupil[key] = {value: {}}

                self.pupil[key][value] = {"achievements": _ach_lst,
                                          "bonus": int(self.bonus_ach.text()),
                                          "extra": int(self.extra_ach.text()),
                                          "reprimands": int(self.reprimands_amount.text()),
                                          "notes": self.note_field.toPlainText()}

                self.table.setItem(self.table.currentRow(), self.table.currentColumn(),
                                   QTableWidgetItem(str(int(points * 10 + b + e))))
            except:
                print("Не сработала функция cell_fill")
            finally:
                self.calculate_sum()

    def cell_select(self):
        self.reset_flags()
        try:
            t = self.table
            if t.item(t.currentRow(), t.currentColumn()) is not None:
                key = self.table.item(self.table.currentRow(), 0).text()
                value = self.table.horizontalHeaderItem(self.table.currentColumn()).text()
                for chb in self.achievement_chb_list:
                    if chb.text()[2:] in self.pupil[key][value]["achievements"]:
                        chb.setCheckState(Qt.Checked)
                    elif chb.text()[2:] == "Выполнение бонусных заданий" and self.pupil[key][value]["bonus"] != 0:
                        chb.setCheckState(Qt.Checked)
                    elif chb.text()[2:] == "Выполнение дополнительных заданий" and self.pupil[key][value]["extra"] != 0:
                        chb.setCheckState(Qt.Checked)

                self.bonus_ach.setText(str(self.pupil[key][value]["bonus"]))
                self.extra_ach.setText(str(self.pupil[key][value]["extra"]))
                self.reprimands_amount.setText(str(self.pupil[key][value]["reprimands"]))
                self.note_field.setText(self.pupil[key][value]["notes"])
            else:
                self.reset_flags()
        except:
            print("Не сработала функция cell_select")

    # закончил +- тут. Надо затестить сохранение и загрузку
    def pupil_fill(self):
        if self.table.currentItem():
            key = self.table.item(self.table.currentRow(), 0).text()
            value = self.table.horizontalHeaderItem(self.table.currentColumn()).text()
            for chb in self.achievement_chb_list:
                if chb.text()[2:] == "Выполнение бонусных заданий" and chb.checkState():
                    self.pupil[key][value]["bonus"] = int(self.bonus_ach.text())
                if chb.text()[2:] == "Выполнение дополнительных заданий" and chb.checkState():
                    self.pupil[key][value]["extra"] = int(self.extra_ach.text())
            self.pupil[key][value]["reprimands"] = int(self.reprimands_amount.text())
            self.pupil[key][value]["notes"] = self.note_field.toPlainText()
            c = 0

    def inc_repr(self):
        count = int(self.reprimands_amount.text()) + 1
        self.reprimands_amount.setText(str(count))
        if self.table.currentItem() is not None:
            key = self.table.item(self.table.currentRow(), 0).text()
            value = self.table.horizontalHeaderItem(self.table.currentColumn()).text()
            current_value = len(self.pupil[key][value]["achievements"]) * 10
            current_value -= count * 10
            self.table.currentItem().setText(str(current_value))
        self.pupil[key][value]["reprimands"] = count
        self.calculate_sum()
        self.pupil_fill()

    def dec_repr(self):
        count = int(self.reprimands_amount.text())
        if count > 0:
            count -= 1
            self.reprimands_amount.setText(str(count))
        if self.table.currentItem() is not None:
            key = self.table.item(self.table.currentRow(), 0).text()
            value = self.table.horizontalHeaderItem(self.table.currentColumn()).text()
            current_value = len(self.pupil[key][value]["achievements"]) * 10
            current_value -= count * 10
            self.table.currentItem().setText(str(current_value))
        self.pupil[key][value]["reprimands"] = count
        self.calculate_sum()
        self.pupil_fill()

    def bonus_up(self):
        count = int(self.bonus_ach.text()) + 1
        self.bonus_ach.setText(str(count))
        for chb in self.achievement_chb_list:
            if chb.text()[2:] == "Выполнение бонусных заданий" and not chb.checkState():
                chb.setCheckState(True)

        self.calculate_sum()
        self.pupil_fill()
        self.cell_fill()

    def bonus_down(self):
        count = int(self.bonus_ach.text())
        if count > 0:
            count -= 1
            self.bonus_ach.setText(str(count))

        self.calculate_sum()
        self.pupil_fill()
        self.cell_fill()

    def extra_up(self):
        count = int(self.extra_ach.text()) + 1
        self.extra_ach.setText(str(count))
        for chb in self.achievement_chb_list:
            if chb.text()[2:] == "Выполнение дополнительных заданий" and not chb.checkState():
                chb.toggle()
                # chb.setCheckState(Qt.Checked)

        self.calculate_sum()
        self.pupil_fill()
        self.cell_fill()

    def extra_down(self):
        count = int(self.extra_ach.text())
        if count > 0:
            count -= 1
            self.extra_ach.setText(str(count))

        self.calculate_sum()
        self.pupil_fill()
        self.cell_fill()

    def calculate_sum(self):
        self.table.setFocus()
        for row in range(self.table.rowCount()):
            if self.table.item(row, 0) is not None:
                total_sum = 0
                for col in range(1, self.table.columnCount() - 1):
                    if self.table.item(row, col) is not None:
                        total_sum += int(self.table.item(row, col).text())
                self.table.setItem(row, col + 1, QTableWidgetItem(str(total_sum)))  # последний столбец для общей суммы
            else:
                return

    def test(self):
        for chb in self.achievement_chb_list:
            chb.toggle()

    def connects(self):
        self.calendar.selectionChanged.connect(self.choose_day)
        self.add_table_col_btn.clicked.connect(self.test)
        for chb in self.achievement_chb_list:
            chb.clicked.connect(self.cell_fill)
        self.bonus_up_btn.clicked.connect(self.bonus_up)
        self.bonus_down_btn.clicked.connect(self.bonus_down)
        self.extra_up_btn.clicked.connect(self.extra_up)
        self.extra_down_btn.clicked.connect(self.extra_down)
        self.table.clicked.connect(self.cell_select)
        self.save_btn.clicked.connect(self.save_table_to_file)
        self.inc_repr_btn.clicked.connect(self.inc_repr)
        self.dec_repr_btn.clicked.connect(self.dec_repr)
        self.note_field.textChanged.connect(self.pupil_fill)
        self.prev_btn.clicked.connect(self.test)


if __name__ == "__main__":
    app = QApplication([])
    main_win = MainWidget()
    app.exec_()
