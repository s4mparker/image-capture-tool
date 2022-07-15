if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    qt = QApplication([])

    from src.application import Application
    from sys import exit
    app = Application()
    exit(qt.exec())
