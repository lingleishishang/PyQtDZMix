# -*- coding: utf-8 -*-

"""
Module implementing PyMainSub.
"""

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot,Qt,QAbstractTableModel
from PyQt5.QtWidgets import QMainWindow,QApplication,QMessageBox,QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.rcParams['font.sans-serif']=['SimHei']

import numpy as np
import scipy.stats as st
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
import matplotlib.gridspec as gridspec
import matplotlib.ticker as ticker  # 导入刻度控制模块
import Similarity  as sim
import Likeness as lk
import KUTest as kut
import KSTest as ks
import R2new as r
import QQ as Qr
import csv
import random
from scipy.interpolate import griddata
from mpl_toolkits.mplot3d import Axes3D  # 关键：启用3D投影功能
from scipy.spatial import ConvexHull

from Ui_PySubData import Ui_MainWindow
class SimpleTableModel(QAbstractTableModel):
    def __init__(self, data, headers=None, parent=None):
        """
        初始化表格模型
        
        参数:
        data: 二维列表，表格数据
        headers: 列表，列标题(可选)
        parent: 父对象(可选)
        """
        super().__init__(parent)
        self.data_list = data  # 存储数据列表
        self.headers = headers if headers is not None else []  # 存储表头数据
        
        # 计算最大列数
        if self.data_list:
            self.max_col = max(len(row) for row in self.data_list)
        else:
            self.max_col = len(self.headers) if self.headers else 0  # 如果没有数据但有表头，使用表头长度

    def rowCount(self, parent=None):
        return len(self.data_list)

    def columnCount(self, parent=None):
        return self.max_col

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        
        row = index.row()
        col = index.column()
        current_row = self.data_list[row] if row < len(self.data_list) else []

        # 第1列：显示"Method"
        if col == 0:
            if role == Qt.DisplayRole:
                return current_row[0] if current_row else ""
            if role == Qt.TextAlignmentRole:
                return Qt.AlignCenter
        
        # 其他列：显示数值
        else:
            if role == Qt.DisplayRole:
                if col < len(current_row):
                    return f"{current_row[col]:.4f}"  # 保留4位小数
            if role == Qt.TextAlignmentRole:
                return Qt.AlignCenter
        
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
                # 水平表头（列标题）
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == 0:
                return "Method"  # 第1列标题
            elif section == self.columnCount() - 1:  # 最后一个列的情况
                return  f"Results" # 或者你想要的最后一个列的标题
            else:
                return self.headers[section*2]  # 后续列标题（数值1、数值2...）
        return None  # 垂直表头（行号）不需要，返回空

class PyMainSub(QMainWindow, Ui_MainWindow):
    """
    Class documentation goes here.
    """
    def generate_100_colors(self):
    # 使用tab20颜色映射（包含20种明显不同的颜色）
        cmap = plt.get_cmap('tab20')
        colors = [cmap(i % 20) for i in range(100)]  # 循环使用20种颜色
        
        # 或者使用hsv颜色空间生成100种不同颜色
        # colors = plt.cm.hsv(np.linspace(0, 1, 100))
        
        return colors
    def set_table_data(self, headers, data):
            """
            接收从主窗口传来的表头和二维数据
            headers: list of str，列名
            data: list of list，二维字符串/数字矩阵
            """
            self.headers = headers
            self.data = data
            print("数据已接收，列名：", headers)
#            print(len(self.data))
#            print(self.data)
            # 你可以在这里触发绘图或其他逻辑

    def closeEvent(self, event):
            """
            重写关闭事件，弹出确认对话框
            """
            # 创建确认对话框

            reply = QMessageBox.question(
                self,
                "Confirm Exit",  # Dialog title
                "Are you sure you want to quit the program?",  # Prompt text
                QMessageBox.Yes | QMessageBox.No,  # Buttons
                QMessageBox.No  # Default button
            )
    
            if reply == QMessageBox.Yes:
                event.accept()  # 确认关闭
            else:
                event.ignore()  # 取消关闭
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super(PyMainSub, self).__init__(parent)
        self.setupUi(self)
        self.main_window = parent
        self.value1=[]#values
        self.value2=[]#values
        self.value3=[]#values
        self.value4=[]#values
        self.value5=[]#values
        self.value6=[]#values
        self.allvalues=[]
        screen = QApplication.primaryScreen().availableGeometry()
        width = int(screen.width())
        height = int(screen.height())
        self.color=['blue','red','green','orange']
        # 设置窗口大小和位置（居中）
        self.setGeometry(
            int((screen.width() - width) / 2),  # x位置
            int((screen.height() - height) / 2), # y位置
            width,                              # 宽度
            height                              # 高度
        )
        
    
        
        self.groupBox_3.setGeometry(
            int(0),          # x坐标（左边界）
            int(height/50),       # y坐标（上边界）
            int(width/4-width/100),     # 宽度（按原比例）
            int(height/13)          # 高度（按原比例）
        )
 

        self.label.setGeometry(0,self.groupBox_3.height()/10,self.groupBox_3.width()/4,50)
        self.label_8.setGeometry(self.groupBox_3.width()/3,self.groupBox_3.height()/10,self.groupBox_3.width()/4,50)
        self.label_9.setGeometry(self.groupBox_3.width()*2/3,self.groupBox_3.height()/10,self.groupBox_3.width()/4,50)
        self.lineEdit.setGeometry(0,self.groupBox_3.height()/3+self.groupBox_3.height()/5,self.groupBox_3.width()/4,30)
        self.lineEdit_2.setGeometry(self.groupBox_3.width()/3,self.groupBox_3.height()/3+self.groupBox_3.height()/5,self.groupBox_3.width()/4,30)
        self.lineEdit_8.setGeometry(self.groupBox_3.width()*2/3,self.groupBox_3.height()/3+self.groupBox_3.height()/5,self.groupBox_3.width()/4,30)        
        self.label_3.setGeometry(0,height/4+height/50,width/20,height/20)
        self.lineEdit_4.setGeometry(width/20,height/4+height/50,width/20,height/20)
        self.label_4.setGeometry(width/10+width/50,height/4+height/50,width/20,height/20)
        self.lineEdit_5.setGeometry(width/20+width/10,height/4+height/50,width/20,height/20)
        
        self.groupBox.setGeometry(
            int(0),          # x坐标（左边界）
            int(height/13+height/25),       # y坐标（上边界）
            int(width/4-width/100),     # 宽度（按原比例）
            int(height/7)          # 高度（按原比例）
        )
        self.radioButton.setGeometry(0,self.groupBox.height()/10,self.groupBox.width(),50)
        self.radioButton_2.setGeometry(0,self.groupBox.height()*2/5,self.groupBox.width(),50)
        self.label_2.setGeometry(self.groupBox.width()/5, self.groupBox.height()*4/7, self.groupBox.width()/2, 50)
        self.lineEdit_3.setGeometry(self.groupBox.width()/5+self.groupBox.width()/3, self.groupBox.height()*2/3, self.groupBox.width()/5, 25)
                

        
        # ------------------- 步骤1：正确定义 groupBox_4 和布局容器 -------------------

        self.groupBox_2.setGeometry(
            int(width/4),          # x坐标（左边界）
            int(0),       # y坐标（上边界）
            int(width*3/4),     # 宽度（按原比例）
            int(height*95/300)          # 高度（按原比例）
        )
        
        # 定义布局容器（verticalLayoutWidget_7）并设置其充满 groupBox_4
        self.verticalLayoutWidget = QtWidgets.QWidget(self.groupBox_2)  # 父控件设为 groupBox_4
        self.verticalLayoutWidget.setGeometry(
            0, 0,  # x=0, y=0（容器左上角紧贴 groupBox_7 左上角）
            self.groupBox_2.width(),  # 容器宽度 = groupBox_7 宽度
            self.groupBox_2.height()  # 容器高度 = groupBox_7 高度
        )
        
        # ------------------- 步骤2：初始化垂直布局并绑定到容器 -------------------
        # 创建垂直布局（verticalLayout_3），并绑定到布局容器
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        # 清除布局内边距和间距（关键：避免容器内留白）
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)  # 上下左右内边距0
        self.verticalLayout.setSpacing(0)  # 控件间距0
        
        # ------------------- 步骤3：初始化 Matplotlib 画布并添加到布局 -------------------
        # 创建图形和画布
        self.figure = Figure(dpi=80)  # 高DPI确保清晰度
        self.canvas = FigureCanvas(self.figure)
        
        # 设置画布尺寸策略（强制填充布局）
        self.canvas.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,  # 水平方向扩展
            QtWidgets.QSizePolicy.Expanding   # 垂直方向扩展
        )
        
        # 将画布添加到布局（stretch=1 确保画布填充整个布局空间）
        self.verticalLayout.addWidget(self.canvas, stretch=1)
        
        # ------------------- 步骤4：同步画布与容器尺寸（窗口缩放时） -------------------
        def resize_canvas6():
            # 确保布局容器始终充满 groupBox_7
            self.verticalLayoutWidget.setGeometry(10, 30, 0.8*self.groupBox_2.width(), 0.8*self.groupBox_2.width()-870)
            
            # 同步 Matplotlib 图形尺寸（避免拉伸变形）
            canvas_width = self.canvas.width()
            canvas_height = self.canvas.height()
            self.figure.set_size_inches(canvas_width / self.figure.dpi, canvas_height / self.figure.dpi)
            self.canvas.draw()
        
        # 绑定窗口缩放事件（确保容器和画布尺寸同步更新）
        self.groupBox_2.resizeEvent = lambda event: resize_canvas6()
        
        self.pushButton.setGeometry(0.84*self.groupBox_2.width(), self.groupBox_2.height()/6, 0.15*self.groupBox_2.width(), 40)
        self.pushButton_2.setGeometry(0.84*self.groupBox_2.width(), self.groupBox_2.height()*2/6, 0.15*self.groupBox_2.width(), 40)
        self.pushButton_3.setGeometry(0.84*self.groupBox_2.width(), self.groupBox_2.height()*3/6, 0.15*self.groupBox_2.width(), 40)         
        
        
        
        # ------------------- 步骤1：正确定义 groupBox_4 和布局容器 -------------------

        self.groupBox_4.setGeometry(
            int(0),          # x坐标（左边界）
            int(height/3-10),       # y坐标（上边界）
            int(width*98/400),     # 宽度（按原比例）
            int(height/3)          # 高度（按原比例）
        )
        
        # 定义布局容器（verticalLayoutWidget_7）并设置其充满 groupBox_4
        self.verticalLayoutWidget_3 = QtWidgets.QWidget(self.groupBox_4)  # 父控件设为 groupBox_4
        self.verticalLayoutWidget_3.setGeometry(
            0, 0,  # x=0, y=0（容器左上角紧贴 groupBox_7 左上角）
            self.groupBox_4.width(),  # 容器宽度 = groupBox_7 宽度
            self.groupBox_4.height()  # 容器高度 = groupBox_7 高度
        )
        
        # ------------------- 步骤2：初始化垂直布局并绑定到容器 -------------------
        # 创建垂直布局（verticalLayout_3），并绑定到布局容器
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_3)
        # 清除布局内边距和间距（关键：避免容器内留白）
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)  # 上下左右内边距0
        self.verticalLayout_3.setSpacing(0)  # 控件间距0
        
        # ------------------- 步骤3：初始化 Matplotlib 画布并添加到布局 -------------------
        # 创建图形和画布
        self.figure2 = Figure(dpi=100)  # 高DPI确保清晰度
        self.canvas2 = FigureCanvas(self.figure2)
        
        # 设置画布尺寸策略（强制填充布局）
        self.canvas2.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,  # 水平方向扩展
            QtWidgets.QSizePolicy.Expanding   # 垂直方向扩展
        )
        
        # 将画布添加到布局（stretch=1 确保画布填充整个布局空间）
        self.verticalLayout_3.addWidget(self.canvas2, stretch=1)
        
        # ------------------- 步骤4：同步画布与容器尺寸（窗口缩放时） -------------------
        def resize_canvas5():
            # 确保布局容器始终充满 groupBox_7
            self.verticalLayoutWidget_3.setGeometry(10, 30, 0.8*self.groupBox_4.width(), 0.8*self.groupBox_4.width()-60)
            
            # 同步 Matplotlib 图形尺寸（避免拉伸变形）
            canvas_width = self.canvas2.width()
            canvas_height = self.canvas2.height()
            self.figure2.set_size_inches(canvas_width / self.figure2.dpi, canvas_height / self.figure2.dpi)
            self.canvas2.draw()
        
        # 绑定窗口缩放事件（确保容器和画布尺寸同步更新）
        self.groupBox_4.resizeEvent = lambda event: resize_canvas5()
        
        self.pushButton_4.setGeometry(0.84*self.groupBox_4.width(), self.groupBox_4.height()/6, 0.15*self.groupBox_4.width(), 40)
        self.pushButton_5.setGeometry(0.84*self.groupBox_4.width(), self.groupBox_4.height()*2/6, 0.15*self.groupBox_4.width(), 40)
        self.pushButton_6.setGeometry(0.84*self.groupBox_4.width(), self.groupBox_4.height()*3/6, 0.15*self.groupBox_4.width(), 40) 
        # ------------------- 步骤1：正确定义 groupBox_5 和布局容器 -------------------

        self.groupBox_5.setGeometry(
            int(width/4),          # x坐标（左边界）
            int(height/3-10),       # y坐标（上边界）
            int(width*98/400),     # 宽度（按原比例）
            int(height/3)          # 高度（按原比例）
        )
        
        # 定义布局容器（verticalLayoutWidget_7）并设置其充满 groupBox_5
        self.verticalLayoutWidget_4 = QtWidgets.QWidget(self.groupBox_5)  # 父控件设为 groupBox_6
        self.verticalLayoutWidget_4.setGeometry(
            0, 0,  # x=0, y=0（容器左上角紧贴 groupBox_7 左上角）
            self.groupBox_5.width(),  # 容器宽度 = groupBox_7 宽度
            self.groupBox_5.height()  # 容器高度 = groupBox_7 高度
        )
        
        # ------------------- 步骤2：初始化垂直布局并绑定到容器 -------------------
        # 创建垂直布局（verticalLayout_6），并绑定到布局容器
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_4)
        # 清除布局内边距和间距（关键：避免容器内留白）
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)  # 上下左右内边距0
        self.verticalLayout_6.setSpacing(0)  # 控件间距0
        
        # ------------------- 步骤3：初始化 Matplotlib 画布并添加到布局 -------------------
        # 创建图形和画布
        self.figure3 = Figure(dpi=100)  # 高DPI确保清晰度
        self.canvas3 = FigureCanvas(self.figure3)
        
        # 设置画布尺寸策略（强制填充布局）
        self.canvas3.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,  # 水平方向扩展
            QtWidgets.QSizePolicy.Expanding   # 垂直方向扩展
        )
        
        # 将画布添加到布局（stretch=1 确保画布填充整个布局空间）
        self.verticalLayout_6.addWidget(self.canvas3, stretch=1)
        
        # ------------------- 步骤4：同步画布与容器尺寸（窗口缩放时） -------------------
        def resize_canvas4():
            # 确保布局容器始终充满 groupBox_7
            self.verticalLayoutWidget_4.setGeometry(10, 30, 0.8*self.groupBox_5.width(), 0.8*self.groupBox_5.width()-60)
            
            # 同步 Matplotlib 图形尺寸（避免拉伸变形）
            canvas_width = self.canvas3.width()
            canvas_height = self.canvas3.height()
            self.figure3.set_size_inches(canvas_width / self.figure3.dpi, canvas_height / self.figure3.dpi)
            self.canvas3.draw()
        
        # 绑定窗口缩放事件（确保容器和画布尺寸同步更新）
        self.groupBox_5.resizeEvent = lambda event: resize_canvas4()
        
        self.pushButton_10.setGeometry(0.84*self.groupBox_5.width(), self.groupBox_5.height()/6, 0.15*self.groupBox_5.width(), 40)
        self.pushButton_11.setGeometry(0.84*self.groupBox_5.width(), self.groupBox_5.height()*2/6, 0.15*self.groupBox_5.width(), 40)
        self.pushButton_12.setGeometry(0.84*self.groupBox_5.width(), self.groupBox_5.height()*3/6, 0.15*self.groupBox_5.width(), 40) 
        
        # ------------------- 步骤1：正确定义 groupBox_69 和布局容器 -------------------

        self.groupBox_6.setGeometry(
            int(width/2),          # x坐标（左边界）
            int(height/3-10),       # y坐标（上边界）
            int(width*98/400),     # 宽度（按原比例）
            int(height/3)          # 高度（按原比例）
        )
        
        # 定义布局容器（verticalLayoutWidget_7）并设置其充满 groupBox_6
        self.verticalLayoutWidget_5 = QtWidgets.QWidget(self.groupBox_6)  # 父控件设为 groupBox_6
        self.verticalLayoutWidget_5.setGeometry(
            0, 0,  # x=0, y=0（容器左上角紧贴 groupBox_7 左上角）
            self.groupBox_6.width(),  # 容器宽度 = groupBox_7 宽度
            self.groupBox_6.height()  # 容器高度 = groupBox_7 高度
        )
        
        # ------------------- 步骤2：初始化垂直布局并绑定到容器 -------------------
        # 创建垂直布局（verticalLayout_7），并绑定到布局容器
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_5)
        # 清除布局内边距和间距（关键：避免容器内留白）
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)  # 上下左右内边距0
        self.verticalLayout_7.setSpacing(0)  # 控件间距0
        
        # ------------------- 步骤3：初始化 Matplotlib 画布并添加到布局 -------------------
        # 创建图形和画布
        self.figure4 = Figure(dpi=100)  # 高DPI确保清晰度
        self.canvas4 = FigureCanvas(self.figure4)
        
        # 设置画布尺寸策略（强制填充布局）
        self.canvas4.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,  # 水平方向扩展
            QtWidgets.QSizePolicy.Expanding   # 垂直方向扩展
        )
        
        # 将画布添加到布局（stretch=1 确保画布填充整个布局空间）
        self.verticalLayout_7.addWidget(self.canvas4, stretch=1)
        
        # ------------------- 步骤4：同步画布与容器尺寸（窗口缩放时） -------------------
        def resize_canvas3():
            # 确保布局容器始终充满 groupBox_7
            self.verticalLayoutWidget_5.setGeometry(10, 30, 0.8*self.groupBox_6.width(), 0.8*self.groupBox_6.width()-60)
            
            # 同步 Matplotlib 图形尺寸（避免拉伸变形）
            canvas_width = self.canvas4.width()
            canvas_height = self.canvas4.height()
            self.figure4.set_size_inches(canvas_width / self.figure4.dpi, canvas_height / self.figure4.dpi)
            self.canvas4.draw()
        
        # 绑定窗口缩放事件（确保容器和画布尺寸同步更新）
        self.groupBox_6.resizeEvent = lambda event: resize_canvas3()
        
        self.pushButton_13.setGeometry(0.84*self.groupBox_6.width(), self.groupBox_6.height()/6, 0.15*self.groupBox_6.width(), 40)
        self.pushButton_14.setGeometry(0.84*self.groupBox_6.width(), self.groupBox_6.height()*2/6, 0.15*self.groupBox_6.width(), 40)
        self.pushButton_15.setGeometry(0.84*self.groupBox_6.width(), self.groupBox_6.height()*3/6, 0.15*self.groupBox_6.width(), 40) 
        
 
       # ------------------- 步骤1：正确定义 groupBox_9 和布局容器 -------------------

        self.groupBox_8.setGeometry(
            int(width*3/4),          # x坐标（左边界）
            int(height/3-10),       # y坐标（上边界）
            int(width*98/400),     # 宽度（按原比例）
            int(height/3)          # 高度（按原比例）
        )
        
        # 定义布局容器（verticalLayoutWidget_7）并设置其充满 groupBox_8
        self.verticalLayoutWidget_7 = QtWidgets.QWidget(self.groupBox_8)  # 父控件设为 groupBox_8
        self.verticalLayoutWidget_7.setGeometry(
            0, 0,  # x=0, y=0（容器左上角紧贴 groupBox_7 左上角）
            self.groupBox_8.width(),  # 容器宽度 = groupBox_7 宽度
            self.groupBox_8.height()  # 容器高度 = groupBox_7 高度
        )
        
        # ------------------- 步骤2：初始化垂直布局并绑定到容器 -------------------
        # 创建垂直布局（verticalLayout_8），并绑定到布局容器
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_7)
        # 清除布局内边距和间距（关键：避免容器内留白）
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)  # 上下左右内边距0
        self.verticalLayout_9.setSpacing(0)  # 控件间距0
        
        # ------------------- 步骤3：初始化 Matplotlib 画布并添加到布局 -------------------
        # 创建图形和画布
        self.figure5 = Figure(dpi=100)  # 高DPI确保清晰度
        self.canvas5 = FigureCanvas(self.figure5)
        
        # 设置画布尺寸策略（强制填充布局）
        self.canvas5.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,  # 水平方向扩展
            QtWidgets.QSizePolicy.Expanding   # 垂直方向扩展
        )
        
        # 将画布添加到布局（stretch=1 确保画布填充整个布局空间）
        self.verticalLayout_9.addWidget(self.canvas5, stretch=1)
        
        # ------------------- 步骤4：同步画布与容器尺寸（窗口缩放时） -------------------
        def resize_canvas2():
            # 确保布局容器始终充满 groupBox_7
            self.verticalLayoutWidget_7.setGeometry(10, 30, 0.8*self.groupBox_8.width(), 0.8*self.groupBox_8.width()-60)
            
            # 同步 Matplotlib 图形尺寸（避免拉伸变形）
            canvas_width = self.canvas5.width()
            canvas_height = self.canvas5.height()
            self.figure5.set_size_inches(canvas_width / self.figure5.dpi, canvas_height / self.figure5.dpi)
            self.canvas5.draw()
        
        # 绑定窗口缩放事件（确保容器和画布尺寸同步更新）
        self.groupBox_8.resizeEvent = lambda event: resize_canvas2()
        
        self.pushButton_19.setGeometry(0.84*self.groupBox_8.width(), self.groupBox_8.height()/6, 0.15*self.groupBox_8.width(), 40)
        self.pushButton_20.setGeometry(0.84*self.groupBox_8.width(), self.groupBox_8.height()*2/6, 0.15*self.groupBox_8.width(), 40)
        self.pushButton_21.setGeometry(0.84*self.groupBox_8.width(), self.groupBox_8.height()*3/6, 0.15*self.groupBox_8.width(), 40) 

        # ------------------- 步骤1：正确定义 groupBox_9 和布局容器 -------------------

        self.groupBox_9.setGeometry(
            int(0),          # x坐标（左边界）
            int(2*height/3-10),       # y坐标（上边界）
            int(width*98/400),     # 宽度（按原比例）
            int(height/3)          # 高度（按原比例）
        )
        
        # 定义布局容器（verticalLayoutWidget_6）并设置其充满 groupBox_9
        self.verticalLayoutWidget_8 = QtWidgets.QWidget(self.groupBox_9)  # 父控件设为 groupBox_7
        self.verticalLayoutWidget_8.setGeometry(
            0, 0,  # x=0, y=0（容器左上角紧贴 groupBox_7 左上角）
            self.groupBox_9.width(),  # 容器宽度 = groupBox_7 宽度
            self.groupBox_9.height()  # 容器高度 = groupBox_7 高度
        )
        
        # ------------------- 步骤2：初始化垂直布局并绑定到容器 -------------------
        # 创建垂直布局（verticalLayout_8），并绑定到布局容器
        self.verticalLayout_10 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_8)
        # 清除布局内边距和间距（关键：避免容器内留白）
        self.verticalLayout_10.setContentsMargins(0, 0, 0, 0)  # 上下左右内边距0
        self.verticalLayout_10.setSpacing(0)  # 控件间距0
        
        # ------------------- 步骤3：初始化 Matplotlib 画布并添加到布局 -------------------
        # 创建图形和画布
        self.figure6 = Figure(dpi=100)  # 高DPI确保清晰度
        self.canvas6 = FigureCanvas(self.figure6)
        
        # 设置画布尺寸策略（强制填充布局）
        self.canvas6.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,  # 水平方向扩展
            QtWidgets.QSizePolicy.Expanding   # 垂直方向扩展
        )
        
        # 将画布添加到布局（stretch=1 确保画布填充整个布局空间）
        self.verticalLayout_10.addWidget(self.canvas6, stretch=1)
        
        # ------------------- 步骤4：同步画布与容器尺寸（窗口缩放时） -------------------
        def resize_canvas1():
            # 确保布局容器始终充满 groupBox_7
            self.verticalLayoutWidget_8.setGeometry(10, 30, 0.8*self.groupBox_9.width(), 0.8*self.groupBox_9.width()-60)
            
            # 同步 Matplotlib 图形尺寸（避免拉伸变形）
            canvas_width = self.canvas6.width()
            canvas_height = self.canvas6.height()
            self.figure6.set_size_inches(canvas_width / self.figure6.dpi, canvas_height / self.figure6.dpi)
            self.canvas6.draw()
        
        # 绑定窗口缩放事件（确保容器和画布尺寸同步更新）
        self.groupBox_9.resizeEvent = lambda event: resize_canvas1()
        
        self.pushButton_22.setGeometry(0.84*self.groupBox_9.width(), self.groupBox_9.height()/6, 0.15*self.groupBox_9.width(), 40)
        self.pushButton_23.setGeometry(0.84*self.groupBox_9.width(), self.groupBox_9.height()*2/6, 0.15*self.groupBox_9.width(), 40)
        self.pushButton_24.setGeometry(0.84*self.groupBox_9.width(), self.groupBox_9.height()*3/6, 0.15*self.groupBox_9.width(), 40)        


        # ------------------- 步骤1：正确定义 groupBox_7 和布局容器 -------------------

        self.groupBox_7.setGeometry(
            int(width/4),          # x坐标（左边界）
            int(2*height/3-10),       # y坐标（上边界）
            int(width*98/400),     # 宽度（按原比例）
            int(height/3)          # 高度（按原比例）
        )
        
        # 定义布局容器（verticalLayoutWidget_6）并设置其充满 groupBox_7
        self.verticalLayoutWidget_6 = QtWidgets.QWidget(self.groupBox_7)  # 父控件设为 groupBox_7
        self.verticalLayoutWidget_6.setGeometry(
            0, 0,  # x=0, y=0（容器左上角紧贴 groupBox_7 左上角）
            self.groupBox_7.width(),  # 容器宽度 = groupBox_7 宽度
            self.groupBox_7.height()  # 容器高度 = groupBox_7 高度
        )
        
        # ------------------- 步骤2：初始化垂直布局并绑定到容器 -------------------
        # 创建垂直布局（verticalLayout_8），并绑定到布局容器
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_6)
        # 清除布局内边距和间距（关键：避免容器内留白）
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)  # 上下左右内边距0
        self.verticalLayout_8.setSpacing(0)  # 控件间距0
        
        # ------------------- 步骤3：初始化 Matplotlib 画布并添加到布局 -------------------
        # 创建图形和画布
        self.figure7 = Figure(dpi=100)  # 高DPI确保清晰度
        self.canvas7 = FigureCanvas(self.figure7)
        
        # 设置画布尺寸策略（强制填充布局）
        self.canvas7.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,  # 水平方向扩展
            QtWidgets.QSizePolicy.Expanding   # 垂直方向扩展
        )
        
        # 将画布添加到布局（stretch=1 确保画布填充整个布局空间）
        self.verticalLayout_8.addWidget(self.canvas7, stretch=1)
        
        # ------------------- 步骤4：同步画布与容器尺寸（窗口缩放时） -------------------
        def resize_canvas():
            # 确保布局容器始终充满 groupBox_7
            self.verticalLayoutWidget_6.setGeometry(10, 30, 0.8*self.groupBox_7.width(), 0.8*self.groupBox_7.width()-60)
            
            # 同步 Matplotlib 图形尺寸（避免拉伸变形）
            canvas_width = self.canvas7.width()
            canvas_height = self.canvas7.height()
            self.figure7.set_size_inches(canvas_width / self.figure7.dpi, canvas_height / self.figure7.dpi)
            self.canvas7.draw()
        
        # 绑定窗口缩放事件（确保容器和画布尺寸同步更新）
        self.groupBox_7.resizeEvent = lambda event: resize_canvas()
        
        self.pushButton_16.setGeometry(0.84*self.groupBox_7.width(), self.groupBox_7.height()/6, 0.15*self.groupBox_7.width(), 40)
        self.pushButton_17.setGeometry(0.84*self.groupBox_7.width(), self.groupBox_7.height()*2/6, 0.15*self.groupBox_7.width(), 40)
        self.pushButton_18.setGeometry(0.84*self.groupBox_7.width(), self.groupBox_7.height()*3/6, 0.15*self.groupBox_7.width(), 40)
        
        self.tableView.setGeometry(width/2, 2*height/3, width*11/23, height/4)
        self.pushButton_25.setGeometry(width/2+width*16/(23*6), 2*height/3+height/4, width*11/(23*6), height/25)
        self.pushButton_26.setGeometry(width/2+width*16/(23*6)+width*13/(23*6), 2*height/3+height/4, width*11/(23*6), height/25)
        self.pushButton_27.setGeometry(width/2+width*16/(23*6)+width*26/(23*6), 2*height/3+height/4, width*11/(23*6), height/25)
        # 设置窗口不可改变大小
        self.setFixedSize(width, height)  
    def kde_pdf(self,ages, T, bandwidth=50):
        """Compute KDE over grid T using ages from age_vec with fixed bandwidth."""
        ages = np.array(ages)
        # Gaussian KDE: bw_method 是乘在样本标准差上的因子
        kde = gaussian_kde(ages, bw_method=bandwidth / ages.std(ddof=1))
        pdf_values = kde(T)
        pdf_values /= pdf_values.sum()  # normalize
        return pdf_values    
    @pyqtSlot()
    def on_pushButton_16_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        print('你好')
