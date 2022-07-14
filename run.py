from sys import exit
from src import Application
from PyQt6.QtWidgets import QApplication

if __name__ == '__main__':
    qt = QApplication([])
    app = Application()
    exit(qt.exec())
