from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QProgressBar, QSlider, QLineEdit, QPushButton


# Окно для выбора
class CustomDialog(QDialog):
    def __init__(self, items, dev):
        super().__init__()
        self.setWindowTitle("Введите предпочтения")
        self.setMinimumSize(300, 300)

        layout = QVBoxLayout()

        self.label_1 = QLabel("Жанр")
        self.genres = QComboBox()
        self.genres.addItem('ALL')
        for i in items:
            self.genres.addItem(i)

        self.label_2 = QLabel("Издатель")
        self.developer = QComboBox()
        self.developer.addItem('ALL')
        for i in dev:
            self.developer.addItem(list(i)[0])

        self.label_3 = QLabel("Рейтинг")
        self.rating = QProgressBar()
        self.rating.setMinimum(0)
        self.rating.setMaximum(100)

        self.rating_slider = QSlider(Qt.Orientation.Horizontal)
        self.rating_slider.setMinimum(0)
        self.rating_slider.setMaximum(100)
        self.rating_slider.setValue(50)  # Установить начальное значение

        self.rating_slider.valueChanged.connect(self.rating.setValue)

        self.min_price = QLineEdit()
        self.min_price.setPlaceholderText("Максимальная цена")

        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Показать все игры")

        layout.addWidget(self.label_1)
        layout.addWidget(self.genres)
        layout.addWidget(self.label_2)
        layout.addWidget(self.developer)
        layout.addWidget(self.label_3)
        layout.addWidget(self.rating)
        layout.addWidget(self.rating_slider)
        layout.addWidget(self.min_price)
        layout.addWidget(self.ok_button)
        layout.addWidget(self.cancel_button)

        self.setLayout(layout)

        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def get_selected_item(self):
        return [self.genres.currentText(), self.developer.currentText(), self.rating.value(), self.min_price.text()]