#        print(self.aaa)
#        print(len(self.aaa))
        show_original = True
        
        self.value_ks=[]
        
        min_age = int(self.lineEdit.text())
        max_age = int(self.lineEdit_2.text())
#        dT_value = int(self.lineEdit_8.text())
#        self.age_range = [min_age, max_age]
#        self.dT = dT_value
#        self.T = np.zeros((self.age_range[1] - self.age_range[0]) // self.dT)
        num = (len(self.headers)-2)//2
        if num == 2:
            self.aa = []
            Ratio_A = []
            self.value6=[]
            self.canvas7.figure.clear()
#            print(self.aaa[0])
            for j in range (len(self.aaa6)):
                for i in range(101):
                    Ratio_A.append(i/100)
                    ksks=lk.Likeness(self.np_sample, (i/100)*self.aaa6[j][0] + ((100-i)/100)*(i/100)*self.aaa6[j][1])
                    
                    self.aa.append(ksks)
#            print(self.aa)
#            print(len(self.aa))
            
            self.max_aa = np.max(np.array(self.aa)[~np.isnan(self.aa)])
            self.max_aa_index=np.argmax(np.array(self.aa)[~np.isnan(self.aa)])
            print(self.max_aa_index)
            self.max_Ratio_A=Ratio_A[self.max_aa_index]
            #self.value_ks.append[max_Ratio_A,1-max_Ratio_A,max_aa]

            print(self.max_Ratio_A,1-self.max_Ratio_A,self.max_aa)
            self.value6.append('Likeness')
            self.value6.append(self.max_Ratio_A)
            self.value6.append(1-self.max_Ratio_A)
            self.value6.append(self.max_aa)
            # 数据处理和插值（保持不变）
            x_data = np.clip(Ratio_A, 0, 1)
            z_data = np.clip(self.aa, 0, 1)
            sorted_indices = np.argsort(x_data)
            x_sorted, z_sorted = x_data[sorted_indices], z_data[sorted_indices]
            _, unique_mask = np.unique(x_sorted, return_index=True)
            x_unique, z_unique = x_sorted[unique_mask], z_sorted[unique_mask]
            
            if len(x_unique) >= 2:
                from scipy.interpolate import interp1d
                x_interp = np.linspace(0, 1, 1000)
                interp_func = interp1d(x_unique, z_unique, kind="linear", bounds_error=False, fill_value=0.5)
                z_interp = interp_func(x_interp)
                
                # 绘制条带图（保持不变）
                ax = self.canvas7.figure.add_subplot(111)
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.set_yticks([0.5])
                ax.set_yticklabels([self.headers[0]], rotation=90, va="top")
                ax.set_xlabel(self.headers[2], fontsize=10, labelpad=3)
                
                ax_top = ax.twiny()
                ax_top.set_xlim(0, 1)
                ax_top.set_xlabel(self.headers[4], fontsize=10, labelpad=3)
                ax_top.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
                ax_top.set_xticklabels([1.0, 0.8, 0.6, 0.4, 0.2, 0.0])
                ax_top.set_title(str(self.max_Ratio_A)+"_"+str(1-self.max_Ratio_A)+"_ "+str(self.max_aa))
                
                cmap = plt.cm.get_cmap("viridis")
                norm = plt.Normalize(0, 1)
                ax.pcolormesh(
                    x_interp, [0.0, 1.0], z_interp.reshape(1, -1),
                    cmap=cmap, norm=norm, shading="auto", alpha=0.9
                )
                
                if show_original:
                    ax.vlines(x=x_data, ymin=0, ymax=1.0, color="gray", linewidth=0.8, alpha=0.4)
                
                # 颜色条（保持不变）
                sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
                sm.set_array([])
                # 创建水平颜色条（关键参数：orientation="horizontal"）
                cbar = plt.colorbar(
                    sm, 
                    ax=ax, 
                    pad=0.2,                # 颜色条与主图的间距（垂直方向，因水平放置）
                    orientation="horizontal", 
                    aspect=30,
                    shrink=0.8 # 颜色条的长宽比（数值越大越扁长，适配主图宽度）
                )
                cbar.set_label("Likeness", rotation=0, labelpad=5)
                
                
                # 调整边距（使用 canvas6.figure）
                self.canvas7.figure.set_constrained_layout(True)
        
        # 4. 刷新画布
        #plt.tight_layout()
                self.canvas7.draw()
                
                self.canvas.figure.clear()
                gs = gridspec.GridSpec(1, 2, width_ratios=[2, 1], wspace=0.3) 
                
                # 第一个子图（占据2/3宽度）
                ax1 = self.canvas.figure.add_subplot(gs[0])
                inter=self.max_aa_index//101
                print(inter)
              
                self.all=self.max_Ratio_A*self.aaa6[inter][0]+(1-self.max_Ratio_A)*self.aaa6[inter][1]
                print(self.all)
                ax1.plot(self.T, self.all, color='blue', label='option model')  
                ax1.plot(self.T, self.np_sample, color='black', label=self.headers[0])
                ax1.set_xlabel("Zircon U-Pb age (Ma)")
                if self.radioButton.isChecked():
                    ax1.set_ylabel("PDF")
                if self.radioButton_2.isChecked():
                    ax1.set_ylabel("KDE")
   
                ax1.legend()
                    # 关键：设置x轴间隔为100（每100ma一个刻度）
                ax1.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
                ax1.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
                ax1.set_xlim(min_age, max_age)
                ax1.set_ylim(bottom=0)
                
                # 第二个子图（占据1/3宽度）
                ax2 = self.canvas.figure.add_subplot(gs[1])
                
                ax2.plot(self.T, np.cumsum(self.all), color='blue', label='option model')  
#        
                ax2.plot(self.T, self.cdf_value_sample, color='black', label=self.headers[0])
                ax2.set_xlabel("Zircon U-Pb age (Ma)")
                ax2.set_ylabel("CDFs")
                ax2.legend()
                ax2.set_xlim(min_age, max_age)
                ax2.set_ylim(0,1)
                ax2.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
                ax2.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
                
                self.canvas.figure.set_constrained_layout(True)
                   # 5. 关键优化：调整整个图形的边距和布局
                #plt.subplots_adjust(left=0.08, right=0.95, top=0.92, bottom=0.2)  # 手动调整边距
                self.canvas.draw()
                

                
        if num == 3:
            self.ratios = []  # 存储所有 [A, B, C] 比例
            self.aa = []      # 存储所有相似度值
            self.value6=[]
            self.canvas7.figure.clear()  # 清空 canvas6 画布

            print(len(self.aaa6))
            for mmm in range (len(self.aaa6)):
                            # 生成 A/B/C 比例和相似度值
                for i in range(101):     
                    for j in range(101 - i):
                        self.ratios.append([i/100, j/100, (100 - i - j)/100])  # A, B, C 比例
                        self.aa.append(lk.Likeness(self.np_sample, 
                                    (i/100)*self.aaa6[mmm][0] + 
                                    (j/100)*self.aaa6[mmm][1] + 
                                    ((100-i-j)/100)*self.aaa6[mmm][2]
                                ))
    #            print(self.aa)
#            print(len(self.aa))
    
            print(self.aa)
            print(len(self.aa))
                        # ---------------------- 提取数据并计算三元坐标 ----------------------
            ratios_np = np.array(self.ratios)  # (N, 3)：A, B, C 列
            A, B, C = ratios_np[:, 0], ratios_np[:, 1], ratios_np[:, 2]
            values = np.array(self.aa)  # 相似度值
                    
            # 三元坐标投影（将 A/B/C 转换为 2D 平面坐标）
            denominator = A + B + C + 1e-12  # 避免除零
            x = 0.5 * (2 * B + C) / denominator  # 三元图 x 坐标
            y = (np.sqrt(3) / 2) * C / denominator  # 三元图 y 坐标
                    
            # ---------------------- 找到最高相似度点 ----------------------
            idx_max = np.argmax(values)
            x_max, y_max = x[idx_max], y[idx_max]  # 最高相似度点坐标
            A_max, B_max, C_max = A[idx_max], B[idx_max], C[idx_max]  # 最优比例
            self.value6.append('Likeness')
            self.value6.append(A_max)
            self.value6.append(B_max)
            self.value6.append(C_max)
            self.value6.append(max(self.aa))            
                                                        
            print("最高相似度点比例：")
            print(f"A={A_max:.3f}, B={B_max:.3f}, C={C_max:.3f}")
            print(f"最高相似度值：{values[idx_max]:.4f}")
            
            # ---------------------- 在 canvas6 中绘制三元相图 ----------------------
            # 创建子图（替换原 plt.figure() 和 ax = plt.subplot()）
            ax = self.canvas7.figure.add_subplot(111)  # 使用 canvas6 的 figure 添加子图
                    
            # 1. 绘制插值网格背景（平滑颜色）
            grid_x, grid_y = np.mgrid[0:1:200j, 0:np.sqrt(3)/2:200j]
            grid_z = griddata((x, y), values, (grid_x, grid_y), method='linear')
            #grid_z = np.nan_to_num(grid_z, nan=0.0)  # NaN用0填充（或用values.min()）
            ax.pcolormesh(grid_x, grid_y, grid_z, cmap='viridis', alpha=0.8, shading='gouraud',  vmin=0,vmax=1)
                    
            # 2. 绘制三角边界（等边三角形）
            triangle = np.array([[0, 0], [1, 0], [0.5, np.sqrt(3)/2], [0, 0]])
            ax.plot(triangle[:, 0], triangle[:, 1], 'k-', linewidth=1.5)
                    
            # 3. 绘制原始数据点（可选）
            ax.scatter(x, y, c=values, cmap='viridis', s=5, alpha=0.3,  vmin=0,vmax=1)
                    
            # 4. 标记最高相似度点（红色五角星）
            ax.scatter(x_max, y_max, marker="*", c="red", s=200, edgecolor="k", label="最高相似度点")
                    
            # 5. 添加 A/B/C 轴刻度和标签
            n_ticks = 5
            tick_values = np.linspace(0, 1, n_ticks + 1)
                    
            # A 轴刻度（左下 -> 上顶点）
            for t in tick_values[1:-1]:
                x_tick = 0.5 * (1 - t)
                y_tick = (np.sqrt(3)/2) * (1 - t)
                ax.plot([x_tick, x_tick - 0.02], [y_tick, y_tick], 'k-', linewidth=0.8)
                ax.text(x_tick - 0.04, y_tick, f"{t:.1f}", fontsize=9, ha="right", va="center")
                    
            # B 轴刻度（右下 -> 上顶点）
            for t in tick_values[1:-1]:
                x_tick = 0.5 * (1 + t)
                y_tick = (np.sqrt(3)/2) * (1 - t)
                ax.plot([x_tick, x_tick + 0.02], [y_tick, y_tick], 'k-', linewidth=0.8)
                ax.text(x_tick + 0.04, y_tick, f"{t:.1f}", fontsize=9, ha="left", va="center")
                    
            # C 轴刻度（底部 -> 上顶点）
            for t in tick_values[1:-1]:
                x_tick = t
                y_tick = 0
                ax.plot([x_tick, x_tick], [y_tick, y_tick - 0.02], 'k-', linewidth=0.8)
                ax.text(x_tick, y_tick - 0.05, f"{t:.1f}", fontsize=9, ha="center", va="top")
                    
            # 顶点标签（A/B/C）
            ax.text(-0.05, -0.05, self.headers[2], fontsize=12, ha="right", va="top", fontweight="bold")
            ax.text(1.05, -0.05, self.headers[4], fontsize=12, ha="left", va="top", fontweight="bold")
            ax.text(0.5, np.sqrt(3)/2 + 0.05, self.headers[6], fontsize=12, ha="center", va="bottom", fontweight="bold")
                    
            # ---------------------- 图表设置 ----------------------
            #ax.set_title(f"三元相图 (最高相似度: {max(values):.4f})", fontsize=12, pad=20)
            ax.set_aspect("equal")  # 等比例坐标轴（保证三角形为正三角形）
            ax.axis("off")  # 关闭默认坐标轴
                    
            # 添加颜色条（绑定到 canvas6 的 figure）
            #sm = plt.cm.ScalarMappable(cmap='viridis', norm=plt.Normalize(values.min(), values.max()))
            sm = plt.cm.ScalarMappable(cmap='viridis', norm=plt.Normalize(0,1))
            sm.set_array([])
            cbar = self.canvas7.figure.colorbar(sm, ax=ax, pad=0.05, orientation="horizontal", aspect=40)
            cbar.set_label("Likeness", rotation=0, labelpad=10)
                    
            # 调整布局（防止标签被裁剪）
            self.canvas7.figure.set_constrained_layout(True)
                    
            # ---------------------- 刷新 canvas6 画布 ----------------------
            self.canvas7.draw()
            self.canvas.figure.clear()
            gs = gridspec.GridSpec(1, 2, width_ratios=[2, 1], wspace=0.3) 

                
            # 第一个子图（占据2/3宽度）
            print(idx_max)
            ax1 = self.canvas.figure.add_subplot(gs[0])
            inter=idx_max//5151
            print(inter)
            #print(self.aaa[3])
            self.all=A_max*self.aaa6[inter][0]+B_max*self.aaa6[inter][1]+C_max*self.aaa6[inter][2]
            print(self.all)
            ax1.plot(self.T, self.all, color='blue', label='option model')  
            ax1.plot(self.T, self.np_sample, color='black', label=self.headers[0])
            ax1.set_xlabel("Zircon U-Pb age (Ma)")
            if self.radioButton.isChecked():
                ax1.set_ylabel("PDF")
            if self.radioButton_2.isChecked():
                ax1.set_ylabel("KDE")
            ax1.legend()
                    # 关键：设置x轴间隔为100（每100ma一个刻度）
            ax1.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
            ax1.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
            ax1.set_xlim(min_age, max_age)
            ax1.set_ylim(bottom=0)
                
                # 第二个子图（占据1/3宽度）
            ax2 = self.canvas.figure.add_subplot(gs[1])
                
            ax2.plot(self.T, np.cumsum(self.all), color='blue', label='option model')  
#        
            ax2.plot(self.T, self.cdf_value_sample, color='black', label=self.headers[0])
            ax2.set_xlabel("Zircon U-Pb age (Ma)")
            ax2.set_ylabel("CDFs")
            ax2.legend()
            ax2.set_xlim(min_age, max_age)
            ax2.set_ylim(0,1)
            ax2.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
            ax2.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
                
            self.canvas.figure.set_constrained_layout(True)
                   # 5. 关键优化：调整整个图形的边距和布局
                #plt.subplots_adjust(left=0.08, right=0.95, top=0.92, bottom=0.2)  # 手动调整边距
            self.canvas.draw()                    
        if num == 4:
            
            
            
                    # ---------------------- 初始化空列表（放在循环外！） ----------------------
            self.ratios = []  # 存储所有 [A, B, C] 比例
            self.aa = []      # 存储所有相似度值
            self.value6=[]
            self.canvas7.figure.clear()  # 清空 canvas6 画布
            SUM=0
            print(len(self.aaa6))
            for mmm in range (len(self.aaa6)):       
            # 生成 A/B/C 比例和相似度值
                for i in range(0,101,5):     
                    for j in range(0,101 - i,3):
                        for k in range(101-i-j):
                            SUM+=1
                            self.ratios.append([i/100, j/100, k/100, (100-i-j-k)/100])  # A, B, C 比例
                            self.aa.append(lk.Likeness(self.np_sample, 
                                        (i/100)*self.aaa6[mmm][0] + 
                                        (j/100)*self.aaa6[mmm][1] + 
                                        (k/100)*self.aaa6[mmm][2]+((100-i-j-k)/100)*self.aaa6[mmm][3]
                                    ))
            print(str(SUM)+"次")
                    
            # ---------------------- 提取数据并计算三元坐标 ----------------------
            print(self.ratios)

            ratios_np = np.array(self.ratios)  # (N, 4)：A, B, C, D 列
            print(ratios_np)
            A, B, C, D = ratios_np[:, 0], ratios_np[:, 1], ratios_np[:, 2], ratios_np[:, 3]
            print(A)
            values = np.array(self.aa)  # 相似度值  

            
            # ---------------------- 找到相似度最高点 ----------------------
            idx_max = np.argmax(values)
            A_max, B_max, C_max, D_max = A[idx_max], B[idx_max], C[idx_max], D[idx_max]
            self.value6.append('Likeness')
            self.value6.append(A_max)
            self.value6.append(B_max)
            self.value6.append(C_max)
            self.value6.append(D_max)
            self.value6.append(max(self.aa))  
            print("相似度最高点的比例：")
            print(f"A={A_max:.3f}, B={B_max:.3f}, C={C_max:.3f}, D={D_max:.3f}")
            
            # ---------------------- 创建仅包含3D四面体的画布 ----------------------
            
            
            # --------------------------------------------
            # 3D四面体展示（无坐标轴，添加刻度）
            # --------------------------------------------
            #ax1 = fig.add_subplot(111, projection='3d')  # 仅一个子图
            ax1 = self.canvas7.figure.add_subplot(111, projection='3d')  # 使用 canvas6 的 figure 添加子图
            # 四面体顶点坐标（保留原始定义）
            vertices = np.array([
                [0, 0, 0],    # A
                [1, 0, 0],    # B
                [0.5, np.sqrt(3)/2, 0],  # C
                [0.5, np.sqrt(3)/6, np.sqrt(6)/3]  # D
            ])
            
            # 绘制四面体边
            edges = [
                [vertices[0], vertices[1]],  # A-B
                [vertices[0], vertices[2]],  # A-C
                [vertices[0], vertices[3]],  # A-D
                [vertices[1], vertices[2]],  # B-C
                [vertices[1], vertices[3]],  # B-D
                [vertices[2], vertices[3]]   # C-D
            ]
            for edge in edges:
                ax1.plot3D(*zip(*edge), 'k-', linewidth=1.5)
            
            # 计算3D坐标（四面体坐标）
            x = A * vertices[0,0] + B * vertices[1,0] + C * vertices[2,0] + D * vertices[3,0]
            y = A * vertices[0,1] + B * vertices[1,1] + C * vertices[2,1] + D * vertices[3,1]
            z = A * vertices[0,2] + B * vertices[1,2] + C * vertices[2,2] + D * vertices[3,2]

            # 绘制散点图
            ax1.scatter(x, y, z, c=values, cmap='viridis', s=5, alpha=0.3, vmin=0,vmax=1)

            # 最高点
            ax1.scatter(
                x[idx_max], y[idx_max], z[idx_max], 
                marker='*', c='red', s=100, edgecolor='k'
            )

            
            # 添加刻度标签到棱上
            def add_ticks(ax, start, end, ticks=5, label=""):
                """在棱上添加刻度标签"""
                direction = end - start
                length = np.linalg.norm(direction)
                unit_vector = direction / length
                
                # 添加刻度线
                for i in range(1, ticks):
                    fraction = i / ticks
                    position = start + fraction * direction
                    
                    # 计算刻度线方向（与棱垂直）
                    # 简单起见，使用XY平面的垂直方向
                    if np.allclose(direction[:2], [0, 0]):  # 如果是垂直棱
                        tick_dir = np.array([1, 0, 0])
                    else:
                        tick_dir = np.array([-direction[1], direction[0], 0])
                        tick_dir = tick_dir / np.linalg.norm(tick_dir[:2])
                    
                    tick_size = 0.03
                    tick_start = position - tick_size * tick_dir
                    tick_end = position + tick_size * tick_dir
                    ax.plot3D(*zip(tick_start, tick_end), 'k-', linewidth=0.8)
                    
                    # 添加刻度标签
#                    label_pos = position + 0.1 * tick_dir
#                    ax.text(*label_pos, f"{fraction:.1f}", fontsize=8, ha='center', va='center')
                
                # 添加端点标签
                ax.text(*(start - 0.05 * unit_vector), "0", fontsize=8, ha='right', va='center')
                ax.text(*(end + 0.05 * unit_vector), "1", fontsize=8, ha='left', va='center')
                ax.text(*((start + end)/2 + 0.1 * tick_dir), label, fontsize=8, ha='center', va='center')
            
            # 在每条棱上添加刻度
            add_ticks(ax1, vertices[0], vertices[1], label="")  # A-B棱
            add_ticks(ax1, vertices[0], vertices[2], label="")  # A-C棱
            add_ticks(ax1, vertices[0], vertices[3], label="")  # A-D棱
            add_ticks(ax1, vertices[1], vertices[2], label="")  # B-C棱
            add_ticks(ax1, vertices[1], vertices[3], label="")  # B-D棱
            add_ticks(ax1, vertices[2], vertices[3], label="")  # C-D棱
            
            # 添加顶点标签
            # ax1.text(*vertices[0], "A", fontsize=14, ha='right', va='top', weight='bold')
            # ax1.text(*vertices[1], "B", fontsize=14, ha='left', va='top', weight='bold')
            # ax1.text(*vertices[2], "C", fontsize=14, ha='center', va='bottom', weight='bold')
            # ax1.text(*vertices[3], "D", fontsize=14, ha='center', va='top', weight='bold')
            # 添加顶点标签（带偏移量）
            offset = 0.2  # 偏移量，可以根据需要调整
            
            # A点标签（左下角）
            ax1.text(vertices[0][0]-offset, vertices[0][1]-offset, vertices[0][2]-offset, 
                     self.headers[2], fontsize=10, ha='right', va='top', weight='bold')
            
            # B点标签（右下角）
            ax1.text(vertices[1][0]+offset, vertices[1][1]-offset, vertices[1][2]-offset, 
                     self.headers[4], fontsize=10, ha='left', va='top', weight='bold')
            
            # C点标签（顶部）
            ax1.text(vertices[2][0], vertices[2][1]+offset, vertices[2][2]-offset, 
                     self.headers[6], fontsize=10, ha='center', va='bottom', weight='bold')  # 修复了重复的va参数
            
            # D点标签（上方）
            ax1.text(vertices[3][0], vertices[3][1], vertices[3][2]+offset, 
                     self.headers[8], fontsize=10, ha='center', va='bottom', weight='bold')
            
            #ax1.set_title("四元比例四面体图 (带刻度)")
            ax1.axis('off')  # 关闭坐标轴
            ax1.view_init(25, 90)  # 设置视角
            #ax1.legend()
            sm = plt.cm.ScalarMappable(cmap='viridis', norm=plt.Normalize(0,1))
            sm.set_array([])
            cbar = self.canvas6.figure.colorbar(
                sm, 
                ax=ax1, 
                pad=0.05,          # 与图形的间距
                aspect=40,         # 核心：减小aspect值（默认20，值越小颜色条越“短粗”）
                orientation="horizontal"
               
            )
            cbar.set_label("Likeness", rotation=0, labelpad=5)  # 标签水平放置，更易读
            
            # 调整布局（防止标签被裁剪）
            self.canvas7.figure.set_constrained_layout(True)
                    
            # ---------------------- 刷新 canvas6 画布 ----------------------
            self.canvas7.draw()


            self.canvas.figure.clear()
            

                    
            # 创建1行2列的网格，宽度比例为2:1
            gs = gridspec.GridSpec(1, 2, width_ratios=[2, 1], wspace=0.3) 
                    
            # 第一个子图（占据2/3宽度）
            ax1 = self.canvas.figure.add_subplot(gs[0])

            print(idx_max)
            
            inter=idx_max//12852
            print(inter)
            #print(self.aaa[3])
            self.all=A_max*self.aaa6[inter][0]+B_max*self.aaa6[inter][1]+C_max*self.aaa6[inter][2]+D_max*self.aaa6[inter][2]
            print(self.all)
            ax1.plot(self.T, self.all, color='blue', label='option model')  
       
            ax1.plot(self.T, self.np_sample, color='black', label=self.headers[0])
            ax1.set_xlabel("Zircon U-Pb age (Ma)")
            if self.radioButton.isChecked():
                ax1.set_ylabel("PDF")
            if self.radioButton_2.isChecked():
                ax1.set_ylabel("KDE")
            ax1.legend()
                        # 关键：设置x轴间隔为100（每100ma一个刻度）
            ax1.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
            ax1.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
            ax1.set_xlim(min_age, max_age)
            ax1.set_ylim(bottom=0)
                    
            # 第二个子图（占据1/3宽度）
            ax2 = self.canvas.figure.add_subplot(gs[1])
                
            ax2.plot(self.T, np.cumsum(self.all), color='blue', label='option model')  
