# -*- coding: utf-8 -*-

"""
Module implementing MainDesk.
"""
import sys
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMainWindow,QApplication

from Ui_PyDesktop import Ui_MainWindow
from PyDZmain import MainWindow
from PyOneSource import OneSource
from PyBigSource import MainBigSource
class MainDesk(QMainWindow, Ui_MainWindow):
    """
    Class documentation goes here.
    """
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super(MainDesk, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("PyQtDZMix V1.0")
        
        # 获取屏幕尺寸并计算2/3大小
        screen = QApplication.primaryScreen().availableGeometry()
        width = int(screen.width() / 4)
        height = int(screen.height()/6)
        
        # 设置窗口大小和位置（居中）
        self.setGeometry(
            int((screen.width() - width) / 2),  # x位置
            int((screen.height() - height) / 2), # y位置
            width,                              # 宽度
            height                              # 高度
        )
        self.pushButton.setGeometry(width/10,height/3,width*2/9,height/3)
        self.pushButton_2.setGeometry(width*4/10,height/3,width*2/9,height/3)
        self.pushButton_3.setGeometry(width*7/10,height/3,width*2/9,height/3)
        # 设置窗口不可改变大小
        self.setFixedSize(width, height)
    
    @pyqtSlot()
    def on_pushButton_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.source1 = OneSource()
        self.source1.show()
    
    @pyqtSlot()
    def on_pushButton_2_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.source2 = MainWindow()
        self.source2.show()
    
    @pyqtSlot()
    def on_pushButton_3_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.source3=MainBigSource()
        self.source3.show()
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 设置全局样式，使界面更美观
    app.setStyle("Fusion")
    
    desktop = MainDesk()
    desktop.show()
    sys.exit(app.exec_())
