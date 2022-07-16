from os import getcwd, listdir, remove
from os.path import exists, isdir, isfile
from sys import argv, exit

if __name__ == '__main__':
    if len(argv) == 1:
        from PyQt6.QtWidgets import QApplication
        qt = QApplication([])
        from src.application import Application
        app = Application()
        exit(qt.exec())
    elif len(argv) == 3 and argv[1] == '-clear':
        path = f'{getcwd()}/{argv[2]}'
        if not exists(path) or not isdir(path):
            print(f'Failed to find directory ({path})')
        else:
            all_files = [file for file in listdir(f'{path}/') if isfile(f'{path}/{file}')]
            image_files = [file for file in all_files if any([ex in file for ex in ['.jpg', '.jpeg', 'png']])] 
            for file in image_files:
                remove(f'{path}/{file}')
    else:
        print(f'Unrecognized command line arguments\n   python3 run.py [-clear <path>]')