#        
            ax2.plot(self.T, self.cdf_value_sample, color='black', label=self.headers[0])
            ax2.set_xlabel("Zircon U-Pb age (Ma)")
            ax2.set_ylabel("CDFs")
            ax2.legend()
            ax2.set_xlim(min_age, max_age)
            ax2.set_ylim(0,1)
            ax2.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
            ax2.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度


                # 调整子图间距
            self.canvas.figure.set_constrained_layout(True)
                   # 5. 关键优化：调整整个图形的边距和布局
                #plt.subplots_adjust(left=0.08, right=0.95, top=0.92, bottom=0.2)  # 手动调整边距
            self.canvas.draw()
    
    @pyqtSlot()
    def on_pushButton_17_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.canvas7.figure.clear()
        self.canvas7.draw() 
        self.value6=[]
    
    @pyqtSlot()
    def on_pushButton_18_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        file_path, ok=  QFileDialog.getSaveFileName(self,"Import","" ,"PDF File (*.pdf);;image(*.jpg);;all files(*.*)")   
        print(file_path.strip())
        #判断有点问题可以重新检查下
        if file_path.strip()=='':
            QMessageBox.warning(self, 'Waring', 'Failed!')
        else:
            self.save=self.figure7.savefig(file_path)
            #print(self.save)
            QMessageBox.information(self,'Save','Sucessful!')
    
    @pyqtSlot()
    def on_pushButton_13_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        print('你好')
#        print(self.aaa)
#        print(len(self.aaa))
        show_original = True
        
        self.value_ks=[]
        
        min_age = int(self.lineEdit.text())
        max_age = int(self.lineEdit_2.text())
#        dT_value = int(self.lineEdit_8.text())
#        self.age_range = [min_age, max_age]
#        self.dT = dT_value
#        self.T = np.zeros((self.age_range[1] - self.age_range[0]) // self.dT)
            
            
        num = (len(self.headers)-2)//2
        if num == 2:
            self.aa = []
            Ratio_A = []
            self.value3=[]
                       
            
            self.slope=[]
            self.intercept=[]
            self.canvas4.figure.clear()

#            print(self.aaa[0])
            for j in range (len(self.aaa3)):
                for i in range(101):
                    Ratio_A.append(i/100)
                    ksks=r.calculate_cross_correlation(self.np_sample, (i/100)*self.aaa3[j][0] + ((100-i)/100)*(i/100)*self.aaa3[j][1])[0]
                    
                    self.aa.append(ksks)
                    
                    ssss=r.calculate_cross_correlation(self.np_sample, (i/100)*self.aaa3[j][0] + ((100-i)/100)*(i/100)*self.aaa3[j][1])[1]
                    self.slope.append(ssss)
                    
                    kkkk=r.calculate_cross_correlation(self.np_sample, (i/100)*self.aaa3[j][0] + ((100-i)/100)*(i/100)*self.aaa3[j][1])[2]
                    self.intercept.append(kkkk)
#            print(len(self.aa))
            
            self.max_aa=np.max(self.aa)
            self.max_aa_index=np.argmax(self.aa)
            self.max_Ratio_A=Ratio_A[self.max_aa_index]
            self.max_slope=self.slope[self.max_aa_index]
            self.max_intercept=self.intercept[self.max_aa_index]
            #self.value_ks.append[max_Ratio_A,1-max_Ratio_A,max_aa]
            print(self.aa)
            print(self.max_Ratio_A,1-self.max_Ratio_A,self.max_aa)
            self.value3.append('Cross')
            self.value3.append(self.max_Ratio_A)
            self.value3.append(1-self.max_Ratio_A)
            self.value3.append(self.max_aa)
            # 数据处理和插值（保持不变）
            x_data = np.clip(Ratio_A, 0, 1)
            z_data = np.clip(self.aa, 0, 1)
            sorted_indices = np.argsort(x_data)
            x_sorted, z_sorted = x_data[sorted_indices], z_data[sorted_indices]
            _, unique_mask = np.unique(x_sorted, return_index=True)
            x_unique, z_unique = x_sorted[unique_mask], z_sorted[unique_mask]
            
            if len(x_unique) >= 2:
                from scipy.interpolate import interp1d
                x_interp = np.linspace(0, 1, 1000)
                interp_func = interp1d(x_unique, z_unique, kind="linear", bounds_error=False, fill_value=0.5)
                z_interp = interp_func(x_interp)
                
                # 绘制条带图（保持不变）
                ax = self.canvas4.figure.add_subplot(111)
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.set_yticks([0.5])
                ax.set_yticklabels([self.headers[0]], rotation=90, va="top")
                ax.set_xlabel(self.headers[2], fontsize=10, labelpad=3)
                
                ax_top = ax.twiny()
                ax_top.set_xlim(0, 1)
                ax_top.set_xlabel(self.headers[4], fontsize=10, labelpad=3)
                ax_top.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
                ax_top.set_xticklabels([1.0, 0.8, 0.6, 0.4, 0.2, 0.0])
                ax_top.set_title(str(self.max_Ratio_A)+"_"+str(1-self.max_Ratio_A)+"_ "+str(self.max_aa))
                
                cmap = plt.cm.get_cmap("viridis")
                norm = plt.Normalize(0, 1)
                ax.pcolormesh(
                    x_interp, [0.0, 1.0], z_interp.reshape(1, -1),
                    cmap=cmap, norm=norm, shading="auto", alpha=0.9
                )
                
                if show_original:
                    ax.vlines(x=x_data, ymin=0, ymax=1.0, color="gray", linewidth=0.8, alpha=0.4)
                
                # 颜色条（保持不变）
                sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
                sm.set_array([])
                # 创建水平颜色条（关键参数：orientation="horizontal"）
                cbar = plt.colorbar(
                    sm, 
                    ax=ax, 
                    pad=0.2,                # 颜色条与主图的间距（垂直方向，因水平放置）
                    orientation="horizontal", 
                    aspect=30,
                    shrink=0.8 # 颜色条的长宽比（数值越大越扁长，适配主图宽度）
                )
                cbar.set_label("R^2", rotation=0, labelpad=5)
                
                
                # 调整边距（使用 canvas6.figure）
                self.canvas4.figure.set_constrained_layout(True)
        
        # 4. 刷新画布
        #plt.tight_layout()
                self.canvas4.draw()
                
            
                
                
                
                self.canvas.figure.clear()
                # 创建1行2列的网格，宽度比例为2:1
                gs = gridspec.GridSpec(1, 3, width_ratios=[3, 1,1], wspace=0.3) 
                
                # 第一个子图（占据2/3宽度）
                ax1 = self.canvas.figure.add_subplot(gs[0])

                # 第一个子图（占据2/3宽度）
              
                inter=self.max_aa_index//101
                print(inter)
              
                self.all=self.max_Ratio_A*self.aaa3[inter][0]+(1-self.max_Ratio_A)*self.aaa3[inter][1]
                print(self.all)
                ax1.plot(self.T, self.all, color='blue', label='option model')  
                ax1.plot(self.T, self.np_sample, color='black', label=self.headers[0])
                ax1.set_xlabel("Zircon U-Pb age (Ma)")
                if self.radioButton.isChecked():
                    ax1.set_ylabel("PDF")
                if self.radioButton_2.isChecked():
                    ax1.set_ylabel("KDE")
   
                ax1.legend()
                    # 关键：设置x轴间隔为100（每100ma一个刻度）
                ax1.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
                ax1.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
                ax1.set_xlim(min_age, max_age)
                ax1.set_ylim(bottom=0)
                
                
                
                # 第二个子图（占据1/3宽度）
                ax2 = self.canvas.figure.add_subplot(gs[1])
                
                ax2.plot(self.T, np.cumsum(self.all), color='blue', label='option model')  
#        
                ax2.plot(self.T, self.cdf_value_sample, color='black', label=self.headers[0])
                ax2.set_xlabel("Zircon U-Pb age (Ma)")
                ax2.set_ylabel("CDFs")
                ax2.legend()
                ax2.set_xlim(min_age, max_age)
                ax2.set_ylim(0,1)
                ax2.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
                ax2.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
                
                                # 第三个子图（占据1/3宽度）
                ax3 = self.canvas.figure.add_subplot(gs[2])
                    
                ax3.scatter(self.np_sample, self.all, s=30, color='blue', alpha=0.6, marker='d')
                 #添加拟合线
                x_range = np.linspace(0, 1, 100)
                ax3.plot(x_range, self.max_slope * x_range + self.max_intercept, 
                         'k--', linewidth=2, alpha=0.7, label='拟合线')
                ax3.set_xlabel(self.headers[0], fontsize=12)
                ax3.set_ylabel('Optional model', fontsize=12)
                
                #ax3.set_aspect("equal") 
                ax3.set_xlim(0,max(np.max(self.np_sample), np.max(self.all)))
                ax3.set_ylim(0,max(np.max(self.np_sample), np.max(self.all)))
                ax3.set_aspect("equal")  # 关键参数
#
#                ax3.grid(alpha=0.3)
                ax3.text(max(self.np_sample)/2, 4*max(self.all)/5, f'R^2= {self.max_aa:.2f}', fontsize=12,
                         bbox=dict(facecolor='white', alpha=0.8))
                
                self.canvas.figure.set_constrained_layout(True)
                   # 5. 关键优化：调整整个图形的边距和布局
                #plt.subplots_adjust(left=0.08, right=0.95, top=0.92, bottom=0.2)  # 手动调整边距
                self.canvas.draw()
                

                
        if num == 3:
            self.ratios = []  # 存储所有 [A, B, C] 比例
            self.aa = []      # 存储所有相似度值
            self.value3=[]
                       
            
            self.slope=[]
            self.intercept=[]
            self.canvas4.figure.clear()

            print(len(self.aaa3))
            for mmm in range (len(self.aaa3)):
                            # 生成 A/B/C 比例和相似度值
                for i in range(101):     
                    for j in range(101 - i):
                        self.ratios.append([i/100, j/100, (100 - i - j)/100])  # A, B, C 比例
                        self.aa.append(r.calculate_cross_correlation(self.np_sample, 
                                    (i/100)*self.aaa3[mmm][0] + 
                                    (j/100)*self.aaa3[mmm][1] + 
                                    ((100-i-j)/100)*self.aaa3[mmm][2]
                                )[0])
                        self.slope.append(r.calculate_cross_correlation(self.np_sample, 
                                    (i/100)*self.aaa3[mmm][0] + 
                                    (j/100)*self.aaa3[mmm][1] + 
                                    ((100-i-j)/100)*self.aaa3[mmm][2]
                                )[1])
                        self.intercept.append(r.calculate_cross_correlation(self.np_sample, 
                                    (i/100)*self.aaa3[mmm][0] + 
                                    (j/100)*self.aaa3[mmm][1] + 
                                    ((100-i-j)/100)*self.aaa3[mmm][2]
                                )[2]) 
                        
                        
                        
                        
                        
    #            print(self.aa)
#            print(len(self.aa))
    
            print(self.aa)
            print(len(self.aa))
                        # ---------------------- 提取数据并计算三元坐标 ----------------------
            # ---------------------- 提取数据并计算三元坐标 ----------------------
            ratios_np = np.array(self.ratios)  # (N, 3)：A, B, C 列
            A, B, C = ratios_np[:, 0], ratios_np[:, 1], ratios_np[:, 2]
            values = np.array(self.aa)  # 相似度值
                    
            # 三元坐标投影（将 A/B/C 转换为 2D 平面坐标）
            denominator = A + B + C + 1e-12  # 避免除零
            x = 0.5 * (2 * B + C) / denominator  # 三元图 x 坐标
            y = (np.sqrt(3) / 2) * C / denominator  # 三元图 y 坐标
                    
            # ---------------------- 找到最高相似度点 ----------------------
            idx_max = np.argmax(values)
            x_max, y_max = x[idx_max], y[idx_max]  # 最高相似度点坐标
            A_max, B_max, C_max = A[idx_max], B[idx_max], C[idx_max]  # 最优比例
            self.max_slope=self.slope[idx_max]
            self.max_intercept=self.intercept[idx_max]
            self.value3.append('Cross')
            self.value3.append(A_max)
            self.value3.append(B_max)
            self.value3.append(C_max)
            self.value3.append(max(self.aa))

            print("最高相似度点比例：")
            print(f"A={A_max:.3f}, B={B_max:.3f}, C={C_max:.3f}")
            print(f"最高相似度值：{values[idx_max]:.4f}")
            
            # ---------------------- 在 canvas6 中绘制三元相图 ----------------------
            # 创建子图（替换原 plt.figure() 和 ax = plt.subplot()）
            ax = self.canvas4.figure.add_subplot(111)  # 使用 canvas6 的 figure 添加子图
                    
            # 1. 绘制插值网格背景（平滑颜色）
            grid_x, grid_y = np.mgrid[0:1:200j, 0:np.sqrt(3)/2:200j]
            grid_z = griddata((x, y), values, (grid_x, grid_y), method='linear')
            #grid_z = np.nan_to_num(grid_z, nan=0.0)  # NaN用0填充（或用values.min()）
            ax.pcolormesh(grid_x, grid_y, grid_z, cmap='viridis', alpha=0.8, shading='gouraud',  vmin=0,vmax=1)
                    
            # 2. 绘制三角边界（等边三角形）
            triangle = np.array([[0, 0], [1, 0], [0.5, np.sqrt(3)/2], [0, 0]])
            ax.plot(triangle[:, 0], triangle[:, 1], 'k-', linewidth=1.5)
                    
            # 3. 绘制原始数据点（可选）
            ax.scatter(x, y, c=values, cmap='viridis', s=5, alpha=0.3,  vmin=0,vmax=1)
                    
            # 4. 标记最高相似度点（红色五角星）
            ax.scatter(x_max, y_max, marker="*", c="red", s=200, edgecolor="k", label="最高相似度点")
                    
            # 5. 添加 A/B/C 轴刻度和标签
            n_ticks = 5
            tick_values = np.linspace(0, 1, n_ticks + 1)
                    
            # A 轴刻度（左下 -> 上顶点）
            for t in tick_values[1:-1]:
                x_tick = 0.5 * (1 - t)
                y_tick = (np.sqrt(3)/2) * (1 - t)
                ax.plot([x_tick, x_tick - 0.02], [y_tick, y_tick], 'k-', linewidth=0.8)
                ax.text(x_tick - 0.04, y_tick, f"{t:.1f}", fontsize=9, ha="right", va="center")
                    
            # B 轴刻度（右下 -> 上顶点）
            for t in tick_values[1:-1]:
                x_tick = 0.5 * (1 + t)
                y_tick = (np.sqrt(3)/2) * (1 - t)
                ax.plot([x_tick, x_tick + 0.02], [y_tick, y_tick], 'k-', linewidth=0.8)
                ax.text(x_tick + 0.04, y_tick, f"{t:.1f}", fontsize=9, ha="left", va="center")
                    
            # C 轴刻度（底部 -> 上顶点）
            for t in tick_values[1:-1]:
                x_tick = t
                y_tick = 0
                ax.plot([x_tick, x_tick], [y_tick, y_tick - 0.02], 'k-', linewidth=0.8)
                ax.text(x_tick, y_tick - 0.05, f"{t:.1f}", fontsize=9, ha="center", va="top")
                    
            # 顶点标签（A/B/C）
            ax.text(-0.05, -0.05, self.headers[2], fontsize=12, ha="right", va="top", fontweight="bold")
            ax.text(1.05, -0.05, self.headers[4], fontsize=12, ha="left", va="top", fontweight="bold")
            ax.text(0.5, np.sqrt(3)/2 + 0.05, self.headers[6], fontsize=12, ha="center", va="bottom", fontweight="bold")
                    
            # ---------------------- 图表设置 ----------------------
            #ax.set_title(f"三元相图 (最高相似度: {max(values):.4f})", fontsize=12, pad=20)
            ax.set_aspect("equal")  # 等比例坐标轴（保证三角形为正三角形）
            ax.axis("off")  # 关闭默认坐标轴
                    
            # 添加颜色条（绑定到 canvas6 的 figure）
            #sm = plt.cm.ScalarMappable(cmap='viridis', norm=plt.Normalize(values.min(), values.max()))
            sm = plt.cm.ScalarMappable(cmap='viridis', norm=plt.Normalize(0,1))
            sm.set_array([])
            cbar = self.canvas4.figure.colorbar(sm, ax=ax, pad=0.05, orientation="horizontal", aspect=40)
            cbar.set_label("R^2", rotation=0, labelpad=10)
                    
            # 调整布局（防止标签被裁剪）
            self.canvas4.figure.set_constrained_layout(True)
                    
            # ---------------------- 刷新 canvas6 画布 ----------------------
            self.canvas4.draw()
            
            
            

            
            
            
            
            self.canvas.figure.clear()
            gs = gridspec.GridSpec(1, 3, width_ratios=[3, 1,1], wspace=0.3) 

                
            # 第一个子图（占据2/3宽度）
            print(idx_max)
            ax1 = self.canvas.figure.add_subplot(gs[0])
            inter=idx_max//5151
            print(inter)
            #print(self.aaa[3])
            self.all=A_max*self.aaa3[inter][0]+B_max*self.aaa3[inter][1]+C_max*self.aaa3[inter][2]
            print(self.all)
            ax1.plot(self.T, self.all, color='blue', label='option model')  
            ax1.plot(self.T, self.np_sample, color='black', label=self.headers[0])
            ax1.set_xlabel("Zircon U-Pb age (Ma)")
            if self.radioButton.isChecked():
                ax1.set_ylabel("PDF")
            if self.radioButton_2.isChecked():
                ax1.set_ylabel("KDE")
            ax1.legend()
                    # 关键：设置x轴间隔为100（每100ma一个刻度）
            ax1.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
            ax1.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
            ax1.set_xlim(min_age, max_age)
            ax1.set_ylim(bottom=0)
                
                # 第二个子图（占据1/3宽度）
            ax2 = self.canvas.figure.add_subplot(gs[1])
                
            ax2.plot(self.T, np.cumsum(self.all), color='blue', label='option model')  
#        
            ax2.plot(self.T, self.cdf_value_sample, color='black', label=self.headers[0])
            ax2.set_xlabel("Zircon U-Pb age (Ma)")
            ax2.set_ylabel("CDFs")
            ax2.legend()
            ax2.set_xlim(min_age, max_age)
            ax2.set_ylim(0,1)
            ax2.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
            ax2.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
            ax3 = self.canvas.figure.add_subplot(gs[2])
                
            ax3.scatter(self.np_sample, self.all, s=30, color='blue', alpha=0.6, marker='d')
            # 添加拟合线
            x_range = np.linspace(0, 1, 100)
            ax3.plot(x_range, self.max_slope * x_range + self.max_intercept, 
                     'k--', linewidth=2, alpha=0.7, label='拟合线')
            ax3.set_xlabel(self.headers[0], fontsize=12)
            ax3.set_ylabel('Optional model', fontsize=12)
            
            ax3.set_xlim(0,max(np.max(self.np_sample), np.max(self.all)))
            ax3.set_ylim(0,max(np.max(self.np_sample), np.max(self.all)))
            ax3.set_aspect("equal")  # 关键参数
#            ax3.set_aspect("equal") 
            #ax3.grid(alpha=0.3)
            ax3.text(max(self.np_sample)/2, 4*max(self.all)/5, f'R^2= {max(values):.2f}', fontsize=12,
                     bbox=dict(facecolor='white', alpha=0.8))    
            self.canvas.figure.set_constrained_layout(True)
                   # 5. 关键优化：调整整个图形的边距和布局
                #plt.subplots_adjust(left=0.08, right=0.95, top=0.92, bottom=0.2)  # 手动调整边距
            self.canvas.draw()                    
        if num == 4:
            
            
            
                    # ---------------------- 初始化空列表（放在循环外！） ----------------------
            self.ratios = []  # 存储所有 [A, B, C] 比例
            self.aa = []      # 存储所有相似度值
            self.value3=[]
            self.slope=[]
            self.intercept=[]
            self.canvas4.figure.clear()  # 清空 canvas6 画布
            SUM=0
            print(len(self.aaa3))
            for mmm in range (len(self.aaa3)):       
            # 生成 A/B/C 比例和相似度值
                for i in range(0,101,5):     
                    for j in range(0,101 - i,3):
                        for k in range(101-i-j):
                            SUM+=1
                            self.ratios.append([i/100, j/100, k/100, (100-i-j-k)/100])  # A, B, C 比例
                            self.aa.append(r.calculate_cross_correlation(self.np_sample, 
                                        (i/100)*self.aaa3[mmm][0] + 
                                        (j/100)*self.aaa3[mmm][1] + 
                                        (k/100)*self.aaa3[mmm][2]+((100-i-j-k)/100)*self.aaa3[mmm][3]
                                    )[0])
                            self.slope.append(r.calculate_cross_correlation(self.np_sample, 
                                    (i/100)*self.aaa3[mmm][0] + 
                                    (j/100)*self.aaa3[mmm][1] + 
                                    (k/100)*self.aaa3[mmm][2]+((100-i-j-k)/100)*self.aaa3[mmm][3]
                                )[1]) 
                            self.intercept.append(r.calculate_cross_correlation(self.np_sample, 
                                        (i/100)*self.aaa3[mmm][0] + 
                                        (j/100)*self.aaa3[mmm][1] + 
                                        (k/100)*self.aaa3[mmm][2]+((100-i-j-k)/100)*self.aaa3[mmm][3]
                                )[2]) 
            print(str(SUM)+"次")
                    
            # ---------------------- 提取数据并计算三元坐标 ----------------------
            print(self.ratios)
            print()
            ratios_np = np.array(self.ratios)  # (N, 4)：A, B, C, D 列
            print(ratios_np)
            A, B, C, D = ratios_np[:, 0], ratios_np[:, 1], ratios_np[:, 2], ratios_np[:, 3]
            print(A)
            values = np.array(self.aa)  # 相似度值  

            
            # ---------------------- 找到相似度最高点 ----------------------
            idx_max = np.argmax(values)
            A_max, B_max, C_max, D_max = A[idx_max], B[idx_max], C[idx_max], D[idx_max]
            self.max_slope=self.slope[idx_max]
            self.max_intercept=self.intercept[idx_max]
            self.value3.append('Cross')
            self.value3.append(A_max)
            self.value3.append(B_max)
            self.value3.append(C_max)
            self.value3.append(D_max)
            self.value3.append(max(self.aa))
            print("相似度最高点的比例：")
            print(f"A={A_max:.3f}, B={B_max:.3f}, C={C_max:.3f}, D={D_max:.3f}")
            
            # ---------------------- 创建仅包含3D四面体的画布 ----------------------
            
            
            # --------------------------------------------
            # 3D四面体展示（无坐标轴，添加刻度）
            # --------------------------------------------
            #ax1 = fig.add_subplot(111, projection='3d')  # 仅一个子图
            ax1 = self.canvas4.figure.add_subplot(111, projection='3d')  # 使用 canvas6 的 figure 添加子图
            # 四面体顶点坐标（保留原始定义）
            vertices = np.array([
                [0, 0, 0],    # A
                [1, 0, 0],    # B
                [0.5, np.sqrt(3)/2, 0],  # C
                [0.5, np.sqrt(3)/6, np.sqrt(6)/3]  # D
            ])
            
            # 绘制四面体边
            edges = [
                [vertices[0], vertices[1]],  # A-B
                [vertices[0], vertices[2]],  # A-C
                [vertices[0], vertices[3]],  # A-D
                [vertices[1], vertices[2]],  # B-C
                [vertices[1], vertices[3]],  # B-D
                [vertices[2], vertices[3]]   # C-D
            ]
            for edge in edges:
                ax1.plot3D(*zip(*edge), 'k-', linewidth=1.5)
            
            # 计算3D坐标（四面体坐标）
            x = A * vertices[0,0] + B * vertices[1,0] + C * vertices[2,0] + D * vertices[3,0]
            y = A * vertices[0,1] + B * vertices[1,1] + C * vertices[2,1] + D * vertices[3,1]
            z = A * vertices[0,2] + B * vertices[1,2] + C * vertices[2,2] + D * vertices[3,2]

            # 绘制散点图
            ax1.scatter(x, y, z, c=values, cmap='viridis', s=5, alpha=0.3, vmin=0,vmax=1)

            # 最高点
            ax1.scatter(
                x[idx_max], y[idx_max], z[idx_max], 
                marker='*', c='red', s=100, edgecolor='k'
            )

            
            # 添加刻度标签到棱上
            def add_ticks(ax, start, end, ticks=5, label=""):
                """在棱上添加刻度标签"""
                direction = end - start
                length = np.linalg.norm(direction)
                unit_vector = direction / length
                
                # 添加刻度线
                for i in range(1, ticks):
                    fraction = i / ticks
                    position = start + fraction * direction
                    
                    # 计算刻度线方向（与棱垂直）
                    # 简单起见，使用XY平面的垂直方向
                    if np.allclose(direction[:2], [0, 0]):  # 如果是垂直棱
                        tick_dir = np.array([1, 0, 0])
                    else:
                        tick_dir = np.array([-direction[1], direction[0], 0])
                        tick_dir = tick_dir / np.linalg.norm(tick_dir[:2])
                    
                    tick_size = 0.03
                    tick_start = position - tick_size * tick_dir
                    tick_end = position + tick_size * tick_dir
                    ax.plot3D(*zip(tick_start, tick_end), 'k-', linewidth=0.8)
                    
                    # 添加刻度标签
