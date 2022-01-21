
# надо выйти из папки source ../
# pyinstaller --onefile --icon=source/ico.ico --noconsole --name "Астрокойны" source/main.py

"""
Доработки:
3. Добавление групп без работы с файлом
5. ГЛОБАЛЬННО - сделать выгрузку для ЗП и синхронизировать их
6. Фокус на текущий день - работает по разному при открытии и созранении


"""

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import json

readme = """Небольшой гайд

1. После первого запуска программы автоматически создаст файл groups_list.json
2. Программу необходимо закрыть (при нажатии на ОК она закроется сама)
3. Перечислите в файле groups_list.json все группы в формате: ПН 10-30 ВП

Пример готового файла groups_list.json:
{
    "groups": [
        "ПН 18-00 ОЛ",
        "ВТ 10-00 ПС",
        "СР 17-15 CC",
        "СР 19-00 ПС2",
        "ЧТ 19-00 КГ",
        "ПТ 15-30 ВП",
        "СБ 10-00 ГР",
        "СБ 11-45 ГД",
        "СБ 15-30 СС",
        "СБ 17-15 ВП",
        "ВС 11-15 КГ",
        "ВС 13-30 ГД2",
        "ПТ 19-00 ГД",
        "ВС 15-30 ГД",
        "ВС 19-00 ПС"
    ]
}

4. Для добавления учеников необходимо нажать на значок карандаша справа от кнопки СОХРАНИТЬ
5. Сохраните изменения
6. Наслаждайтесь выставлением баллов:)

Пример готового файла ВС 13-30 ГД2.json:
{
    "Алгоритмиков Супер": {},
    "Ракетов Кеплер": {},
    "Марсоботов Кадет": {}
}


Возможные проблемы:
ПРОБЛЕМА
Все заполнено, но не отображается
РЕШЕНИЕ
Посмотрите внимательно структуру файла. Возможно не хватает запятой или стоит лишний символ


ПРОБЛЕМА
Имена детей в программе отображаются иероглифами
РЕШЕНИЕ
Через блокнот необходимо ересозранить файл:
1. Файл
2. Сохранить как
3. Внизу выбрать кодировку ANSI
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

# спиок достижений
achievements_list = ["Посещение",
                     "Пунктуальность",
                     "Турбо-режим",
                     "Ответы на вопросы преподавателя",
                     "Выполнение основных заданий",
                     "Помощь нуждающимся"]

base_price = 10  # базовая стоимость
visit_price = 5  # стоимость одно посещения
on_time_price = 15  # стоимость пунктуальности
turbo_price = 5  # скорость турбо-режима
bonus_price = 10  # стоимость одного бонустного задания
extra_price = 15  # стоимость одного дополнительного задания

students_amount = 1  # количество человек в группе
today_column = 0

state = 1
is_table_edit = False
groups = dict()

# чтение из файла словаря с группами
try:
    with open("groups_list.json", 'r', encoding="utf-8") as file:
        groups = json.load(file)
except Exception as EX:
    print(EX)
    with open("groups_list.json", 'w') as file:
        json.dump({"groups": []}, file, indent=4, sort_keys=True, ensure_ascii=False)
    with open("groups_list.json", 'r', encoding="utf-8") as file:
        groups = json.load(file)

# список названий групп из файла groups_list.json
groups_list = groups["groups"]
if len(groups_list) == 0:
    state = 0

# создание шаблонов групп в файлах по названию группы
for _g in groups_list:
    filename = str(_g) + ".json"
    try:
        # попытка открыть файл с группой
        group_file_open = open(filename, "r")
        group_file_open.close()
    except IOError as EX:
        # если не удалось открыть файл, то он создаётся с шаблоном {"": []}
        with open(filename, 'w') as file:
            json.dump({"": {}}, file, indent=4, sort_keys=True, ensure_ascii=False)

dates = {
    "ПН": None,
    "ВТ": None,
    "СР": None,
    "ЧТ": None,
    "ПТ": None,
    "СБ": None,
    "ВС": None
}

# формирование словаря дат по дням
start_day = QDate(2021, 8, 30)  # первый понедельник месяца
# start_day = QDate(2022, 1, 3)   # первый понедельник месяца
for d in dates.keys():
    days = []
    _day = start_day
    while _day.month() > 1: # > 1 - до НГ, < 6 - после НГ
    # while _day.month() < 6: # > 1 - до НГ, < 6 - после НГ
        days.append(_day.toString("dd MMM"))
        _day = _day.addDays(7)
    dates[d] = days
    start_day = start_day.addDays(1)

# start_day = QDate(2021, 8, 30)  # первый понедельник месяца
start_day = QDate(2022, 1, 3)   # первый понедельник месяца
for d in dates.keys():
    days = []
    _day = start_day
    # while _day.month() > 1: # > 1 - до НГ, < 6 - после НГ
    while _day.month() < 6: # > 1 - до НГ, < 6 - после НГ
        days.append(_day.toString("dd MMM"))
        _day = _day.addDays(7)
    dates[d] += days
    start_day = start_day.addDays(1)

# дополнительные дни вне расписания
# dates["СБ"].append("1 мая д.")
# dates["ВС"].append("3 мая д.")
# dates["СБ"].append("8 мая д.")
# dates["ВС"].append("10 мая д.")
# dates["ВС"].append("16 мая д.")
# dates["СБ"].append("22 мая д.")
# dates["ВС"].append("23 мая д.")
# dates["ВС"].append("30 мая д.")


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
        archieve_group = dict()
        if action == del_row_menu:
            current_row_index = self.currentRow()
            if self.item(current_row_index, 0) is not None:

                # добавление удалённой записи в архив
                archieve_group.clear()
                filename = "archieve.json"
                try:
                    file = open(filename, 'r')
                    delete_name = self.item(current_row_index, 0).text()
                    archieve_group[delete_name] = main_win.pupil[self.item(current_row_index, 0).text()]
                    data = json.load(open(filename))
                    data.append(main_win.group_name_lbl.text())
                    data.append(archieve_group)
                    with open(filename, "w") as write_file:
                        json.dump(data, write_file, indent=4, ensure_ascii=False)
                    file.close()
                except Exception as EX:
                    print(EX)
                    json_data = []
                    json_data.append(main_win.group_name_lbl.text())
                    json_data.append(archieve_group)
                    with open(filename, 'w') as file:
                        file.write(json.dumps(json_data, indent=4, ensure_ascii=False))

                # удаление из словарая в памяти
                del main_win.pupil[self.item(current_row_index, 0).text()]
                # удаление строки в таблице
                self.removeRow(current_row_index)

                main_win.bottom_row()
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
        self.table = TableWidget()
        # self.table.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.add_table_col_btn = PushButton("Добавить столбец")
        self.achievements_gb = QGroupBox("Достижения")
        self.achievements_gb.setStyleSheet("background-color:#D9BBFF; color: #2B2235")
        self.bonus_ach = LineEdit()
        self.bonus_ach.setFixedWidth(60)
        self.bonus_ach.setAlignment(Qt.AlignCenter)
        self.bonus_ach.setReadOnly(True)
        self.bonus_up_btn = PushButton("▲")
        self.bonus_up_btn.setFixedWidth(60)
        self.bonus_down_btn = PushButton("▼")
        self.bonus_down_btn.setFixedWidth(60)
        self.extra_ach = LineEdit()
        self.extra_ach.setAlignment(Qt.AlignCenter)
        self.extra_ach.setReadOnly(True)
        self.extra_ach.setFixedWidth(60)
        self.extra_up_btn = PushButton("▲")
        self.extra_up_btn.setFixedWidth(60)
        self.extra_down_btn = PushButton("▼")
        self.extra_down_btn.setFixedWidth(60)
        self.reprimands_amount = QLineEdit()
        self.reprimands_amount.setReadOnly(True)
        self.reprimands_amount.setText("0")
        self.reprimands_amount.setAlignment(Qt.AlignCenter)
        self.inc_repr_btn = PushButton("▲")
        self.inc_repr_btn.setFixedWidth(60)
        self.dec_repr_btn = PushButton("▼")
        self.dec_repr_btn.setFixedWidth(60)
        self.save_btn = PushButton("Сохранить")
        self.edit_btn = PushButton("🖊")
        self.note_field = QTextEdit()
        self.groups_list_btn_gb = QGroupBox("Список групп сегодня")
        self.calendar = QCalendarWidget()
        self.calendar.setFont(QFont("Times", 12))

        # словарь вида: ФИ : {дата : [список достижений за занятие]}
        self.pupil = dict()
        # self.resize(1366, 768)
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
                    width:  30%;
                    height: 30%;
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
        # chb_names = [
        #     "😎 Посещение"+" ("+str(visit_price)+")",
        #     "⏰ Пунктуальность"+" ("+str(on_time_price)+")",
        #     "✋ Ответы на вопросы преподавателя"+" ("+str(base_price)+")",
        #     "✅ Выполнение основных заданий"+" ("+str(base_price)+")",
        #     "🤝 Помощь нуждающимся"+" ("+str(base_price)+")",
        #     "🚀 Турбо режим"+" ("+str(turbo_price)+")",
        #     "⭐ Выполнение бонусных заданий"+" ("+str(bonus_price)+")",
        #     "🏠 Выполнение дополнительных заданий"+" ("+str(extra_price)+")"]

        chb_names = [
            "😎 Посещение",
            "⏰ Пунктуальность",
            "✋ Ответы на вопросы преподавателя",
            "✅ Выполнение основных заданий",
            "🤝 Помощь нуждающимся",
            "🚀 Турбо режим",
            "⭐ Выполнение бонусных заданий",
            "🏠 Выполнение дополнительных заданий"]
        for _ in range(len(chb_names)):
            chb = QCheckBox(chb_names[_])
            self.achievement_chb_list.append(chb)

            if _ == len(chb_names) - 2:
                row1 = QHBoxLayout()
                row1.addWidget(self.achievement_chb_list[_])
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
        under_table_layout = QHBoxLayout()
        under_table_layout.addWidget(self.save_btn, stretch=9)
        under_table_layout.addWidget(self.edit_btn, stretch=1)
        table_layout.addLayout(under_table_layout)

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
        main_layout.addLayout(top_layout, stretch=3)
        main_layout.addLayout(bottom_layout, stretch=2)
        self.setLayout(main_layout)

    def prev_group(self):
        i = 0
        for b in self.groups_btn_list:
            if b.isChecked() and i >= 0:
                self.groups_btn_list[i - 1].setChecked(1)
                break
            i += 1
        self.button_click()

    def next_group(self):
        i = 0
        for b in self.groups_btn_list:
            if b.isChecked() and i < len(self.groups_btn_list) - 1:
                self.groups_btn_list[i + 1].setChecked(1)
                break
            i += 1
        self.button_click()

    def reset_flags(self):

        # сокрытие столбца для редактирования с фамаилиями
        global is_table_edit
        if not is_table_edit:
            self.table.setColumnHidden(0, True)

        # сброс чекбоксов
        for chb in self.achievement_chb_list:
            chb.setCheckState(Qt.Unchecked)

        # сброс счетчика бонсуных и доп. заданий
        self.bonus_ach.setText("0")
        self.extra_ach.setText("0")

        # обнуление замечаний
        self.reprimands_amount.setText("0")

        # очистка комментариев
        # self.note_field.clear()

        self.visualisation()

    # выбор дня в календаре
    def choose_day(self):
        self.reset_flags()
        self.note_field.clear()
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
                r_btn.setStyleSheet(
                    'QRadioButton{font: 12pt None;} QRadioButton::indicator { width: 40%; height: 40%;};')
                self.groups_list_layout.addWidget(self.groups_btn_list[i])
            self.groups_btn_list[0].setChecked(1)
            self.groups_list_btn_gb.setLayout(self.groups_list_layout)
            self.button_click()
        except Exception as EX:
            print("Не срабтала функция choose_day", EX)
        else:
            # т.к. кнопки создаются всякий раз при выборе дня, то и клики обрабатывать нужно всегдя по новой
            for self.b in self.groups_btn_list:
                self.b.clicked.connect(self.button_click)
        finally:
            # self.reset_flags()
            pass
    # выбор группы (клик по radiobutton)
    def button_click(self):
        self.reset_flags()
        self.note_field.clear()
        for b in self.groups_btn_list:
            if b.isChecked():
                self.group_name_lbl.setText(b.text())
                self.open_table()
                break

    def pupils_load(self):
        pass
        # group = {None: []}
        # filename = str(self.group_name_lbl.text()) + ".json"
        # with open("data.json", 'r', encoding="utf-8") as file:
        #     group = json.load(file)
        # row = 0
        # for p in group[str(self.group_name_lbl.text())]:
        #     if self.table.item(row, 0) is not None:
        #         return
        #     else:
        #         self.table.setItem(row, 0, QTableWidgetItem(p))
        #     row += 1

    def save_table_to_file(self):
        global is_table_edit
        if is_table_edit:
            # self.pupil.clear() # очистка словаря и его обновление
            t = self.table
            t.setFocus()
            temp_pupil = dict(self.pupil)
            for row in range(t.rowCount()):
                original_name = t.verticalHeaderItem(row).text().split()
                if t.item(row, 0) is not None:
                    try:
                        temp_name = ""
                        for _ in range(2, len(original_name)):
                            temp_name += original_name[_]+" "
                        original_name = temp_name.strip()
                        #if original_name == "":
                            #temp_pupil[t.item(row, 0).text()] = dict()
                    except Exception as EX:
                        # print("Ошибка original_name", EX)
                        self.pupil[t.item(row, 0).text()] = dict()
                    else:
                        if original_name == "" and t.verticalHeaderItem(row).text().isdigit():
                            self.pupil[t.item(row, 0).text()] = dict()
                        elif t.item(row, 0).text() in self.pupil:
                            del temp_pupil[t.item(row, 0).text()]
                        else:
                            chaged_name = t.item(row, 0).text()
                            try:
                                self.pupil[chaged_name] = temp_pupil[original_name]
                                del temp_pupil[original_name]
                                del self.pupil[original_name]
                            except Exception as EX:
                                print("Ошибка при добавлении/редактирвоании человека", EX)
                                return
                #else:
                #    self.pupil[t.item(row, 0).text()] = dict()
            # self.table.setColumnHidden(0, True)
            # t.setCurrentItem(None)
            # is_table_edit = False
        try:
            if len(self.pupil) > 0:
                filename = str(self.group_name_lbl.text()) + ".json"
                with open(filename, 'w') as file:
                    json.dump(self.pupil, file, indent=4, sort_keys=True, ensure_ascii=False)
            self.open_table()
        except Exception as EX:
            print("Ошибка при сохранении файла", EX)

    def open_file(self):
        try:
            self.pupil.clear()
            filename = str(self.group_name_lbl.text()) + ".json"
            file = open(filename, 'r')
        except Exception as EX:
            print(EX)
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
        # при открытии таблицы создается 1 столбец для 10 учеников
        try:
            self.open_file()
            global students_amount
            students_amount = len(self.pupil) + 1
            self.table.clear()
            self.table.setColumnCount(1)
            self.table.setRowCount(students_amount+1)
            self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
            self.table.setVerticalHeaderLabels([str(i + 1) for i in range(students_amount)])
            for _d in dates.keys():
                if self.calendar.selectedDate().shortDayName(
                        self.calendar.selectedDate().dayOfWeek()).lower() == _d.lower():
                    for _i in dates[_d]:
                        self.add_col()
                    break
            group_dates = [str(_) for _ in dates[_d]]
            group_dates.insert(0, "Фамилия Имя")
            group_dates.append("ИТОГО")
            self.add_col()
            self.table.setHorizontalHeaderLabels(group_dates)


        except Exception as EX:
            print("Что-то не так при создании шаблона страницы", EX)
        else:
            try:
                row = 0
                for pup in self.pupil:
                    self.table.setItem(row, 0, QTableWidgetItem(pup))
                    _sum = 0
                    for col in range(1, self.table.columnCount() - 1):
                        if self.table.horizontalHeaderItem(col).text() in self.pupil[pup]:
                            value = self.pupil[pup][str(self.table.horizontalHeaderItem(col).text())][
                                "achievements"]
                            visited = 0
                            base = len(value)
                            tur = 0
                            if "Посещение" in value:
                                base -= 1  # чтобы не дублировалось
                                visited += visit_price
                                if "Пунктуальность" in value:
                                    base -= 1  # чтобы не дублировалось
                                    visited += on_time_price
                            if "Турбо-режим" in value:
                                tur = turbo_price
                            bon = self.pupil[pup][str(self.table.horizontalHeaderItem(col).text())]["bonus"]
                            extr = self.pupil[pup][str(self.table.horizontalHeaderItem(col).text())]["extra"]
                            rep = self.pupil[pup][str(self.table.horizontalHeaderItem(col).text())]["reprimands"]

                            curr_sum = base * base_price + visited + tur + bon * bonus_price + extr * extra_price - rep * 15  # подсчёт суммы астрокойнов из всех данных
                            _sum += curr_sum  # итоговая сумма
                            self.table.setItem(row, col, QTableWidgetItem(str(curr_sum)))
                    self.table.setVerticalHeaderItem(row, QTableWidgetItem(str(_sum) + " - " + pup))
                    self.table.setItem(row, col + 1, QTableWidgetItem(str(_sum)))  # последний столбец для общей суммы
                    row += 1
            except Exception as EX:
                print("Опять что-то не так, но уже при загрузке данных из файла", EX)
            finally:
                self.table.setColumnHidden(0, True)
                # автоскроллинг до столбца с текущей датой
                # !!! ПРОВЕРИТ В НАЧАЛЕ ГОДА!!!!
                self.pupils_load()
        finally:
            global is_table_edit
            for num in range(len(group_dates)):
                if group_dates[num] == self.calendar.selectedDate().toString("dd MMM"):
                    if not is_table_edit:
                        global today_column
                        today_column = num
                        self.table.horizontalScrollBar().setValue(num-6)
                    break
            # global is_table_edit
            # is_table_edit = False
            # self.table.setColumnHidden(0, True)
            # добавление строки с количетством присутствующих
            self.bottom_row()

    def bottom_row(self):
        self.table.setVerticalHeaderItem(students_amount, QTableWidgetItem("Посещаемость"))
        for day_for_visits in range(1, self.table.columnCount()):
            visits = 0
            for p in self.pupil:
                if self.table.horizontalHeaderItem(day_for_visits).text() in self.pupil[p]:
                    if "Посещение" in self.pupil[p][self.table.horizontalHeaderItem(day_for_visits).text()][
                        'achievements']:
                        visits += 1
            self.table.setItem(students_amount, day_for_visits,
                               QTableWidgetItem(str(visits)))  # +'/'+str(len(self.pupil))))

    # заполнение ячейки баллами
    def cell_fill(self):
        t = self.table
        # обработка нажатия на каждый чекбокс
        if t.currentColumn() != 0:
            try:
                points, b, e = 0, 0, 0
                key = t.item(t.currentRow(), 0).text()  # фамилия
                value = t.horizontalHeaderItem(t.currentColumn()).text()  # дата
                _ach_lst = []
                for chb in self.achievement_chb_list:
                    if chb.checkState():
                        if chb.text().find("Посещение") != -1:
                            points += 0.5
                        elif chb.text().find("Пунктуальность") != -1:
                            points += 1.5
                        elif chb.text().find("Турбо-режим") != -1:
                            points += 0.5
                        elif chb.text().find("бонус") != -1:
                            b = int(self.bonus_ach.text()) * bonus_price
                        elif chb.text().find("допол") != -1:
                            e = int(self.extra_ach.text()) * extra_price
                        else:
                            points += 1

                        if chb.text().find("бонус") == -1 and chb.text().find("допол") == -1:
                            _ach_lst.append(chb.text()[2:])

                r = int(self.reprimands_amount.text())
                if key not in self.pupil:
                    self.pupil[key] = {value: {}}

                self.pupil[key][value] = {"achievements": _ach_lst,
                                          "bonus": int(self.bonus_ach.text()),
                                          "extra": int(self.extra_ach.text()),
                                          "reprimands": int(self.reprimands_amount.text()),
                                          "notes": self.note_field.toPlainText()}

                t.setItem(t.currentRow(), t.currentColumn(),
                          QTableWidgetItem(str(int(points * base_price - r * 15 + b + e))))
            except Exception as EX:
                print("Не сработала функция cell_fill", EX)
            finally:
                self.calculate_sum()

    # щелчок по ячейке 
    def cell_select(self):
        self.reset_flags()
        try:
            global is_table_edit
            if not is_table_edit:
                t = self.table
                if t.item(t.currentRow(), t.currentColumn()) is not None:
                    key = t.item(t.currentRow(), 0).text()
                    value = t.horizontalHeaderItem(t.currentColumn()).text()
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
                    self.note_field.clear()
        except Exception as EX:
            print("Не сработала функция cell_select", EX)

    def pupil_fill(self):
        t = self.table
        # main_win.table.setCurrentItem(None)
        if t.currentItem():
            key = t.item(t.currentRow(), 0).text()
            value = t.horizontalHeaderItem(t.currentColumn()).text()
            if value == "Фамилия Имя":
                return
            else:
                for chb in self.achievement_chb_list:
                    if chb.text()[2:] == "Выполнение бонусных заданий" and chb.checkState():
                        self.pupil[key][value]["bonus"] = int(self.bonus_ach.text())
                    if chb.text()[2:] == "Выполнение дополнительных заданий" and chb.checkState():
                        self.pupil[key][value]["extra"] = int(self.extra_ach.text())
                self.pupil[key][value]["reprimands"] = int(self.reprimands_amount.text())
                self.pupil[key][value]["notes"] = self.note_field.toPlainText()

    def inc_repr(self):
        count = int(self.reprimands_amount.text()) + 1
        self.reprimands_amount.setText(str(count))
        self.cell_fill()

    def dec_repr(self):
        count = int(self.reprimands_amount.text())
        if count > 0:
            count -= 1
            self.reprimands_amount.setText(str(count))
        self.cell_fill()

    def bonus_up(self):
        count = int(self.bonus_ach.text()) + 1
        self.bonus_ach.setText(str(count))
        for chb in self.achievement_chb_list:
            if chb.text()[2:] == "Выполнение бонусных заданий" and not chb.checkState():
                chb.setCheckState(Qt.Checked)

        self.calculate_sum()
        self.pupil_fill()
        self.cell_fill()

    def bonus_down(self):
        count = int(self.bonus_ach.text())
        if count > 0:
            count -= 1
            self.bonus_ach.setText(str(count))
        if int(self.bonus_ach.text()) == 0:
            for chb in self.achievement_chb_list:
                if chb.text()[2:] == "Выполнение бонусных заданий" and chb.checkState():
                    chb.setCheckState(Qt.Unchecked)

        self.calculate_sum()
        self.pupil_fill()
        self.cell_fill()

    def extra_up(self):
        count = int(self.extra_ach.text()) + 1
        self.extra_ach.setText(str(count))
        for chb in self.achievement_chb_list:
            if chb.text()[2:] == "Выполнение дополнительных заданий" and not chb.checkState():
                chb.setCheckState(Qt.Checked)

        self.calculate_sum()
        self.pupil_fill()
        self.cell_fill()

    def extra_down(self):
        count = int(self.extra_ach.text())
        if count > 0:
            count -= 1
            self.extra_ach.setText(str(count))
        if int(self.extra_ach.text()) == 0:
            for chb in self.achievement_chb_list:
                if chb.text()[2:] == "Выполнение дополнительных заданий" and chb.checkState():
                    chb.setCheckState(Qt.Unchecked)

        self.calculate_sum()
        self.pupil_fill()
        self.cell_fill()

    def calculate_sum(self):
        t = self.table
        t.setFocus()
        for row in range(t.rowCount()):
            if t.item(row, 0) is not None:
                total_sum = 0
                for col in range(1, t.columnCount() - 1):
                    if t.item(row, col) is not None:
                        total_sum += int(t.item(row, col).text())
                t.setItem(row, col + 1, QTableWidgetItem(str(total_sum)))  # последний столбец для общей суммы
                self.table.setVerticalHeaderItem(row, QTableWidgetItem(str(total_sum)))
                self.table.setVerticalHeaderItem(row, QTableWidgetItem(str(total_sum) + " - " + t.item(row, 0).text()))
            else:
                return

    def SurnameEditing(self):
        # редактирование столбца с фамилиями
        global is_table_edit
        is_table_edit = not is_table_edit
        if is_table_edit:
            self.table.setColumnHidden(0, False)
            self.table.horizontalScrollBar().setValue(0)

        else:
            self.table.setColumnHidden(0, True)
            self.table.horizontalScrollBar().setValue(today_column - 6)

    def test(self):
        pass

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
        self.edit_btn.clicked.connect(self.SurnameEditing)
        self.inc_repr_btn.clicked.connect(self.inc_repr)
        self.dec_repr_btn.clicked.connect(self.dec_repr)
        self.note_field.textChanged.connect(self.pupil_fill)
        self.prev_btn.clicked.connect(self.prev_group)
        self.next_btn.clicked.connect(self.next_group)


def show_json():
    global readme
    os.startfile("groups_list.json")
    with open("README.txt", "w") as f:
        f.write(readme)
    os.startfile("README.txt")
    app.closeAllWindows()


import os

if __name__ == "__main__":
    app = QApplication([])
    main_win = MainWidget()
    if not state:
        modal = QMessageBox(main_win)
        modal.setWindowTitle("РЕДАКТИРУЙТЕ ФАЙЛ В БЛОКНОТЕ")
        modal.setText("Заполните файл groups_list.json\nНажмите ОК, чтобы открыть")
        modal.setStandardButtons(QMessageBox.Ok)
        modal.showNormal()
        modal.buttonClicked.connect(show_json)
    app.exec_()
