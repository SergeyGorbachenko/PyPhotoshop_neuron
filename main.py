import os
import easyocr
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QWidget,
    QFileDialog,
    QLabel, QPushButton, QListWidget,
    QHBoxLayout, QVBoxLayout, QTextEdit, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPalette, QColor, QFont
from PIL import Image, UnidentifiedImageError

app = QApplication([])

palette = QPalette()
palette.setColor(QPalette.Window, QColor(30, 30, 30))
palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
palette.setColor(QPalette.Base, QColor(50, 50, 50))
palette.setColor(QPalette.AlternateBase, QColor(75, 75, 75))
palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
palette.setColor(QPalette.ToolTipText, QColor(30, 30, 30))
palette.setColor(QPalette.Text, QColor(255, 255, 255))
palette.setColor(QPalette.Button, QColor(60, 60, 60))
palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
palette.setColor(QPalette.Highlight, QColor(90, 90, 90))
palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
app.setPalette(palette)

win = QWidget()
win.resize(800, 600)
win.setWindowTitle('Easy Editor')

font = QFont("Arial", 10)
app.setFont(font)

lb_image = QLabel("Картинка")
lb_image.setAlignment(Qt.AlignCenter)

btn_dir = QPushButton("Выбрать Папку")
lw_files = QListWidget()

btn_left = QPushButton("Поворот влево")
btn_right = QPushButton("Поворот вправо")
btn_flip = QPushButton("Зеркальное отражение")
btn_sharp = QPushButton("Резкость")
btn_bw = QPushButton("Чёрно-белый")
btn_ocr = QPushButton("Распознать текст")
btn_remove_bg = QPushButton("Удалить фон")

btn_change_theme = QPushButton("Сменить тему")
btn_change_theme.setStyleSheet("""
    QPushButton {
        background-color: rgb(60, 60, 60);
        border: none;
        padding: 10px;
        font-size: 14px;
        color: white;
        border-radius: 5px;
    }
    QPushButton:hover {
        background-color: rgb(80, 80, 80);
    }
""")

text_edit = QTextEdit()
text_edit.setPlaceholderText("Распознанный текст...")
text_edit.setStyleSheet("color: white; background-color: rgb(50, 50, 50);")

error_display = QTextEdit()
error_display.setPlaceholderText("Ошибки будут отображаться здесь...")
error_display.setStyleSheet("color: red; background-color: rgb(50, 50, 50);")
error_display.setReadOnly(True)
error_display.setFixedHeight(50)

for btn in [btn_dir, btn_left, btn_right, btn_flip, btn_sharp, btn_bw, btn_ocr, btn_remove_bg]:
    btn.setStyleSheet("""
        QPushButton {
            background-color: rgb(60, 60, 60);
            border: none;
            padding: 10px;
            font-size: 14px;
            color: white;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: rgb(80, 80, 80);
        }
    """)

row = QHBoxLayout()
col1 = QVBoxLayout()
col2 = QVBoxLayout()
col1.addWidget(btn_dir)
col1.addWidget(lw_files)
col1.addWidget(btn_change_theme)
col2.addWidget(lb_image, 95)

row_tools = QHBoxLayout()
row_tools.addWidget(btn_left)
row_tools.addWidget(btn_right)
row_tools.addWidget(btn_flip)
row_tools.addWidget(btn_sharp)
row_tools.addWidget(btn_bw)
row_tools.addWidget(btn_ocr)
row_tools.addWidget(btn_remove_bg)
col2.addLayout(row_tools)

col2.addWidget(text_edit)
col2.addWidget(error_display)

row.addLayout(col1, 25)
row.addLayout(col2, 75)
win.setLayout(row)

win.show()

workdir = ''

def filter(files, extensions):
    return [filename for filename in files if any(filename.endswith(ext) for ext in extensions)]

def chooseWorkdir():
    global workdir
    workdir = QFileDialog.getExistingDirectory()

def showFilenamesList():
    global workdir
    workdir = QFileDialog.getExistingDirectory()

    if not workdir:
        return

    extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
    filenames = filter(os.listdir(workdir), extensions)

    lw_files.clear()
    for filename in filenames:
        lw_files.addItem(filename)

btn_dir.clicked.connect(showFilenamesList)

