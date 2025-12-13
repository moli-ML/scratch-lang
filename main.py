"""
ScratchLang IDE 主程序入口
"""
import sys
from PyQt5.QtWidgets import QApplication
from ide.mainwindow import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setApplicationName("ScratchLang IDE")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()