#                    label_pos = position + 0.1 * tick_dir
#                    ax.text(*label_pos, f"{fraction:.1f}", fontsize=8, ha='center', va='center')
                
                # 添加端点标签
                ax.text(*(start - 0.05 * unit_vector), "0", fontsize=8, ha='right', va='center')
                ax.text(*(end + 0.05 * unit_vector), "1", fontsize=8, ha='left', va='center')
                ax.text(*((start + end)/2 + 0.1 * tick_dir), label, fontsize=8, ha='center', va='center')
            
            # 在每条棱上添加刻度
            add_ticks(ax1, vertices[0], vertices[1], label="")  # A-B棱
            add_ticks(ax1, vertices[0], vertices[2], label="")  # A-C棱
            add_ticks(ax1, vertices[0], vertices[3], label="")  # A-D棱
            add_ticks(ax1, vertices[1], vertices[2], label="")  # B-C棱
            add_ticks(ax1, vertices[1], vertices[3], label="")  # B-D棱
            add_ticks(ax1, vertices[2], vertices[3], label="")  # C-D棱
            
            # 添加顶点标签
            # ax1.text(*vertices[0], "A", fontsize=14, ha='right', va='top', weight='bold')
            # ax1.text(*vertices[1], "B", fontsize=14, ha='left', va='top', weight='bold')
            # ax1.text(*vertices[2], "C", fontsize=14, ha='center', va='bottom', weight='bold')
            # ax1.text(*vertices[3], "D", fontsize=14, ha='center', va='top', weight='bold')
            # 添加顶点标签（带偏移量）
            offset = 0.2  # 偏移量，可以根据需要调整
            
            # A点标签（左下角）
            ax1.text(vertices[0][0]-offset, vertices[0][1]-offset, vertices[0][2]-offset, 
                     self.headers[2], fontsize=10, ha='right', va='top', weight='bold')
            
            # B点标签（右下角）
            ax1.text(vertices[1][0]+offset, vertices[1][1]-offset, vertices[1][2]-offset, 
                     self.headers[4], fontsize=10, ha='left', va='top', weight='bold')
            
            # C点标签（顶部）
            ax1.text(vertices[2][0], vertices[2][1]+offset, vertices[2][2]-offset, 
                     self.headers[6], fontsize=10, ha='center', va='bottom', weight='bold')  # 修复了重复的va参数
            
            # D点标签（上方）
            ax1.text(vertices[3][0], vertices[3][1], vertices[3][2]+offset, 
                     self.headers[8], fontsize=10, ha='center', va='bottom', weight='bold')
            
            #ax1.set_title("四元比例四面体图 (带刻度)")
            ax1.axis('off')  # 关闭坐标轴
            ax1.view_init(25, 90)  # 设置视角
            #ax1.legend()
            sm = plt.cm.ScalarMappable(cmap='viridis', norm=plt.Normalize(0,1))
            sm.set_array([])
            cbar = self.canvas6.figure.colorbar(
                sm, 
                ax=ax1, 
                pad=0.05,          # 与图形的间距
                aspect=40,         # 核心：减小aspect值（默认20，值越小颜色条越“短粗”）
                orientation="horizontal"
               
            )
            cbar.set_label("R^2", rotation=0, labelpad=5)  # 标签水平放置，更易读
            
            # 调整布局（防止标签被裁剪）
            self.canvas4.figure.set_constrained_layout(True)
                    
            # ---------------------- 刷新 canvas6 画布 ----------------------
            self.canvas4.draw()


            
            
            
            self.canvas.figure.clear()
            

                    
            # 创建1行2列的网格，宽度比例为2:1
            gs = gridspec.GridSpec(1, 3, width_ratios=[3, 1, 1], wspace=0.3)
                    
            # 第一个子图（占据2/3宽度）
            ax1 = self.canvas.figure.add_subplot(gs[0])

            print(idx_max)
            
            inter=idx_max//12852
            print(inter)
            #print(self.aaa[3])
            self.all=A_max*self.aaa3[inter][0]+B_max*self.aaa3[inter][1]+C_max*self.aaa3[inter][2]+D_max*self.aaa3[inter][3]
            print(self.all)
            ax1.plot(self.T, self.all, color='blue', label='option model')  
       
            ax1.plot(self.T, self.np_sample, color='black', label=self.headers[0])
            ax1.set_xlabel("Zircon U-Pb age (Ma)")
            if self.radioButton.isChecked():
                ax1.set_ylabel("PDF")
            if self.radioButton_2.isChecked():
                ax1.set_ylabel("KDE")
            ax1.legend()
                        # 关键：设置x轴间隔为100（每100ma一个刻度）
            ax1.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
            ax1.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
            ax1.set_xlim(min_age, max_age)
            ax1.set_ylim(bottom=0)
                    
            # 第二个子图（占据1/3宽度）
            ax2 = self.canvas.figure.add_subplot(gs[1])
                
            ax2.plot(self.T, np.cumsum(self.all), color='blue', label='option model')  
#        
            ax2.plot(self.T, self.cdf_value_sample, color='black', label=self.headers[0])
            ax2.set_xlabel("Zircon U-Pb age (Ma)")
            ax2.set_ylabel("CDFs")
            ax2.legend()
            ax2.set_xlim(min_age, max_age)
            ax2.set_ylim(0,1)
            ax2.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
            ax2.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
# 第三个子图（占据1/3宽度）
            ax3 = self.canvas.figure.add_subplot(gs[2])
                
            ax3.scatter(self.np_sample, self.all, s=30, color='blue', alpha=0.6, marker='d')
            # 添加拟合线
            x_range = np.linspace(0, 1, 100)
            ax3.plot(x_range, self.max_slope * x_range + self.max_intercept, 
                     'k--', linewidth=2, alpha=0.7, label='拟合线')
            ax3.set_xlabel(self.headers[0], fontsize=12)
            ax3.set_ylabel('Optional model', fontsize=12)
            #ax3.set_aspect("equal") 
            ax3.set_xlim(0,max(np.max(self.np_sample), np.max(self.all)))
            ax3.set_ylim(0,max(np.max(self.np_sample), np.max(self.all)))
            ax3.set_aspect("equal")  # 关键参数
            #ax3.grid(alpha=0.3)
            ax3.text(max(self.np_sample)/2, 4*max(self.all)/5, f'R^2 = {max(values):.2f}', fontsize=12,
                     bbox=dict(facecolor='white', alpha=0.8))

                # 调整子图间距
            self.canvas.figure.set_constrained_layout(True)
                   # 5. 关键优化：调整整个图形的边距和布局
                #plt.subplots_adjust(left=0.08, right=0.95, top=0.92, bottom=0.2)  # 手动调整边距
            self.canvas.draw()
    
    @pyqtSlot()
    def on_pushButton_14_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.canvas4.figure.clear()
        self.canvas4.draw() 
        self.value3=[]
    
    @pyqtSlot()
    def on_pushButton_15_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        file_path, ok=  QFileDialog.getSaveFileName(self,"Import","" ,"PDF File (*.pdf);;image(*.jpg);;all files(*.*)")   
        print(file_path.strip())
        #判断有点问题可以重新检查下
        if file_path.strip()=='':
            QMessageBox.warning(self, 'Waring', 'Failed!')
        else:
            self.save=self.figure4.savefig(file_path)
            #print(self.save)
            QMessageBox.information(self,'Save','Sucessful!')
    
    @pyqtSlot()
    def on_pushButton_25_clicked(self):
        """
        Slot documentation goes here.
        """
        self.allvalues=[]
        if self.value1:
            self.allvalues.append(self.value1)
        if self.value2:
            self.allvalues.append(self.value2)
        if self.value3:
            self.allvalues.append(self.value3)
        if self.value4:
            self.allvalues.append(self.value4)
        if self.value5:
            self.allvalues.append(self.value5)
        if self.value6:
            self.allvalues.append(self.value6)
            
        print(self.allvalues)
        
        # TODO: not implemented yet
        # 1. 准备数据（替换为你的实际数据列表，如 self.ratios 或 self.data_list）
#        data_list = [
#            [0.1, 0.2, 0.3, 0.4],  # 第1行数据（尺寸=4）
#            [0.5, 0.6],            # 第2行数据（尺寸=2）
#            [0.7]                  # 第3行数据（尺寸=1）
#        ]
#        method=['K-S','Kupier','Cross','Q-Q','Simlarity','Likeness']
#        

        
        # 3. 创建模型实例并绑定数据
        model = SimpleTableModel(self.allvalues,self.headers)
        
        # 4. 将模型绑定到 QTableView
        self.tableView.setModel(model)
        
        # 5. 调整列宽（自适应内容）
        #self.tableView.resizeColumnsToContents()
        self.tableView.horizontalHeader().setDefaultSectionSize(self.groupBox_7.width()/3)
        
        # （可选）设置表格为只读模式
