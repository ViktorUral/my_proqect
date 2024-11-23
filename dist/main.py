import json
import sqlite3
import sys

import vlc
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QPixmap
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QTableWidget, QWidget
from graph import BarChartWidget
from dialog import CustomDialog

from myprodgect import Ui_MainWindow


class ImageLabel(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.last_sort = ''
        self.genres = []
        self.user_genre = ''
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.number_of_game_in_genres_list = 0
        self.last_language = 'english'
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)

        self.con = sqlite3.connect('games.sqlite')
        self.cursor = self.con.cursor()
        self.games = self.cursor.execute(f'SELECT g.name, g.price, g.positive, g.negative '
                                         f'FROM Game g').fetchall()
        self.image_catalog(self.games)
        self.choice_genres()

        self.developer.setEnabled(False)
        self.rating.setEnabled(False)
        self.price.setEnabled(False)
        self.year.setEnabled(False)
        self.in_wishlist.setEnabled(False)
        self.gameWidget.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.game_genres.setReadOnly(True)
        self.about_game.setReadOnly(True)

        self.forth.clicked.connect(self.forth_choice_genres)
        self.back.clicked.connect(self.back_choice_genres)

        self.ubdate_genres.clicked.connect(self.choice_genres)

        self.pause.clicked.connect(self.pause_video)

        self.sort_name.clicked.connect(self.sort_catalog)
        self.sort_prices.clicked.connect(self.sort_catalog)
        self.sort_rating.clicked.connect(self.sort_catalog)
        self.sort_countreview.clicked.connect(self.sort_catalog)

        self.volume_slider.valueChanged.connect(self.set_volume)

        self.add_in_wishlist.clicked.connect(self.add_wishlist)

        self.wishlist.clicked.connect(self.image_wishlist)

        self.gameWidget.cellDoubleClicked.connect(self.image_game_from_catalog)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        central_widget.setLayout(self.verticalLayout_5)

        self.trayler.setFixedHeight(400)
        self.gameWidget.setFixedWidth(440)

        self.sort_name.setFixedSize(100, 25)
        self.sort_rating.setFixedSize(100, 25)
        self.sort_prices.setFixedSize(100, 25)
        self.sort_countreview.setFixedSize(100, 25)

    # Для сортировки каталога
    def sort_catalog(self):
        d = {
            'name': lambda x: x[0],
            'prices': lambda x: x[1],
            'rating': lambda x: x[2] / (x[2] + x[3]),
            'countreview': lambda x: x[3] + x[2]
        }
        last_but = self.sender().objectName().split('_')[1]
        if self.last_sort != last_but:
            reverse = True
            self.last_sort = last_but
        else:
            reverse = False
            self.last_sort = ''
        name_button = d[self.sender().objectName().split('_')[1]]

        self.image_catalog(sorted(self.games, key=name_button, reverse=reverse))

    # Показ Каталога
    def image_catalog(self, for_catalog):
        if for_catalog == '':
            for_catalog = self.cursor.execute(f'SELECT g.name, g.price, g.positive, g.negative '
                                              f'FROM Game g').fetchall()
        self.gameWidget.clear()
        self.gameWidget.setRowCount(len(for_catalog))
        self.gameWidget.setColumnCount(4)
        for el in range(len(for_catalog)):
            name, price, positive, negative = for_catalog[el]
            self.gameWidget.setItem(el, 0, QTableWidgetItem(name))
            self.gameWidget.setItem(el, 1, QTableWidgetItem(str(price) + ' руб.'))
            self.gameWidget.setItem(el, 2, QTableWidgetItem(str(positive + negative)))
            self.gameWidget.setItem(el, 3,
                                    QTableWidgetItem(str(round(positive / (positive + negative) * 100, 2)) + '%'))
        self.gameWidget.setHorizontalHeaderLabels(['Игра', "Цена", "Кол. отзывов", 'Рейтинг'])

        if self.player.is_playing():
            self.player.play()

    # Окошко для выбора жанров
    def choice_genres(self):
        if not self.genres:
            self.create_genres()
        items, dev = self.genres
        dialog = CustomDialog(sorted(items), sorted(dev))
        request = []
        if dialog.exec():
            selected_item = dialog.get_selected_item()
            if selected_item[0] != 'ALL':
                request.append("g.genresdata like '%" + selected_item[0] + "%'")
            if selected_item[1] != 'ALL':
                request.append("d.name = '" + selected_item[1] + "'")
            if selected_item[2] != '-1':
                request.append("(g.positive * 100.0 / (g.positive + g.negative)) > " + str(selected_item[2]))
            if selected_item[3]:
                request.append("g.price <= " + selected_item[3])

        if request:
            request = 'WHERE ' + ' AND '.join(request)
        else:
            request = ''

        self.result = self.cursor.execute("""
                           SELECT g.id_game, g.name, g.year, g.price, g.image, g.trailer, g.genresdata, 
                                  g.positive, g.negative, g.mettacritick, g.about, d.name AS developer_name
                           FROM Game g
                           JOIN Developers d ON g.developer = d.id """ + request).fetchall()
        self.number_of_game_in_genres_list = 0
        self.games = [[self.result[i][1], self.result[i][3], self.result[i][7], self.result[i][8]] for i in
                      range(len(self.result))]
        self.image_catalog(self.games)
        try:
            self.image_game_info(self.result[0])
        except Exception:
            return

    # Следующая игра соответствующая критериям пользователя
    def forth_choice_genres(self):
        try:
            self.image_game_info(self.result[self.number_of_game_in_genres_list + 1])
            self.number_of_game_in_genres_list += 1
        except Exception:
            return

    # Назад к предыдущей игре
    def back_choice_genres(self):
        try:
            if self.number_of_game_in_genres_list != 0:
                self.image_game_info(self.result[self.number_of_game_in_genres_list - 1])
                self.number_of_game_in_genres_list -= 1
        except Exception:
            return

    # Показать игры в списке желаемых
    def image_wishlist(self):
        self.result = self.cursor.execute("SELECT g.id_game, g.name, g.year, g.price, g.image, g.trailer, "
                                          "g.genresdata, g.positive, g.negative, g.mettacritick, g.about, "
                                          "d.name AS developer_name FROM Game g JOIN Developers d ON g.developer = "
                                          "d.id JOIN Wishlist w on w.id_game = g.id_game").fetchall()
        self.number_of_game_in_genres_list = 0
        self.games = [[self.result[i][1], self.result[i][3], self.result[i][7], self.result[i][8]] for i in
                      range(len(self.result))]
        self.image_catalog(self.games)
        try:
            self.image_game_info(self.result[0])
        except Exception:
            return

    # Создание списка всех жанров и издателей в бд
    def create_genres(self):
        result = self.cursor.execute('SELECT genresdata FROM Game').fetchall()
        a = set()
        b = set()
        for el in result:
            for genre in json.loads(el[0]):
                a.add(genre)
        result = self.cursor.execute('SELECT name FROM Developers').fetchall()
        for name in result:
            b.add(name)
        self.genres = [list(a), list(b)]

    # Показ информации об игре
    def image_game_info(self, result):
        name, year, price, image, trailer, genres, positive, negative, mettacritick, about, developer = result[1:]
        self.developer.setText('Издатель: ' + developer)
        self.year.setText('Год выпуска: ' + year)
        self.price.setText('Цена: ' + str(price) + ' руб.')
        self.game_name.setText(name)
        self.rating.setText('Рейтинг: ' + str(round(positive / (positive + negative) * 100, 2)))
        self.about_game.setText(about)

        if (result[0],) in self.cursor.execute('SELECT id_game FROM Wishlist').fetchall():
            self.in_wishlist.setText('★')
        else:
            self.in_wishlist.setText('☆')

        genres_this_game = json.loads(genres)
        self.game_genres.setText('\n'.join(genres_this_game))
        if trailer:
            self.video_player(trailer)
        self.pause.setText("⏸️")

        self.game_pic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.network_manager = QNetworkAccessManager()
        self.network_manager.finished.connect(self.on_finished)
        self.network_manager.get(QNetworkRequest(QUrl(image)))

        item = self.graph_rewiew.takeAt(0)
        if item is not None:
            widget = item.widget()
            widget.deleteLater()

        item = self.graph_rating.takeAt(0)
        if item is not None:
            widget = item.widget()
            widget.deleteLater()

        self.graph_rewiew.addWidget(BarChartWidget([positive, negative], ['Положительные', 'Отрицательные'],
                                                   'Количество отзывов', 'Отзывы'))

        self.graph_rating.addWidget(
            BarChartWidget([round(positive / (positive + negative) * 100, 2), 100], ['у игры', '100'],
                           '%', 'Соот. Полож. отзывов к отриц.'))

    def image_game_from_catalog(self, row, col):
        rowData = [self.gameWidget.item(row, col).text() for col in range(self.gameWidget.columnCount())]
        self.result = self.cursor.execute('''SELECT g.id_game, g.name, g.year, g.price, g.image, g.trailer, 
                g.genresdata, g.positive, g.negative, g.mettacritick, g.about, d.name AS developer_name 
                FROM Game g 
                JOIN Developers d ON g.developer = d.id 
                WHERE g.name = ?''', (rowData[0],)).fetchall()
        self.number_of_game_in_genres_list = 0
        self.image_game_info(self.result[0])

    # Для изображения
    def on_finished(self, reply):
        image_data = reply.readAll()
        pixmap = QPixmap()
        pixmap.loadFromData(image_data)
        self.game_pic.setPixmap(pixmap.scaled(419, 221, Qt.AspectRatioMode.KeepAspectRatio))

    # Для трейлера
    def video_player(self, video_url):
        self.trayler.setStyleSheet("background-color: black;")
        self.player.set_hwnd(self.trayler.winId())
        media = self.instance.media_new(video_url)
        self.player.set_media(media)
        self.player.play()

    # Изменение звука
    def set_volume(self, value):
        self.player.audio_set_volume(value)

    # пауза/продолжить
    def pause_video(self):
        if self.player.is_playing():
            self.player.pause()
            self.pause.setText("▶️")
        else:
            self.player.play()
            self.pause.setText("⏸️")

    # добавить в список жел.
    def add_wishlist(self):
        id_game = self.result[self.number_of_game_in_genres_list][0]
        if not (id_game,) in self.cursor.execute('SELECT id_game FROM Wishlist').fetchall():
            self.cursor.execute(f"INSERT INTO Wishlist(id_game) Values({id_game})")
            self.in_wishlist.setText('★')
        else:
            self.cursor.execute(f"DELETE from Wishlist WHERE id_game = {id_game}")
            self.in_wishlist.setText('☆')
        self.con.commit()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    label = ImageLabel()
    label.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
