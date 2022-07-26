import sqlite3
from PyQt5 import uic
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QTableWidgetItem, QMessageBox
from math import gcd

# Подключение к БД
con = sqlite3.connect('Менделеев_перевернулся_в_гробу_когда_увидел_что_сделали_с_его_таблицей.db')
# Создание курсора
cur = con.cursor()


class History(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("history.ui", self)
        self.con = sqlite3.connect("Менделеев_перевернулся_в_гробу_когда_увидел_что_сделали_с_его_таблицей.db")
        self.modified = {}
        self.titles = None
        cur = self.con.cursor()
        result = cur.execute("SELECT * FROM equations""").fetchall()
        self.tableWidget.setRowCount(len(result))
        self.titles = [description[0] for description in cur.description]
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
        self.modified = {}


def coefficients(result, coefficients_of_elements):
    e = 0
    for substance in result:
        e += 1
        if substance == 'H2O':
            coefficients_of_elements['H'] = (1, e)
            coefficients_of_elements['OH'] = (1, e)
        else:
            if substance[1].isalpha():
                if substance[1].islower():
                    coefficients_of_elements[substance[0:2]] = (1, e)
                    if substance[2].isdigit():
                        coefficients_of_elements[substance[0:2]] = (int(substance[2]), e)
                        if substance[3] == '(':
                            coefficients_of_elements[substance[4:-2]] = (int(substance[-1]), e)
                        else:
                            if len([i for i in substance[3:] if i.isalpha() and i.isupper()]) == 2:
                                coefficients_of_elements[substance[3:]] = (1, e)
                            elif len([i for i in substance[3:] if i.isalpha() and i.isupper()]) == 1:
                                if substance[-1].isdigit():
                                    coefficients_of_elements[substance[3:-1]] = (int(substance[-1]), e)
                                else:
                                    coefficients_of_elements[substance[3:]] = (1, e)
                    elif substance[2] == '(':
                        coefficients_of_elements[substance[3:-2]] = (int(substance[-1]), e)
                    else:
                        if len([i for i in substance[2:] if i.isalpha() and i.isupper()]) == 2:
                            coefficients_of_elements[substance[2:]] = (1, e)
                        elif len([i for i in substance[2:] if i.isalpha() and i.isupper()]) == 1:
                            if substance[-1].isdigit():
                                coefficients_of_elements[substance[2:-1]] = (int(substance[-1]), e)
                            else:
                                coefficients_of_elements[substance[2:]] = (1, e)
                else:
                    if len([i for i in substance[1:] if i.isalpha() and i.isupper()]) == 2:
                        coefficients_of_elements[substance[1:]] = (1, e)
                    elif len([i for i in substance[1:] if i.isalpha() and i.isupper()]) == 1:
                        if substance[-1].isdigit():
                            coefficients_of_elements[substance[1:-1]] = (int(substance[-1]), e)
                        else:
                            coefficients_of_elements[substance[1:]] = (1, e)
            else:
                coefficients_of_elements[substance[0]] = (1, e)
                if substance[1].isdigit():
                    coefficients_of_elements[substance[0]] = (int(substance[1]), e)
                    if substance[2] == '(':
                        coefficients_of_elements[substance[3:-2]] = (int(substance[-1]), e)
                    else:
                        if len([i for i in substance[2:] if i.isalpha() and i.isupper()]) == 2:
                            coefficients_of_elements[substance[2:]] = (1, e)
                        elif len([i for i in substance[2:] if i.isalpha() and i.isupper()]) == 1:
                            if substance[-1].isdigit():
                                coefficients_of_elements[substance[2:-1]] = (int(substance[-1]), e)
                            else:
                                coefficients_of_elements[substance[2:]] = (1, e)
                elif substance[1] == '(':
                    coefficients_of_elements[2:-2] = (int(substance[-1]), e)


class Equation(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('equation.ui', self)  # Загружаем дизайн
        self.result_button.clicked.connect(self.equation)
        self.con = con
        self.history.clicked.connect(self.show_history)
        self.list_of_examples = []
        self.back_to.clicked.connect(self.exit)

    def exit(self):
        self.close()

    def closeEvent(self, a0):
        a0 = QMessageBox.question(self, 'История', "Стереть историю?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if a0 == QMessageBox.Yes:
            for id in self.list_of_examples:
                id = id[0]
                cur.execute("""DELETE from equations
                where id = ?""", (id,))
                con.commit()

    def open_new_window_form(self):
        self.new_window = History()
        self.new_window.show()

    def show_history(self):
        self.open_new_window_form()

    def equation(self):
        try:
            self.error_label.setText('')
            id = cur.execute("""select id from equations""").fetchall()
            if id:
                id = id[-1][0]
            else:
                id = 0
            coefficients_of_elements_in_first_string = {}
            if not (self.notresult.text() and self.result.text()):
                raise Exception
            self.list_of_examples.append([id + 1, self.notresult.text() + ' --> ' + self.result.text()])
            notresult = self.notresult.text().strip().split(' + ')
            coefficients(notresult, coefficients_of_elements_in_first_string)
            result = self.result.text().strip().split(' + ')
            coefficients_of_elements_in_second_string = {}
            coefficients(result, coefficients_of_elements_in_second_string)
            all_missed_coefficients = {}
            for i in coefficients_of_elements_in_second_string:  # получение нужных коэффициентов
                if coefficients_of_elements_in_first_string[i][0] != coefficients_of_elements_in_second_string[i][0]:
                    min_coefficient = min(coefficients_of_elements_in_first_string[i][0],
                                          coefficients_of_elements_in_second_string[i][0])
                    max_coefficient = max(coefficients_of_elements_in_first_string[i][0],
                                          coefficients_of_elements_in_second_string[i][0])
                    for e in range(20):
                        if min_coefficient * e == max_coefficient:
                            all_missed_coefficients[i] = (e, 1 if min_coefficient ==
                                                                  coefficients_of_elements_in_first_string[i][0] else 2)
                            break
                    else:
                        if gcd(min_coefficient, max_coefficient):
                            all_missed_coefficients[i] = (
                                max_coefficient,
                                1 if min_coefficient == coefficients_of_elements_in_first_string[i][0] else 2,
                                min_coefficient,
                                1 if max_coefficient == coefficients_of_elements_in_first_string[i][0] else 2)
            for i in all_missed_coefficients:
                values = list(all_missed_coefficients[i])
                if len(values) > 2:
                    if values[1] == 1:
                        for e in [i for i in coefficients_of_elements_in_first_string if i in all_missed_coefficients]:
                            if e != i:
                                if len(all_missed_coefficients[e]) == 2:
                                    if coefficients_of_elements_in_first_string[e][1] == \
                                            coefficients_of_elements_in_first_string[i][1]:
                                        if values[0] == all_missed_coefficients[e][0]:
                                            if notresult[coefficients_of_elements_in_first_string
                                                         [e][1] - 1][0].isalpha():
                                                notresult[coefficients_of_elements_in_first_string
                                                          [e][1] - 1] = "{0}{1}".format(
                                                    str(values[0]), notresult[
                                                        coefficients_of_elements_in_first_string[
                                                            e][1] - 1])
                                            break
                                        else:
                                            min_coefficient = min(coefficients_of_elements_in_first_string[i][0],
                                                                  coefficients_of_elements_in_second_string[i][0])
                                            max_coefficient = max(coefficients_of_elements_in_first_string[i][0],
                                                                  coefficients_of_elements_in_second_string[i][0])
                                            for g in range(20):
                                                if min_coefficient * g == max_coefficient:
                                                    values[0] = g
                                                    if notresult[coefficients_of_elements_in_first_string
                                                                 [e][1] - 1][0].isalpha():
                                                        notresult[coefficients_of_elements_in_first_string[e][
                                                                      1] - 1] = "{0}{1}".format(
                                                            str(values[0]), notresult[
                                                                coefficients_of_elements_in_first_string[
                                                                    e][
                                                                    1] - 1])
                                                    break
                                            else:
                                                if gcd(min_coefficient, max_coefficient):
                                                    values[0] = min_coefficient * max_coefficient
                                                    if notresult[coefficients_of_elements_in_first_string
                                                                 [e][1] - 1][0].isalpha():
                                                        notresult[coefficients_of_elements_in_first_string[e][1] - 1] \
                                                            = "{0}{1}".format(str(values[0]), notresult[
                                                            coefficients_of_elements_in_first_string[e][1] - 1])
                                            break
                                else:
                                    value_e = list(all_missed_coefficients[e])
                                    if coefficients_of_elements_in_first_string[e][1] == \
                                            coefficients_of_elements_in_first_string[i][1]:
                                        if values[1] == value_e[1]:
                                            if values[0] == all_missed_coefficients[e][0]:
                                                if notresult[coefficients_of_elements_in_first_string
                                                             [e][1] - 1][0].isalpha():
                                                    notresult[coefficients_of_elements_in_first_string[e][
                                                                  1] - 1] = "{0}{1}".format(
                                                        str(values[0]), notresult[
                                                            coefficients_of_elements_in_first_string[
                                                                e][1] - 1])
                                                break
                                            else:
                                                min_coefficient = min(coefficients_of_elements_in_first_string[i][0],
                                                                      coefficients_of_elements_in_second_string[i][0])
                                                max_coefficient = max(coefficients_of_elements_in_first_string[i][0],
                                                                      coefficients_of_elements_in_second_string[i][0])
                                                for g in range(20):
                                                    if min_coefficient * g == max_coefficient:
                                                        values[0] = g
                                                        if \
                                                                notresult[
                                                                    coefficients_of_elements_in_first_string[e][1] - 1][
                                                                    0].isalpha():
                                                            notresult[coefficients_of_elements_in_first_string[e][
                                                                          1] - 1] = "{0}{1}".format(
                                                                str(values[0]),
                                                                notresult[coefficients_of_elements_in_first_string[
                                                                              e][1] - 1])
                                                        break
                                                else:
                                                    if gcd(min_coefficient, max_coefficient):
                                                        notresult[coefficients_of_elements_in_first_string[e][1] - 1] \
                                                            = "{0}{1}".format(str(values[0]), notresult[
                                                            coefficients_of_elements_in_first_string[e][1] - 1])
                                                        values[0] = min_coefficient * max_coefficient
                                                break
                                        elif values[1] == value_e[3]:
                                            if values[0] == value_e[2]:
                                                if notresult[coefficients_of_elements_in_first_string[e][1] - 1][
                                                    0].isalpha():
                                                    notresult[coefficients_of_elements_in_first_string[e][
                                                                  1] - 1] = "{0}{1}".format(
                                                        str(values[0]),
                                                        notresult[coefficients_of_elements_in_first_string[
                                                                      e][1] - 1])
                                                break
                                            else:
                                                min_coefficient = min(coefficients_of_elements_in_first_string[i][0],
                                                                      coefficients_of_elements_in_second_string[i][0])
                                                max_coefficient = max(coefficients_of_elements_in_first_string[i][0],
                                                                      coefficients_of_elements_in_second_string[i][0])
                                                for g in range(20):
                                                    if min_coefficient * g == max_coefficient:
                                                        values[0] = g
                                                        notresult[coefficients_of_elements_in_first_string[e][1] - 1] \
                                                            = str(values[0]) + notresult[
                                                            coefficients_of_elements_in_first_string[e][1] - 1]
                                                        break
                                                else:
                                                    if gcd(min_coefficient, max_coefficient):
                                                        values[0] = min_coefficient * max_coefficient
                                                        notresult[coefficients_of_elements_in_first_string[e][1] - 1] \
                                                            = str(values[0]) + notresult[
                                                            coefficients_of_elements_in_first_string[e][1] - 1]
                                                break
                            else:
                                notresult[coefficients_of_elements_in_first_string[i][1] - 1] \
                                    = str(values[0]) + notresult[
                                    coefficients_of_elements_in_first_string[i][1] - 1]

                    if values[1] == 2:
                        for e in [i for i in coefficients_of_elements_in_second_string if i in all_missed_coefficients]:
                            if e != i:
                                if len(all_missed_coefficients[e]) == 2:
                                    if coefficients_of_elements_in_second_string[e][1] == \
                                            coefficients_of_elements_in_second_string[i][1]:
                                        if values[0] == all_missed_coefficients[e][0]:
                                            if result[coefficients_of_elements_in_second_string[e][1] - 1][0].isalpha():
                                                result[coefficients_of_elements_in_second_string[e][
                                                           1] - 1] = "{0}{1}".format(
                                                    str(values[0]), result[
                                                        coefficients_of_elements_in_second_string[
                                                            e][1] - 1])
                                            break
                                        else:
                                            min_coefficient = min(coefficients_of_elements_in_first_string[i][0],
                                                                  coefficients_of_elements_in_second_string[i][0])
                                            max_coefficient = max(coefficients_of_elements_in_first_string[i][0],
                                                                  coefficients_of_elements_in_second_string[i][0])
                                            for g in range(20):
                                                if min_coefficient * g == max_coefficient:
                                                    values[0] = g
                                                    if result[coefficients_of_elements_in_second_string[e][1] - 1][
                                                        0].isalpha():
                                                        result[
                                                            coefficients_of_elements_in_second_string[e][
                                                                1] - 1] = "{0}{1}".format(
                                                            str(values[0]), result[
                                                                coefficients_of_elements_in_second_string[
                                                                    e][1] - 1])
                                                    break
                                            else:
                                                if gcd(min_coefficient, max_coefficient):
                                                    values[0] = min_coefficient * max_coefficient
                                                    if result[coefficients_of_elements_in_second_string[e][1] - 1][
                                                        0].isalpha():
                                                        result[
                                                            coefficients_of_elements_in_second_string[e][
                                                                1] - 1] = "{0}{1}".format(
                                                            str(values[0]), result[
                                                                coefficients_of_elements_in_second_string[
                                                                    e][1] - 1])
                                            break
                                else:
                                    value_e = list(all_missed_coefficients[e])
                                    if coefficients_of_elements_in_second_string[e][1] == \
                                            coefficients_of_elements_in_second_string[i][1]:
                                        if values[1] == value_e[1]:
                                            if values[0] == all_missed_coefficients[e][0]:
                                                if result[coefficients_of_elements_in_second_string[e][1] - 1][
                                                    0].isalpha():
                                                    result[coefficients_of_elements_in_second_string[e][
                                                               1] - 1] = "{0}{1}".format(
                                                        str(values[0]), result[
                                                            coefficients_of_elements_in_second_string[
                                                                e][1] - 1])
                                                break
                                            else:
                                                min_coefficient = min(coefficients_of_elements_in_second_string[i][0],
                                                                      coefficients_of_elements_in_second_string[i][0])
                                                max_coefficient = max(coefficients_of_elements_in_second_string[i][0],
                                                                      coefficients_of_elements_in_second_string[i][0])
                                                for g in range(20):
                                                    if min_coefficient * g == max_coefficient:
                                                        values[0] = g
                                                        if result[coefficients_of_elements_in_second_string[e][1] - 1][
                                                            0].isalpha():
                                                            result[coefficients_of_elements_in_second_string[e][
                                                                       1] - 1] = "{0}{1}".format(
                                                                str(values[0]), result[
                                                                    coefficients_of_elements_in_second_string[
                                                                        e][1] - 1])
                                                        break
                                                else:
                                                    if gcd(min_coefficient, max_coefficient):
                                                        values[0] = min_coefficient * max_coefficient
                                                        if result[coefficients_of_elements_in_second_string[e][1] - 1][
                                                            0].isalpha():
                                                            result[coefficients_of_elements_in_second_string[e][
                                                                       1] - 1] = "{0}{1}".format(
                                                                str(values[0]), result[
                                                                    coefficients_of_elements_in_second_string[
                                                                        e][1] - 1])
                                                break
                                        elif values[1] == value_e[3]:
                                            if values[0] == value_e[2]:
                                                if result[coefficients_of_elements_in_second_string[e][1] - 1][
                                                    0].isalpha():
                                                    result[coefficients_of_elements_in_second_string[e][
                                                               1] - 1] = "{0}{1}".format(
                                                        str(values[0]), result[
                                                            coefficients_of_elements_in_second_string[
                                                                e][1] - 1])
                                                break
                                            else:
                                                min_coefficient = min(coefficients_of_elements_in_second_string[i][0],
                                                                      coefficients_of_elements_in_second_string[i][0])
                                                max_coefficient = max(coefficients_of_elements_in_first_string[i][0],
                                                                      coefficients_of_elements_in_second_string[i][0])
                                                for g in range(20):
                                                    if min_coefficient * g == max_coefficient:
                                                        values[0] = g
                                                        if result[coefficients_of_elements_in_second_string[e][1] - 1][
                                                            0].isalpha():
                                                            result[coefficients_of_elements_in_second_string[e][
                                                                       1] - 1] = "{0}{1}".format(
                                                                str(values[0]), result[
                                                                    coefficients_of_elements_in_second_string[
                                                                        e][1] - 1])
                                                        break
                                                else:
                                                    if gcd(min_coefficient, max_coefficient):
                                                        values[0] = min_coefficient * max_coefficient
                                                        if result[coefficients_of_elements_in_second_string[e][1] - 1][
                                                            0].isalpha():
                                                            result[coefficients_of_elements_in_second_string[e][
                                                                       1] - 1] = "{0}{1}".format(
                                                                str(values[0]), result[
                                                                    coefficients_of_elements_in_second_string[
                                                                        e][1] - 1])
                                                break
                            else:
                                if result[coefficients_of_elements_in_second_string[i][1] - 1][0].isalpha():
                                    result[coefficients_of_elements_in_second_string[i][1] - 1] = "{0}{1}".format(
                                        str(values[0]), result[
                                            coefficients_of_elements_in_second_string[
                                                i][1] - 1])
                    if values[3] == 1:
                        for e in [i for i in coefficients_of_elements_in_first_string if i in all_missed_coefficients]:
                            if e != i:
                                if len(all_missed_coefficients[e]) == 2:
                                    if coefficients_of_elements_in_first_string[e][1] == \
                                            coefficients_of_elements_in_first_string[i][1]:
                                        if values[0] == all_missed_coefficients[e][0]:
                                            if notresult[coefficients_of_elements_in_first_string[e][1] - 1][
                                                0].isalpha():
                                                notresult[coefficients_of_elements_in_first_string[e][
                                                              1] - 1] = "{0}{1}".format(
                                                    str(values[0]), notresult[
                                                        coefficients_of_elements_in_first_string[
                                                            e][1] - 1])
                                            break
                                        else:
                                            min_coefficient = min(coefficients_of_elements_in_first_string[i][0],
                                                                  coefficients_of_elements_in_second_string[i][0])
                                            max_coefficient = max(coefficients_of_elements_in_first_string[i][0],
                                                                  coefficients_of_elements_in_second_string[i][0])
                                            for g in range(20):
                                                if min_coefficient * g == max_coefficient:
                                                    values[0] = g
                                                    if notresult[coefficients_of_elements_in_first_string[e][1] - 1][
                                                        0].isalpha():
                                                        notresult[
                                                            coefficients_of_elements_in_first_string[e][
                                                                1] - 1] = "{0}{1}".format(
                                                            str(values[0]), notresult[
                                                                coefficients_of_elements_in_first_string[
                                                                    e][1] - 1])
                                                    break
                                            else:
                                                if gcd(min_coefficient, max_coefficient):
                                                    values[0] = min_coefficient * max_coefficient
                                                    if notresult[coefficients_of_elements_in_first_string[e][1] - 1][
                                                        0].isalpha():
                                                        notresult[
                                                            coefficients_of_elements_in_first_string[e][
                                                                1] - 1] = "{0}{1}".format(
                                                            str(values[0]), notresult[
                                                                coefficients_of_elements_in_first_string[
                                                                    e][1] - 1])
                                            break
                                else:
                                    value_e = list(all_missed_coefficients[e])
                                    if coefficients_of_elements_in_first_string[e][1] == \
                                            coefficients_of_elements_in_first_string[i][1]:
                                        if values[1] == value_e[1]:
                                            if values[0] == all_missed_coefficients[e][0]:
                                                if notresult[coefficients_of_elements_in_first_string[e][1] - 1][
                                                    0].isalpha():
                                                    notresult[coefficients_of_elements_in_first_string[e][
                                                                  1] - 1] = "{0}{1}".format(
                                                        str(values[0]),
                                                        notresult[coefficients_of_elements_in_first_string[
                                                                      e][1] - 1])
                                                break
                                            else:
                                                min_coefficient = min(coefficients_of_elements_in_first_string[i][0],
                                                                      coefficients_of_elements_in_second_string[i][0])
                                                max_coefficient = max(coefficients_of_elements_in_first_string[i][0],
                                                                      coefficients_of_elements_in_second_string[i][0])
                                                for g in range(20):
                                                    if min_coefficient * g == max_coefficient:
                                                        values[0] = g
                                                        if \
                                                                notresult[
                                                                    coefficients_of_elements_in_first_string[e][1] - 1][
                                                                    0].isalpha():
                                                            notresult[coefficients_of_elements_in_first_string[e][
                                                                          1] - 1] = "{0}{1}".format(
                                                                str(values[0]), notresult[
                                                                    coefficients_of_elements_in_first_string[
                                                                        e][1] - 1])
                                                        break
                                                else:
                                                    if gcd(min_coefficient, max_coefficient):
                                                        values[0] = min_coefficient * max_coefficient
                                                        if \
                                                                notresult[
                                                                    coefficients_of_elements_in_first_string[e][1] - 1][
                                                                    0].isalpha():
                                                            notresult[coefficients_of_elements_in_first_string[e][
                                                                          1] - 1] = "{0}{1}".format(
                                                                str(values[0]), notresult[
                                                                    coefficients_of_elements_in_first_string[
                                                                        e][1] - 1])
                                                break
                                        elif values[1] == value_e[3]:
                                            if values[0] == value_e[2]:
                                                if notresult[coefficients_of_elements_in_first_string[e][1] - 1][
                                                    0].isalpha():
                                                    notresult[coefficients_of_elements_in_first_string[e][
                                                                  1] - 1] = "{0}{1}".format(
                                                        str(values[0]), notresult[
                                                            coefficients_of_elements_in_first_string[
                                                                e][1] - 1])
                                                break
                                            else:
                                                min_coefficient = min(coefficients_of_elements_in_first_string[i][0],
                                                                      coefficients_of_elements_in_second_string[i][0])
                                                max_coefficient = max(coefficients_of_elements_in_first_string[i][0],
                                                                      coefficients_of_elements_in_second_string[i][0])
                                                for g in range(20):
                                                    if min_coefficient * g == max_coefficient:
                                                        values[0] = g
                                                        if \
                                                                notresult[
                                                                    coefficients_of_elements_in_first_string[e][1] - 1][
                                                                    0].isalpha():
                                                            notresult[coefficients_of_elements_in_first_string[e][
                                                                          1] - 1] = "{0}{1}".format(
                                                                str(values[0]), notresult[
                                                                    coefficients_of_elements_in_first_string[
                                                                        e][1] - 1])
                                                        break
                                                else:
                                                    if gcd(min_coefficient, max_coefficient):
                                                        values[0] = min_coefficient * max_coefficient
                                                        if \
                                                                notresult[
                                                                    coefficients_of_elements_in_first_string[e][1] - 1][
                                                                    0].isalpha():
                                                            notresult[coefficients_of_elements_in_first_string[e][
                                                                          1] - 1] = "{0}{1}".format(
                                                                str(values[0]), notresult[
                                                                    coefficients_of_elements_in_first_string[
                                                                        e][1] - 1])
                                                break
                            else:
                                if notresult[coefficients_of_elements_in_first_string[i][1] - 1][0].isalpha():
                                    notresult[coefficients_of_elements_in_first_string[i][1] - 1] = "{0}{1}".format(
                                        str(values[0]), notresult[
                                            coefficients_of_elements_in_first_string[
                                                i][1] - 1])

                    if values[3] == 2:
                        for e in [i for i in coefficients_of_elements_in_second_string if i in all_missed_coefficients]:
                            if e != i:
                                if len(all_missed_coefficients[e]) == 2:
                                    if coefficients_of_elements_in_second_string[e][1] == \
                                            coefficients_of_elements_in_second_string[i][1]:
                                        if values[2] == all_missed_coefficients[e][0]:
                                            if result[coefficients_of_elements_in_second_string[e][1] - 1][0].isalpha():
                                                result[coefficients_of_elements_in_second_string[e][
                                                           1] - 1] = "{0}{1}".format(
                                                    str(values[0]), result[
                                                        coefficients_of_elements_in_second_string[
                                                            e][1] - 1])
                                            break
                                        else:
                                            min_coefficient = min(coefficients_of_elements_in_first_string[i][0],
                                                                  coefficients_of_elements_in_second_string[i][0])
                                            max_coefficient = max(coefficients_of_elements_in_first_string[i][0],
                                                                  coefficients_of_elements_in_second_string[i][0])
                                            for g in range(20):
                                                if min_coefficient * g == max_coefficient:
                                                    values[2] = g
                                                    if result[coefficients_of_elements_in_second_string[e][1] - 1][
                                                        0].isalpha():
                                                        result[
                                                            coefficients_of_elements_in_second_string[e][
                                                                1] - 1] = "{0}{1}".format(
                                                            str(values[0]), result[
                                                                coefficients_of_elements_in_second_string[
                                                                    e][1] - 1])
                                                    break
                                            else:
                                                if gcd(min_coefficient, max_coefficient):
                                                    values[2] = min_coefficient * max_coefficient
                                                    if result[coefficients_of_elements_in_second_string[e][1] - 1][
                                                        0].isalpha():
                                                        result[
                                                            coefficients_of_elements_in_second_string[e][
                                                                1] - 1] = "{0}{1}".format(
                                                            str(values[0]), result[
                                                                coefficients_of_elements_in_second_string[
                                                                    e][1] - 1])
                                            break
                                else:
                                    value_e = list(all_missed_coefficients[e])
                                    if coefficients_of_elements_in_second_string[e][1] == \
                                            coefficients_of_elements_in_second_string[i][1]:
                                        if values[1] == value_e[1]:
                                            if values[2] == all_missed_coefficients[e][0]:
                                                if result[coefficients_of_elements_in_second_string[e][1] - 1][
                                                    0].isalpha():
                                                    result[coefficients_of_elements_in_second_string[e][
                                                               1] - 1] = "{0}{1}".format(
                                                        str(values[0]), result[
                                                            coefficients_of_elements_in_second_string[
                                                                e][1] - 1])
                                                break
                                            else:
                                                min_coefficient = min(coefficients_of_elements_in_second_string[i][0],
                                                                      coefficients_of_elements_in_second_string[i][0])
                                                max_coefficient = max(coefficients_of_elements_in_second_string[i][0],
                                                                      coefficients_of_elements_in_second_string[i][0])
                                                for g in range(20):
                                                    if min_coefficient * g == max_coefficient:
                                                        values[2] = g
                                                        if result[coefficients_of_elements_in_second_string[e][1] - 1][
                                                            0].isalpha():
                                                            result[coefficients_of_elements_in_second_string[e][
                                                                       1] - 1] = "{0}{1}".format(
                                                                str(values[0]), result[
                                                                    coefficients_of_elements_in_second_string[
                                                                        e][1] - 1])
                                                        break
                                                else:
                                                    if gcd(min_coefficient, max_coefficient):
                                                        values[2] = min_coefficient * max_coefficient
                                                        if result[coefficients_of_elements_in_second_string[e][1] - 1][
                                                            0].isalpha():
                                                            result[coefficients_of_elements_in_second_string[e][
                                                                       1] - 1] = "{0}{1}".format(
                                                                str(values[0]), result[
                                                                    coefficients_of_elements_in_second_string[
                                                                        e][1] - 1])
                                                break
                                        elif values[1] == value_e[3]:
                                            if values[2] == value_e[2]:
                                                if result[coefficients_of_elements_in_second_string[e][1] - 1][
                                                    0].isalpha():
                                                    result[coefficients_of_elements_in_second_string[e][
                                                               1] - 1] = "{0}{1}".format(
                                                        str(values[0]), result[
                                                            coefficients_of_elements_in_second_string[
                                                                e][1] - 1])
                                                break
                                            else:
                                                min_coefficient = min(coefficients_of_elements_in_second_string[i][0],
                                                                      coefficients_of_elements_in_second_string[i][0])
                                                max_coefficient = max(coefficients_of_elements_in_first_string[i][0],
                                                                      coefficients_of_elements_in_second_string[i][0])
                                                for g in range(20):
                                                    if min_coefficient * g == max_coefficient:
                                                        values[2] = g
                                                        if result[coefficients_of_elements_in_second_string[e][1] - 1][
                                                            0].isalpha():
                                                            result[coefficients_of_elements_in_second_string[e][
                                                                       1] - 1] = "{0}{1}".format(
                                                                str(values[0]), result[
                                                                    coefficients_of_elements_in_second_string[
                                                                        e][1] - 1])
                                                        break
                                                else:
                                                    if gcd(min_coefficient, max_coefficient):
                                                        values[2] = min_coefficient * max_coefficient
                                                        if result[coefficients_of_elements_in_second_string[e][1] - 1][
                                                            0].isalpha():
                                                            result[coefficients_of_elements_in_second_string[e][
                                                                       1] - 1] = "{0}{1}".format(
                                                                str(values[0]), result[
                                                                    coefficients_of_elements_in_second_string[
                                                                        e][1] - 1])
                                                break
                            else:
                                if result[coefficients_of_elements_in_second_string[i][1] - 1][0].isalpha():
                                    result[coefficients_of_elements_in_second_string[i][1] - 1] = "{0}{1}".format(
                                        str(values[0]), result[
                                            coefficients_of_elements_in_second_string[
                                                i][1] - 1])
                else:
                    if values[1] == 1:
                        for e in [i for i in coefficients_of_elements_in_first_string if i in all_missed_coefficients]:
                            if e != i:
                                if len(all_missed_coefficients[e]) == 2:
                                    if coefficients_of_elements_in_first_string[e][1] == \
                                            coefficients_of_elements_in_first_string[i][1]:
                                        if values[0] == all_missed_coefficients[e][0]:
                                            if notresult[coefficients_of_elements_in_first_string[e][1] - 1][
                                                0].isalpha():
                                                notresult[coefficients_of_elements_in_first_string[e][
                                                              1] - 1] = "{0}{1}".format(
                                                    str(values[0]), notresult[
                                                        coefficients_of_elements_in_first_string[
                                                            e][1] - 1])
                                            break
                                        else:
                                            min_coefficient = min(coefficients_of_elements_in_first_string[i][0],
                                                                  coefficients_of_elements_in_second_string[i][0])
                                            max_coefficient = max(coefficients_of_elements_in_first_string[i][0],
                                                                  coefficients_of_elements_in_second_string[i][0])
                                            for g in range(20):
                                                if min_coefficient * g == max_coefficient:
                                                    values[0] = g
                                                    if notresult[coefficients_of_elements_in_first_string[e][1] - 1][
                                                        0].isalpha():
                                                        notresult[
                                                            coefficients_of_elements_in_first_string[e][
                                                                1] - 1] = "{0}{1}".format(
                                                            str(values[0]), notresult[
                                                                coefficients_of_elements_in_first_string[
                                                                    e][1] - 1])
                                                    break
                                            else:
                                                if gcd(min_coefficient, max_coefficient):
                                                    values[0] = min_coefficient * max_coefficient
                                                    if notresult[coefficients_of_elements_in_first_string[e][1] - 1][
                                                        0].isalpha():
                                                        notresult[
                                                            coefficients_of_elements_in_first_string[e][
                                                                1] - 1] = "{0}{1}".format(
                                                            str(values[0]), notresult[
                                                                coefficients_of_elements_in_first_string[
                                                                    e][1] - 1])
                                            break
                                else:
                                    value_e = list(all_missed_coefficients[e])
                                    if coefficients_of_elements_in_first_string[e][1] == \
                                            coefficients_of_elements_in_first_string[i][1]:
                                        if values[1] == value_e[1]:
                                            if values[0] == all_missed_coefficients[e][0]:
                                                if notresult[coefficients_of_elements_in_first_string[e][1] - 1][
                                                    0].isalpha():
                                                    notresult[coefficients_of_elements_in_first_string[e][
                                                                  1] - 1] = "{0}{1}".format(
                                                        str(values[0]), notresult[
                                                            coefficients_of_elements_in_first_string[
                                                                e][1] - 1])
                                                break
                                            else:
                                                min_coefficient = min(coefficients_of_elements_in_first_string[i][0],
                                                                      coefficients_of_elements_in_second_string[i][0])
                                                max_coefficient = max(coefficients_of_elements_in_first_string[i][0],
                                                                      coefficients_of_elements_in_second_string[i][0])
                                                for g in range(20):
                                                    if min_coefficient * g == max_coefficient:
                                                        values[0] = g
                                                        if \
                                                                notresult[
                                                                    coefficients_of_elements_in_first_string[e][1] - 1][
                                                                    0].isalpha():
                                                            notresult[coefficients_of_elements_in_first_string[e][
                                                                          1] - 1] = "{0}{1}".format(
                                                                str(values[0]), notresult[
                                                                    coefficients_of_elements_in_first_string[
                                                                        e][1] - 1])
                                                        break
                                                else:
                                                    if gcd(min_coefficient, max_coefficient):
                                                        values[0] = min_coefficient * max_coefficient
                                                        if \
                                                                notresult[
                                                                    coefficients_of_elements_in_first_string[e][1] - 1][
                                                                    0].isalpha():
                                                            notresult[coefficients_of_elements_in_first_string[e][
                                                                          1] - 1] = "{0}{1}".format(
                                                                str(values[0]), notresult[
                                                                    coefficients_of_elements_in_first_string[
                                                                        e][1] - 1])
                                                break
                                        elif values[1] == value_e[3]:
                                            if values[0] == value_e[2]:
                                                if notresult[coefficients_of_elements_in_first_string[e][1] - 1][
                                                    0].isalpha():
                                                    notresult[coefficients_of_elements_in_first_string[e][
                                                                  1] - 1] = "{0}{1}".format(
                                                        str(values[0]), notresult[
                                                            coefficients_of_elements_in_first_string[
                                                                e][1] - 1])
                                                break
                                            else:
                                                min_coefficient = min(coefficients_of_elements_in_first_string[i][0],
                                                                      coefficients_of_elements_in_second_string[i][0])
                                                max_coefficient = max(coefficients_of_elements_in_first_string[i][0],
                                                                      coefficients_of_elements_in_second_string[i][0])
                                                for g in range(20):
                                                    if min_coefficient * g == max_coefficient:
                                                        values[0] = g
                                                        if \
                                                                notresult[
                                                                    coefficients_of_elements_in_first_string[e][1] - 1][
                                                                    0].isalpha():
                                                            notresult[coefficients_of_elements_in_first_string[e][
                                                                          1] - 1] = "{0}{1}".format(
                                                                str(values[0]), notresult[
                                                                    coefficients_of_elements_in_first_string[
                                                                        e][1] - 1])
                                                        break
                                                else:
                                                    if gcd(min_coefficient, max_coefficient):
                                                        values[0] = min_coefficient * max_coefficient
                                                        if \
                                                                notresult[
                                                                    coefficients_of_elements_in_first_string[e][1] - 1][
                                                                    0].isalpha():
                                                            notresult[coefficients_of_elements_in_first_string[e][
                                                                          1] - 1] = "{0}{1}".format(
                                                                str(values[0]), notresult[
                                                                    coefficients_of_elements_in_first_string[
                                                                        e][1] - 1])
                                                break
                        else:
                            if notresult[coefficients_of_elements_in_first_string[i][1] - 1][0].isalpha():
                                notresult[coefficients_of_elements_in_first_string[i][1] - 1] = "{0}{1}".format(
                                    str(values[0]), notresult[
                                        coefficients_of_elements_in_first_string[
                                            i][1] - 1])
                    if values[1] == 2:
                        for e in [i for i in coefficients_of_elements_in_second_string if i in all_missed_coefficients]:
                            if e != i:
                                if len(all_missed_coefficients[e]) == 2:
                                    if coefficients_of_elements_in_second_string[e][1] == \
                                            coefficients_of_elements_in_second_string[i][1]:
                                        if values[0] == all_missed_coefficients[e][0]:
                                            if result[coefficients_of_elements_in_second_string[e][1] - 1][0].isalpha():
                                                result[coefficients_of_elements_in_second_string[e][
                                                           1] - 1] = "{0}{1}".format(
                                                    str(values[0]), result[
                                                        coefficients_of_elements_in_second_string[
                                                            e][1] - 1])
                                            break
                                        else:
                                            min_coefficient = min(coefficients_of_elements_in_first_string[i][0],
                                                                  coefficients_of_elements_in_second_string[i][0])
                                            max_coefficient = max(coefficients_of_elements_in_first_string[i][0],
                                                                  coefficients_of_elements_in_second_string[i][0])
                                            for g in range(20):
                                                if min_coefficient * g == max_coefficient:
                                                    values[0] = g
                                                    if result[coefficients_of_elements_in_second_string[e][1] - 1][
                                                        0].isalpha():
                                                        result[coefficients_of_elements_in_second_string[e][
                                                                   1] - 1] = "{0}{1}".format(
                                                            str(values[0]), result[
                                                                coefficients_of_elements_in_second_string[
                                                                    e][1] - 1])
                                                    break
                                            else:
                                                if gcd(min_coefficient, max_coefficient):
                                                    values[0] = min_coefficient * max_coefficient
                                                    if result[coefficients_of_elements_in_second_string[e][1] - 1][
                                                        0].isalpha():
                                                        result[coefficients_of_elements_in_second_string[e][
                                                                   1] - 1] = "{0}{1}".format(
                                                            str(values[0]), result[
                                                                coefficients_of_elements_in_second_string[
                                                                    e][1] - 1])
                                            break
                                else:
                                    value_e = list(all_missed_coefficients[e])
                                    if coefficients_of_elements_in_second_string[e][1] == \
                                            coefficients_of_elements_in_second_string[i][1]:
                                        if values[1] == value_e[1]:
                                            if values[0] == all_missed_coefficients[e][0]:
                                                if result[coefficients_of_elements_in_second_string[e][1] - 1][
                                                    0].isalpha():
                                                    result[coefficients_of_elements_in_second_string[e][
                                                               1] - 1] = "{0}{1}".format(
                                                        str(values[0]), result[
                                                            coefficients_of_elements_in_second_string[
                                                                e][1] - 1])
                                                break
                                            else:
                                                min_coefficient = min(coefficients_of_elements_in_first_string[i][0],
                                                                      coefficients_of_elements_in_second_string[i][0])
                                                max_coefficient = max(coefficients_of_elements_in_first_string[i][0],
                                                                      coefficients_of_elements_in_second_string[i][0])
                                                for g in range(20):
                                                    if min_coefficient * g == max_coefficient:
                                                        values[0] = g
                                                        if result[coefficients_of_elements_in_second_string[e][1] - 1][
                                                            0].isalpha():
                                                            result[coefficients_of_elements_in_second_string[e][
                                                                       1] - 1] = "{0}{1}".format(
                                                                str(values[0]), result[
                                                                    coefficients_of_elements_in_second_string[
                                                                        e][1] - 1])
                                                        break
                                                else:
                                                    if gcd(min_coefficient, max_coefficient):
                                                        values[0] = min_coefficient * max_coefficient
                                                        if result[coefficients_of_elements_in_second_string[e][1] - 1][
                                                            0].isalpha():
                                                            result[coefficients_of_elements_in_second_string[e][
                                                                       1] - 1] = "{0}{1}".format(
                                                                str(values[0]), result[
                                                                    coefficients_of_elements_in_second_string[
                                                                        e][1] - 1])
                                                break
                                        elif values[1] == value_e[3]:
                                            if values[0] == value_e[2]:
                                                if result[coefficients_of_elements_in_second_string[e][1] - 1][
                                                    0].isalpha():
                                                    result[coefficients_of_elements_in_second_string[e][
                                                               1] - 1] = "{0}{1}".format(
                                                        str(values[0]), result[
                                                            coefficients_of_elements_in_second_string[
                                                                e][1] - 1])
                                                break
                                            else:
                                                min_coefficient = min(coefficients_of_elements_in_first_string[i][0],
                                                                      coefficients_of_elements_in_second_string[i][0])
                                                max_coefficient = max(coefficients_of_elements_in_first_string[i][0],
                                                                      coefficients_of_elements_in_second_string[i][0])
                                                for g in range(20):
                                                    if min_coefficient * g == max_coefficient:
                                                        values[0] = g
                                                        if result[coefficients_of_elements_in_second_string[e][1] - 1][
                                                            0].isalpha():
                                                            result[coefficients_of_elements_in_second_string[e][
                                                                       1] - 1] = "{0}{1}".format(
                                                                str(values[0]), result[
                                                                    coefficients_of_elements_in_second_string[
                                                                        e][1] - 1])
                                                        break
                                                else:
                                                    if gcd(min_coefficient, max_coefficient):
                                                        values[0] = min_coefficient * max_coefficient
                                                        if result[coefficients_of_elements_in_second_string[e][1] - 1][
                                                            0].isalpha():
                                                            result[coefficients_of_elements_in_second_string[e][
                                                                       1] - 1] = "{0}{1}".format(
                                                                str(values[0]), result[
                                                                    coefficients_of_elements_in_second_string[
                                                                        e][1] - 1])
                                                break
                        else:
                            if result[coefficients_of_elements_in_second_string[i][1] - 1][0].isalpha():
                                result[coefficients_of_elements_in_second_string[i][
                                           1] - 1] = "{0}{1}".format(
                                    str(values[0]), result[
                                        coefficients_of_elements_in_second_string[
                                            i][1] - 1])
            self.new_notresult.setText(' + '.join(notresult))
            self.new_result.setText(' + '.join(result))
            cur.execute("""INSERT INTO equations(condition) 
            VALUES(?)""", (self.notresult.text() + ' --> ' + self.result.text(),))
            cur.execute("""update equations
            set decision = ?
            where condition == ?""", ((self.new_notresult.text() + ' --> ' + self.new_result.text()),
                                      (self.notresult.text() + ' --> ' + self.result.text()),))
            con.commit()
        except Exception:
            self.error_label.setText('Упс! Что-то пошло не так, попробуйте еще раз.')
            self.error_label.setStyleSheet('color:#ff0000')


class Element(QWidget):
    def __init__(self, value):
        super().__init__()
        uic.loadUi('element.ui', self)
        self.value = value
        self.ID.setText(str(value[0]))
        self.name.setText(str(value[1]))
        self.symbol.setText(str(value[2]))
        self.period.setText(str(value[3]))
        self.group.setText(str(value[4]) + ' (Подгруппа ' + ''.join(
            cur.execute("""select subgroup from groups where id_of_element = ?""",
                        (value[0],)).fetchone()) + ')')
        self.mass.setText(str(value[5]))
        self.property.setText(' '.join(
            cur.execute("""select property from properties where id_of_element = ?""",
                        (value[0],)).fetchone()))
        self.back_button.clicked.connect(self.exit)
        self.change_button.clicked.connect(self.change)
        self.ok_button.clicked.connect(self.update)

    def change(self):
        self.ok_button.setEnabled(True)
        self.property.setReadOnly(False)

    def update(self):  # Обновление базы данных
        self.ok_button.setEnabled(False)
        cur.execute("""update properties
        set property = ?
        where id_of_element = ?""", (self.property.toPlainText(), str(self.value[0]),))
        self.property.setReadOnly(True)
        con.commit()

    def exit(self):
        self.close()


class Table(QWidget):
    def __init__(self):
        super().__init__()
        self.frame_x = 10
        self.frame_y = 87
        uic.loadUi('table_mind.ui', self)  # Загружаем дизайн
        self.frame.setStyleSheet('border-style: solid; border-width: 5px; border-color: black;')
        self.to_chemical_calc.clicked.connect(self.equation)

    def equation(self):
        self.ex = Equation()
        self.ex.show()

    def open_element_form(self, value):
        self.selected_element = Element(value)
        self.selected_element.show()

    def mousePressEvent(self, event):
        e = 0
        value = ''
        for i in cur.execute("""select coords from information""").fetchall():
            e += 1
            i = [int(i) for i in str(i)[3:-4].split(', ')]
            if i[0] <= event.x() <= i[2] and i[1] <= event.y() <= i[3]:
                value = cur.execute("""select * from information
                                     WHERE id == ?""", (e,)).fetchone()
        if value:
            self.open_element_form(value)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_E:
            # Выводим информацию о выбранном элементе
            value = cur.execute("""SELECT * FROM information
                                    where coords = ?""",
                                (f'{self.frame_x, self.frame_y, self.frame_x + 70, self.frame_y + 79}',)).fetchone()
            self.open_element_form(value)
        # Передвигаем рамку
        if event.key() == Qt.Key_S:
            # Рамка не должна выходить за границы таблицы
            if self.frame_y == 561:
                if self.frame_x <= 220:
                    self.frame_x = 290
                elif self.frame_x == 1266:
                    self.frame_x = 1196
                self.frame_y += 143
            elif self.frame_y == 783:
                if self.frame_x >= 916:
                    self.frame_y = 166
                else:
                    self.frame_y = 324
            else:
                self.frame_y += 79
            self.frame.move(self.frame_x, self.frame_y)
        if event.key() == Qt.Key_W:
            # Рамка не должна выходить за границы таблицы
            if self.frame_y == 704:
                self.frame_y -= 143
            elif self.frame_y == 324 and 220 <= self.frame_x <= 846:
                if self.frame_x == 220:
                    self.frame_x = 290
                self.frame_y = 783
            elif (self.frame_y == 166 or self.frame_y == 167) and 916 <= self.frame_x <= 1196:
                self.frame_y = 783
            elif (self.frame_y == 166 or self.frame_y == 167) and self.frame_x == 80:
                self.frame_y = 561
            elif (self.frame_y == 88 or self.frame_y == 87) and self.frame_x == 10:
                self.frame_y = 561
            elif (self.frame_y == 88 or self.frame_y == 87) and self.frame_x == 1266:
                self.frame_y = 561
            else:
                self.frame_y -= 79
            self.frame.move(self.frame_x, self.frame_y)

        if event.key() == Qt.Key_D:
            if self.frame_x == 500:
                self.frame_x += 66
            else:
                self.frame_x += 70
                # Рамка не должна выходить за границы таблицы
                if self.frame_x == 150:
                    if self.frame_y < 324:
                        self.frame_y = 324
                    self.frame_x += 70
                elif self.frame_x == 1266 and self.frame_y == 704:
                    self.frame_x = 290
                elif self.frame_x == 1266 and self.frame_y == 783:
                    self.frame_x = 290
                elif self.frame_x > 1266:
                    self.frame_x = 10
                elif self.frame_x == 80 and self.frame_y == 87:
                    self.frame_y = 167
            self.frame.move(self.frame_x, self.frame_y)

        if event.key() == Qt.Key_A:
            # Рамка не должна выходить за границы таблицы
            if self.frame_x == 566:
                self.frame_x -= 66
            else:
                self.frame_x -= 70
                if self.frame_x == 150:
                    self.frame_x -= 70
                elif self.frame_y < 324 and self.frame_x == 846:
                    self.frame_y = 324
                elif self.frame_x == 220 and self.frame_y == 704:
                    self.frame_x = 1196
                elif self.frame_x == 220 and self.frame_y == 783:
                    self.frame_x = 1196
                elif self.frame_x < 0:
                    self.frame_x = 1266
                elif self.frame_x == 1196 and self.frame_y == 87:
                    self.frame_y = 167
            self.frame.move(self.frame_x, self.frame_y)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Table()
    ex.show()
    sys.exit(app.exec())