#        self.tableView.setEditTriggers(QTableView.NoEditTriggers)
#        
#        # ---------------------- 4. 将模型绑定到 QTableView ----------------------
#        self.tableView.setModel(model)
#        self.tableView.horizontalHeader().setStretchLastSection(True)  # 自动拉伸最后一列
#        self.tableView.horizontalHeader().resizeSections(QHeaderView.ResizeToContents)  # 列宽自适应内容
    
    @pyqtSlot()
    def on_pushButton_26_clicked(self):
        """强制清空 TableView"""
           # 正确绑定示例
        print(self.headers)
        self.allvalues = []
        model = SimpleTableModel(self.allvalues)
        self.tableView.setModel(model)  # 替换模型
        self.tableView.viewport().update()  # 强制重绘
    


    @pyqtSlot()
    def on_pushButton_27_clicked(self):
        """
        导出 TableView 数据到 CSV 文件
        """
        try:
            model = SimpleTableModel(self.allvalues,self.headers)
            self.tableView.setModel(model)  # 替换模型
            if not model or model.rowCount() == 0:
                QMessageBox.warning(self, "警告", "没有可导出的数据！")
                return
    
            # 获取文件保存路径
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "保存为 CSV 文件",
                "",
                "CSV 文件 (*.csv);;所有文件 (*)"
            )
            
            if not file_path:
                return  # 用户取消保存
    
            # 确保文件以 .csv 结尾
            if not file_path.endswith('.csv'):
                file_path += '.csv'
    
            # 写入 CSV 文件
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # 写入表头
                headers = []
                for col in range(model.columnCount()):
                    header = model.headerData(col, Qt.Horizontal, Qt.DisplayRole)
                    headers.append(header if header else f"Column {col+1}")
                writer.writerow(headers)
                
                # 写入数据行
                for row in range(model.rowCount()):
                    row_data = []
                    for col in range(model.columnCount()):
                        index = model.index(row, col)
                        cell_data = model.data(index, Qt.DisplayRole)
                        row_data.append(str(cell_data) if cell_data is not None else "")
                    writer.writerow(row_data)
    
            QMessageBox.information(self, "成功", f"数据已导出到:\n{file_path}")
    
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败:\n{str(e)}")
    
    @pyqtSlot()
    def on_pushButton_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        min_age = int(self.lineEdit.text())
        max_age = int(self.lineEdit_2.text())
        dT_value = int(self.lineEdit_8.text())
        number = len(self.headers)
        random_seed = 42  # 可以改为你想要的任何固定值
        np.random.seed(random_seed)
        random.seed(random_seed)
        if number > 5 and number <= 10:
            print('yes')
            self.age_range = [min_age, max_age]
            self.dT = dT_value
            self.T = np.zeros((self.age_range[1] - self.age_range[0]) // self.dT)
            self.dd=self.data[2:]
            #print(self.dd)
            self.min_length = min(len(lst) for lst in self.dd)
            if self.min_length < int(self.lineEdit_4.text()):
                            # 弹出警告框，但继续执行（不报错）
                            QMessageBox.warning(
                                self,  # 父窗口（通常是 self）
                                "抽样数量不足",
                                f"最短子列表只有 {self.min_length} 个元素，无法抽取 {int(self.lineEdit_4.text())} 个。"
                            )
            else: 
                            

                    
                if self.radioButton.isChecked():

                    self.canvas.figure.clear()
                                    # 创建画布布局
                    gs = gridspec.GridSpec(1, 2, width_ratios=[2, 1], wspace=0.3) 
                    
                    # 第一个子图（占据2/3宽度）
                    ax1 = self.canvas.figure.add_subplot(gs[0])
                    ax2 = self.canvas.figure.add_subplot(gs[1])
                    for i in range(len(self.T)):
                        self.T[i] = min_age + i * dT_value
                    self.aaa=[]
                    self.aaa2=[]
                    self.aaa3=[]
                    self.aaa4=[]
                    self.aaa5=[]
                    self.aaa6=[]
                    self.sample = self.data[0]
                    self.sample_err = self.data[1]
                    self.np_sample = np.zeros(len(self.T))
                    for i in range(len(self.sample)):
                        self.np_sample = self.np_sample + st.norm.pdf(self.T, self.sample[i], 2*self.sample_err[i])
                    self.np_sample = self.np_sample / len(self.sample)
                    print(self.np_sample)
                    self.cdf_value_sample=np.cumsum(self.np_sample)
                    
                    for j in range(int(self.lineEdit_5.text())):  # 或者 range(int(self.lineEdit_5.text()))
                        self.ks= []
                        self.kut= []
                        self.r2= []
                        self.qr2= []
                        self.sim= []
                        self.like= []
             
    
    #                    min_length = min(len(lst) for lst in self.dd)
                        sampled_indices = random.sample(range(self.min_length), int(self.lineEdit_4.text()))
                        self.sampled_data = [
                                [lst[i] for i in sampled_indices]
                                for lst in self.dd
                            ]
#                        self.aaa.append(self.sampled_data)
                        print("第"+str(j)+"次")
                        print(self.sampled_data)
                        self.pair_count = (len(self.sampled_data)) // 2
                        self.source = [[] for _ in range(self.pair_count)]#source
                        self.se = [[] for _ in range(self.pair_count)]#source error
                        self.np_source = [[] for _ in range(self.pair_count)] #Normalized source
                        self.cdf_value = [[] for _ in range(self.pair_count)]#/np.sum(np_rvr)
                        
                        for mm in range(self.pair_count):
                            self.source[mm] = self.sampled_data[mm*2]
                            self.se[mm] = self.sampled_data[mm*2+1]
                            self.np_source[mm] = np.zeros(len(self.T))
                        for m in range(self.pair_count):
                            for n in range(len(self.source[m])):
                                self.np_source[m] = self.np_source[m] + st.norm.pdf(self.T, self.source[m][n], 2*self.se[m][n])    
  
                        for a in range(self.pair_count):
                            self.np_source[a] = self.np_source[a] / len(self.source[a])
                            self.cdf_value[a]=np.cumsum(self.np_source[a])
#                    all_sources.append(self.np_source)
                        self.aaa.append(self.np_source)
                        self.aaa2.append(self.np_source)
                        self.aaa3.append(self.np_source)
                        self.aaa4.append(self.np_source)
                        self.aaa5.append(self.np_source)
                        self.aaa6.append(self.np_source)
                        for cc in range(len(self.np_source)):
                            ax1.plot(self.T,self.np_source[cc],color=self.color[cc])
                            ax2.plot(self.T,self.cdf_value[cc], color=self.color[cc]) 
                    ax1.plot(self.T, self.np_sample, color='black', label=self.headers[0])   
                    ax1.set_xlabel("Zircon U-Pb age (Ma)")
                    
                    ax1.set_ylabel("PDF")
                   

                    for cc in range(len(self.np_source)):
                        ax1.plot([],[],color=self.color[cc],label=self.headers[cc*2 + 2])
                    ax1.legend()
                                # 关键：设置x轴间隔为100（每100ma一个刻度）
                    ax1.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
                    ax1.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
                    ax1.set_xlim(min_age, max_age)
                    ax1.set_ylim(bottom=0)
                        
                    ax2.plot(self.T, self.cdf_value_sample, color='black', label=self.headers[0])
                    ax2.set_xlabel("Zircon U-Pb age (Ma)")
                    ax2.set_ylabel("CDFs")
                    for cc in range(len(self.np_source)):
                        ax2.plot([],[],color=self.color[cc],label=self.headers[cc*2 + 2])
                    ax2.legend()
                    ax2.set_xlim(min_age, max_age)
                    ax2.set_ylim(0,1)
                    ax2.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
                    ax2.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
                    self.canvas.figure.set_constrained_layout(True)
                       # 5. 关键优化：调整整个图形的边距和布局
                    #plt.subplots_adjust(left=0.08, right=0.95, top=0.92, bottom=0.2)  # 手动调整边距
                    self.canvas.draw()                    
                if self.radioButton_2.isChecked():

                    self.canvas.figure.clear()
                                    # 创建画布布局
                    gs = gridspec.GridSpec(1, 2, width_ratios=[2, 1], wspace=0.3) 
                    
                    # 第一个子图（占据2/3宽度）
                    ax1 = self.canvas.figure.add_subplot(gs[0])
                    ax2 = self.canvas.figure.add_subplot(gs[1])
                    self.T = np.arange(min_age, max_age + dT_value, dT_value)
                    self.aaa=[]
                    self.aaa2=[]
                    self.aaa3=[]
                    self.aaa4=[]
                    self.aaa5=[]
                    self.aaa6=[]
                    self.sample = self.data[0]
                    self.np_sample=self.kde_pdf(self.sample,self.T, bandwidth=int(self.lineEdit_3.text()))
                    
                    print(self.np_sample)
                    self.cdf_value_sample=np.cumsum(self.np_sample)
                    
                    for j in range(int(self.lineEdit_5.text())):  # 或者 range(int(self.lineEdit_5.text()))
                        self.ks= []
                        self.kut= []
                        self.r2= []
                        self.qr2= []
                        self.sim= []
                        self.like= []
             
    
    #                    min_length = min(len(lst) for lst in self.dd)
                        sampled_indices = random.sample(range(self.min_length), int(self.lineEdit_4.text()))
                        self.sampled_data = [
                                [lst[i] for i in sampled_indices]
                                for lst in self.dd
                            ]
#                        self.aaa.append(self.sampled_data)
                        print("第"+str(j)+"次")
                        print(self.sampled_data)
                        self.pair_count = (len(self.sampled_data)) // 2
                        self.source = [[] for _ in range(self.pair_count)]#source
                        self.np_source = [[] for _ in range(self.pair_count)] #Normalized source
                        self.cdf_value = [[] for _ in range(self.pair_count)]#/np.sum(np_rvr)
                        

                        
                        for mm in range(self.pair_count):
                            self.source[mm] = self.sampled_data[mm*2]
                            self.np_source[mm]=self.kde_pdf(self.source[mm],self.T, bandwidth= int(self.lineEdit_4.text()))
                            
                       
  
                        for a in range(self.pair_count):
                            self.cdf_value[a]=np.cumsum(self.np_source[a])
#                    all_sources.append(self.np_source)
                        self.aaa.append(self.np_source)
                        self.aaa2.append(self.np_source)
                        self.aaa3.append(self.np_source)
                        self.aaa4.append(self.np_source)
                        self.aaa5.append(self.np_source)
                        self.aaa6.append(self.np_source)
                        
                        for cc in range(len(self.np_source)):
                            ax1.plot(self.T,self.np_source[cc],color=self.color[cc])
                            ax2.plot(self.T,self.cdf_value[cc], color=self.color[cc]) 
                    ax1.plot(self.T, self.np_sample, color='black', label=self.headers[0])   
                    ax1.set_xlabel("Zircon U-Pb age (Ma)")
                    ax1.set_ylabel("KDE")
                    for cc in range(len(self.np_source)):
                        ax1.plot([],[],color=self.color[cc],label=self.headers[cc*2 + 2])
                    ax1.legend()
                                # 关键：设置x轴间隔为100（每100ma一个刻度）
                    ax1.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
                    ax1.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
                    ax1.set_xlim(min_age, max_age)
                    ax1.set_ylim(bottom=0)
                        
                    ax2.plot(self.T, self.cdf_value_sample, color='black', label=self.headers[0])
                    ax2.set_xlabel("Zircon U-Pb age (Ma)")
                    ax2.set_ylabel("CDFs")
                    for cc in range(len(self.np_source)):
                        ax2.plot([],[],color=self.color[cc],label=self.headers[cc*2 + 2])
                    ax2.legend()
                    ax2.set_xlim(min_age, max_age)
                    ax2.set_ylim(0,1)
                    ax2.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
                    ax2.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
                    self.canvas.figure.set_constrained_layout(True)
                       # 5. 关键优化：调整整个图形的边距和布局
                    #plt.subplots_adjust(left=0.08, right=0.95, top=0.92, bottom=0.2)  # 手动调整边距
                    self.canvas.draw()                      
                 
        else:
            QMessageBox.warning(self,'Warning','Please import the data needed')
    
    @pyqtSlot()
    def on_pushButton_2_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.canvas.figure.clear()
        self.canvas.draw()  
    
    @pyqtSlot()
    def on_pushButton_3_clicked(self):
        """
        Slot documentation goes here.
        """
        file_path, ok=  QFileDialog.getSaveFileName(self,"Import","" ,"PDF File (*.pdf);;image(*.jpg);;all files(*.*)")   
        print(file_path.strip())
        #判断有点问题可以重新检查下
        if file_path.strip()=='':
            QMessageBox.warning(self, 'Waring', 'Failed!')
        else:
            self.save=self.figure.savefig(file_path)
            #print(self.save)
            QMessageBox.information(self,'Save','Sucessful!')
    
    @pyqtSlot()
    def on_pushButton_19_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        print('你好')
#        print(self.aaa)
#        print(len(self.aaa))
        show_original = True
        
        self.value_ks=[]
        
        min_age = int(self.lineEdit.text())
        max_age = int(self.lineEdit_2.text())
#        dT_value = int(self.lineEdit_8.text())
#        self.age_range = [min_age, max_age]
#        self.dT = dT_value
#        self.T = np.zeros((self.age_range[1] - self.age_range[0]) // self.dT)
            
            
        num = (len(self.headers)-2)//2
        if num == 2:
            self.aa = []
            Ratio_A = []
            self.aa = []
            self.value4=[]
            self.q1=[]
            self.q2=[]
            self.slope=[]
            self.intercept=[]
            self.canvas5.figure.clear()

#            print(self.aaa[0])
            for j in range (len(self.aaa4)):
                for i in range(101):
                    Ratio_A.append(i/100)
                    ksks=Qr.calculate_qq_plot(self.np_sample, (i/100)*self.aaa4[j][0] + ((100-i)/100)*(i/100)*self.aaa4[j][1],500)[2]
                    self.aa.append(ksks)
                    
                    qq1=Qr.calculate_qq_plot(self.np_sample, (i/100)*self.aaa4[j][0] + ((100-i)/100)*(i/100)*self.aaa4[j][1],500)[0]
                    self.q1.append(qq1)
                    
                    qq2=Qr.calculate_qq_plot(self.np_sample, (i/100)*self.aaa4[j][0] + ((100-i)/100)*(i/100)*self.aaa4[j][1],500)[1]
                    self.q2.append(qq2)
                    
                    ssss=Qr.calculate_qq_plot(self.np_sample, (i/100)*self.aaa4[j][0] + ((100-i)/100)*(i/100)*self.aaa4[j][1],500)[3]
                    self.slope.append(ssss)
                    
                    kkkk=Qr.calculate_qq_plot(self.np_sample, (i/100)*self.aaa4[j][0] + ((100-i)/100)*(i/100)*self.aaa4[j][1],500)[4]
                    self.intercept.append(kkkk)
#            print(len(self.aa))
            
            self.max_aa=np.max(self.aa)
            self.max_aa_index=np.argmax(self.aa)
            self.max_Ratio_A=Ratio_A[self.max_aa_index]
            self.max_slope=self.slope[self.max_aa_index]
            self.max_intercept=self.intercept[self.max_aa_index]
            #self.value_ks.append[max_Ratio_A,1-max_Ratio_A,max_aa]
            print(self.aa)
            print(self.max_Ratio_A,1-self.max_Ratio_A,self.max_aa)
            self.value4.append('Q-Q')
            self.value4.append(self.max_Ratio_A)
            self.value4.append(1-self.max_Ratio_A)
            self.value4.append(self.max_aa)
            # 数据处理和插值（保持不变）
            x_data = np.clip(Ratio_A, 0, 1)
            z_data = np.clip(self.aa, 0, 1)
            sorted_indices = np.argsort(x_data)
            x_sorted, z_sorted = x_data[sorted_indices], z_data[sorted_indices]
            _, unique_mask = np.unique(x_sorted, return_index=True)
            x_unique, z_unique = x_sorted[unique_mask], z_sorted[unique_mask]
            
            if len(x_unique) >= 2:
                from scipy.interpolate import interp1d
                x_interp = np.linspace(0, 1, 1000)
                interp_func = interp1d(x_unique, z_unique, kind="linear", bounds_error=False, fill_value=0.5)
                z_interp = interp_func(x_interp)
                
                # 绘制条带图（保持不变）
                ax = self.canvas5.figure.add_subplot(111)
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.set_yticks([0.5])
                ax.set_yticklabels([self.headers[0]], rotation=90, va="top")
                ax.set_xlabel(self.headers[2], fontsize=10, labelpad=3)
                
                ax_top = ax.twiny()
                ax_top.set_xlim(0, 1)
                ax_top.set_xlabel(self.headers[4], fontsize=10, labelpad=3)
                ax_top.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
                ax_top.set_xticklabels([1.0, 0.8, 0.6, 0.4, 0.2, 0.0])
                ax_top.set_title(str(self.max_Ratio_A)+"_"+str(1-self.max_Ratio_A)+"_ "+str(self.max_aa))
                
                cmap = plt.cm.get_cmap("viridis")
                norm = plt.Normalize(0, 1)
                ax.pcolormesh(
                    x_interp, [0.0, 1.0], z_interp.reshape(1, -1),
                    cmap=cmap, norm=norm, shading="auto", alpha=0.9
                )
                
                if show_original:
                    ax.vlines(x=x_data, ymin=0, ymax=1.0, color="gray", linewidth=0.8, alpha=0.4)
                
                # 颜色条（保持不变）
                sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
                sm.set_array([])
                # 创建水平颜色条（关键参数：orientation="horizontal"）
                cbar = plt.colorbar(
                    sm, 
                    ax=ax, 
                    pad=0.2,                # 颜色条与主图的间距（垂直方向，因水平放置）
                    orientation="horizontal", 
                    aspect=30,
                    shrink=0.8 # 颜色条的长宽比（数值越大越扁长，适配主图宽度）
                )
                cbar.set_label("R^2", rotation=0, labelpad=5)
                
                
                # 调整边距（使用 canvas6.figure）
                self.canvas5.figure.set_constrained_layout(True)
        
        # 4. 刷新画布
        #plt.tight_layout()
                self.canvas5.draw()
                
            
                
                
                
                self.canvas.figure.clear()
                # 创建1行2列的网格，宽度比例为2:1
                gs = gridspec.GridSpec(1, 3, width_ratios=[3, 1,1], wspace=0.3) 
                
                # 第一个子图（占据2/3宽度）
                ax1 = self.canvas.figure.add_subplot(gs[0])

                # 第一个子图（占据2/3宽度）
              
                inter=self.max_aa_index//101
                print(inter)
              
                self.all=self.max_Ratio_A*self.aaa4[inter][0]+(1-self.max_Ratio_A)*self.aaa4[inter][1]
                print(self.all)
                ax1.plot(self.T, self.all, color='blue', label='option model')  
                ax1.plot(self.T, self.np_sample, color='black', label=self.headers[0])
                ax1.set_xlabel("Zircon U-Pb age (Ma)")
                if self.radioButton.isChecked():
                    ax1.set_ylabel("PDF")
                if self.radioButton_2.isChecked():
                    ax1.set_ylabel("KDE")
   
                ax1.legend()
                    # 关键：设置x轴间隔为100（每100ma一个刻度）
                ax1.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
                ax1.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
                ax1.set_xlim(min_age, max_age)
                ax1.set_ylim(bottom=0)
                
                
                
                # 第二个子图（占据1/3宽度）
                ax2 = self.canvas.figure.add_subplot(gs[1])
                
                ax2.plot(self.T, np.cumsum(self.all), color='blue', label='option model')  
#        
                ax2.plot(self.T, self.cdf_value_sample, color='black', label=self.headers[0])
                ax2.set_xlabel("Zircon U-Pb age (Ma)")
                ax2.set_ylabel("CDFs")
                ax2.legend()
                ax2.set_xlim(min_age, max_age)
                ax2.set_ylim(0,1)
                ax2.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
                ax2.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
                
                                # 第三个子图（占据1/3宽度）
                
                
              
                                
                                
                                
                
                ax3 = self.canvas.figure.add_subplot(gs[2])
                    
                ax3.scatter(self.q1, self.q2, s=30, color='blue', alpha=0.6, marker='d')
                                # 添加拟合线
                min_val = min(np.array(self.q1).min(), np.array(self.q2).min())
                max_val = max(np.array(self.q1).max(), np.array(self.q2).max())
                ax3.plot([min_val, max_val], [min_val, max_val], 
                                'k--', linewidth=2, alpha=0.7)
                ax3.set_xlabel(self.headers[0], fontsize=12)
                ax3.set_ylabel('Optional model', fontsize=12)
                ax3.set_xlim(min_val, max_val)
                ax3.set_ylim(min_val, max_val)
                ax3.set_aspect("equal")  # 关键参数
                ax3.text(max_val/2, 0.9*max_val, f'R^2 = {max(self.aa):.2f}', fontsize=12,
                                bbox=dict(facecolor='white', alpha=0.8))  
                
                self.canvas.figure.set_constrained_layout(True)
                   # 5. 关键优化：调整整个图形的边距和布局
                #plt.subplots_adjust(left=0.08, right=0.95, top=0.92, bottom=0.2)  # 手动调整边距
                self.canvas.draw()
                

                
        if num == 3:
            self.ratios = []  # 存储所有 [A, B, C] 比例
            self.aa = []      # 存储所有相似度值
            #self.bb=[]
            self.value4=[]
            self.q1=[]
            self.q2=[]
            self.slope=[]
            self.intercept=[]
            self.canvas5.figure.clear()  # 清空 canvas6 画布

            print(len(self.aaa4))
            for mmm in range (len(self.aaa4)):
                            # 生成 A/B/C 比例和相似度值
                for i in range(101):     
                    for j in range(101 - i):
                        self.ratios.append([i/100, j/100, (100 - i - j)/100])  # A, B, C 比例
                        self.q1.append(Qr.calculate_qq_plot(self.np_sample, (i/100)*self.aaa4[mmm][0] + (j/100)*self.aaa4[mmm][1] + 
                                ((100-i-j)/100)*self.aaa4[mmm][2],500)[0])
                        self.q2.append(Qr.calculate_qq_plot(self.np_sample, 
                                (i/100)*self.aaa4[mmm][0] + 
                                (j/100)*self.aaa4[mmm][1] + 
                                ((100-i-j)/100)*self.aaa4[mmm][2],500)[1])                        
                        
                        
                        
                        self.aa.append(Qr.calculate_qq_plot(self.np_sample, 
                                (i/100)*self.aaa4[mmm][0] + 
                                (j/100)*self.aaa4[mmm][1] + 
                                ((100-i-j)/100)*self.aaa4[mmm][2],500)[2])        
                            
                        self.slope.append(Qr.calculate_qq_plot(self.np_sample, 
                                (i/100)*self.aaa4[mmm][0] + 
                                (j/100)*self.aaa4[mmm][1] + 
                                ((100-i-j)/100)*self.aaa4[mmm][2],500)[3])        
                        self.intercept.append(Qr.calculate_qq_plot(self.np_sample, 
                                (i/100)*self.aaa4[mmm][0] + 
                                (j/100)*self.aaa4[mmm][1] + 
                                ((100-i-j)/100)*self.aaa4[mmm][2],500)[4])        
                        
                        
                        
                        
                        
    #            print(self.aa)
#            print(len(self.aa))
    
            # ---------------------- 提取数据并计算三元坐标 ----------------------
            ratios_np = np.array(self.ratios)  # (N, 3)：A, B, C 列
            A, B, C = ratios_np[:, 0], ratios_np[:, 1], ratios_np[:, 2]
            values = np.array(self.aa)  # 相似度值
                    
            # 三元坐标投影（将 A/B/C 转换为 2D 平面坐标）
            denominator = A + B + C + 1e-12  # 避免除零
            x = 0.5 * (2 * B + C) / denominator  # 三元图 x 坐标
            y = (np.sqrt(3) / 2) * C / denominator  # 三元图 y 坐标
                    
            # ---------------------- 找到最高相似度点 ----------------------
            idx_max = np.argmax(values)
            x_max, y_max = x[idx_max], y[idx_max]  # 最高相似度点坐标
            A_max, B_max, C_max = A[idx_max], B[idx_max], C[idx_max]  # 最优比例
            self.max_slope=self.slope[idx_max]
            self.max_intercept=self.intercept[idx_max]
            self.value4.append('Q-Q')
            self.value4.append(A_max)
            self.value4.append(B_max)
            self.value4.append(C_max)
            self.value4.append(max(self.aa))
            
            print("最高相似度点比例：")
            print(f"A={A_max:.3f}, B={B_max:.3f}, C={C_max:.3f}")
            print(f"最高相似度值：{values[idx_max]:.4f}")
            
            # ---------------------- 在 canvas6 中绘制三元相图 ----------------------
            # 创建子图（替换原 plt.figure() 和 ax = plt.subplot()）
            ax = self.canvas5.figure.add_subplot(111)  # 使用 canvas6 的 figure 添加子图
                    
            # 1. 绘制插值网格背景（平滑颜色）
            grid_x, grid_y = np.mgrid[0:1:200j, 0:np.sqrt(3)/2:200j]
            grid_z = griddata((x, y), values, (grid_x, grid_y), method='linear')
            #grid_z = np.nan_to_num(grid_z, nan=0.0)  # NaN用0填充（或用values.min()）
            ax.pcolormesh(grid_x, grid_y, grid_z, cmap='viridis', alpha=0.8, shading='gouraud',  vmin=0,vmax=1)
                    
            # 2. 绘制三角边界（等边三角形）
            triangle = np.array([[0, 0], [1, 0], [0.5, np.sqrt(3)/2], [0, 0]])
            ax.plot(triangle[:, 0], triangle[:, 1], 'k-', linewidth=1.5)
                    
            # 3. 绘制原始数据点（可选）
            ax.scatter(x, y, c=values, cmap='viridis', s=5, alpha=0.3,  vmin=0,vmax=1)
                    
            # 4. 标记最高相似度点（红色五角星）
            ax.scatter(x_max, y_max, marker="*", c="red", s=200, edgecolor="k", label="最高相似度点")
                    
            # 5. 添加 A/B/C 轴刻度和标签
            n_ticks = 5
            tick_values = np.linspace(0, 1, n_ticks + 1)
                    
            # A 轴刻度（左下 -> 上顶点）
            for t in tick_values[1:-1]:
                x_tick = 0.5 * (1 - t)
                y_tick = (np.sqrt(3)/2) * (1 - t)
                ax.plot([x_tick, x_tick - 0.02], [y_tick, y_tick], 'k-', linewidth=0.8)
                ax.text(x_tick - 0.04, y_tick, f"{t:.1f}", fontsize=9, ha="right", va="center")
                    
            # B 轴刻度（右下 -> 上顶点）
            for t in tick_values[1:-1]:
                x_tick = 0.5 * (1 + t)
                y_tick = (np.sqrt(3)/2) * (1 - t)
                ax.plot([x_tick, x_tick + 0.02], [y_tick, y_tick], 'k-', linewidth=0.8)
                ax.text(x_tick + 0.04, y_tick, f"{t:.1f}", fontsize=9, ha="left", va="center")
                    
            # C 轴刻度（底部 -> 上顶点）
            for t in tick_values[1:-1]:
                x_tick = t
                y_tick = 0
                ax.plot([x_tick, x_tick], [y_tick, y_tick - 0.02], 'k-', linewidth=0.8)
                ax.text(x_tick, y_tick - 0.05, f"{t:.1f}", fontsize=9, ha="center", va="top")
                    
            # 顶点标签（A/B/C）
            ax.text(-0.05, -0.05, self.headers[2], fontsize=12, ha="right", va="top", fontweight="bold")
            ax.text(1.05, -0.05, self.headers[4], fontsize=12, ha="left", va="top", fontweight="bold")
            ax.text(0.5, np.sqrt(3)/2 + 0.05, self.headers[6], fontsize=12, ha="center", va="bottom", fontweight="bold")
                    
            # ---------------------- 图表设置 ----------------------
            #ax.set_title(f"三元相图 (最高相似度: {max(values):.4f})", fontsize=12, pad=20)
            ax.set_aspect("equal")  # 等比例坐标轴（保证三角形为正三角形）
            ax.axis("off")  # 关闭默认坐标轴
                    
            # 添加颜色条（绑定到 canvas6 的 figure）
            #sm = plt.cm.ScalarMappable(cmap='viridis', norm=plt.Normalize(values.min(), values.max()))
            sm = plt.cm.ScalarMappable(cmap='viridis', norm=plt.Normalize(0,1))
            sm.set_array([])
            cbar = self.canvas5.figure.colorbar(sm, ax=ax, pad=0.05, orientation="horizontal", aspect=40)
            cbar.set_label("R^2", rotation=0, labelpad=10)
                    
            # 调整布局（防止标签被裁剪）
            self.canvas5.figure.set_constrained_layout(True)
                    
            # ---------------------- 刷新 canvas6 画布 ----------------------
            self.canvas5.draw()
            
            
            

            
            
            
            
            self.canvas.figure.clear()
            gs = gridspec.GridSpec(1, 3, width_ratios=[3, 1,1], wspace=0.3) 

                
            # 第一个子图（占据2/3宽度）
            print(idx_max)
            ax1 = self.canvas.figure.add_subplot(gs[0])
            inter=idx_max//5151
            print(inter)
            #print(self.aaa[3])
            self.all=A_max*self.aaa4[inter][0]+B_max*self.aaa4[inter][1]+C_max*self.aaa4[inter][2]
            print(self.all)
            ax1.plot(self.T, self.all, color='blue', label='option model')  
            ax1.plot(self.T, self.np_sample, color='black', label=self.headers[0])
            ax1.set_xlabel("Zircon U-Pb age (Ma)")
            if self.radioButton.isChecked():
                ax1.set_ylabel("PDF")
            if self.radioButton_2.isChecked():
                ax1.set_ylabel("KDE")
            ax1.legend()
                    # 关键：设置x轴间隔为100（每100ma一个刻度）
            ax1.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
            ax1.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
            ax1.set_xlim(min_age, max_age)
            ax1.set_ylim(bottom=0)
                
                # 第二个子图（占据1/3宽度）
            ax2 = self.canvas.figure.add_subplot(gs[1])
                
            ax2.plot(self.T, np.cumsum(self.all), color='blue', label='option model')  
#        
            ax2.plot(self.T, self.cdf_value_sample, color='black', label=self.headers[0])
            ax2.set_xlabel("Zircon U-Pb age (Ma)")
            ax2.set_ylabel("CDFs")
            ax2.legend()
            ax2.set_xlim(min_age, max_age)
            ax2.set_ylim(0,1)
            ax2.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
            ax2.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
            
            ax3 = self.canvas.figure.add_subplot(gs[2])
                    
            ax3.scatter(self.q1, self.q2, s=30, color='blue', alpha=0.6, marker='d')
                                # 添加拟合线
            min_val = min(np.array(self.q1).min(), np.array(self.q2).min())
            max_val = max(np.array(self.q1).max(), np.array(self.q2).max())
            ax3.plot([min_val, max_val], [min_val, max_val], 
                                'k--', linewidth=2, alpha=0.7)
            ax3.set_xlabel(self.headers[0], fontsize=12)
            ax3.set_ylabel('Optional model', fontsize=12)
            ax3.set_xlim(min_val, max_val)
            ax3.set_ylim(min_val, max_val)
            ax3.set_aspect("equal")  # 关键参数
            ax3.text(max_val/2, 0.9*max_val, f'R^2 = {max(self.aa):.2f}', fontsize=12,
                                bbox=dict(facecolor='white', alpha=0.8))  
            
            
            
            
            
                
            self.canvas.figure.set_constrained_layout(True)
                   # 5. 关键优化：调整整个图形的边距和布局
                #plt.subplots_adjust(left=0.08, right=0.95, top=0.92, bottom=0.2)  # 手动调整边距
            self.canvas.draw()            
            
            
            
            
        if num == 4:
            
            
            
                    # ---------------------- 初始化空列表（放在循环外！） ----------------------
            self.ratios = []  # 存储所有 [A, B, C] 比例
            self.aa = []      # 存储所有相似度值
            self.q1=[]
            self.q2=[]
            self.value4=[]
            self.slope=[]
            self.intercept=[]
            self.canvas5.figure.clear()  # 清空 canvas6 画布
            SUM=0
            print(len(self.aaa3))
            for mmm in range (len(self.aaa3)):       
            # 生成 A/B/C 比例和相似度值
                for i in range(0,101,5):     
                    for j in range(0,101 - i,3):
                        for k in range(101-i-j):
                            SUM+=1
                            self.ratios.append([i/100, j/100, k/100, (100-i-j-k)/100])  # A, B, C 比例
                            self.q1.append(Qr.calculate_qq_plot(self.np_sample, 
                                        (i/100)*self.aaa4[mmm][0] + 
                                        (j/100)*self.aaa4[mmm][1] + 
                                        (k/100)*self.aaa4[mmm][2]+((100-i-j-k)/100)*self.aaa4[mmm][3],500
                                    )[0])
                            self.q2.append(Qr.calculate_qq_plot(self.np_sample, 
                                        (i/100)*self.aaa4[mmm][0] + 
                                        (j/100)*self.aaa4[mmm][1] + 
                                        (k/100)*self.aaa4[mmm][2]+((100-i-j-k)/100)*self.aaa4[mmm][3],500
                                    )[1])     
                            
                            self.aa.append(Qr.calculate_qq_plot(self.np_sample, 
                                        (i/100)*self.aaa4[mmm][0] + 
                                        (j/100)*self.aaa4[mmm][1] + 
                                        (k/100)*self.aaa4[mmm][2]+((100-i-j-k)/100)*self.aaa4[mmm][3],500
                                    )[2])
                            self.slope.append(Qr.calculate_qq_plot(self.np_sample, 
                                    (i/100)*self.aaa4[mmm][0] + 
                                    (j/100)*self.aaa4[mmm][1] + 
                                    (k/100)*self.aaa4[mmm][2]+((100-i-j-k)/100)*self.aaa4[mmm][3],500
                                )[3]) 
                            self.intercept.append(Qr.calculate_qq_plot(self.np_sample, 
                                    (i/100)*self.aaa4[mmm][0] + 
                                    (j/100)*self.aaa4[mmm][1] + 
                                    (k/100)*self.aaa4[mmm][2]+((100-i-j-k)/100)*self.aaa4[mmm][3],500
                                )[4]) 
            print(str(SUM)+"次")
                    
            # ---------------------- 提取数据并计算三元坐标 ----------------------
            print(self.ratios)
            print()
            ratios_np = np.array(self.ratios)  # (N, 4)：A, B, C, D 列
            print(ratios_np)
            A, B, C, D = ratios_np[:, 0], ratios_np[:, 1], ratios_np[:, 2], ratios_np[:, 3]
            print(A)
            values = np.array(self.aa)  # 相似度值  

            
            # ---------------------- 找到相似度最高点 ----------------------
            idx_max = np.argmax(values)
            A_max, B_max, C_max, D_max = A[idx_max], B[idx_max], C[idx_max], D[idx_max]
            self.max_slope=self.slope[idx_max]
            self.max_intercept=self.intercept[idx_max]
            print("相似度最高点的比例：")
            print(f"A={A_max:.3f}, B={B_max:.3f}, C={C_max:.3f}, D={D_max:.3f}")
            self.value4.append('Q-Q')
            self.value4.append(A_max)
            self.value4.append(B_max)
            self.value4.append(C_max)
            self.value4.append(D_max)
            self.value4.append(max(self.aa))
            
            # ---------------------- 创建仅包含3D四面体的画布 ----------------------
            
            
            # --------------------------------------------
            # 3D四面体展示（无坐标轴，添加刻度）
            # --------------------------------------------
            #ax1 = fig.add_subplot(111, projection='3d')  # 仅一个子图
            ax1 = self.canvas5.figure.add_subplot(111, projection='3d')  # 使用 canvas6 的 figure 添加子图
            # 四面体顶点坐标（保留原始定义）
            vertices = np.array([
                [0, 0, 0],    # A
                [1, 0, 0],    # B
                [0.5, np.sqrt(3)/2, 0],  # C
                [0.5, np.sqrt(3)/6, np.sqrt(6)/3]  # D
            ])
            
            # 绘制四面体边
            edges = [
                [vertices[0], vertices[1]],  # A-B
                [vertices[0], vertices[2]],  # A-C
                [vertices[0], vertices[3]],  # A-D
                [vertices[1], vertices[2]],  # B-C
                [vertices[1], vertices[3]],  # B-D
                [vertices[2], vertices[3]]   # C-D
            ]
            for edge in edges:
                ax1.plot3D(*zip(*edge), 'k-', linewidth=1.5)
            
            # 计算3D坐标（四面体坐标）
            x = A * vertices[0,0] + B * vertices[1,0] + C * vertices[2,0] + D * vertices[3,0]
            y = A * vertices[0,1] + B * vertices[1,1] + C * vertices[2,1] + D * vertices[3,1]
            z = A * vertices[0,2] + B * vertices[1,2] + C * vertices[2,2] + D * vertices[3,2]

            # 绘制散点图
            ax1.scatter(x, y, z, c=values, cmap='viridis', s=5, alpha=0.3, vmin=0,vmax=1)

            # 最高点
            ax1.scatter(
                x[idx_max], y[idx_max], z[idx_max], 
                marker='*', c='red', s=100, edgecolor='k'
            )

            
            # 添加刻度标签到棱上
            def add_ticks(ax, start, end, ticks=5, label=""):
                """在棱上添加刻度标签"""
                direction = end - start
                length = np.linalg.norm(direction)
                unit_vector = direction / length
                
                # 添加刻度线
                for i in range(1, ticks):
                    fraction = i / ticks
                    position = start + fraction * direction
                    
                    # 计算刻度线方向（与棱垂直）
                    # 简单起见，使用XY平面的垂直方向
                    if np.allclose(direction[:2], [0, 0]):  # 如果是垂直棱
                        tick_dir = np.array([1, 0, 0])
                    else:
                        tick_dir = np.array([-direction[1], direction[0], 0])
                        tick_dir = tick_dir / np.linalg.norm(tick_dir[:2])
                    
                    tick_size = 0.03
                    tick_start = position - tick_size * tick_dir
                    tick_end = position + tick_size * tick_dir
                    ax.plot3D(*zip(tick_start, tick_end), 'k-', linewidth=0.8)
                    
                    # 添加刻度标签
#                    label_pos = position + 0.1 * tick_dir
#                    ax.text(*label_pos, f"{fraction:.1f}", fontsize=8, ha='center', va='center')
                
                # 添加端点标签
                ax.text(*(start - 0.05 * unit_vector), "0", fontsize=8, ha='right', va='center')
                ax.text(*(end + 0.05 * unit_vector), "1", fontsize=8, ha='left', va='center')
                ax.text(*((start + end)/2 + 0.1 * tick_dir), label, fontsize=8, ha='center', va='center')
            
            # 在每条棱上添加刻度
            add_ticks(ax1, vertices[0], vertices[1], label="")  # A-B棱
            add_ticks(ax1, vertices[0], vertices[2], label="")  # A-C棱
            add_ticks(ax1, vertices[0], vertices[3], label="")  # A-D棱
            add_ticks(ax1, vertices[1], vertices[2], label="")  # B-C棱
            add_ticks(ax1, vertices[1], vertices[3], label="")  # B-D棱
            add_ticks(ax1, vertices[2], vertices[3], label="")  # C-D棱
            
            # 添加顶点标签
            # ax1.text(*vertices[0], "A", fontsize=14, ha='right', va='top', weight='bold')
            # ax1.text(*vertices[1], "B", fontsize=14, ha='left', va='top', weight='bold')
            # ax1.text(*vertices[2], "C", fontsize=14, ha='center', va='bottom', weight='bold')
            # ax1.text(*vertices[3], "D", fontsize=14, ha='center', va='top', weight='bold')
            # 添加顶点标签（带偏移量）
            offset = 0.2  # 偏移量，可以根据需要调整
            
            # A点标签（左下角）
            ax1.text(vertices[0][0]-offset, vertices[0][1]-offset, vertices[0][2]-offset, 
                     self.headers[2], fontsize=10, ha='right', va='top', weight='bold')
            
            # B点标签（右下角）
            ax1.text(vertices[1][0]+offset, vertices[1][1]-offset, vertices[1][2]-offset, 
                     self.headers[4], fontsize=10, ha='left', va='top', weight='bold')
            
            # C点标签（顶部）
            ax1.text(vertices[2][0], vertices[2][1]+offset, vertices[2][2]-offset, 
                     self.headers[6], fontsize=10, ha='center', va='bottom', weight='bold')  # 修复了重复的va参数
            
            # D点标签（上方）
            ax1.text(vertices[3][0], vertices[3][1], vertices[3][2]+offset, 
                     self.headers[8], fontsize=10, ha='center', va='bottom', weight='bold')
            
            #ax1.set_title("四元比例四面体图 (带刻度)")
            ax1.axis('off')  # 关闭坐标轴
            ax1.view_init(25, 90)  # 设置视角
            #ax1.legend()
            sm = plt.cm.ScalarMappable(cmap='viridis', norm=plt.Normalize(0,1))
            sm.set_array([])
            cbar = self.canvas6.figure.colorbar(
                sm, 
                ax=ax1, 
                pad=0.05,          # 与图形的间距
                aspect=40,         # 核心：减小aspect值（默认20，值越小颜色条越“短粗”）
                orientation="horizontal"
               
            )
            cbar.set_label("R^2", rotation=0, labelpad=5)  # 标签水平放置，更易读
            
            # 调整布局（防止标签被裁剪）
            self.canvas5.figure.set_constrained_layout(True)
                    
            # ---------------------- 刷新 canvas6 画布 ----------------------
            self.canvas5.draw()


            
            
            
            self.canvas.figure.clear()
            

                    
            # 创建1行2列的网格，宽度比例为2:1
            gs = gridspec.GridSpec(1, 3, width_ratios=[3, 1, 1], wspace=0.3)
                    
            # 第一个子图（占据2/3宽度）
            ax1 = self.canvas.figure.add_subplot(gs[0])

            print(idx_max)
            
            inter=idx_max//12852
            print(inter)
            #print(self.aaa[3])
            self.all=A_max*self.aaa4[inter][0]+B_max*self.aaa4[inter][1]+C_max*self.aaa4[inter][2]+D_max*self.aaa4[inter][3]
            print(self.all)
            ax1.plot(self.T, self.all, color='blue', label='option model')  
       
            ax1.plot(self.T, self.np_sample, color='black', label=self.headers[0])
            ax1.set_xlabel("Zircon U-Pb age (Ma)")
            if self.radioButton.isChecked():
                ax1.set_ylabel("PDF")
            if self.radioButton_2.isChecked():
                ax1.set_ylabel("KDE")
            ax1.legend()
                        # 关键：设置x轴间隔为100（每100ma一个刻度）
            ax1.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
            ax1.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
            ax1.set_xlim(min_age, max_age)
            ax1.set_ylim(bottom=0)
                    
            # 第二个子图（占据1/3宽度）
            ax2 = self.canvas.figure.add_subplot(gs[1])
                
            ax2.plot(self.T, np.cumsum(self.all), color='blue', label='option model')  
#        
            ax2.plot(self.T, self.cdf_value_sample, color='black', label=self.headers[0])
            ax2.set_xlabel("Zircon U-Pb age (Ma)")
            ax2.set_ylabel("CDFs")
            ax2.legend()
            ax2.set_xlim(min_age, max_age)
            ax2.set_ylim(0,1)
            ax2.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
            ax2.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
            
            
# 第三个子图（占据1/3宽度）
            ax3 = self.canvas.figure.add_subplot(gs[2])
                    
            ax3.scatter(self.q1, self.q2, s=30, color='blue', alpha=0.6, marker='d')
                                # 添加拟合线
            min_val = min(np.array(self.q1).min(), np.array(self.q2).min())
            max_val = max(np.array(self.q1).max(), np.array(self.q2).max())
            ax3.plot([min_val, max_val], [min_val, max_val], 
                                'k--', linewidth=2, alpha=0.7)
            ax3.set_xlabel(self.headers[0], fontsize=12)
            ax3.set_ylabel('Optional model', fontsize=12)
            ax3.set_xlim(min_val, max_val)
            ax3.set_ylim(min_val, max_val)
            ax3.set_aspect("equal")  # 关键参数
            ax3.text(max_val/2, 0.9*max_val, f'R^2 = {max(self.aa):.2f}', fontsize=12,
                                bbox=dict(facecolor='white', alpha=0.8))  

                # 调整子图间距
            self.canvas.figure.set_constrained_layout(True)
                   # 5. 关键优化：调整整个图形的边距和布局
                #plt.subplots_adjust(left=0.08, right=0.95, top=0.92, bottom=0.2)  # 手动调整边距
            self.canvas.draw()
    
    @pyqtSlot()
    def on_pushButton_20_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.canvas5.figure.clear()
        self.canvas5.draw() 
        self.value4=[]
    
    @pyqtSlot()
    def on_pushButton_21_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        file_path, ok=  QFileDialog.getSaveFileName(self,"Import","" ,"PDF File (*.pdf);;image(*.jpg);;all files(*.*)")   
        print(file_path.strip())
        #判断有点问题可以重新检查下
        if file_path.strip()=='':
            QMessageBox.warning(self, 'Waring', 'Failed!')
        else:
            self.save=self.figure5.savefig(file_path)
            #print(self.save)
            QMessageBox.information(self,'Save','Sucessful!')
    
    @pyqtSlot()
    def on_pushButton_10_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        print('你好')
#        print(self.aaa)
#        print(len(self.aaa))
        show_original = True
        
        self.value_ks=[]
        
        min_age = int(self.lineEdit.text())
        max_age = int(self.lineEdit_2.text())
#        dT_value = int(self.lineEdit_8.text())
#        self.age_range = [min_age, max_age]
#        self.dT = dT_value
#        self.T = np.zeros((self.age_range[1] - self.age_range[0]) // self.dT)
        num = (len(self.headers)-2)//2
        if num == 2:
            self.aa = []
            Ratio_A = []
            self.value2=[]
            self.canvas3.figure.clear()
#            print(self.aaa[0])
            for j in range (len(self.aaa2)):
                for i in range(101):
                    Ratio_A.append(i/100)
                    ksks=kut.kuipertest2_tnc(self.np_sample, (i/100)*self.aaa2[j][0] + ((100-i)/100)*(i/100)*self.aaa2[j][1],len(self.T))[1]
                    self.aa.append(ksks)
#            print(self.aa)
#            print(len(self.aa))
            
            self.max_aa = np.max(np.array(self.aa)[~np.isnan(self.aa)])
            self.max_aa_index=np.argmax(np.array(self.aa)[~np.isnan(self.aa)])
            print(self.max_aa_index)
            self.max_Ratio_A=Ratio_A[self.max_aa_index]
            #self.value_ks.append[max_Ratio_A,1-max_Ratio_A,max_aa]

            print(self.max_Ratio_A,1-self.max_Ratio_A,self.max_aa)
            self.value2.append('Kuiper')
            self.value2.append(self.max_Ratio_A)
            self.value2.append(1-self.max_Ratio_A)
            self.value2.append(self.max_aa)
            # 数据处理和插值（保持不变）
            x_data = np.clip(Ratio_A, 0, 1)
            z_data = np.clip(self.aa, 0, 1)
            sorted_indices = np.argsort(x_data)
            x_sorted, z_sorted = x_data[sorted_indices], z_data[sorted_indices]
            _, unique_mask = np.unique(x_sorted, return_index=True)
            x_unique, z_unique = x_sorted[unique_mask], z_sorted[unique_mask]
            
            if len(x_unique) >= 2:
                from scipy.interpolate import interp1d
                x_interp = np.linspace(0, 1, 1000)
                interp_func = interp1d(x_unique, z_unique, kind="linear", bounds_error=False, fill_value=0.5)
                z_interp = interp_func(x_interp)
                
                # 绘制条带图（保持不变）
                ax = self.canvas3.figure.add_subplot(111)
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.set_yticks([0.5])
                ax.set_yticklabels([self.headers[0]], rotation=90, va="top")
                ax.set_xlabel(self.headers[2], fontsize=10, labelpad=3)
                
                ax_top = ax.twiny()
                ax_top.set_xlim(0, 1)
                ax_top.set_xlabel(self.headers[4], fontsize=10, labelpad=3)
                ax_top.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
                ax_top.set_xticklabels([1.0, 0.8, 0.6, 0.4, 0.2, 0.0])
                ax_top.set_title(str(self.max_Ratio_A)+"_"+str(1-self.max_Ratio_A)+"_ "+str(self.max_aa))
                
                cmap = plt.cm.get_cmap("viridis")
                norm = plt.Normalize(0, 1)
                ax.pcolormesh(
                    x_interp, [0.0, 1.0], z_interp.reshape(1, -1),
                    cmap=cmap, norm=norm, shading="auto", alpha=0.9
                )
                
                if show_original:
                    ax.vlines(x=x_data, ymin=0, ymax=1.0, color="gray", linewidth=0.8, alpha=0.4)
                
                # 颜色条（保持不变）
                sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
                sm.set_array([])
                # 创建水平颜色条（关键参数：orientation="horizontal"）
                cbar = plt.colorbar(
                    sm, 
                    ax=ax, 
                    pad=0.2,                # 颜色条与主图的间距（垂直方向，因水平放置）
                    orientation="horizontal", 
                    aspect=30,
                    shrink=0.8 # 颜色条的长宽比（数值越大越扁长，适配主图宽度）
                )
                cbar.set_label("V value", rotation=0, labelpad=5)
                
                
                # 调整边距（使用 canvas6.figure）
                self.canvas3.figure.set_constrained_layout(True)
        
        # 4. 刷新画布
        #plt.tight_layout()
                self.canvas3.draw()
                
                self.canvas.figure.clear()
                gs = gridspec.GridSpec(1, 2, width_ratios=[2, 1], wspace=0.3) 
                
                # 第一个子图（占据2/3宽度）
                ax1 = self.canvas.figure.add_subplot(gs[0])
                inter=self.max_aa_index//101
                print(inter)
                print(self.aaa2[3])
                self.all=self.max_Ratio_A*self.aaa2[inter][0]+(1-self.max_Ratio_A)*self.aaa2[inter][1]
                print(self.all)
                ax1.plot(self.T, self.all, color='blue', label='option model')  
                ax1.plot(self.T, self.np_sample, color='black', label=self.headers[0])
                ax1.set_xlabel("Zircon U-Pb age (Ma)")
                if self.radioButton.isChecked():
                    ax1.set_ylabel("PDF")
                if self.radioButton_2.isChecked():
                    ax1.set_ylabel("KDE")
   
                ax1.legend()
                    # 关键：设置x轴间隔为100（每100ma一个刻度）
                ax1.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
                ax1.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
                ax1.set_xlim(min_age, max_age)
                ax1.set_ylim(bottom=0)
                
                # 第二个子图（占据1/3宽度）
                ax2 = self.canvas.figure.add_subplot(gs[1])
                
                ax2.plot(self.T, np.cumsum(self.all), color='blue', label='option model')  
#        
                ax2.plot(self.T, self.cdf_value_sample, color='black', label=self.headers[0])
                ax2.set_xlabel("Zircon U-Pb age (Ma)")
                ax2.set_ylabel("CDFs")
                ax2.legend()
                ax2.set_xlim(min_age, max_age)
                ax2.set_ylim(0,1)
                ax2.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
                ax2.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
                
                self.canvas.figure.set_constrained_layout(True)
                   # 5. 关键优化：调整整个图形的边距和布局
                #plt.subplots_adjust(left=0.08, right=0.95, top=0.92, bottom=0.2)  # 手动调整边距
                self.canvas.draw()
                

                
        if num == 3:
            self.ratios = []  # 存储所有 [A, B, C] 比例
            self.aa = []      # 存储所有相似度值
            self.value2=[]
            self.canvas3.figure.clear()  # 清空 canvas6 画布

            print(len(self.aaa2))
            for mmm in range (len(self.aaa2)):
                            # 生成 A/B/C 比例和相似度值
                for i in range(101):     
                    for j in range(101 - i):
                        self.ratios.append([i/100, j/100, (100 - i - j)/100])  # A, B, C 比例
                        self.aa.append(kut.kuipertest2_tnc(self.np_sample, 
                                    (i/100)*self.aaa2[mmm][0] + 
                                    (j/100)*self.aaa2[mmm][1] + 
                                    ((100-i-j)/100)*self.aaa2[mmm][2],len(self.T)
                                )[1])
    #            print(self.aa)
#            print(len(self.aa))
    
            print(self.aa)
            print(len(self.aa))
                        # ---------------------- 提取数据并计算三元坐标 ----------------------
            ratios_np = np.array(self.ratios)  # (N, 3)：A, B, C 列
            A, B, C = ratios_np[:, 0], ratios_np[:, 1], ratios_np[:, 2]
            values = np.array(self.aa)  # 相似度值
                    
            # 三元坐标投影（将 A/B/C 转换为 2D 平面坐标）
            denominator = A + B + C + 1e-12  # 避免除零
            x = 0.5 * (2 * B + C) / denominator  # 三元图 x 坐标
            y = (np.sqrt(3) / 2) * C / denominator  # 三元图 y 坐标
                    
            # ---------------------- 找到最高相似度点 ----------------------
            idx_max = np.argmax(values)
            x_max, y_max = x[idx_max], y[idx_max]  # 最高相似度点坐标
            A_max, B_max, C_max = A[idx_max], B[idx_max], C[idx_max]  # 最优比例
            self.value2.append('Kuiper')
            self.value2.append(A_max)
            self.value2.append(B_max)
            self.value2.append(C_max)
            self.value2.append(max(self.aa))            
                                                        
            print("最高相似度点比例：")
            print(f"A={A_max:.3f}, B={B_max:.3f}, C={C_max:.3f}")
            print(f"最高相似度值：{values[idx_max]:.4f}")
            
            # ---------------------- 在 canvas6 中绘制三元相图 ----------------------
            # 创建子图（替换原 plt.figure() 和 ax = plt.subplot()）
            ax = self.canvas3.figure.add_subplot(111)  # 使用 canvas6 的 figure 添加子图
                    
            # 1. 绘制插值网格背景（平滑颜色）
            grid_x, grid_y = np.mgrid[0:1:200j, 0:np.sqrt(3)/2:200j]
            grid_z = griddata((x, y), values, (grid_x, grid_y), method='linear')
            #grid_z = np.nan_to_num(grid_z, nan=0.0)  # NaN用0填充（或用values.min()）
            ax.pcolormesh(grid_x, grid_y, grid_z, cmap='viridis', alpha=0.8, shading='gouraud',  vmin=0,vmax=1)
                    
            # 2. 绘制三角边界（等边三角形）
            triangle = np.array([[0, 0], [1, 0], [0.5, np.sqrt(3)/2], [0, 0]])
            ax.plot(triangle[:, 0], triangle[:, 1], 'k-', linewidth=1.5)
                    
            # 3. 绘制原始数据点（可选）
            ax.scatter(x, y, c=values, cmap='viridis', s=5, alpha=0.3,  vmin=0,vmax=1)
                    
            # 4. 标记最高相似度点（红色五角星）
            ax.scatter(x_max, y_max, marker="*", c="red", s=200, edgecolor="k", label="最高相似度点")
                    
            # 5. 添加 A/B/C 轴刻度和标签
            n_ticks = 5
            tick_values = np.linspace(0, 1, n_ticks + 1)
                    
            # A 轴刻度（左下 -> 上顶点）
            for t in tick_values[1:-1]:
                x_tick = 0.5 * (1 - t)
                y_tick = (np.sqrt(3)/2) * (1 - t)
                ax.plot([x_tick, x_tick - 0.02], [y_tick, y_tick], 'k-', linewidth=0.8)
                ax.text(x_tick - 0.04, y_tick, f"{t:.1f}", fontsize=9, ha="right", va="center")
                    
            # B 轴刻度（右下 -> 上顶点）
            for t in tick_values[1:-1]:
                x_tick = 0.5 * (1 + t)
                y_tick = (np.sqrt(3)/2) * (1 - t)
                ax.plot([x_tick, x_tick + 0.02], [y_tick, y_tick], 'k-', linewidth=0.8)
                ax.text(x_tick + 0.04, y_tick, f"{t:.1f}", fontsize=9, ha="left", va="center")
                    
            # C 轴刻度（底部 -> 上顶点）
            for t in tick_values[1:-1]:
                x_tick = t
                y_tick = 0
                ax.plot([x_tick, x_tick], [y_tick, y_tick - 0.02], 'k-', linewidth=0.8)
                ax.text(x_tick, y_tick - 0.05, f"{t:.1f}", fontsize=9, ha="center", va="top")
                    
            # 顶点标签（A/B/C）
            ax.text(-0.05, -0.05, self.headers[2], fontsize=12, ha="right", va="top", fontweight="bold")
            ax.text(1.05, -0.05, self.headers[4], fontsize=12, ha="left", va="top", fontweight="bold")
            ax.text(0.5, np.sqrt(3)/2 + 0.05, self.headers[6], fontsize=12, ha="center", va="bottom", fontweight="bold")
                    
            # ---------------------- 图表设置 ----------------------
            #ax.set_title(f"三元相图 (最高相似度: {max(values):.4f})", fontsize=12, pad=20)
            ax.set_aspect("equal")  # 等比例坐标轴（保证三角形为正三角形）
            ax.axis("off")  # 关闭默认坐标轴
                    
            # 添加颜色条（绑定到 canvas6 的 figure）
            #sm = plt.cm.ScalarMappable(cmap='viridis', norm=plt.Normalize(values.min(), values.max()))
            sm = plt.cm.ScalarMappable(cmap='viridis', norm=plt.Normalize(0,1))
            sm.set_array([])
            cbar = self.canvas3.figure.colorbar(sm, ax=ax, pad=0.05, orientation="horizontal", aspect=40)
            cbar.set_label("V value", rotation=0, labelpad=10)
                    
            # 调整布局（防止标签被裁剪）
            self.canvas3.figure.set_constrained_layout(True)
                    
            # ---------------------- 刷新 canvas6 画布 ----------------------
            self.canvas3.draw()
            self.canvas.figure.clear()
            gs = gridspec.GridSpec(1, 2, width_ratios=[2, 1], wspace=0.3) 

                
            # 第一个子图（占据2/3宽度）
            print(idx_max)
            ax1 = self.canvas.figure.add_subplot(gs[0])
            inter=idx_max//5151
            print(inter)
            #print(self.aaa[3])
            self.all=A_max*self.aaa2[inter][0]+B_max*self.aaa2[inter][1]+C_max*self.aaa2[inter][2]
            print(self.all)
            ax1.plot(self.T, self.all, color='blue', label='option model')  
            ax1.plot(self.T, self.np_sample, color='black', label=self.headers[0])
            ax1.set_xlabel("Zircon U-Pb age (Ma)")
            if self.radioButton.isChecked():
                ax1.set_ylabel("PDF")
            if self.radioButton_2.isChecked():
                ax1.set_ylabel("KDE")
            ax1.legend()
                    # 关键：设置x轴间隔为100（每100ma一个刻度）
            ax1.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
            ax1.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
            ax1.set_xlim(min_age, max_age)
            ax1.set_ylim(bottom=0)
                
                # 第二个子图（占据1/3宽度）
            ax2 = self.canvas.figure.add_subplot(gs[1])
                
            ax2.plot(self.T, np.cumsum(self.all), color='blue', label='option model')  
#        
            ax2.plot(self.T, self.cdf_value_sample, color='black', label=self.headers[0])
            ax2.set_xlabel("Zircon U-Pb age (Ma)")
            ax2.set_ylabel("CDFs")
            ax2.legend()
            ax2.set_xlim(min_age, max_age)
            ax2.set_ylim(0,1)
            ax2.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
            ax2.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
                
            self.canvas.figure.set_constrained_layout(True)
                   # 5. 关键优化：调整整个图形的边距和布局
                #plt.subplots_adjust(left=0.08, right=0.95, top=0.92, bottom=0.2)  # 手动调整边距
            self.canvas.draw()                    
        if num == 4:
            
            
            
                    # ---------------------- 初始化空列表（放在循环外！） ----------------------
            self.ratios = []  # 存储所有 [A, B, C] 比例
            self.aa = []      # 存储所有相似度值
            self.value2=[]
            self.canvas3.figure.clear()  # 清空 canvas6 画布
            SUM=0
            print(len(self.aaa2))
            for mmm in range (len(self.aaa2)):       
            # 生成 A/B/C 比例和相似度值
                for i in range(0,101,5):     
                    for j in range(0,101 - i,3):
                        for k in range(101-i-j):
                            SUM+=1
                            self.ratios.append([i/100, j/100, k/100, (100-i-j-k)/100])  # A, B, C 比例
                            self.aa.append(kut.kuipertest2_tnc(self.np_sample, 
                                        (i/100)*self.aaa2[mmm][0] + 
                                        (j/100)*self.aaa2[mmm][1] + 
                                        (k/100)*self.aaa2[mmm][2]+((100-i-j-k)/100)*self.aaa2[mmm][3],len(self.T)
                                    )[1])
            print(str(SUM)+"次")
                    
            # ---------------------- 提取数据并计算三元坐标 ----------------------
            print(self.ratios)

            ratios_np = np.array(self.ratios)  # (N, 4)：A, B, C, D 列
            print(ratios_np)
            A, B, C, D = ratios_np[:, 0], ratios_np[:, 1], ratios_np[:, 2], ratios_np[:, 3]
            print(A)
            values = np.array(self.aa)  # 相似度值  

            
            # ---------------------- 找到相似度最高点 ----------------------
            idx_max = np.argmax(values)
            A_max, B_max, C_max, D_max = A[idx_max], B[idx_max], C[idx_max], D[idx_max]
            self.value2.append('Kuiper')
            self.value2.append(A_max)
            self.value2.append(B_max)
            self.value2.append(C_max)
            self.value2.append(D_max)
            self.value2.append(max(self.aa))  
            print("相似度最高点的比例：")
            print(f"A={A_max:.3f}, B={B_max:.3f}, C={C_max:.3f}, D={D_max:.3f}")
            
            # ---------------------- 创建仅包含3D四面体的画布 ----------------------
            
            
            # --------------------------------------------
            # 3D四面体展示（无坐标轴，添加刻度）
            # --------------------------------------------
            #ax1 = fig.add_subplot(111, projection='3d')  # 仅一个子图
            ax1 = self.canvas3.figure.add_subplot(111, projection='3d')  # 使用 canvas6 的 figure 添加子图
            # 四面体顶点坐标（保留原始定义）
            vertices = np.array([
                [0, 0, 0],    # A
                [1, 0, 0],    # B
                [0.5, np.sqrt(3)/2, 0],  # C
                [0.5, np.sqrt(3)/6, np.sqrt(6)/3]  # D
            ])
            
            # 绘制四面体边
            edges = [
                [vertices[0], vertices[1]],  # A-B
                [vertices[0], vertices[2]],  # A-C
                [vertices[0], vertices[3]],  # A-D
                [vertices[1], vertices[2]],  # B-C
                [vertices[1], vertices[3]],  # B-D
                [vertices[2], vertices[3]]   # C-D
            ]
            for edge in edges:
                ax1.plot3D(*zip(*edge), 'k-', linewidth=1.5)
            
            # 计算3D坐标（四面体坐标）
            x = A * vertices[0,0] + B * vertices[1,0] + C * vertices[2,0] + D * vertices[3,0]
            y = A * vertices[0,1] + B * vertices[1,1] + C * vertices[2,1] + D * vertices[3,1]
            z = A * vertices[0,2] + B * vertices[1,2] + C * vertices[2,2] + D * vertices[3,2]

            # 绘制散点图
            ax1.scatter(x, y, z, c=values, cmap='viridis', s=5, alpha=0.3, vmin=0,vmax=1)

            # 最高点
            ax1.scatter(
                x[idx_max], y[idx_max], z[idx_max], 
                marker='*', c='red', s=100, edgecolor='k'
            )

            
            # 添加刻度标签到棱上
            def add_ticks(ax, start, end, ticks=5, label=""):
                """在棱上添加刻度标签"""
                direction = end - start
                length = np.linalg.norm(direction)
                unit_vector = direction / length
                
                # 添加刻度线
                for i in range(1, ticks):
                    fraction = i / ticks
                    position = start + fraction * direction
                    
                    # 计算刻度线方向（与棱垂直）
                    # 简单起见，使用XY平面的垂直方向
                    if np.allclose(direction[:2], [0, 0]):  # 如果是垂直棱
                        tick_dir = np.array([1, 0, 0])
                    else:
                        tick_dir = np.array([-direction[1], direction[0], 0])
                        tick_dir = tick_dir / np.linalg.norm(tick_dir[:2])
                    
                    tick_size = 0.03
                    tick_start = position - tick_size * tick_dir
                    tick_end = position + tick_size * tick_dir
                    ax.plot3D(*zip(tick_start, tick_end), 'k-', linewidth=0.8)
                    
                    # 添加刻度标签
#                    label_pos = position + 0.1 * tick_dir
#                    ax.text(*label_pos, f"{fraction:.1f}", fontsize=8, ha='center', va='center')
                
                # 添加端点标签
                ax.text(*(start - 0.05 * unit_vector), "0", fontsize=8, ha='right', va='center')
                ax.text(*(end + 0.05 * unit_vector), "1", fontsize=8, ha='left', va='center')
                ax.text(*((start + end)/2 + 0.1 * tick_dir), label, fontsize=8, ha='center', va='center')
            
            # 在每条棱上添加刻度
            add_ticks(ax1, vertices[0], vertices[1], label="")  # A-B棱
            add_ticks(ax1, vertices[0], vertices[2], label="")  # A-C棱
            add_ticks(ax1, vertices[0], vertices[3], label="")  # A-D棱
            add_ticks(ax1, vertices[1], vertices[2], label="")  # B-C棱
            add_ticks(ax1, vertices[1], vertices[3], label="")  # B-D棱
            add_ticks(ax1, vertices[2], vertices[3], label="")  # C-D棱
            
            # 添加顶点标签
            # ax1.text(*vertices[0], "A", fontsize=14, ha='right', va='top', weight='bold')
            # ax1.text(*vertices[1], "B", fontsize=14, ha='left', va='top', weight='bold')
            # ax1.text(*vertices[2], "C", fontsize=14, ha='center', va='bottom', weight='bold')
            # ax1.text(*vertices[3], "D", fontsize=14, ha='center', va='top', weight='bold')
            # 添加顶点标签（带偏移量）
            offset = 0.2  # 偏移量，可以根据需要调整
            
            # A点标签（左下角）
            ax1.text(vertices[0][0]-offset, vertices[0][1]-offset, vertices[0][2]-offset, 
                     self.headers[2], fontsize=10, ha='right', va='top', weight='bold')
            
            # B点标签（右下角）
            ax1.text(vertices[1][0]+offset, vertices[1][1]-offset, vertices[1][2]-offset, 
                     self.headers[4], fontsize=10, ha='left', va='top', weight='bold')
            
            # C点标签（顶部）
            ax1.text(vertices[2][0], vertices[2][1]+offset, vertices[2][2]-offset, 
                     self.headers[6], fontsize=10, ha='center', va='bottom', weight='bold')  # 修复了重复的va参数
            
            # D点标签（上方）
            ax1.text(vertices[3][0], vertices[3][1], vertices[3][2]+offset, 
                     self.headers[8], fontsize=10, ha='center', va='bottom', weight='bold')
            
            #ax1.set_title("四元比例四面体图 (带刻度)")
            ax1.axis('off')  # 关闭坐标轴
            ax1.view_init(25, 90)  # 设置视角
            #ax1.legend()
            sm = plt.cm.ScalarMappable(cmap='viridis', norm=plt.Normalize(0,1))
            sm.set_array([])
            cbar = self.canvas3.figure.colorbar(
                sm, 
                ax=ax1, 
                pad=0.05,          # 与图形的间距
                aspect=40,         # 核心：减小aspect值（默认20，值越小颜色条越“短粗”）
                orientation="horizontal"
               
            )
            cbar.set_label("V value", rotation=0, labelpad=5)  # 标签水平放置，更易读
            
            # 调整布局（防止标签被裁剪）
            self.canvas3.figure.set_constrained_layout(True)
                    
            # ---------------------- 刷新 canvas6 画布 ----------------------
            self.canvas3.draw()


            self.canvas.figure.clear()
            

                    
            # 创建1行2列的网格，宽度比例为2:1
            gs = gridspec.GridSpec(1, 2, width_ratios=[2, 1], wspace=0.3) 
                    
            # 第一个子图（占据2/3宽度）
            ax1 = self.canvas.figure.add_subplot(gs[0])

            print(idx_max)
            
            inter=idx_max//12852
            print(inter)
            #print(self.aaa[3])
            self.all=A_max*self.aaa2[inter][0]+B_max*self.aaa2[inter][1]+C_max*self.aaa2[inter][2]+D_max*self.aaa2[inter][2]
            print(self.all)
            ax1.plot(self.T, self.all, color='blue', label='option model')  
       
            ax1.plot(self.T, self.np_sample, color='black', label=self.headers[0])
            ax1.set_xlabel("Zircon U-Pb age (Ma)")
            if self.radioButton.isChecked():
                ax1.set_ylabel("PDF")
            if self.radioButton_2.isChecked():
                ax1.set_ylabel("KDE")
            ax1.legend()
                        # 关键：设置x轴间隔为100（每100ma一个刻度）
            ax1.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
            ax1.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
            ax1.set_xlim(min_age, max_age)
            ax1.set_ylim(bottom=0)
                    
            # 第二个子图（占据1/3宽度）
            ax2 = self.canvas.figure.add_subplot(gs[1])
                
            ax2.plot(self.T, np.cumsum(self.all), color='blue', label='option model')  
#        
            ax2.plot(self.T, self.cdf_value_sample, color='black', label=self.headers[0])
            ax2.set_xlabel("Zircon U-Pb age (Ma)")
            ax2.set_ylabel("CDFs")
            ax2.legend()
            ax2.set_xlim(min_age, max_age)
            ax2.set_ylim(0,1)
            ax2.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
            ax2.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度


                # 调整子图间距
            self.canvas.figure.set_constrained_layout(True)
                   # 5. 关键优化：调整整个图形的边距和布局
                #plt.subplots_adjust(left=0.08, right=0.95, top=0.92, bottom=0.2)  # 手动调整边距
            self.canvas.draw()
    
    @pyqtSlot()
    def on_pushButton_11_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.canvas3.figure.clear()
        self.canvas3.draw() 
        self.value2=[]
    
    @pyqtSlot()
    def on_pushButton_12_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        file_path, ok=  QFileDialog.getSaveFileName(self,"Import","" ,"PDF File (*.pdf);;image(*.jpg);;all files(*.*)")   
        print(file_path.strip())
        #判断有点问题可以重新检查下
        if file_path.strip()=='':
            QMessageBox.warning(self, 'Waring', 'Failed!')
        else:
            self.save=self.figure3.savefig(file_path)
            #print(self.save)
            QMessageBox.information(self,'Save','Sucessful!')
    
    @pyqtSlot()
    def on_pushButton_22_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        print('你好')
#        print(self.aaa)
#        print(len(self.aaa))
        show_original = True
        
        self.value_ks=[]
        
        min_age = int(self.lineEdit.text())
        max_age = int(self.lineEdit_2.text())
#        dT_value = int(self.lineEdit_8.text())
#        self.age_range = [min_age, max_age]
#        self.dT = dT_value
#        self.T = np.zeros((self.age_range[1] - self.age_range[0]) // self.dT)
        num = (len(self.headers)-2)//2
        if num == 2:
            self.aa = []
            Ratio_A = []
            self.value5=[]
            self.canvas6.figure.clear()
#            print(self.aaa[0])
            for j in range (len(self.aaa5)):
                for i in range(101):
                    Ratio_A.append(i/100)
                    ksks=sim.Similarity(self.np_sample, (i/100)*self.aaa5[j][0] + ((100-i)/100)*(i/100)*self.aaa5[j][1])
                    
                    self.aa.append(ksks)
#            print(self.aa)
#            print(len(self.aa))
            
            self.max_aa = np.max(np.array(self.aa)[~np.isnan(self.aa)])
            self.max_aa_index=np.argmax(np.array(self.aa)[~np.isnan(self.aa)])
            print(self.max_aa_index)
            self.max_Ratio_A=Ratio_A[self.max_aa_index]
            #self.value_ks.append[max_Ratio_A,1-max_Ratio_A,max_aa]

            print(self.max_Ratio_A,1-self.max_Ratio_A,self.max_aa)
            self.value5.append('Similarity')
            self.value5.append(self.max_Ratio_A)
            self.value5.append(1-self.max_Ratio_A)
            self.value5.append(self.max_aa)
            # 数据处理和插值（保持不变）
            x_data = np.clip(Ratio_A, 0, 1)
            z_data = np.clip(self.aa, 0, 1)
            sorted_indices = np.argsort(x_data)
            x_sorted, z_sorted = x_data[sorted_indices], z_data[sorted_indices]
            _, unique_mask = np.unique(x_sorted, return_index=True)
            x_unique, z_unique = x_sorted[unique_mask], z_sorted[unique_mask]
            
            if len(x_unique) >= 2:
                from scipy.interpolate import interp1d
                x_interp = np.linspace(0, 1, 1000)
                interp_func = interp1d(x_unique, z_unique, kind="linear", bounds_error=False, fill_value=0.5)
                z_interp = interp_func(x_interp)
                
                # 绘制条带图（保持不变）
                ax = self.canvas6.figure.add_subplot(111)
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.set_yticks([0.5])
                ax.set_yticklabels([self.headers[0]], rotation=90, va="top")
                ax.set_xlabel(self.headers[2], fontsize=10, labelpad=3)
                
                ax_top = ax.twiny()
                ax_top.set_xlim(0, 1)
                ax_top.set_xlabel(self.headers[4], fontsize=10, labelpad=3)
                ax_top.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
                ax_top.set_xticklabels([1.0, 0.8, 0.6, 0.4, 0.2, 0.0])
                ax_top.set_title(str(self.max_Ratio_A)+"_"+str(1-self.max_Ratio_A)+"_ "+str(self.max_aa))
                
                cmap = plt.cm.get_cmap("viridis")
                norm = plt.Normalize(0, 1)
                ax.pcolormesh(
                    x_interp, [0.0, 1.0], z_interp.reshape(1, -1),
                    cmap=cmap, norm=norm, shading="auto", alpha=0.9
                )
                
                if show_original:
                    ax.vlines(x=x_data, ymin=0, ymax=1.0, color="gray", linewidth=0.8, alpha=0.4)
                
                # 颜色条（保持不变）
                sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
                sm.set_array([])
                # 创建水平颜色条（关键参数：orientation="horizontal"）
                cbar = plt.colorbar(
                    sm, 
                    ax=ax, 
                    pad=0.2,                # 颜色条与主图的间距（垂直方向，因水平放置）
                    orientation="horizontal", 
                    aspect=30,
                    shrink=0.8 # 颜色条的长宽比（数值越大越扁长，适配主图宽度）
                )
                cbar.set_label("Similarity", rotation=0, labelpad=5)
                
                
                # 调整边距（使用 canvas6.figure）
                self.canvas6.figure.set_constrained_layout(True)
        
        # 4. 刷新画布
        #plt.tight_layout()
                self.canvas6.draw()
                
                self.canvas.figure.clear()
                gs = gridspec.GridSpec(1, 2, width_ratios=[2, 1], wspace=0.3) 
                
                # 第一个子图（占据2/3宽度）
                ax1 = self.canvas.figure.add_subplot(gs[0])
                inter=self.max_aa_index//101
                print(inter)
              
                self.all=self.max_Ratio_A*self.aaa5[inter][0]+(1-self.max_Ratio_A)*self.aaa5[inter][1]
                print(self.all)
                ax1.plot(self.T, self.all, color='blue', label='option model')  
                ax1.plot(self.T, self.np_sample, color='black', label=self.headers[0])
                ax1.set_xlabel("Zircon U-Pb age (Ma)")
                if self.radioButton.isChecked():
                    ax1.set_ylabel("PDF")
                if self.radioButton_2.isChecked():
                    ax1.set_ylabel("KDE")
   
                ax1.legend()
                    # 关键：设置x轴间隔为100（每100ma一个刻度）
                ax1.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
                ax1.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
                ax1.set_xlim(min_age, max_age)
                ax1.set_ylim(bottom=0)
                
                # 第二个子图（占据1/3宽度）
                ax2 = self.canvas.figure.add_subplot(gs[1])
                
                ax2.plot(self.T, np.cumsum(self.all), color='blue', label='option model')  
#        
                ax2.plot(self.T, self.cdf_value_sample, color='black', label=self.headers[0])
                ax2.set_xlabel("Zircon U-Pb age (Ma)")
                ax2.set_ylabel("CDFs")
                ax2.legend()
                ax2.set_xlim(min_age, max_age)
                ax2.set_ylim(0,1)
                ax2.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
                ax2.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
                
                self.canvas.figure.set_constrained_layout(True)
                   # 5. 关键优化：调整整个图形的边距和布局
                #plt.subplots_adjust(left=0.08, right=0.95, top=0.92, bottom=0.2)  # 手动调整边距
                self.canvas.draw()
                

                
        if num == 3:
            self.ratios = []  # 存储所有 [A, B, C] 比例
            self.aa = []      # 存储所有相似度值
            self.value5=[]
            self.canvas6.figure.clear()  # 清空 canvas6 画布

            print(len(self.aaa5))
            for mmm in range (len(self.aaa5)):
                            # 生成 A/B/C 比例和相似度值
                for i in range(101):     
                    for j in range(101 - i):
                        self.ratios.append([i/100, j/100, (100 - i - j)/100])  # A, B, C 比例
                        self.aa.append(sim.Similarity(self.np_sample, 
                                    (i/100)*self.aaa5[mmm][0] + 
                                    (j/100)*self.aaa5[mmm][1] + 
                                    ((100-i-j)/100)*self.aaa5[mmm][2]
                                ))
    #            print(self.aa)
#            print(len(self.aa))
    
            print(self.aa)
            print(len(self.aa))
                        # ---------------------- 提取数据并计算三元坐标 ----------------------
            ratios_np = np.array(self.ratios)  # (N, 3)：A, B, C 列
            A, B, C = ratios_np[:, 0], ratios_np[:, 1], ratios_np[:, 2]
            values = np.array(self.aa)  # 相似度值
                    
            # 三元坐标投影（将 A/B/C 转换为 2D 平面坐标）
            denominator = A + B + C + 1e-12  # 避免除零
            x = 0.5 * (2 * B + C) / denominator  # 三元图 x 坐标
            y = (np.sqrt(3) / 2) * C / denominator  # 三元图 y 坐标
                    
            # ---------------------- 找到最高相似度点 ----------------------
            idx_max = np.argmax(values)
            x_max, y_max = x[idx_max], y[idx_max]  # 最高相似度点坐标
            A_max, B_max, C_max = A[idx_max], B[idx_max], C[idx_max]  # 最优比例
            self.value5.append('Similarity')
            self.value5.append(A_max)
            self.value5.append(B_max)
            self.value5.append(C_max)
            self.value5.append(max(self.aa))            
                                                        
            print("最高相似度点比例：")
            print(f"A={A_max:.3f}, B={B_max:.3f}, C={C_max:.3f}")
            print(f"最高相似度值：{values[idx_max]:.4f}")
            
            # ---------------------- 在 canvas6 中绘制三元相图 ----------------------
            # 创建子图（替换原 plt.figure() 和 ax = plt.subplot()）
            ax = self.canvas6.figure.add_subplot(111)  # 使用 canvas6 的 figure 添加子图
                    
            # 1. 绘制插值网格背景（平滑颜色）
            grid_x, grid_y = np.mgrid[0:1:200j, 0:np.sqrt(3)/2:200j]
            grid_z = griddata((x, y), values, (grid_x, grid_y), method='linear')
            #grid_z = np.nan_to_num(grid_z, nan=0.0)  # NaN用0填充（或用values.min()）
            ax.pcolormesh(grid_x, grid_y, grid_z, cmap='viridis', alpha=0.8, shading='gouraud',  vmin=0,vmax=1)
                    
            # 2. 绘制三角边界（等边三角形）
            triangle = np.array([[0, 0], [1, 0], [0.5, np.sqrt(3)/2], [0, 0]])
            ax.plot(triangle[:, 0], triangle[:, 1], 'k-', linewidth=1.5)
                    
            # 3. 绘制原始数据点（可选）
            ax.scatter(x, y, c=values, cmap='viridis', s=5, alpha=0.3,  vmin=0,vmax=1)
                    
            # 4. 标记最高相似度点（红色五角星）
            ax.scatter(x_max, y_max, marker="*", c="red", s=200, edgecolor="k", label="最高相似度点")
                    
            # 5. 添加 A/B/C 轴刻度和标签
            n_ticks = 5
            tick_values = np.linspace(0, 1, n_ticks + 1)
                    
            # A 轴刻度（左下 -> 上顶点）
            for t in tick_values[1:-1]:
                x_tick = 0.5 * (1 - t)
                y_tick = (np.sqrt(3)/2) * (1 - t)
                ax.plot([x_tick, x_tick - 0.02], [y_tick, y_tick], 'k-', linewidth=0.8)
                ax.text(x_tick - 0.04, y_tick, f"{t:.1f}", fontsize=9, ha="right", va="center")
                    
            # B 轴刻度（右下 -> 上顶点）
            for t in tick_values[1:-1]:
                x_tick = 0.5 * (1 + t)
                y_tick = (np.sqrt(3)/2) * (1 - t)
                ax.plot([x_tick, x_tick + 0.02], [y_tick, y_tick], 'k-', linewidth=0.8)
                ax.text(x_tick + 0.04, y_tick, f"{t:.1f}", fontsize=9, ha="left", va="center")
                    
            # C 轴刻度（底部 -> 上顶点）
            for t in tick_values[1:-1]:
                x_tick = t
                y_tick = 0
                ax.plot([x_tick, x_tick], [y_tick, y_tick - 0.02], 'k-', linewidth=0.8)
                ax.text(x_tick, y_tick - 0.05, f"{t:.1f}", fontsize=9, ha="center", va="top")
                    
            # 顶点标签（A/B/C）
            ax.text(-0.05, -0.05, self.headers[2], fontsize=12, ha="right", va="top", fontweight="bold")
            ax.text(1.05, -0.05, self.headers[4], fontsize=12, ha="left", va="top", fontweight="bold")
            ax.text(0.5, np.sqrt(3)/2 + 0.05, self.headers[6], fontsize=12, ha="center", va="bottom", fontweight="bold")
                    
            # ---------------------- 图表设置 ----------------------
            #ax.set_title(f"三元相图 (最高相似度: {max(values):.4f})", fontsize=12, pad=20)
            ax.set_aspect("equal")  # 等比例坐标轴（保证三角形为正三角形）
            ax.axis("off")  # 关闭默认坐标轴
                    
            # 添加颜色条（绑定到 canvas6 的 figure）
            #sm = plt.cm.ScalarMappable(cmap='viridis', norm=plt.Normalize(values.min(), values.max()))
            sm = plt.cm.ScalarMappable(cmap='viridis', norm=plt.Normalize(0,1))
            sm.set_array([])
            cbar = self.canvas3.figure.colorbar(sm, ax=ax, pad=0.05, orientation="horizontal", aspect=40)
            cbar.set_label("Similarity", rotation=0, labelpad=10)
                    
            # 调整布局（防止标签被裁剪）
            self.canvas6.figure.set_constrained_layout(True)
                    
            # ---------------------- 刷新 canvas6 画布 ----------------------
            self.canvas6.draw()
            self.canvas.figure.clear()
            gs = gridspec.GridSpec(1, 2, width_ratios=[2, 1], wspace=0.3) 

                
            # 第一个子图（占据2/3宽度）
            print(idx_max)
            ax1 = self.canvas.figure.add_subplot(gs[0])
            inter=idx_max//5151
            print(inter)
            #print(self.aaa[3])
            self.all=A_max*self.aaa5[inter][0]+B_max*self.aaa5[inter][1]+C_max*self.aaa5[inter][2]
            print(self.all)
            ax1.plot(self.T, self.all, color='blue', label='option model')  
            ax1.plot(self.T, self.np_sample, color='black', label=self.headers[0])
            ax1.set_xlabel("Zircon U-Pb age (Ma)")
            if self.radioButton.isChecked():
                ax1.set_ylabel("PDF")
            if self.radioButton_2.isChecked():
                ax1.set_ylabel("KDE")
            ax1.legend()
                    # 关键：设置x轴间隔为100（每100ma一个刻度）
            ax1.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
            ax1.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
            ax1.set_xlim(min_age, max_age)
            ax1.set_ylim(bottom=0)
                
                # 第二个子图（占据1/3宽度）
            ax2 = self.canvas.figure.add_subplot(gs[1])
                
            ax2.plot(self.T, np.cumsum(self.all), color='blue', label='option model')  
#        
            ax2.plot(self.T, self.cdf_value_sample, color='black', label=self.headers[0])
            ax2.set_xlabel("Zircon U-Pb age (Ma)")
            ax2.set_ylabel("CDFs")
            ax2.legend()
            ax2.set_xlim(min_age, max_age)
            ax2.set_ylim(0,1)
            ax2.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
            ax2.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
                
            self.canvas.figure.set_constrained_layout(True)
                   # 5. 关键优化：调整整个图形的边距和布局
                #plt.subplots_adjust(left=0.08, right=0.95, top=0.92, bottom=0.2)  # 手动调整边距
            self.canvas.draw()                    
        if num == 4:
            
            
            
                    # ---------------------- 初始化空列表（放在循环外！） ----------------------
            self.ratios = []  # 存储所有 [A, B, C] 比例
            self.aa = []      # 存储所有相似度值
            self.value5=[]
            self.canvas6.figure.clear()  # 清空 canvas6 画布
            SUM=0
            print(len(self.aaa5))
            for mmm in range (len(self.aaa5)):       
            # 生成 A/B/C 比例和相似度值
                for i in range(0,101,5):     
                    for j in range(0,101 - i,3):
                        for k in range(101-i-j):
                            SUM+=1
                            self.ratios.append([i/100, j/100, k/100, (100-i-j-k)/100])  # A, B, C 比例
                            self.aa.append(sim.Similarity(self.np_sample, 
                                        (i/100)*self.aaa5[mmm][0] + 
                                        (j/100)*self.aaa5[mmm][1] + 
                                        (k/100)*self.aaa5[mmm][2]+((100-i-j-k)/100)*self.aaa5[mmm][3]
                                    ))
            print(str(SUM)+"次")
                    
            # ---------------------- 提取数据并计算三元坐标 ----------------------
            print(self.ratios)

            ratios_np = np.array(self.ratios)  # (N, 4)：A, B, C, D 列
            print(ratios_np)
            A, B, C, D = ratios_np[:, 0], ratios_np[:, 1], ratios_np[:, 2], ratios_np[:, 3]
            print(A)
            values = np.array(self.aa)  # 相似度值  

            
            # ---------------------- 找到相似度最高点 ----------------------
            idx_max = np.argmax(values)
            A_max, B_max, C_max, D_max = A[idx_max], B[idx_max], C[idx_max], D[idx_max]
            self.value5.append('Similarity')
            self.value5.append(A_max)
            self.value5.append(B_max)
            self.value5.append(C_max)
            self.value5.append(D_max)
            self.value5.append(max(self.aa))  
            print("相似度最高点的比例：")
            print(f"A={A_max:.3f}, B={B_max:.3f}, C={C_max:.3f}, D={D_max:.3f}")
            
            # ---------------------- 创建仅包含3D四面体的画布 ----------------------
            
            
            # --------------------------------------------
            # 3D四面体展示（无坐标轴，添加刻度）
            # --------------------------------------------
            #ax1 = fig.add_subplot(111, projection='3d')  # 仅一个子图
            ax1 = self.canvas6.figure.add_subplot(111, projection='3d')  # 使用 canvas6 的 figure 添加子图
            # 四面体顶点坐标（保留原始定义）
            vertices = np.array([
                [0, 0, 0],    # A
                [1, 0, 0],    # B
                [0.5, np.sqrt(3)/2, 0],  # C
                [0.5, np.sqrt(3)/6, np.sqrt(6)/3]  # D
            ])
            
            # 绘制四面体边
            edges = [
                [vertices[0], vertices[1]],  # A-B
                [vertices[0], vertices[2]],  # A-C
                [vertices[0], vertices[3]],  # A-D
                [vertices[1], vertices[2]],  # B-C
                [vertices[1], vertices[3]],  # B-D
                [vertices[2], vertices[3]]   # C-D
            ]
            for edge in edges:
                ax1.plot3D(*zip(*edge), 'k-', linewidth=1.5)
            
            # 计算3D坐标（四面体坐标）
            x = A * vertices[0,0] + B * vertices[1,0] + C * vertices[2,0] + D * vertices[3,0]
            y = A * vertices[0,1] + B * vertices[1,1] + C * vertices[2,1] + D * vertices[3,1]
            z = A * vertices[0,2] + B * vertices[1,2] + C * vertices[2,2] + D * vertices[3,2]

            # 绘制散点图
            ax1.scatter(x, y, z, c=values, cmap='viridis', s=5, alpha=0.3, vmin=0,vmax=1)

            # 最高点
            ax1.scatter(
                x[idx_max], y[idx_max], z[idx_max], 
                marker='*', c='red', s=100, edgecolor='k'
            )

            
            # 添加刻度标签到棱上
            def add_ticks(ax, start, end, ticks=5, label=""):
                """在棱上添加刻度标签"""
                direction = end - start
                length = np.linalg.norm(direction)
                unit_vector = direction / length
                
                # 添加刻度线
                for i in range(1, ticks):
                    fraction = i / ticks
                    position = start + fraction * direction
                    
                    # 计算刻度线方向（与棱垂直）
                    # 简单起见，使用XY平面的垂直方向
                    if np.allclose(direction[:2], [0, 0]):  # 如果是垂直棱
                        tick_dir = np.array([1, 0, 0])
                    else:
                        tick_dir = np.array([-direction[1], direction[0], 0])
                        tick_dir = tick_dir / np.linalg.norm(tick_dir[:2])
                    
                    tick_size = 0.03
                    tick_start = position - tick_size * tick_dir
                    tick_end = position + tick_size * tick_dir
                    ax.plot3D(*zip(tick_start, tick_end), 'k-', linewidth=0.8)
                    
                    # 添加刻度标签
#                    label_pos = position + 0.1 * tick_dir
#                    ax.text(*label_pos, f"{fraction:.1f}", fontsize=8, ha='center', va='center')
                
                # 添加端点标签
                ax.text(*(start - 0.05 * unit_vector), "0", fontsize=8, ha='right', va='center')
                ax.text(*(end + 0.05 * unit_vector), "1", fontsize=8, ha='left', va='center')
                ax.text(*((start + end)/2 + 0.1 * tick_dir), label, fontsize=8, ha='center', va='center')
            
            # 在每条棱上添加刻度
            add_ticks(ax1, vertices[0], vertices[1], label="")  # A-B棱
            add_ticks(ax1, vertices[0], vertices[2], label="")  # A-C棱
            add_ticks(ax1, vertices[0], vertices[3], label="")  # A-D棱
            add_ticks(ax1, vertices[1], vertices[2], label="")  # B-C棱
            add_ticks(ax1, vertices[1], vertices[3], label="")  # B-D棱
            add_ticks(ax1, vertices[2], vertices[3], label="")  # C-D棱
            
            # 添加顶点标签
            # ax1.text(*vertices[0], "A", fontsize=14, ha='right', va='top', weight='bold')
            # ax1.text(*vertices[1], "B", fontsize=14, ha='left', va='top', weight='bold')
            # ax1.text(*vertices[2], "C", fontsize=14, ha='center', va='bottom', weight='bold')
            # ax1.text(*vertices[3], "D", fontsize=14, ha='center', va='top', weight='bold')
            # 添加顶点标签（带偏移量）
            offset = 0.2  # 偏移量，可以根据需要调整
            
            # A点标签（左下角）
            ax1.text(vertices[0][0]-offset, vertices[0][1]-offset, vertices[0][2]-offset, 
                     self.headers[2], fontsize=10, ha='right', va='top', weight='bold')
            
            # B点标签（右下角）
            ax1.text(vertices[1][0]+offset, vertices[1][1]-offset, vertices[1][2]-offset, 
                     self.headers[4], fontsize=10, ha='left', va='top', weight='bold')
            
            # C点标签（顶部）
            ax1.text(vertices[2][0], vertices[2][1]+offset, vertices[2][2]-offset, 
                     self.headers[6], fontsize=10, ha='center', va='bottom', weight='bold')  # 修复了重复的va参数
            
            # D点标签（上方）
            ax1.text(vertices[3][0], vertices[3][1], vertices[3][2]+offset, 
                     self.headers[8], fontsize=10, ha='center', va='bottom', weight='bold')
            
            #ax1.set_title("四元比例四面体图 (带刻度)")
            ax1.axis('off')  # 关闭坐标轴
            ax1.view_init(25, 90)  # 设置视角
            #ax1.legend()
            sm = plt.cm.ScalarMappable(cmap='viridis', norm=plt.Normalize(0,1))
            sm.set_array([])
            cbar = self.canvas6.figure.colorbar(
                sm, 
                ax=ax1, 
                pad=0.05,          # 与图形的间距
                aspect=40,         # 核心：减小aspect值（默认20，值越小颜色条越“短粗”）
                orientation="horizontal"
               
            )
            cbar.set_label("Similarity", rotation=0, labelpad=5)  # 标签水平放置，更易读
            
            # 调整布局（防止标签被裁剪）
            self.canvas6.figure.set_constrained_layout(True)
                    
            # ---------------------- 刷新 canvas6 画布 ----------------------
            self.canvas6.draw()


            self.canvas.figure.clear()
            

                    
            # 创建1行2列的网格，宽度比例为2:1
            gs = gridspec.GridSpec(1, 2, width_ratios=[2, 1], wspace=0.3) 
                    
            # 第一个子图（占据2/3宽度）
            ax1 = self.canvas.figure.add_subplot(gs[0])

            print(idx_max)
            
            inter=idx_max//12852
            print(inter)
            #print(self.aaa[3])
            self.all=A_max*self.aaa5[inter][0]+B_max*self.aaa5[inter][1]+C_max*self.aaa5[inter][2]+D_max*self.aaa5[inter][2]
            print(self.all)
            ax1.plot(self.T, self.all, color='blue', label='option model')  
       
            ax1.plot(self.T, self.np_sample, color='black', label=self.headers[0])
            ax1.set_xlabel("Zircon U-Pb age (Ma)")
            if self.radioButton.isChecked():
                ax1.set_ylabel("PDF")
            if self.radioButton_2.isChecked():
                ax1.set_ylabel("KDE")
            ax1.legend()
                        # 关键：设置x轴间隔为100（每100ma一个刻度）
            ax1.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
            ax1.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
            ax1.set_xlim(min_age, max_age)
            ax1.set_ylim(bottom=0)
                    
            # 第二个子图（占据1/3宽度）
            ax2 = self.canvas.figure.add_subplot(gs[1])
                
            ax2.plot(self.T, np.cumsum(self.all), color='blue', label='option model')  
#        
            ax2.plot(self.T, self.cdf_value_sample, color='black', label=self.headers[0])
            ax2.set_xlabel("Zircon U-Pb age (Ma)")
            ax2.set_ylabel("CDFs")
            ax2.legend()
            ax2.set_xlim(min_age, max_age)
            ax2.set_ylim(0,1)
            ax2.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
            ax2.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度


                # 调整子图间距
            self.canvas.figure.set_constrained_layout(True)
                   # 5. 关键优化：调整整个图形的边距和布局
                #plt.subplots_adjust(left=0.08, right=0.95, top=0.92, bottom=0.2)  # 手动调整边距
            self.canvas.draw()
    
    @pyqtSlot()
    def on_pushButton_23_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.canvas6.figure.clear()
        self.canvas6.draw() 
        self.value5=[]
    
    @pyqtSlot()
    def on_pushButton_24_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        file_path, ok=  QFileDialog.getSaveFileName(self,"Import","" ,"PDF File (*.pdf);;image(*.jpg);;all files(*.*)")   
        print(file_path.strip())
        #判断有点问题可以重新检查下
        if file_path.strip()=='':
            QMessageBox.warning(self, 'Waring', 'Failed!')
        else:
            self.save=self.figure6.savefig(file_path)
            #print(self.save)
            QMessageBox.information(self,'Save','Sucessful!')
    


    
    @pyqtSlot()
    def on_pushButton_4_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        print('你好')
#        print(self.aaa)
#        print(len(self.aaa))
        show_original = True
        
        self.value_ks=[]
        
        min_age = int(self.lineEdit.text())
        max_age = int(self.lineEdit_2.text())
#        dT_value = int(self.lineEdit_8.text())
#        self.age_range = [min_age, max_age]
#        self.dT = dT_value
#        self.T = np.zeros((self.age_range[1] - self.age_range[0]) // self.dT)
        num = (len(self.headers)-2)//2
        if num == 2:
            self.aa = []
            Ratio_A = []
            self.value1=[]
            self.canvas2.figure.clear()
#            print(self.aaa[0])
            for j in range (len(self.aaa)):
                for i in range(101):
                    Ratio_A.append(i/100)
                    ksks=ks.kstest2b_tnc(self.np_sample, (i/100)*self.aaa[j][0] + ((100-i)/100)*(i/100)*self.aaa[j][1],0.05,'unequal',len(self.T))[2]
                    self.aa.append(ksks)
#            print(self.aa)
#            print(len(self.aa))
            
            self.max_aa = np.max(np.array(self.aa)[~np.isnan(self.aa)])
            self.max_aa_index=np.argmax(np.array(self.aa)[~np.isnan(self.aa)])
            print(self.max_aa_index)
            self.max_Ratio_A=Ratio_A[self.max_aa_index]
            #self.value_ks.append[max_Ratio_A,1-max_Ratio_A,max_aa]

            print(self.max_Ratio_A,1-self.max_Ratio_A,self.max_aa)
            self.value1.append('K-S')
            self.value1.append(self.max_Ratio_A)
            self.value1.append(1-self.max_Ratio_A)
            self.value1.append(self.max_aa)
            # 数据处理和插值（保持不变）
            x_data = np.clip(Ratio_A, 0, 1)
            z_data = np.clip(self.aa, 0, 1)
            sorted_indices = np.argsort(x_data)
            x_sorted, z_sorted = x_data[sorted_indices], z_data[sorted_indices]
            _, unique_mask = np.unique(x_sorted, return_index=True)
            x_unique, z_unique = x_sorted[unique_mask], z_sorted[unique_mask]
            
            if len(x_unique) >= 2:
                from scipy.interpolate import interp1d
                x_interp = np.linspace(0, 1, 1000)
                interp_func = interp1d(x_unique, z_unique, kind="linear", bounds_error=False, fill_value=0.5)
                z_interp = interp_func(x_interp)
                
                # 绘制条带图（保持不变）
                ax = self.canvas2.figure.add_subplot(111)
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.set_yticks([0.5])
                ax.set_yticklabels([self.headers[0]], rotation=90, va="top")
                ax.set_xlabel(self.headers[2], fontsize=10, labelpad=3)
                
                ax_top = ax.twiny()
                ax_top.set_xlim(0, 1)
                ax_top.set_xlabel(self.headers[4], fontsize=10, labelpad=3)
                ax_top.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
                ax_top.set_xticklabels([1.0, 0.8, 0.6, 0.4, 0.2, 0.0])
                ax_top.set_title(str(self.max_Ratio_A)+"_"+str(1-self.max_Ratio_A)+"_ "+str(self.max_aa))
                
                cmap = plt.cm.get_cmap("viridis")
                norm = plt.Normalize(0, 1)
                ax.pcolormesh(
                    x_interp, [0.0, 1.0], z_interp.reshape(1, -1),
                    cmap=cmap, norm=norm, shading="auto", alpha=0.9
                )
                
                if show_original:
                    ax.vlines(x=x_data, ymin=0, ymax=1.0, color="gray", linewidth=0.8, alpha=0.4)
                
                # 颜色条（保持不变）
                sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
                sm.set_array([])
                # 创建水平颜色条（关键参数：orientation="horizontal"）
                cbar = plt.colorbar(
                    sm, 
                    ax=ax, 
                    pad=0.2,                # 颜色条与主图的间距（垂直方向，因水平放置）
                    orientation="horizontal", 
                    aspect=30,
                    shrink=0.8 # 颜色条的长宽比（数值越大越扁长，适配主图宽度）
                )
                cbar.set_label("D value", rotation=0, labelpad=5)
                
                
                # 调整边距（使用 canvas6.figure）
                self.canvas2.figure.set_constrained_layout(True)
        
        # 4. 刷新画布
        #plt.tight_layout()
                self.canvas2.draw()
                
                self.canvas.figure.clear()
                gs = gridspec.GridSpec(1, 2, width_ratios=[2, 1], wspace=0.3) 
                
                # 第一个子图（占据2/3宽度）
                ax1 = self.canvas.figure.add_subplot(gs[0])
                inter=self.max_aa_index//101
                print(inter)
                print(self.aaa[3])
                self.all=self.max_Ratio_A*self.aaa[inter][0]+(1-self.max_Ratio_A)*self.aaa[inter][1]
                print(self.all)
                ax1.plot(self.T, self.all, color='blue', label='option model')  
                ax1.plot(self.T, self.np_sample, color='black', label=self.headers[0])
                ax1.set_xlabel("Zircon U-Pb age (Ma)")
                if self.radioButton.isChecked():
                    ax1.set_ylabel("PDF")
                if self.radioButton_2.isChecked():
                    ax1.set_ylabel("KDE")
                ax1.legend()
                    # 关键：设置x轴间隔为100（每100ma一个刻度）
                ax1.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
                ax1.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
                ax1.set_xlim(min_age, max_age)
                ax1.set_ylim(bottom=0)
                
                # 第二个子图（占据1/3宽度）
                ax2 = self.canvas.figure.add_subplot(gs[1])
                
                ax2.plot(self.T, np.cumsum(self.all), color='blue', label='option model')  
#        
                ax2.plot(self.T, self.cdf_value_sample, color='black', label=self.headers[0])
                ax2.set_xlabel("Zircon U-Pb age (Ma)")
                ax2.set_ylabel("CDFs")
                ax2.legend()
                ax2.set_xlim(min_age, max_age)
                ax2.set_ylim(0,1)
                ax2.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
                ax2.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
                
                self.canvas.figure.set_constrained_layout(True)
                   # 5. 关键优化：调整整个图形的边距和布局
                #plt.subplots_adjust(left=0.08, right=0.95, top=0.92, bottom=0.2)  # 手动调整边距
                self.canvas.draw()
                

                
        if num == 3:
            self.ratios = []  # 存储所有 [A, B, C] 比例
            self.aa = []      # 存储所有相似度值
            self.value1=[]
            self.canvas2.figure.clear()  # 清空 canvas6 画布

            print(len(self.aaa))
            for mmm in range (len(self.aaa)):
                            # 生成 A/B/C 比例和相似度值
                for i in range(101):     
                    for j in range(101 - i):
                        self.ratios.append([i/100, j/100, (100 - i - j)/100])  # A, B, C 比例
                        self.aa.append(ks.kstest2b_tnc(self.np_sample, 
                                    (i/100)*self.aaa[mmm][0] + 
                                    (j/100)*self.aaa[mmm][1] + 
                                    ((100-i-j)/100)*self.aaa[mmm][2],0.05,'unequal',len(self.T)
                                )[2])
    #            print(self.aa)
#            print(len(self.aa))
            print(self.aa)
            print(len(self.aa))
                        # ---------------------- 提取数据并计算三元坐标 ----------------------
            ratios_np = np.array(self.ratios)  # (N, 3)：A, B, C 列
            A, B, C = ratios_np[:, 0], ratios_np[:, 1], ratios_np[:, 2]
            values = np.array(self.aa)  # 相似度值
                    
            # 三元坐标投影（将 A/B/C 转换为 2D 平面坐标）
            denominator = A + B + C + 1e-12  # 避免除零
            x = 0.5 * (2 * B + C) / denominator  # 三元图 x 坐标
            y = (np.sqrt(3) / 2) * C / denominator  # 三元图 y 坐标
                    
            # ---------------------- 找到最高相似度点 ----------------------
            idx_max = np.argmax(values)
            x_max, y_max = x[idx_max], y[idx_max]  # 最高相似度点坐标
            A_max, B_max, C_max = A[idx_max], B[idx_max], C[idx_max]  # 最优比例
            self.value1.append('K-S')
            self.value1.append(A_max)
            self.value1.append(B_max)
            self.value1.append(C_max)
            self.value1.append(max(self.aa))            
                                                        
            print("最高相似度点比例：")
            print(f"A={A_max:.3f}, B={B_max:.3f}, C={C_max:.3f}")
            print(f"最高相似度值：{values[idx_max]:.4f}")
            
            # ---------------------- 在 canvas6 中绘制三元相图 ----------------------
            # 创建子图（替换原 plt.figure() 和 ax = plt.subplot()）
            ax = self.canvas2.figure.add_subplot(111)  # 使用 canvas6 的 figure 添加子图
                    
            # 1. 绘制插值网格背景（平滑颜色）
            grid_x, grid_y = np.mgrid[0:1:200j, 0:np.sqrt(3)/2:200j]
            grid_z = griddata((x, y), values, (grid_x, grid_y), method='linear')
            #grid_z = np.nan_to_num(grid_z, nan=0.0)  # NaN用0填充（或用values.min()）
            ax.pcolormesh(grid_x, grid_y, grid_z, cmap='viridis', alpha=0.8, shading='gouraud',  vmin=0,vmax=1)
                    
            # 2. 绘制三角边界（等边三角形）
            triangle = np.array([[0, 0], [1, 0], [0.5, np.sqrt(3)/2], [0, 0]])
            ax.plot(triangle[:, 0], triangle[:, 1], 'k-', linewidth=1.5)
                    
            # 3. 绘制原始数据点（可选）
            ax.scatter(x, y, c=values, cmap='viridis', s=5, alpha=0.3,  vmin=0,vmax=1)
                    
            # 4. 标记最高相似度点（红色五角星）
            ax.scatter(x_max, y_max, marker="*", c="red", s=200, edgecolor="k", label="最高相似度点")
                    
            # 5. 添加 A/B/C 轴刻度和标签
            n_ticks = 5
            tick_values = np.linspace(0, 1, n_ticks + 1)
                    
            # A 轴刻度（左下 -> 上顶点）
            for t in tick_values[1:-1]:
                x_tick = 0.5 * (1 - t)
                y_tick = (np.sqrt(3)/2) * (1 - t)
                ax.plot([x_tick, x_tick - 0.02], [y_tick, y_tick], 'k-', linewidth=0.8)
                ax.text(x_tick - 0.04, y_tick, f"{t:.1f}", fontsize=9, ha="right", va="center")
                    
            # B 轴刻度（右下 -> 上顶点）
            for t in tick_values[1:-1]:
                x_tick = 0.5 * (1 + t)
                y_tick = (np.sqrt(3)/2) * (1 - t)
                ax.plot([x_tick, x_tick + 0.02], [y_tick, y_tick], 'k-', linewidth=0.8)
                ax.text(x_tick + 0.04, y_tick, f"{t:.1f}", fontsize=9, ha="left", va="center")
                    
            # C 轴刻度（底部 -> 上顶点）
            for t in tick_values[1:-1]:
                x_tick = t
                y_tick = 0
                ax.plot([x_tick, x_tick], [y_tick, y_tick - 0.02], 'k-', linewidth=0.8)
                ax.text(x_tick, y_tick - 0.05, f"{t:.1f}", fontsize=9, ha="center", va="top")
                    
            # 顶点标签（A/B/C）
            ax.text(-0.05, -0.05, self.headers[2], fontsize=12, ha="right", va="top", fontweight="bold")
            ax.text(1.05, -0.05, self.headers[4], fontsize=12, ha="left", va="top", fontweight="bold")
            ax.text(0.5, np.sqrt(3)/2 + 0.05, self.headers[6], fontsize=12, ha="center", va="bottom", fontweight="bold")
                    
            # ---------------------- 图表设置 ----------------------
            #ax.set_title(f"三元相图 (最高相似度: {max(values):.4f})", fontsize=12, pad=20)
            ax.set_aspect("equal")  # 等比例坐标轴（保证三角形为正三角形）
            ax.axis("off")  # 关闭默认坐标轴
                    
            # 添加颜色条（绑定到 canvas6 的 figure）
            #sm = plt.cm.ScalarMappable(cmap='viridis', norm=plt.Normalize(values.min(), values.max()))
            sm = plt.cm.ScalarMappable(cmap='viridis', norm=plt.Normalize(0,1))
            sm.set_array([])
            cbar = self.canvas2.figure.colorbar(sm, ax=ax, pad=0.05, orientation="horizontal", aspect=40)
            cbar.set_label("D value", rotation=0, labelpad=10)
                    
            # 调整布局（防止标签被裁剪）
            self.canvas2.figure.set_constrained_layout(True)
                    
            # ---------------------- 刷新 canvas6 画布 ----------------------
            self.canvas2.draw()
            self.canvas.figure.clear()
            gs = gridspec.GridSpec(1, 2, width_ratios=[2, 1], wspace=0.3) 

                
            # 第一个子图（占据2/3宽度）
            print(idx_max)
            ax1 = self.canvas.figure.add_subplot(gs[0])
            inter=idx_max//5151
            print(inter)
            #print(self.aaa[3])
            self.all=A_max*self.aaa[inter][0]+B_max*self.aaa[inter][1]+C_max*self.aaa[inter][2]
            print(self.all)
            ax1.plot(self.T, self.all, color='blue', label='option model')  
            ax1.plot(self.T, self.np_sample, color='black', label=self.headers[0])
            ax1.set_xlabel("Zircon U-Pb age (Ma)")
            if self.radioButton.isChecked():
                ax1.set_ylabel("PDF")
            if self.radioButton_2.isChecked():
                ax1.set_ylabel("KDE")
            ax1.legend()
                    # 关键：设置x轴间隔为100（每100ma一个刻度）
            ax1.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
            ax1.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
            ax1.set_xlim(min_age, max_age)
            ax1.set_ylim(bottom=0)
                
                # 第二个子图（占据1/3宽度）
            ax2 = self.canvas.figure.add_subplot(gs[1])
                
            ax2.plot(self.T, np.cumsum(self.all), color='blue', label='option model')  
#        
            ax2.plot(self.T, self.cdf_value_sample, color='black', label=self.headers[0])
            ax2.set_xlabel("Zircon U-Pb age (Ma)")
            ax2.set_ylabel("CDFs")
            ax2.legend()
            ax2.set_xlim(min_age, max_age)
            ax2.set_ylim(0,1)
            ax2.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
            ax2.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
                
            self.canvas.figure.set_constrained_layout(True)
                   # 5. 关键优化：调整整个图形的边距和布局
                #plt.subplots_adjust(left=0.08, right=0.95, top=0.92, bottom=0.2)  # 手动调整边距
            self.canvas.draw()                    
        if num == 4:
            
            
            
                    # ---------------------- 初始化空列表（放在循环外！） ----------------------
            self.ratios = []  # 存储所有 [A, B, C] 比例
            self.aa = []      # 存储所有相似度值
            self.value1=[]
            self.canvas2.figure.clear()  # 清空 canvas6 画布
            SUM=0
            print(len(self.aaa))
            for mmm in range (len(self.aaa)):       
            # 生成 A/B/C 比例和相似度值
                for i in range(0,101,5):     
                    for j in range(0,101 - i,3):
                        for k in range(101-i-j):
                            SUM+=1
                            self.ratios.append([i/100, j/100, k/100, (100-i-j-k)/100])  # A, B, C 比例
                            self.aa.append(ks.kstest2b_tnc(self.np_sample, 
                                        (i/100)*self.aaa[mmm][0] + 
                                        (j/100)*self.aaa[mmm][1] + 
                                        (k/100)*self.aaa[mmm][2]+((100-i-j-k)/100)*self.aaa[mmm][3],0.05,'unequal',len(self.T)
                                    )[2])
            print(str(SUM)+"次")
                    
            # ---------------------- 提取数据并计算三元坐标 ----------------------
            print(self.ratios)

            ratios_np = np.array(self.ratios)  # (N, 4)：A, B, C, D 列
            print(ratios_np)
            A, B, C, D = ratios_np[:, 0], ratios_np[:, 1], ratios_np[:, 2], ratios_np[:, 3]
            print(A)
            values = np.array(self.aa)  # 相似度值  

            
            # ---------------------- 找到相似度最高点 ----------------------
            idx_max = np.argmax(values)
            A_max, B_max, C_max, D_max = A[idx_max], B[idx_max], C[idx_max], D[idx_max]
            self.value1.append('K-S')
            self.value1.append(A_max)
            self.value1.append(B_max)
            self.value1.append(C_max)
            self.value1.append(D_max)
            self.value1.append(max(self.aa))  
            print("相似度最高点的比例：")
            print(f"A={A_max:.3f}, B={B_max:.3f}, C={C_max:.3f}, D={D_max:.3f}")
            
            # ---------------------- 创建仅包含3D四面体的画布 ----------------------
            
            
            # --------------------------------------------
            # 3D四面体展示（无坐标轴，添加刻度）
            # --------------------------------------------
            #ax1 = fig.add_subplot(111, projection='3d')  # 仅一个子图
            ax1 = self.canvas2.figure.add_subplot(111, projection='3d')  # 使用 canvas6 的 figure 添加子图
            # 四面体顶点坐标（保留原始定义）
            vertices = np.array([
                [0, 0, 0],    # A
                [1, 0, 0],    # B
                [0.5, np.sqrt(3)/2, 0],  # C
                [0.5, np.sqrt(3)/6, np.sqrt(6)/3]  # D
            ])
            
            # 绘制四面体边
            edges = [
                [vertices[0], vertices[1]],  # A-B
                [vertices[0], vertices[2]],  # A-C
                [vertices[0], vertices[3]],  # A-D
                [vertices[1], vertices[2]],  # B-C
                [vertices[1], vertices[3]],  # B-D
                [vertices[2], vertices[3]]   # C-D
            ]
            for edge in edges:
                ax1.plot3D(*zip(*edge), 'k-', linewidth=1.5)
            
            # 计算3D坐标（四面体坐标）
            x = A * vertices[0,0] + B * vertices[1,0] + C * vertices[2,0] + D * vertices[3,0]
            y = A * vertices[0,1] + B * vertices[1,1] + C * vertices[2,1] + D * vertices[3,1]
            z = A * vertices[0,2] + B * vertices[1,2] + C * vertices[2,2] + D * vertices[3,2]

            # 绘制散点图
            ax1.scatter(x, y, z, c=values, cmap='viridis', s=5, alpha=0.3, vmin=0,vmax=1)

            # 最高点
            ax1.scatter(
                x[idx_max], y[idx_max], z[idx_max], 
                marker='*', c='red', s=100, edgecolor='k'
            )

            
            # 添加刻度标签到棱上
            def add_ticks(ax, start, end, ticks=5, label=""):
                """在棱上添加刻度标签"""
                direction = end - start
                length = np.linalg.norm(direction)
                unit_vector = direction / length
                
                # 添加刻度线
                for i in range(1, ticks):
                    fraction = i / ticks
                    position = start + fraction * direction
                    
                    # 计算刻度线方向（与棱垂直）
                    # 简单起见，使用XY平面的垂直方向
                    if np.allclose(direction[:2], [0, 0]):  # 如果是垂直棱
                        tick_dir = np.array([1, 0, 0])
                    else:
                        tick_dir = np.array([-direction[1], direction[0], 0])
                        tick_dir = tick_dir / np.linalg.norm(tick_dir[:2])
                    
                    tick_size = 0.03
                    tick_start = position - tick_size * tick_dir
                    tick_end = position + tick_size * tick_dir
                    ax.plot3D(*zip(tick_start, tick_end), 'k-', linewidth=0.8)
                    
                    # 添加刻度标签
#                    label_pos = position + 0.1 * tick_dir
#                    ax.text(*label_pos, f"{fraction:.1f}", fontsize=8, ha='center', va='center')
                
                # 添加端点标签
                ax.text(*(start - 0.05 * unit_vector), "0", fontsize=8, ha='right', va='center')
                ax.text(*(end + 0.05 * unit_vector), "1", fontsize=8, ha='left', va='center')
                ax.text(*((start + end)/2 + 0.1 * tick_dir), label, fontsize=8, ha='center', va='center')
            
            # 在每条棱上添加刻度
            add_ticks(ax1, vertices[0], vertices[1], label="")  # A-B棱
            add_ticks(ax1, vertices[0], vertices[2], label="")  # A-C棱
            add_ticks(ax1, vertices[0], vertices[3], label="")  # A-D棱
            add_ticks(ax1, vertices[1], vertices[2], label="")  # B-C棱
            add_ticks(ax1, vertices[1], vertices[3], label="")  # B-D棱
            add_ticks(ax1, vertices[2], vertices[3], label="")  # C-D棱
            
            # 添加顶点标签
            # ax1.text(*vertices[0], "A", fontsize=14, ha='right', va='top', weight='bold')
            # ax1.text(*vertices[1], "B", fontsize=14, ha='left', va='top', weight='bold')
            # ax1.text(*vertices[2], "C", fontsize=14, ha='center', va='bottom', weight='bold')
            # ax1.text(*vertices[3], "D", fontsize=14, ha='center', va='top', weight='bold')
            # 添加顶点标签（带偏移量）
            offset = 0.2  # 偏移量，可以根据需要调整
            
            # A点标签（左下角）
            ax1.text(vertices[0][0]-offset, vertices[0][1]-offset, vertices[0][2]-offset, 
                     self.headers[2], fontsize=10, ha='right', va='top', weight='bold')
            
            # B点标签（右下角）
            ax1.text(vertices[1][0]+offset, vertices[1][1]-offset, vertices[1][2]-offset, 
                     self.headers[4], fontsize=10, ha='left', va='top', weight='bold')
            
            # C点标签（顶部）
            ax1.text(vertices[2][0], vertices[2][1]+offset, vertices[2][2]-offset, 
                     self.headers[6], fontsize=10, ha='center', va='bottom', weight='bold')  # 修复了重复的va参数
            
            # D点标签（上方）
            ax1.text(vertices[3][0], vertices[3][1], vertices[3][2]+offset, 
                     self.headers[8], fontsize=10, ha='center', va='bottom', weight='bold')
            
            #ax1.set_title("四元比例四面体图 (带刻度)")
            ax1.axis('off')  # 关闭坐标轴
            ax1.view_init(25, 90)  # 设置视角
            #ax1.legend()
            sm = plt.cm.ScalarMappable(cmap='viridis', norm=plt.Normalize(0,1))
            sm.set_array([])
            cbar = self.canvas2.figure.colorbar(
                sm, 
                ax=ax1, 
                pad=0.05,          # 与图形的间距
                aspect=40,         # 核心：减小aspect值（默认20，值越小颜色条越“短粗”）
                orientation="horizontal"
               
            )
            cbar.set_label("D value", rotation=0, labelpad=5)  # 标签水平放置，更易读
            
            # 调整布局（防止标签被裁剪）
            self.canvas2.figure.set_constrained_layout(True)
                    
            # ---------------------- 刷新 canvas6 画布 ----------------------
            self.canvas2.draw()


            self.canvas.figure.clear()
            

                    
            # 创建1行2列的网格，宽度比例为2:1
            gs = gridspec.GridSpec(1, 2, width_ratios=[2, 1], wspace=0.3) 
                    
            # 第一个子图（占据2/3宽度）
            ax1 = self.canvas.figure.add_subplot(gs[0])

            print(idx_max)
            
            inter=idx_max//12852
            print(inter)
            #print(self.aaa[3])
            self.all=A_max*self.aaa[inter][0]+B_max*self.aaa[inter][1]+C_max*self.aaa[inter][2]+D_max*self.aaa[inter][2]
            print(self.all)
            ax1.plot(self.T, self.all, color='blue', label='option model')  
       
            ax1.plot(self.T, self.np_sample, color='black', label=self.headers[0])
            ax1.set_xlabel("Zircon U-Pb age (Ma)")
            if self.radioButton.isChecked():
                ax1.set_ylabel("PDF")
            if self.radioButton_2.isChecked():
                ax1.set_ylabel("KDE")
            ax1.legend()
                        # 关键：设置x轴间隔为100（每100ma一个刻度）
            ax1.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
            ax1.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
            ax1.set_xlim(min_age, max_age)
            ax1.set_ylim(bottom=0)
                    
            # 第二个子图（占据1/3宽度）
            ax2 = self.canvas.figure.add_subplot(gs[1])
                
            ax2.plot(self.T, np.cumsum(self.all), color='blue', label='option model')  
#        
            ax2.plot(self.T, self.cdf_value_sample, color='black', label=self.headers[0])
            ax2.set_xlabel("Zircon U-Pb age (Ma)")
            ax2.set_ylabel("CDFs")
            ax2.legend()
            ax2.set_xlim(min_age, max_age)
            ax2.set_ylim(0,1)
            ax2.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
            ax2.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度


                # 调整子图间距
            self.canvas.figure.set_constrained_layout(True)
                   # 5. 关键优化：调整整个图形的边距和布局
                #plt.subplots_adjust(left=0.08, right=0.95, top=0.92, bottom=0.2)  # 手动调整边距
            self.canvas.draw()               
    
    @pyqtSlot()
    def on_pushButton_5_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.canvas2.figure.clear()
        self.canvas2.draw() 
        self.value1=[]
    
    @pyqtSlot()
    def on_pushButton_6_clicked(self):
        """
        Slot documentation goes here.
        """
        file_path, ok=  QFileDialog.getSaveFileName(self,"Import","" ,"PDF File (*.pdf);;image(*.jpg);;all files(*.*)")   
        print(file_path.strip())
        #判断有点问题可以重新检查下
        if file_path.strip()=='':
            QMessageBox.warning(self, 'Waring', 'Failed!')
        else:
            self.save=self.figure2.savefig(file_path)
            #print(self.save)
            QMessageBox.information(self,'Save','Sucessful!')
    @pyqtSlot()
    def on_radioButton_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.lineEdit_3.setEnabled(False)
    
    @pyqtSlot()
    def on_radioButton_2_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.lineEdit_3.setEnabled(True)
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    ui =  PyMainSub()
    ui.show()
    sys.exit(app.exec_())
    

