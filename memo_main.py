from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget

from memo_app import app
from memo_data import *
from memo_main_layout import *
from memo_card_layout import *
from memo_edit_layout import txt_Question, txt_Answer, txt_Wrong1, txt_Wrong2, txt_Wrong3

######################################              Константи:              #############################################
main_width, main_height = 1000, 450  # початкові розміри головного вікна
card_width, card_height = 600, 500  # початкові розміри вікна "картка"
time_unit = 1000  # стільки триває одна одиниця часу із тих, на які потрібно засинати


######################################          Глобальні змінні:      #############################################
questions_listmodel = QuestionListModel()  # список питань
frm_edit = QuestionEdit(0, txt_Question, txt_Answer, txt_Wrong1, txt_Wrong2,
                        txt_Wrong3)  # запам'ятовуємо, що у формі редагування запитання з чим пов'язано
radio_list = [rbtn_1, rbtn_2, rbtn_3,
              rbtn_4]  # список віджетів,які потрібно перемішати (для випадкового розміщення відповідей)
frm_card = 0  # тут будут зв'язуватися питання з формою тесту
timer = QTimer()  # таймер для можливості "заснути" на певний час та прокинутися
win_card = QWidget()  # вікно картки
win_main = QWidget()  # вікно редагування запитань, основне у програмі


######################################             Тестові данні:         #############################################
def testlist():
    frm = Question('Яблуко', 'apple', 'application', 'pinapple', 'apply')
    questions_listmodel.form_list.append(frm)
    frm = Question('Дім', 'house', 'horse', 'hurry', 'hour')
    questions_listmodel.form_list.append(frm)
    frm = Question('Миша', 'mouse', 'mouth', 'muse', 'museum')
    questions_listmodel.form_list.append(frm)
    frm = Question('Число', 'number', 'digit', 'amount', 'summary')
    questions_listmodel.form_list.append(frm)


######################################     Функції для проведення теста:    #############################################

def set_card():
    ''' задає, початковий вигляд вікна картки'''
    win_card.resize(card_width, card_height)
    win_card.move(300, 300)
    win_card.setWindowTitle('Memory Card')
    win_card.setLayout(layout_card)


def sleep_card():
    ''' картка ховається на час, вказаний у таймері'''
    win_card.hide()
    timer.setInterval(time_unit * box_Minutes.value())
    timer.start()


def show_card():
    ''' показує вікно (по таймеру), таймер зупиняється'''
    win_card.show()
    timer.stop()


def show_random():
    ''' показати випадкове запитання '''
    global frm_card  # властивість вікна - поточна форма с даними картки
    # отримуємо випадкові данні, та випадково же розподіляємо варіанти відповідей по радіокнопкам:
    frm_card = random_AnswerCheck(questions_listmodel, lb_Question, radio_list, lb_Correct, lb_Result)
    # ми будемо запускати функцію, коли вікно вже відкрито. Тоді показуємо:
    frm_card.show()  # загрузити нужні данні у відповідні віджети
    show_question()  # показати на формі панель запитань


def click_OK():
    ''' перевіряє питання, або завантажує нове запитання '''
    if btn_OK.text() != 'Наступне запитання':
        frm_card.check()
        show_result()
    else:
        # напис на кнопці дорівнює 'Наступний', ось і створюємо нове випадкове запитання:
        show_random()


def back_to_menu():
    ''' повернення із теста у вікно редактора '''
    win_card.hide()
    win_main.showNormal()


######################################     Функції для редагування запитання:    ######################################
def set_main():
    ''' задає, як виглядає основне вікно'''
    win_main.resize(main_width, main_height)
    win_main.move(100, 100)
    win_main.setWindowTitle('Список запитань')
    win_main.setLayout(layout_main)


def edit_question(index):
    ''' завантажує у форму запитання та відповіді, відповідні переданному рядку '''
    #  index - це об'єкт класу QModelIndex, див. потрібні методи нижче
    if index.isValid():
        i = index.row()
        frm = questions_listmodel.form_list[i]
        frm_edit.change(frm)
        frm_edit.show()


def add_form():
    ''' добавляет новый вопрос и предлагает его изменить '''
    questions_listmodel.insertRows()  # нові запитання з'являються в даних та автоматично у списку на екрані
    last = questions_listmodel.rowCount(0) - 1  # нове запитання - останнє в списку. Знайдемо його позицію.
    # В rowCount передаём 0, чтобы соответствовать требованиям функции:
    # этот параметр все равно не используется, но
    # нужен по стандарту библиотеки (метод с параметром index вызывается при отрисовке списка)
    index = questions_listmodel.index(
        last)  # получаем объект класса QModelIndex, который соответствует последнему элементу в данных
    list_questions.setCurrentIndex(index)  # делаем соответствующую строку списка на экране текущей
    edit_question(index)  # этот вопрос надо подгрузить в форму редактирования
    # клика мышкой у нас тут нет, вызовем нужную функцию из программы
    txt_Question.setFocus(
        Qt.TabFocusReason)  # переводим фокус на поле редактирования вопроса, чтобы сразу убирались "болванки"
    # Qt.TabFocusReason переводит фокус так, как если бы была нажата клавиша "tab"
    # это удобно тем, что выделяет "болванку", её легко сразу убрать


def del_form():
    ''' удаляет вопрос и переключает фокус '''
    questions_listmodel.removeRows(list_questions.currentIndex().row())
    edit_question(list_questions.currentIndex())


def start_test():
    ''' при начале теста форма связывается со случайным вопросом и показывается'''
    show_random()
    win_card.show()
    win_main.showMinimized()


######################################      Установка нужных соединений:    #############################################
def connects():
    list_questions.setModel(questions_listmodel)  # связать список на экране со списком вопросов
    list_questions.clicked.connect(
        edit_question)  # при нажатии на элемент списка будет открываться для редактирования нужный вопрос
    btn_add.clicked.connect(add_form)  # соединили нажатие кнопки "новый вопрос" с функцией добавления
    btn_delete.clicked.connect(del_form)  # соединили нажатие кнопки "удалить вопрос" с функцией удаления
    btn_start.clicked.connect(start_test)  # нажатие кнопки "начать тест"
    btn_OK.clicked.connect(click_OK)  # нажатие кнопки "OK" на форме теста
    btn_Menu.clicked.connect(back_to_menu)  # нажатие кнопки "Меню" для возврата из формы теста в редактор вопросов
    timer.timeout.connect(show_card)  # показываем форму теста по истечении таймера
    btn_Sleep.clicked.connect(sleep_card)  # нажатие кнопки "спать" у карточки-теста


######################################            Запуск программы:         #############################################
# Основной алгоритм иногда оформляют в функцию, которая запускается, только если код выполняется из этого файла,
# а не при подключении как модуль. Детям это совершенно не нужно.
testlist()
set_card()
set_main()
connects()
win_main.show()
app.exec_()