class ImageProcessor():
    def __init__(self, error_display):
        self.image = None
        self.filename = None
        self.save_dir = "Modified/"
        self.reader = easyocr.Reader(['ru'])
        self.error_display = error_display

    def loadImage(self, filename):
        if filename:
            self.filename = filename
            fullname = os.path.join(workdir, filename)

            try:
                self.original_image = Image.open(fullname)
                self.image = self.original_image.copy()
                self.showImage(fullname)
            except UnidentifiedImageError:
                self.showError(f"Ошибка: Не удалось распознать файл изображения: {fullname}")
            except FileNotFoundError:
                self.showError(f"Ошибка: Файл не найден: {fullname}")

    def showError(self, message):
        self.error_display.append(message)

    def saveImage(self):
        path = os.path.join(workdir, self.save_dir)
        if not os.path.exists(path):
            try:
                os.mkdir(path)
            except OSError as e:
                self.showError(f"Ошибка: не удалось создать директорию {path}. {e}")
                return

        fullname = os.path.join(path, self.filename)

        try:
            if self.image.mode == 'RGBA':
                self.image = self.image.convert('RGB')

            self.image.save(fullname)
        except Exception as e:
            self.showError(f"Ошибка при сохранении изображения: {e}")
            return

        self.showError(f"Изображение успешно сохранено: {fullname}")



    def do_bw(self):
        self.image = self.image.convert("L")
        self.saveImage()
        self.showImage(os.path.join(workdir, self.save_dir, self.filename))

    def do_left(self):
        self.image = self.image.transpose(Image.ROTATE_90)
        self.saveImage()
        self.showImage(os.path.join(workdir, self.save_dir, self.filename))

    def do_right(self):
        self.image = self.image.transpose(Image.ROTATE_270)
        self.saveImage()
        self.showImage(os.path.join(workdir, self.save_dir, self.filename))

    def do_flip(self):
        self.image = self.image.transpose(Image.FLIP_LEFT_RIGHT)
        self.saveImage()
        self.showImage(os.path.join(workdir, self.save_dir, self.filename))

    def do_sharpen(self):
        from PIL import ImageFilter
        self.image = self.image.filter(ImageFilter.SHARPEN)
        self.saveImage()
        self.showImage(os.path.join(workdir, self.save_dir, self.filename))

    def showImage(self, path):
        lb_image.hide()
        pixmapimage = QPixmap(path)
        w, h = lb_image.width(), lb_image.height()
        pixmapimage = pixmapimage.scaled(w, h, Qt.KeepAspectRatio)
        lb_image.setPixmap(pixmapimage)
        lb_image.show()

    def recognize_text(self):
        if self.image is not None:
            image_np = np.array(self.image)
            results = self.reader.readtext(image_np)
            text = "\n".join([result[1] for result in results])
            text_edit.setPlainText(text)

    def remove_background(self):
        if self.original_image is not None:
            input_image = np.array(self.original_image)
            from rembg import remove
            output_image = remove(input_image)
            self.image = Image.fromarray(output_image)
            self.saveImage()
            self.showImage(os.path.join(workdir, self.save_dir, self.filename))

processor = ImageProcessor(error_display)

def load_image_from_list():
    selected_items = lw_files.selectedItems()
    if selected_items:
        selected_filename = selected_items[0].text()
        processor.loadImage(selected_filename)

lw_files.itemClicked.connect(load_image_from_list)
btn_bw.clicked.connect(processor.do_bw)
btn_left.clicked.connect(processor.do_left)
btn_right.clicked.connect(processor.do_right)
btn_flip.clicked.connect(processor.do_flip)
btn_sharp.clicked.connect(processor.do_sharpen)
btn_ocr.clicked.connect(processor.recognize_text)
btn_remove_bg.clicked.connect(processor.remove_background)

themes = {
    "Чёрный": {
        "Window": QColor(30, 30, 30),
        "WindowText": QColor(255, 255, 255),
        "Base": QColor(50, 50, 50),
        "Text": QColor(255, 255, 255),
        "Button": QColor(60, 60, 60),
        "ButtonText": QColor(255, 255, 255),
    },
    "Белый": {
        "Window": QColor(255, 255, 255),
        "WindowText": QColor(0, 0, 0),
        "Base": QColor(240, 240, 240),
        "Text": QColor(0, 0, 0),
        "Button": QColor(200, 200, 200),
        "ButtonText": QColor(0, 0, 0),
    },
    "Серый": {
        "Window": QColor(50, 50, 50),
        "WindowText": QColor(255, 255, 255),
        "Base": QColor(100, 100, 100),
        "Text": QColor(255, 255, 255),
        "Button": QColor(80, 80, 80),
        "ButtonText": QColor(255, 255, 255),
    },
    "Солнечный": {
        "Window": QColor(255, 255, 150),
        "WindowText": QColor(0, 0, 0),
        "Base": QColor(255, 255, 200),
        "Text": QColor(0, 0, 0),
        "Button": QColor(255, 200, 100),
        "ButtonText": QColor(0, 0, 0),
    },
    "Алмазный": {
        "Window": QColor(200, 220, 255),
        "WindowText": QColor(0, 0, 0),
        "Base": QColor(240, 240, 255),
        "Text": QColor(0, 0, 0),
        "Button": QColor(180, 210, 255),
        "ButtonText": QColor(0, 0, 0),
    },
}

current_theme = 0

def change_theme():
    global current_theme
    current_theme = (current_theme + 1) % len(themes)
    selected_theme = list(themes.values())[current_theme]

    palette = QPalette()
    palette.setColor(QPalette.Window, selected_theme["Window"])
    palette.setColor(QPalette.WindowText, selected_theme["WindowText"])
    palette.setColor(QPalette.Base, selected_theme["Base"])
    palette.setColor(QPalette.Text, selected_theme["Text"])
    palette.setColor(QPalette.Button, selected_theme["Button"])
    palette.setColor(QPalette.ButtonText, selected_theme["ButtonText"])
    
    app.setPalette(palette)

btn_change_theme.clicked.connect(change_theme)

app.exec()
