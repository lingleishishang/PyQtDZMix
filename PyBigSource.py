# -*- coding: utf-8 -*-

"""
Module implementing MainBigSource.
"""

import sys
from PyQt5.QtWidgets import (QApplication,  QFileDialog,QMessageBox,QMainWindow, QHeaderView, 
                            QLineEdit, QStyledItemDelegate)
from PyQt5 import QtWidgets
from PyQt5.QtCore import QAbstractTableModel,Qt, QVariant, pyqtSlot
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
import numpy as np
import scipy.stats as st
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
import matplotlib.pyplot as plt

import random
matplotlib.rcParams['font.sans-serif']=['SimHei']

from Ui_PyBigSource import Ui_MainWindow

class EditableHeaderDelegate2(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._editor = None
        
    def createEditor(self, parent, option, index):
        self._editor = QLineEdit(parent)
        return self._editor
        
    def setEditorData(self, editor, index):
        value = index.model().headerData(index.column(), Qt.Horizontal, Qt.DisplayRole)
        editor.setText(str(value))
        
    def setModelData(self, editor, model, index):
        model.setHeaderData(index.column(), Qt.Horizontal, editor.text(), Qt.EditRole)
        
    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

class EmptyEditableTableModel2(QAbstractTableModel):
    def __init__(self, rows=1000, cols=10, parent=None):
        super().__init__(parent)
        self.rows = rows
        self.cols = cols
        # 初始化所有单元格为空字符串
        self._data = [["" for _ in range(cols)] for _ in range(rows)]
        # 初始化表头数据
        self._horizontal_header = [f"{i+1}" for i in range(cols)]
        self._vertical_header = [f"{i+1}" for i in range(rows)]
        
        # 定义颜色
        self.green_color = QColor(144, 238, 144)  # 草绿色
        self.blue_color = QColor(173, 216, 230)   # 浅蓝色
    
    def rowCount(self, parent=None):
        return self.rows
    
    def columnCount(self, parent=None):
        return self.cols
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()
        
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return self._data[index.row()][index.column()]
        
        # 设置背景色
        if role == Qt.BackgroundRole:
            if index.column() < 2:  # 前两列
                return QBrush(self.green_color)
            else:  # 其他列
                return QBrush(self.blue_color)
        
        return QVariant()
    
    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return False
            
        if role == Qt.EditRole:
            # 允许设置为任意值，包括空字符串
            self._data[index.row()][index.column()] = value
            self.dataChanged.emit(index, index)
            return True
            
        return False
    
    def flags(self, index):
        # 使所有单元格可编辑
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
    
    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._horizontal_header[section]
            else:
                return self._vertical_header[section]
        return QVariant()
    
    def setHeaderData(self, section, orientation, value, role=Qt.EditRole):
        if role != Qt.EditRole:
            return False
            
        if orientation == Qt.Horizontal and section < len(self._horizontal_header):
            self._horizontal_header[section] = value
            self.headerDataChanged.emit(orientation, section, section)
            return True
        elif orientation == Qt.Vertical and section < len(self._vertical_header):
            self._vertical_header[section] = value
            self.headerDataChanged.emit(orientation, section, section)
            return True
            
        return False
class MainBigSource(QMainWindow, Ui_MainWindow):
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
    def generate_random_combinations(self,n, j, target=100, max_num=100):
        combinations = []
        for _ in range(n):
            while True:
                # 生成j-1个随机数（确保剩余部分能补足到100）
                nums = [random.randint(0, max_num) for _ in range(j - 1)]
                remaining = target - sum(nums)
                if 0 <= remaining <= max_num:
                    combination = nums + [remaining]
                    random.shuffle(combination)  # 打乱顺序增强随机性
                    combinations.append(combination)
                    break
        return combinations
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super(MainBigSource, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("More than four sources") 
        screen = QApplication.primaryScreen().availableGeometry()
        width = int(screen.width())
        height = int(screen.height())
        
        # 设置窗口大小和位置（居中）
        self.setGeometry(
            int((screen.width() - width) / 2),  # x位置
            int((screen.height() - height) / 2), # y位置
            width,                              # 宽度
            height                              # 高度
        )
        self.setFixedSize(width, height)  
        self.tableView.setGeometry(0, 0, width/4, height*4/5)
        self.pushButton.setGeometry(width/16, height*4/5+height/20, width/8, height/20)
        self.groupBox.setGeometry(
            width/4+width/100,          # x坐标（左边界）
            0,       # y坐标（上边界）
            width/4,     # 宽度（按原比例）
            height/3         # 高度（按原比例）
        )
        self.radioButton_2.setGeometry(width/100,0,width/4,height/8)
        self.radioButton.setGeometry(width/100,height/16,width/8,height/8)
        self.label_3.setGeometry(width/25,height/10,width/10,height/8)
        self.lineEdit_4.setGeometry(width*4/25,height/10+height/30,width/16,height/20)
        self.label_4.setGeometry(width/25,height/6,width/8,height/8)
        self.lineEdit_5.setGeometry(width*4/25,height/10+height/10,width/16,height/20)
        self.label_5.setGeometry(width/25,height/6+height/10,width/8,height/16)
        self.lineEdit_6.setGeometry(width*4/25,height/6+height/10,width/16,height/20)
        
        self.groupBox_2.setGeometry(
            width/4+width/50+width/4,          # x坐标（左边界）
            0,       # y坐标（上边界）
            width/4,     # 宽度（按原比例）
            height*4/24        # 高度（按原比例）
        )
        self.radioButton_3.setGeometry(width/100,height/32,width/4,height/16)
        self.radioButton_4.setGeometry(width/100,height/16,width/4,height/16)
        self.label_2.setGeometry(width/25,height/15,width/4,height/8)
        self.lineEdit_3.setGeometry(width*4/25,height/10+height/70,width/16,height/30)
        self.groupBox_3.setGeometry(
            width/4+width/50+width/4,          # x坐标（左边界）
            height*4/24+height/200,       # y坐标（上边界）
            width/4,     # 宽度（按原比例）
            height*4/24-height/200        # 高度（按原比例）
        )
        self.layoutWidget.setGeometry(0,height/50,width/4,height/8)
        self.tableView_2.setGeometry(width*3/4+width/50+width/100, 0, width/4-width/25, height/3)
        self.groupBox_4.setGeometry(
            width/4+width/100,          # x坐标（左边界）
            height/3+height/200,       # y坐标（上边界）
            width/2+width/8,     # 宽度（按原比例）
            height*2/3-height/20        # 高度（按原比例）
        )
        self.pushButton_2.setGeometry(width*3/4+width*5/32, height/3+height/10, width*5/64, height/20)
        self.pushButton_3.setGeometry(width*3/4+width*5/32, height/3+height/10+height/10, width*5/64, height/20)
        self.pushButton_4.setGeometry(width*3/4+width*5/32, height/3+height*3/10, width*5/64, height/20)
        self.pushButton_5.setGeometry(width*3/4+width*5/32, height/3+height*2/5, width*5/64, height/20)
        
                # 创建模型并设置
        self.model = EmptyEditableTableModel2(rows=3000, cols=20)
        self.tableView.setModel(self.model)
        
        # 设置表头可编辑
        self.header_delegate = EditableHeaderDelegate2(self.tableView)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.tableView.horizontalHeader().setSectionsClickable(True)
        self.tableView.horizontalHeader().sectionDoubleClicked.connect(self.edit_header)
        
        # 设置表格属性
        self.tableView.horizontalHeader().setDefaultSectionSize(100)
        self.tableView.verticalHeader().setDefaultSectionSize(30)
        
        # 定义布局容器（verticalLayoutWidget_7）并设置其充满 groupBox_4
        self.verticalLayoutWidget = QtWidgets.QWidget(self.groupBox_4)  # 父控件设为 groupBox_4
        self.verticalLayoutWidget.setGeometry(
            0, 0,  # x=0, y=0（容器左上角紧贴 groupBox_7 左上角）
            self.groupBox_4.width(),  # 容器宽度 = groupBox_7 宽度
            self.groupBox_4.height()  # 容器高度 = groupBox_7 高度
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
            self.verticalLayoutWidget.setGeometry(10, 30, 0.98*self.groupBox_4.width(), 0.7*self.groupBox_4.width()-180)
            
            # 同步 Matplotlib 图形尺寸（避免拉伸变形）
            canvas_width = self.canvas.width()
            canvas_height = self.canvas.height()
            self.figure.set_size_inches(canvas_width / self.figure.dpi, canvas_height / self.figure.dpi)
            self.canvas.draw()
        
        # 绑定窗口缩放事件（确保容器和画布尺寸同步更新）
        self.groupBox_4.resizeEvent = lambda event: resize_canvas6()
        self.color=['red','blue','green','orange']

        #self.actionSave_as.setEnabled(False)  # 空表格时禁用
    def edit_header(self, section):
        # 确保模型支持设置表头数据
        if hasattr(self.model, 'setHeaderData'):
            # 创建并显示编辑器
            editor = QLineEdit(self.tableView)
            editor.setText(str(self.model.headerData(section, Qt.Horizontal, Qt.DisplayRole)))
            
            # 设置编辑器位置和大小
            header_pos = self.tableView.horizontalHeader().pos()
            section_pos = self.tableView.horizontalHeader().sectionViewportPosition(section)
            section_size = self.tableView.horizontalHeader().sectionSize(section)
            
            editor.setGeometry(header_pos.x() + section_pos, 
                             header_pos.y(), 
                             section_size, 
                             self.tableView.horizontalHeader().height())
            
            editor.show()
            editor.setFocus()
            
            def on_editing_finished():
                new_text = editor.text()
                self.model.setHeaderData(section, Qt.Horizontal, new_text, Qt.EditRole)
                editor.deleteLater()
                
            editor.editingFinished.connect(on_editing_finished)
    def process_data_kde(self, min_age, max_age, dT_value,bw):
        """Process the data using KDE instead of normal distributions"""
        # Initialize time array
        self.T = np.arange(min_age, max_age + dT_value, dT_value)
        
        # Calculate pair count and initialize arrays
        self.pair_count = (len(self.headers) - 2) // 2
        self.source = [[] for _ in range(self.pair_count)]  # source
        self.np_source = [[] for _ in range(self.pair_count)] #Normalized source
        #self.se = [[] for _ in range(self.pair_count)]      # source error
        
        # Populate source and se arrays
        for j in range(self.pair_count):
            self.source[j] = self.data[j*2 + 2]
            self.np_source[j]=self.kde_pdf(self.source[j],self.T, bandwidth=bw)
    
        
        # Process sample data
        self.sample = self.data[0]
        self.np_sample=self.kde_pdf(self.sample,self.T, bandwidth=bw)
    
        
    
    
    def kde_pdf(self,ages, T, bandwidth=50):
        """Compute KDE over grid T using ages from age_vec with fixed bandwidth."""
        ages = np.array(ages)
        # Gaussian KDE: bw_method 是乘在样本标准差上的因子
        kde = gaussian_kde(ages, bw_method=bandwidth / ages.std(ddof=1))
        pdf_values = kde(T)
        pdf_values /= pdf_values.sum()  # normalize
        return pdf_values
    def process_data(self, min_age, max_age, dT_value):
        """Process the data using the provided parameters"""
        # Initialize time array
        for i in range(len(self.T)):
            self.T[i] = min_age + i * dT_value
        
        # Calculate pair count and initialize arrays
        self.pair_count = (len(self.headers) - 2) // 2
        self.source = [[] for _ in range(self.pair_count)]#source
        self.se = [[] for _ in range(self.pair_count)]#source error
        self.np_source = [[] for _ in range(self.pair_count)] #Normalized source
        self.cdf_value = [[] for _ in range(self.pair_count)]#/np.sum(np_rvr)
        #self.np_source_r = [[] for _ in range(self.pair_count)] #Weigh the ratio
        

        

        # Populate source and se arrays
        for j in range(self.pair_count):
            self.source[j] = self.data[j*2 + 2]
            self.se[j] = self.data[j*2 + 3]
            self.np_source[j] = np.zeros(len(self.T))

        
        # Process sample data
        self.sample = self.data[0]
        self.sample_err = self.data[1]
        self.np_sample = np.zeros(len(self.T))
        
        # Calculate normal distributions
        self.calculate_distributions()
        
        # Normalize the data
        for a in range(self.pair_count):
            self.np_source[a] = self.np_source[a] / len(self.source[a])
            self.cdf_value[a]=np.cumsum(self.np_source[a])
        self.np_sample = self.np_sample / len(self.sample)
        print(self.np_sample)
        print(self.np_source)
        self.cdf_value_sample=np.cumsum(self.np_sample)
    
    def calculate_distributions(self):
        """Calculate normal distributions for sources and sample"""
        for m in range(self.pair_count):
            for n in range(len(self.source[m])):
                self.np_source[m] = self.np_source[m] + st.norm.pdf(self.T, self.source[m][n], 2*self.se[m][n])
        
        for i in range(len(self.sample)):
            self.np_sample = self.np_sample + st.norm.pdf(self.T, self.sample[i], 2*self.sample_err[i])
    
    @pyqtSlot()
    def on_pushButton_5_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        # 1. 获取保存路径
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存CSV文件",
            "",
            "CSV文件 (*.csv);;所有文件 (*)"
        )
        
        if not file_path:  # 用户取消选择
            return
        
        # 确保文件以.csv结尾
        if not file_path.lower().endswith('.csv'):
            file_path += '.csv'
        
        # 2. 获取模型数据
        model = self.tableView_2.model()
        if not model:
            return
        
        # 3. 准备写入CSV
        with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            
            # 写入列标题（水平表头）
            headers = []
            for col in range(model.columnCount()):
                header = model.headerData(col, Qt.Horizontal, Qt.DisplayRole)
                headers.append(str(header) if header else f"列{col+1}")
            writer.writerow([""] + headers)  # 第一格留空用于行标题
            
            # 写入每行数据
            for row in range(model.rowCount()):
                # 获取行标题（垂直表头）
                row_header = model.headerData(row, Qt.Vertical, Qt.DisplayRole)
                row_data = [str(row_header) if row_header else f"行{row+1}"]
                
                # 获取单元格数据
                for col in range(model.columnCount()):
                    index = model.index(row, col)
                    cell_data = model.data(index, Qt.DisplayRole)
                    row_data.append(str(cell_data) if cell_data is not None else "")
                
                writer.writerow(row_data)
        
        # 4. 提示导出成功
        QMessageBox.information(self, "成功", f"数据已导出到:\n{file_path}")
    
    @pyqtSlot()
    def on_actionOpen_triggered(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
                # 1. 弹出文件选择对话框（仅限 CSV 文件）
#        file_path, _ = QFileDialog.getOpenFileName(
#            self,
#            "打开 CSV 文件",
#            "",  # 默认路径（空表示当前目录）
#            "CSV 文件 (*.csv);;所有文件 (*)"
#        )
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open CSV File",  # Dialog title
            "",  # Default path (empty means current directory)
            "CSV Files (*.csv);;All Files (*)"  # File filters
        )
        # 如果用户取消选择，直接返回
        if not file_path:
            return
        
        try:
            # 2. 读取 CSV 文件
            with open(file_path, 'r', encoding='utf-8') as file:
                csv_data = [line.strip().split(',') for line in file if line.strip()]
            
            # 3. 检查列数是否 <= 10
            if not csv_data:
                #QMessageBox.warning(self, "错误", "文件为空！")
                QMessageBox.warning(self,  "Error", "The file is empty!")
                return
                
            num_columns = len(csv_data[0])
            if num_columns <5:
#                QMessageBox.critical(
#                    self,
#                    "数据溢出",
#                    f"CSV 文件有 {num_columns} 列，超过最大 10 列限制！\n请重新选择文件。"
#                )
                QMessageBox.critical(
                    self,
                    "Data Overflow",  # or "Column Limit Exceeded" for more precision
                    f"CSV file has {num_columns} columns, exceeding the maximum limit of 4.\nPlease select a different file."
                )
                return
            
            # 4. 清空现有数据
            self.model._data = [["" for _ in range(self.model.cols)] for _ in range(self.model.rows)]
            
            # 5. 导入数据（第一行为表头，其余为数据）
            # 设置表头
            headers = csv_data[0]
            self.model._horizontal_header = headers + [str(i) for i in range(len(headers), self.model.cols)]
            
            # 导入数据行
            for row_idx, row in enumerate(csv_data[1:]):
                if row_idx >= self.model.rows:  # 防止超出预设行数
                    break
                for col_idx, value in enumerate(row):
                    if col_idx >= self.model.cols:  # 防止超出预设列数
                        break
                    self.model._data[row_idx][col_idx] = value
            
            # 6. 刷新视图
            self.model.layoutChanged.emit()
            
            # 7. 提示导入成功
#            QMessageBox.information(
#                self,
#                "导入成功",
#                f"已成功导入 {min(len(csv_data)-1, self.model.rows)} 行数据。"
#            )
            QMessageBox.information(
                self,
                "Import Successful", 
                f"Successfully imported {min(len(csv_data)-1, self.model.rows)} rows of data."
            )
            
        except Exception as e:
#            QMessageBox.critical(
#                self,
#                "导入失败",
#                f"读取 CSV 文件时出错：\n{str(e)}"
#            )
            QMessageBox.critical(
                self,
                "Import Failed",
                f"Error reading CSV file:\n{str(e)}"
            )
    
    @pyqtSlot()
    def on_pushButton_clicked(self):
        """
        Slot documentation goes here.
        """
        # 检查表格是否为空
        empty_cells_in_gaps = {}  # 存储不连续的空单元格 {列索引: [(空单元格行索引, 前一个非空行索引)]}
        non_numeric_cells = []    # 存储非数字单元格位置
        column_pairs_mismatch = [] # 存储数字个数不一致的列对
        is_all_empty = True       # 标记表格是否全部为空
        
        # 动态确定列对 (相邻两列为一对)
        column_count = self.model.columnCount()
        column_pairs = [(i, i+1) for i in range(0, column_count-1, 2)]
        
        # 检查每列数据
        for col in range(column_count):
            prev_non_empty_row = None  # 记录前一个非空行的行索引
            
            for row in range(self.model.rowCount()):
                value = self.model.data(self.model.index(row, col), Qt.DisplayRole)
                str_value = str(value).strip() if value else ""
                
                # 检查单元格是否为空
                if not str_value:
                    continue  # 空单元格，跳过检查
                    
                # 如果执行到这里，说明表格不是全部为空
                is_all_empty = False
                
                # 检查是否为数字
                try:
                    float(str_value)
                except ValueError:
                    non_numeric_cells.append(f"第{row+1}行第{col+1}列")
                
                # 检查连续性（记录空单元格间隙）
                if prev_non_empty_row is not None and row != prev_non_empty_row + 1:
                    # 找到间隙中的空单元格
                    for gap_row in range(prev_non_empty_row + 1, row):
                        if col not in empty_cells_in_gaps:
                            empty_cells_in_gaps[col] = []
                        empty_cells_in_gaps[col].append(
                            (gap_row, prev_non_empty_row)
                        )
                
                prev_non_empty_row = row
        
        # 检查列对的数字个数是否一致
        for col1, col2 in column_pairs:
            for row in range(self.model.rowCount()):
                value1 = self.model.data(self.model.index(row, col1), Qt.DisplayRole)
                value2 = self.model.data(self.model.index(row, col2), Qt.DisplayRole)
                
                # 计算数字个数（以空格分隔）
                count1 = len(str(value1).split()) if value1 else 0
                count2 = len(str(value2).split()) if value2 else 0
                
                if count1 != count2:
                    column_pairs_mismatch.append(f"Column {col1+1} and Column {col2+1}")
                    break  # 每对列只需要报告一次
        
        # 准备消息
        message_parts = []
        
        if is_all_empty:
            QMessageBox.information(self, "Check Results", "The table is empty")
            return  # 如果是全空表格，直接返回
        
        if empty_cells_in_gaps:
            gap_messages = []
            for col, gaps in empty_cells_in_gaps.items():
                gap_details = []
                for gap in gaps:
                    empty_row, prev_row = gap
                    gap_details.append(
                        f"Row {empty_row+1} (previous non-empty at row {prev_row+1})"
                    )
                gap_messages.append(
                    f"Column {col+1} contains data gaps at:\n" + "\n".join(gap_details)
                )
            message_parts.append("The following columns have data continuity issues:\n" + "\n\n".join(gap_messages))
        else:
            message_parts.append("All columns have continuous data without empty cell gaps")
        
        if non_numeric_cells:
            message_parts.append(
                "The following cells contain non-numeric values:\n" + "\n".join(non_numeric_cells) + 
                "\n\nPlease modify these cells to contain numeric values"
            )
        else:
            message_parts.append("✓ Numeric format: All cells validated")
            self.pushButton_2.setEnabled(True)
            self.pushButton_3.setEnabled(True)
            self.pushButton_4.setEnabled(True)
            self.pushButton_5.setEnabled(True)
        
        if column_pairs_mismatch:
            message_parts.append(
                "Column pairs with mismatched number counts:\n" + "\n".join(column_pairs_mismatch)
            )
        else:
            message_parts.append("All column pairs have matching number counts")
        
        # 显示消息框
        QMessageBox.information(self, "Check Results", "\n\n".join(message_parts))
    
    @pyqtSlot()
    def on_radioButton_2_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        
        self.lineEdit_4.setEnabled(False)
        self.lineEdit_5.setEnabled(False)
    
    @pyqtSlot()
    def on_radioButton_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.lineEdit_4.setEnabled(True)
        self.lineEdit_5.setEnabled(True)
    
    @pyqtSlot()
    def on_radioButton_3_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.lineEdit_3.setEnabled(False)
    
    @pyqtSlot()
    def on_radioButton_4_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.lineEdit_3.setEnabled(True)
    
    @pyqtSlot()
    def on_pushButton_3_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.canvas.figure.clear()
        self.canvas.draw() 
        model = self.tableView_2.model()
    
        # 保留表头结构
        model.clear()
        model.setColumnCount(0)
        model.setRowCount(0)
    
    @pyqtSlot()
    def on_pushButton_4_clicked(self):
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
            self.save=self.figure.savefig(file_path)
            #print(self.save)
            QMessageBox.information(self,'Save','Sucessful!')
    
    @pyqtSlot()
    def on_pushButton_2_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        min_age = int(self.lineEdit.text())
        max_age = int(self.lineEdit_2.text())
        dT_value = int(self.lineEdit_8.text())
#        number = len(self.headers)
        self.age_range = [min_age, max_age]
        self.dT = dT_value
        self.T = np.zeros((self.age_range[1] - self.age_range[0]) // self.dT)
        self.headers = []  # 存储非空列的表头
        self.data = []     # 存储非空列的数据（按列组织）
        # 设置随机种子（确保结果可重复）
        random_seed = 42  # 可以改为你想要的任何固定值
        np.random.seed(random_seed)
        random.seed(random_seed)
        # 遍历所有列
        for col in range(self.model.columnCount()):
            # 获取当前列的表头
            header_text = str(self.model.headerData(col, Qt.Horizontal, Qt.DisplayRole))
            # 收集当前列的非空数据
            column_data = []
            for row in range(self.model.rowCount()):
                val = self.model.data(self.model.index(row, col), Qt.DisplayRole)
                str_val = str(val).strip() if val else ""  # 处理空值和非字符串类型
                if str_val:  # 仅保留非空值
                    try:
                        column_data.append(float(str_val))  # 转换为浮点数
                    except ValueError:
                        # 可选：处理无法转换为数字的情况（如非数值文本）
                        # column_data.append(str_val)  # 如需保留文本可取消注释
                        pass  # 或忽略非数值数据
            
            # 仅当列中有数据时，才添加表头和数据
            if column_data:  # 过滤完全为空的列
                self.headers.append(header_text)
                self.data.append(column_data) 
#        print(self.headers)
#        print(self.data)

#        print(self.sample)


        if self.radioButton_2.isChecked() and self.radioButton_3.isChecked():
            self.ratios = []  # 存储所有 [A, B, C] 比例
            #self.aa = []      # 存储所有相似度值
            #self.bb=[]
            self.ks=[]
            self.kut=[]
            self.r2=[]
            self.qr2=[]
            self.sim=[]
            self.like=[]
            
            
            self.canvas.figure.clear()  # 清空 canvas6 画布
            self.process_data(min_age, max_age, dT_value)  # 处理数据
            
            n = int(self.lineEdit_6.text())
        
            # 计算每组需要的数字个数
            j = len(self.source)
            print(j)
            random_combinations = self.generate_random_combinations(n,j)
            for i, combo in enumerate(random_combinations, 1):
                self.sum=0
                self.ratios.append(combo)
                for a in range (len(combo)):
                    self.sum+=combo[a]/100*self.np_source[a]
                #self.aa.append(sim.Similarity(self.np_sample, self.sum))
                
                self.ks.append(ks.kstest2b_tnc(self.np_sample, self.sum,0.05,'unequal',len(self.T))[2])
            
                self.kut.append(kut.kuipertest2_tnc(self.np_sample, self.sum,len(self.T))[1])
            
                self.r2.append(r.calculate_cross_correlation(self.np_sample, self.sum)[0])

            
#            self.q1=Qr.calculate_qq_plot(self.np_sample, self.np_source,len(self.T))[0]
#            self.q2=Qr.calculate_qq_plot(self.np_sample, self.np_source,len(self.T))[1]
                self.qr2.append(Qr.calculate_qq_plot(self.np_sample, self.sum,len(self.T))[2])
#            self.qslop=Qr.calculate_qq_plot(self.np_sample, self.np_source,len(self.T))[3]
#            self.qinterceptr=Qr.calculate_qq_plot(self.np_sample, self.np_source,len(self.T))[4]     
            
                self.sim.append(sim.Similarity(self.np_sample,self.sum))
            
                self.like.append(lk.Likeness(self.np_sample,self.sum))
                
                
                
                
                
                
                print(f"第{i}组: {combo} (和={sum(combo)}, 长度={len(combo)})")
#            print(self.aa)
            idx_max1 = np.argmax(self.ks)
            print(self.ratios[idx_max1])
            print(max(self.ks))
            idx_max2 = np.argmax(self.kut)
            print(self.ratios[idx_max2])
            print(max(self.kut))
            idx_max3 = np.argmax(self.r2)
            print(self.ratios[idx_max3])
            print(max(self.r2))
            idx_max4 = np.argmax(self.qr2)
            print(self.ratios[idx_max4])
            print(max(self.qr2))
            idx_max5 = np.argmax(self.sim)
            print(self.ratios[idx_max5])
            print(max(self.sim))
            idx_max6 = np.argmax(self.like)
            print(self.ratios[idx_max6])
            print(max(self.like))
            
            outer_grid = gridspec.GridSpec(2, 1, height_ratios=[1, 1], hspace=0.3)
            
            # First row: 1x2 grid with width_ratios=[3, 1] (or [2, 1] if you prefer 2:1)
            first_row = gridspec.GridSpecFromSubplotSpec(1, 2, subplot_spec=outer_grid[0], width_ratios=[3, 1], wspace=0.3)
            ax1 = self.canvas.figure.add_subplot(first_row[0])  # First row, first column (width=3)
            ax2 = self.canvas.figure.add_subplot(first_row[1])  # First row, second column (width=1)
            
            # Second row: 1x2 grid with width_ratios=[1, 1] (or [2, 2])
            second_row = gridspec.GridSpecFromSubplotSpec(1, 2, subplot_spec=outer_grid[1], width_ratios=[3, 1], wspace=0.3)
            ax3 = self.canvas.figure.add_subplot(second_row[0])  # Second row, first column (width=1)
            ax4 = self.canvas.figure.add_subplot(second_row[1])  # Second row, second column (width=1)
            # 创建1行2列的网格，宽度比例为2:1
            
            for a in range(self.pair_count):
                ax1.plot(self.T, self.np_source[a], color=self.generate_100_colors()[a], label=self.headers[a*2 + 2])  
#        
            ax1.plot(self.T, self.np_sample, color='black', label=self.headers[0])
            ax1.set_xlabel("Zircon U-Pb age (Ma)")
            ax1.set_ylabel("PDF")
            ax1.legend()
                    # 关键：设置x轴间隔为100（每100ma一个刻度）
            ax1.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
            ax1.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
            ax1.set_xlim(min_age, max_age)
            ax1.set_ylim(bottom=0)
            
            for a in range(self.pair_count):
                ax2.plot(self.T, np.cumsum(self.np_source[a]), color=self.generate_100_colors()[a], label=self.headers[a*2 + 2])  
#        
            ax2.plot(self.T, np.cumsum(self.np_sample), color='black', label=self.headers[0])
            ax2.set_xlabel("Zircon U-Pb age (Ma)")
            ax2.set_ylabel("CDFs")
            ax2.legend()
            ax2.set_xlim(min_age, max_age)
            ax2.set_ylim(0,1)
            ax2.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
            ax2.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
            
            ax3.plot(self.T, self.np_sample, color='black', label=self.headers[0])
            self.sum1=0
            for i in range(len(self.ratios[idx_max1])):
                self.sum1+=self.ratios[idx_max1][i]/100*self.np_source[i]
            ax3.plot(self.T, self.sum1, color=self.generate_100_colors()[0], label='K-S')
            self.sum2=0
            for i in range(len(self.ratios[idx_max2])):
                self.sum2+=self.ratios[idx_max2][i]/100*self.np_source[i]
            ax3.plot(self.T, self.sum2, color=self.generate_100_colors()[1], label='Kuiper')
            self.sum3=0
            for i in range(len(self.ratios[idx_max3])):
                self.sum3+=self.ratios[idx_max3][i]/100*self.np_source[i]
            ax3.plot(self.T, self.sum3, color=self.generate_100_colors()[2], label='Cross')
            self.sum4=0
            for i in range(len(self.ratios[idx_max4])):
                self.sum4+=self.ratios[idx_max4][i]/100*self.np_source[i]
            ax3.plot(self.T, self.sum4, color=self.generate_100_colors()[3], label='Q-Q')
            self.sum5=0
            for i in range(len(self.ratios[idx_max5])):
                self.sum5+=self.ratios[idx_max5][i]/100*self.np_source[i]
            ax3.plot(self.T, self.sum5, color=self.generate_100_colors()[4], label='Similarity')            
            self.sum6=0
            for i in range(len(self.ratios[idx_max6])):
                self.sum6+=self.ratios[idx_max6][i]/100*self.np_source[i]
            ax3.plot(self.T, self.sum6, color=self.generate_100_colors()[5], label='Likeness')            
            ax3.set_xlabel("Zircon U-Pb age (Ma)")
            ax3.set_ylabel("PDF")
            ax3.legend()
                    # 关键：设置x轴间隔为100（每100ma一个刻度）
            ax3.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
            ax3.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
            ax3.set_xlim(min_age, max_age)
            ax3.set_ylim(bottom=0)
            
                       
            ax4.plot(self.T, np.cumsum(self.sum1), color=self.generate_100_colors()[0], label='K-S') 
            ax4.plot(self.T, np.cumsum(self.sum2), color=self.generate_100_colors()[1], label='Kuiper')
            ax4.plot(self.T, np.cumsum(self.sum3), color=self.generate_100_colors()[2], label='Cross')
            ax4.plot(self.T, np.cumsum(self.sum4), color=self.generate_100_colors()[3], label='Q-Q')
            ax4.plot(self.T, np.cumsum(self.sum5), color=self.generate_100_colors()[4], label='Similarity')
            ax4.plot(self.T, np.cumsum(self.sum6), color=self.generate_100_colors()[5], label='Likeness')
            
            ax4.plot(self.T, np.cumsum(self.np_sample), color='black', label=self.headers[0])
            ax4.set_xlabel("Zircon U-Pb age (Ma)")
            ax4.set_ylabel("CDFs")
            ax4.legend()
            ax4.set_xlim(min_age, max_age)
            ax4.set_ylim(0,1)
            ax4.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
            ax4.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
            
            
            
            
                
            self.canvas.figure.set_constrained_layout(True)
                       # 5. 关键优化：调整整个图形的边距和布局
                    #plt.subplots_adjust(left=0.08, right=0.95, top=0.92, bottom=0.2)  # 手动调整边距
            self.canvas.draw()
            model = QStandardItemModel(6, len(self.headers)//2)
        
            # 3. 设置列名（水平表头）
            for i in range ((len(self.headers)-2)//2):
                model.setHeaderData(i, Qt.Horizontal, self.headers[i*2 + 2])
            column_name = "Results"
            model.setHeaderData(len(self.headers)//2-1, Qt.Horizontal, column_name)
            
            # 4. 设置行名（垂直表头）
            row_names = ['K-S','Kupier','Cross','Q-Q','Simlarity','Likeness']
            for row, name in enumerate(row_names):
                model.setHeaderData(row, Qt.Vertical, name)
                
#            # 5. 填充数据
#            data_to_display=[self.ks,self.kut,self.r2,self.qr2,self.sim,self.like]
#                        print(self.ratios[idx_max1])
#            print(max(self.ks))
#                  
#            
            for i in range(len(self.ratios[idx_max1])):
                item = QStandardItem(str("{:.4f}".format(self.ratios[idx_max1][i]/100)))  
                model.setItem(0, i, item)
            item1 = QStandardItem(str("{:.4f}".format(max(self.ks)))) 
            model.setItem(0, len(self.ratios[idx_max1]), item1)
            
            for i in range(len(self.ratios[idx_max2])):
                item = QStandardItem(str("{:.4f}".format(self.ratios[idx_max2][i]/100)))  
                model.setItem(1, i, item)
            item2 = QStandardItem(str("{:.4f}".format(max(self.kut)))) 
            model.setItem(1, len(self.ratios[idx_max2]), item2)
            
            for i in range(len(self.ratios[idx_max3])):
                item = QStandardItem(str("{:.4f}".format(self.ratios[idx_max3][i]/100)))  
                model.setItem(2, i, item)
            item3 = QStandardItem(str("{:.4f}".format(max(self.r2)))) 
            model.setItem(2, len(self.ratios[idx_max3]), item3) 
            
            for i in range(len(self.ratios[idx_max4])):
                item = QStandardItem(str("{:.4f}".format(self.ratios[idx_max4][i]/100)))  
                model.setItem(3, i, item)
            item4 = QStandardItem(str("{:.4f}".format(max(self.qr2)))) 
            model.setItem(3, len(self.ratios[idx_max4]), item4) 
            
            for i in range(len(self.ratios[idx_max5])):
                item = QStandardItem(str("{:.4f}".format(self.ratios[idx_max5][i]/100)))  
                model.setItem(4, i, item)
            item5 = QStandardItem(str("{:.4f}".format(max(self.sim)))) 
            model.setItem(4, len(self.ratios[idx_max5]), item5)         
            
            for i in range(len(self.ratios[idx_max6])):
                item = QStandardItem(str("{:.4f}".format(self.ratios[idx_max6][i]/100)))  
                model.setItem(5, i, item)
            item6 = QStandardItem(str("{:.4f}".format(max(self.like)))) 
            model.setItem(5, len(self.ratios[idx_max6]), item6)  
            
            self.tableView_2.setModel(model)
            
            # 自动调整列宽和行高
            self.tableView_2.resizeColumnsToContents()  # 自动调整所有列宽
            
            # 自动调整行高（基于内容）
            for row in range(model.rowCount()):
                self.tableView_2.resizeRowToContents(row)
            
            # 可选：设置最小行高（避免内容太少时行高太小）
            self.tableView_2.verticalHeader().setDefaultSectionSize(24)  # 设置默认行高
            
            # 可选：设置列宽弹性（允许用户拖动调整）
            self.tableView_2.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        if self.radioButton_2.isChecked() and self.radioButton_4.isChecked():
            self.ratios = []  # 存储所有 [A, B, C] 比例
            #self.aa = []      # 存储所有相似度值
            #self.bb=[]
            self.ks=[]
            self.kut=[]
            self.r2=[]
            self.qr2=[]
            self.sim=[]
            self.like=[]
            
            
            self.canvas.figure.clear()  # 清空 canvas6 画布
            #self.process_data(min_age, max_age, dT_value)  # 处理数据
            self.process_data_kde(min_age, max_age, dT_value,int(self.lineEdit_3.text()))
            
            n = int(self.lineEdit_6.text())
        
            # 计算每组需要的数字个数
            j = len(self.source)
            print(j)
            random_combinations = self.generate_random_combinations(n,j)
            for i, combo in enumerate(random_combinations, 1):
                self.sum=0
                self.ratios.append(combo)
                for a in range (len(combo)):
                    self.sum+=combo[a]/100*self.np_source[a]
                #self.aa.append(sim.Similarity(self.np_sample, self.sum))
                
                self.ks.append(ks.kstest2b_tnc(self.np_sample, self.sum,0.05,'unequal',len(self.T))[2])
            
                self.kut.append(kut.kuipertest2_tnc(self.np_sample, self.sum,len(self.T))[1])
            
                self.r2.append(r.calculate_cross_correlation(self.np_sample, self.sum)[0])

            
#            self.q1=Qr.calculate_qq_plot(self.np_sample, self.np_source,len(self.T))[0]
#            self.q2=Qr.calculate_qq_plot(self.np_sample, self.np_source,len(self.T))[1]
                self.qr2.append(Qr.calculate_qq_plot(self.np_sample, self.sum,len(self.T))[2])
#            self.qslop=Qr.calculate_qq_plot(self.np_sample, self.np_source,len(self.T))[3]
#            self.qinterceptr=Qr.calculate_qq_plot(self.np_sample, self.np_source,len(self.T))[4]     
            
                self.sim.append(sim.Similarity(self.np_sample,self.sum))
            
                self.like.append(lk.Likeness(self.np_sample,self.sum))
                
                
                
                
                
                
                print(f"第{i}组: {combo} (和={sum(combo)}, 长度={len(combo)})")
#            print(self.aa)
            idx_max1 = np.argmax(self.ks)
            print(self.ratios[idx_max1])
            print(max(self.ks))
            idx_max2 = np.argmax(self.kut)
            print(self.ratios[idx_max2])
            print(max(self.kut))
            idx_max3 = np.argmax(self.r2)
            print(self.ratios[idx_max3])
            print(max(self.r2))
            idx_max4 = np.argmax(self.qr2)
            print(self.ratios[idx_max4])
            print(max(self.qr2))
            idx_max5 = np.argmax(self.sim)
            print(self.ratios[idx_max5])
            print(max(self.sim))
            idx_max6 = np.argmax(self.like)
            print(self.ratios[idx_max6])
            print(max(self.like))
            
            outer_grid = gridspec.GridSpec(2, 1, height_ratios=[1, 1], hspace=0.3)
            
            # First row: 1x2 grid with width_ratios=[3, 1] (or [2, 1] if you prefer 2:1)
            first_row = gridspec.GridSpecFromSubplotSpec(1, 2, subplot_spec=outer_grid[0], width_ratios=[3, 1], wspace=0.3)
            ax1 = self.canvas.figure.add_subplot(first_row[0])  # First row, first column (width=3)
            ax2 = self.canvas.figure.add_subplot(first_row[1])  # First row, second column (width=1)
            
            # Second row: 1x2 grid with width_ratios=[1, 1] (or [2, 2])
            second_row = gridspec.GridSpecFromSubplotSpec(1, 2, subplot_spec=outer_grid[1], width_ratios=[3, 1], wspace=0.3)
            ax3 = self.canvas.figure.add_subplot(second_row[0])  # Second row, first column (width=1)
            ax4 = self.canvas.figure.add_subplot(second_row[1])  # Second row, second column (width=1)
            # 创建1行2列的网格，宽度比例为2:1
            
            for a in range(self.pair_count):
                ax1.plot(self.T, self.np_source[a], color=self.generate_100_colors()[a], label=self.headers[a*2 + 2])  
#        
            ax1.plot(self.T, self.np_sample, color='black', label=self.headers[0])
            ax1.set_xlabel("Zircon U-Pb age (Ma)")
            ax1.set_ylabel("PDF")
            ax1.legend()
                    # 关键：设置x轴间隔为100（每100ma一个刻度）
            ax1.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
            ax1.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
            ax1.set_xlim(min_age, max_age)
            ax1.set_ylim(bottom=0)
            
            for a in range(self.pair_count):
                ax2.plot(self.T, np.cumsum(self.np_source[a]), color=self.generate_100_colors()[a], label=self.headers[a*2 + 2])  
#        
            ax2.plot(self.T, np.cumsum(self.np_sample), color='black', label=self.headers[0])
            ax2.set_xlabel("Zircon U-Pb age (Ma)")
            ax2.set_ylabel("CDFs")
            ax2.legend()
            ax2.set_xlim(min_age, max_age)
            ax2.set_ylim(0,1)
            ax2.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
            ax2.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
            
            ax3.plot(self.T, self.np_sample, color='black', label=self.headers[0])
            self.sum1=0
            for i in range(len(self.ratios[idx_max1])):
                self.sum1+=self.ratios[idx_max1][i]/100*self.np_source[i]
            ax3.plot(self.T, self.sum1, color=self.generate_100_colors()[0], label='K-S')
            self.sum2=0
            for i in range(len(self.ratios[idx_max2])):
                self.sum2+=self.ratios[idx_max2][i]/100*self.np_source[i]
            ax3.plot(self.T, self.sum2, color=self.generate_100_colors()[1], label='Kuiper')
            self.sum3=0
            for i in range(len(self.ratios[idx_max3])):
                self.sum3+=self.ratios[idx_max3][i]/100*self.np_source[i]
            ax3.plot(self.T, self.sum3, color=self.generate_100_colors()[2], label='Cross')
            self.sum4=0
            for i in range(len(self.ratios[idx_max4])):
                self.sum4+=self.ratios[idx_max4][i]/100*self.np_source[i]
            ax3.plot(self.T, self.sum4, color=self.generate_100_colors()[3], label='Q-Q')
            self.sum5=0
            for i in range(len(self.ratios[idx_max5])):
                self.sum5+=self.ratios[idx_max5][i]/100*self.np_source[i]
            ax3.plot(self.T, self.sum5, color=self.generate_100_colors()[4], label='Similarity')            
            self.sum6=0
            for i in range(len(self.ratios[idx_max6])):
                self.sum6+=self.ratios[idx_max6][i]/100*self.np_source[i]
            ax3.plot(self.T, self.sum6, color=self.generate_100_colors()[5], label='Likeness')            
            ax3.set_xlabel("Zircon U-Pb age (Ma)")
            ax3.set_ylabel("PDF")
            ax3.legend()
                    # 关键：设置x轴间隔为100（每100ma一个刻度）
            ax3.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
            ax3.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
            ax3.set_xlim(min_age, max_age)
            ax3.set_ylim(bottom=0)
            
                       
            ax4.plot(self.T, np.cumsum(self.sum1), color=self.generate_100_colors()[0], label='K-S') 
            ax4.plot(self.T, np.cumsum(self.sum2), color=self.generate_100_colors()[1], label='Kuiper')
            ax4.plot(self.T, np.cumsum(self.sum3), color=self.generate_100_colors()[2], label='Cross')
            ax4.plot(self.T, np.cumsum(self.sum4), color=self.generate_100_colors()[3], label='Q-Q')
            ax4.plot(self.T, np.cumsum(self.sum5), color=self.generate_100_colors()[4], label='Similarity')
            ax4.plot(self.T, np.cumsum(self.sum6), color=self.generate_100_colors()[5], label='Likeness')
            
            ax4.plot(self.T, np.cumsum(self.np_sample), color='black', label=self.headers[0])
            ax4.set_xlabel("Zircon U-Pb age (Ma)")
            ax4.set_ylabel("CDFs")
            ax4.legend()
            ax4.set_xlim(min_age, max_age)
            ax4.set_ylim(0,1)
            ax4.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
            ax4.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
            
            
            
            
                
            self.canvas.figure.set_constrained_layout(True)
                       # 5. 关键优化：调整整个图形的边距和布局
                    #plt.subplots_adjust(left=0.08, right=0.95, top=0.92, bottom=0.2)  # 手动调整边距
            self.canvas.draw()
            model = QStandardItemModel(6, len(self.headers)//2)
        
            # 3. 设置列名（水平表头）
            for i in range ((len(self.headers)-2)//2):
                model.setHeaderData(i, Qt.Horizontal, self.headers[i*2 + 2])
            column_name = "Results"
            model.setHeaderData(len(self.headers)//2-1, Qt.Horizontal, column_name)
            
            # 4. 设置行名（垂直表头）
            row_names = ['K-S','Kupier','Cross','Q-Q','Simlarity','Likeness']
            for row, name in enumerate(row_names):
                model.setHeaderData(row, Qt.Vertical, name)
                
#            # 5. 填充数据
#            data_to_display=[self.ks,self.kut,self.r2,self.qr2,self.sim,self.like]
#                        print(self.ratios[idx_max1])
#            print(max(self.ks))
#                  
#            
            for i in range(len(self.ratios[idx_max1])):
                item = QStandardItem(str("{:.4f}".format(self.ratios[idx_max1][i]/100)))  
                model.setItem(0, i, item)
            item1 = QStandardItem(str("{:.4f}".format(max(self.ks)))) 
            model.setItem(0, len(self.ratios[idx_max1]), item1)
            
            for i in range(len(self.ratios[idx_max2])):
                item = QStandardItem(str("{:.4f}".format(self.ratios[idx_max2][i]/100)))  
                model.setItem(1, i, item)
            item2 = QStandardItem(str("{:.4f}".format(max(self.kut)))) 
            model.setItem(1, len(self.ratios[idx_max2]), item2)
            
            for i in range(len(self.ratios[idx_max3])):
                item = QStandardItem(str("{:.4f}".format(self.ratios[idx_max3][i]/100)))  
                model.setItem(2, i, item)
            item3 = QStandardItem(str("{:.4f}".format(max(self.r2)))) 
            model.setItem(2, len(self.ratios[idx_max3]), item3) 
            
            for i in range(len(self.ratios[idx_max4])):
                item = QStandardItem(str("{:.4f}".format(self.ratios[idx_max4][i]/100)))  
                model.setItem(3, i, item)
            item4 = QStandardItem(str("{:.4f}".format(max(self.qr2)))) 
            model.setItem(3, len(self.ratios[idx_max4]), item4) 
            
            for i in range(len(self.ratios[idx_max5])):
                item = QStandardItem(str("{:.4f}".format(self.ratios[idx_max5][i]/100)))  
                model.setItem(4, i, item)
            item5 = QStandardItem(str("{:.4f}".format(max(self.sim)))) 
            model.setItem(4, len(self.ratios[idx_max5]), item5)         
            
            for i in range(len(self.ratios[idx_max6])):
                item = QStandardItem(str("{:.4f}".format(self.ratios[idx_max6][i]/100)))  
                model.setItem(5, i, item)
            item6 = QStandardItem(str("{:.4f}".format(max(self.like)))) 
            model.setItem(5, len(self.ratios[idx_max6]), item6)  
            
            self.tableView_2.setModel(model)
            
            # 自动调整列宽和行高
            self.tableView_2.resizeColumnsToContents()  # 自动调整所有列宽
            
            # 自动调整行高（基于内容）
            for row in range(model.rowCount()):
                self.tableView_2.resizeRowToContents(row)
            
            # 可选：设置最小行高（避免内容太少时行高太小）
            self.tableView_2.verticalHeader().setDefaultSectionSize(24)  # 设置默认行高
            
            # 可选：设置列宽弹性（允许用户拖动调整）
            self.tableView_2.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)

        if self.radioButton.isChecked() and self.radioButton_3.isChecked():
#            self.lineEdit_4.setEnabled(True)
#            self.lineEdit_5.setEnabled(True)
            self.dd=self.data[2:]
            
            print(self.dd)
            self.min_length = min(len(lst) for lst in self.dd)
            print(self.min_length)
            self.ksmax= []
            self.kutmax= []
            self.r2max= []
            self.qr2max= []
            self.simmax= []
            self.likemax= []
            
            self.ksmaxr= []
            self.kutmaxr= []
            self.r2maxr= []
            self.qr2maxr= []
            self.simmaxr= []
            self.likemaxr= []           
#
#
            if self.min_length < int(self.lineEdit_4.text()):
                # 弹出警告框，但继续执行（不报错）
                QMessageBox.warning(
                    self,  # 父窗口（通常是 self）
                    "抽样数量不足",
                    f"最短子列表只有 {self.min_length} 个元素，无法抽取 {int(self.lineEdit_4.text())} 个。"
                )
            else:

                self.canvas.figure.clear()  # 清空 canvas6 画布
#                
#                #计算出样品的pdf
                for i in range(len(self.T)):
                    self.T[i] = min_age + i * dT_value
                self.aaa=[]
                self.sample = self.data[0]
                self.sample_err = self.data[1]
                self.np_sample = np.zeros(len(self.T))
                for i in range(len(self.sample)):
                    self.np_sample = self.np_sample + st.norm.pdf(self.T, self.sample[i], 2*self.sample_err[i])
                self.np_sample = self.np_sample / len(self.sample)
                print(self.np_sample)
                self.cdf_value_sample=np.cumsum(self.np_sample)
#                np_sample = self.kde_pdf(self.data[0], self.T, bandwidth=int(self.lineEdit_3.text()))
                outer_grid = gridspec.GridSpec(2, 1, height_ratios=[1, 1], hspace=0.3)
#            
                # First row: 1x2 grid with width_ratios=[3, 1] (or [2, 1] if you prefer 2:1)
                first_row = gridspec.GridSpecFromSubplotSpec(1, 2, subplot_spec=outer_grid[0], width_ratios=[3, 1], wspace=0.3)
                ax1 = self.canvas.figure.add_subplot(first_row[0])  # First row, first column (width=3)
                ax2 = self.canvas.figure.add_subplot(first_row[1])  # First row, second column (width=1)
#                #            
#                # Second row: 1x2 grid with width_ratios=[1, 1] (or [2, 2])
                second_row = gridspec.GridSpecFromSubplotSpec(1, 2, subplot_spec=outer_grid[1], width_ratios=[3, 1], wspace=0.3)
                ax3 = self.canvas.figure.add_subplot(second_row[0])  # Second row, first column (width=1)
                ax4 = self.canvas.figure.add_subplot(second_row[1])  # Second row, second column (width=1)
#                
                ax1.plot(self.T, self.np_sample, color='black', label=self.headers[0])
                ax2.plot(self.T, self.cdf_value_sample, color='black', label=self.headers[0])
                ax4.plot(self.T, self.cdf_value_sample, color='black', label=self.headers[0])
#                # 循环4次（或根据lineEdit_5的值）
                for j in range(int(self.lineEdit_5.text())):  # 或者 range(int(self.lineEdit_5.text()))
                    # 抽样数据
                    self.ks= []
                    self.kut= []
                    self.r2= []
                    self.qr2= []
                    self.sim= []
                    self.like= []
                    all_sources = []
#                    min_length = min(len(lst) for lst in self.dd)
                    sampled_indices = random.sample(range(self.min_length), int(self.lineEdit_4.text()))
                    self.sampled_data = [
                        [lst[i] for i in sampled_indices]
                        for lst in self.dd
                    ]
                     # 准备数据
                    print(len(self.sampled_data))
                    
                    self.pair_count = (len(self.sampled_data)) // 2
                    self.source = [[] for _ in range(self.pair_count)]#source
                    self.se = [[] for _ in range(self.pair_count)]#source error
                    self.np_source = [[] for _ in range(self.pair_count)] #Normalized source
                    self.cdf_value = [[] for _ in range(self.pair_count)]#/np.sum(np_rvr)
                    
                            # Populate source and se arrays
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
                    for cc in range(len(self.np_source)):
                        ax1.plot(self.T,self.np_source[cc],color=self.generate_100_colors()[cc])
                        ax2.plot(self.T,self.cdf_value[cc], color=self.generate_100_colors()[cc])  
                    nn = int(self.lineEdit_6.text())
                     #            # 计算每组需要的数字个数
                    jj = len(self.np_source)   
                    random_combinations = self.generate_random_combinations(nn,jj)  
                    self.ratios=[]                    
                    for i, combo in enumerate(random_combinations, 1):
                        self.sum=0
                        self.ratios.append(combo)
                        for a in range (len(combo)):
                            self.sum+=combo[a]/100*self.np_source[a]
#                #self.aa.append(sim.Similarity(self.np_sample, self.sum))
#                
                        self.ks.append(ks.kstest2b_tnc(self.np_sample, self.sum,0.05,'unequal',len(self.T))[2])           
                        self.kut.append(kut.kuipertest2_tnc(self.np_sample, self.sum,len(self.T))[1])           
                        self.r2.append(r.calculate_cross_correlation(self.np_sample, self.sum)[0])                      
                        self.qr2.append(Qr.calculate_qq_plot(self.np_sample, self.sum,len(self.T))[2])
                        self.sim.append(sim.Similarity(self.np_sample,self.sum))
                        self.like.append(lk.Likeness(self.np_sample,self.sum))
                    print(str(j+1)+'次')
                    
                    idx_max1 = np.argmax(self.ks)
                    print(self.ratios[idx_max1])
                    print(max(self.ks))
                    self.ksmaxr.append(self.ratios[idx_max1])
                    self.ksmax.append(max(self.ks))
#
#                    
#                    
                    idx_max2 = np.argmax(self.kut)
                    print(self.ratios[idx_max2])
                    print(max(self.kut))
                    self.kutmaxr.append(self.ratios[idx_max2])
                    self.kutmax.append(max(self.kut))
                    
                    
                    idx_max3 = np.argmax(self.r2)
                    print(self.ratios[idx_max3])
                    print(max(self.r2))
                    self.r2maxr.append(self.ratios[idx_max3])
                    self.r2max.append(max(self.r2))
                    
                    idx_max4 = np.argmax(self.qr2)
                    print(self.ratios[idx_max4])
                    print(max(self.qr2))
                    self.qr2maxr.append(self.ratios[idx_max4])
                    self.qr2max.append(max(self.qr2))
                    
                    idx_max5 = np.argmax(self.sim)
                    print(self.ratios[idx_max5])
                    print(max(self.sim))
                    self.simmaxr.append(self.ratios[idx_max5])
                    self.simmax.append(max(self.sim))
                    
              
                    idx_max6 = np.argmax(self.like)
                    print(self.ratios[idx_max6])
                    print(max(self.like))
                    self.likemaxr.append(self.ratios[idx_max6])
                    self.likemax.append(max(self.like))  
                print('*'*100)        
                print('final')
                print(self.aaa)
                k1=np.argmax(self.ksmax)
                print(self.ksmaxr[k1])
                print(max(self.ksmax))   
                
                k2=np.argmax(self.kutmax)
                print(self.kutmaxr[k2])
                print(max(self.kutmax))  
                
                k3=np.argmax(self.r2max)
                print(self.r2maxr[k3])
                print(max(self.r2max))   
                
                k4=np.argmax(self.qr2max)
                print(self.qr2maxr[k4])
                print(max(self.qr2max))  
                
                k5=np.argmax(self.simmax)
                print(self.simmaxr[k5])
                print(max(self.simmax))   
                
                k6=np.argmax(self.likemax)
                print(self.likemaxr[k6])
                print(max(self.likemax))  
#            
#            
#            



#            
#
#            
            ax1.set_xlabel("Zircon U-Pb age (Ma)")
            ax1.set_ylabel("PDF")
            for cc in range(len(self.np_source)):
                ax1.plot([],[],color=self.generate_100_colors()[cc],label=self.headers[cc*2 + 2])
            ax1.legend()
                    # 关键：设置x轴间隔为100（每100ma一个刻度）
            ax1.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
            ax1.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
            ax1.set_xlim(min_age, max_age)
            ax1.set_ylim(bottom=0)
#            
##            for a in range(self.pair_count):
##                ax2.plot(self.T, np.cumsum(self.np_source[a]), color=self.generate_100_colors()[a], label=self.headers[a*2 + 2])  
###        
#
            ax2.set_xlabel("Zircon U-Pb age (Ma)")
            ax2.set_ylabel("CDFs")
            for cc in range(len(self.np_source)):
                ax2.plot([],[],color=self.generate_100_colors()[cc],label=self.headers[cc*2 + 2])
            ax2.legend()
            ax2.set_xlim(min_age, max_age)
            ax2.set_ylim(0,1)
            ax2.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
            ax2.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
#            
            ax3.plot(self.T, self.np_sample, color='black', label=self.headers[0])
#
#
            self.sum1=0
            for i in range(len(self.ksmaxr[k1])):
                self.sum1+=self.ksmaxr[k1][i]/100*self.aaa[k1][i]
            ax3.plot(self.T, self.sum1, color=self.generate_100_colors()[0], label='K-S')
            self.sum2=0
            for i in range(len(self.kutmaxr[k2])):
                self.sum2+=self.kutmaxr[k2][i]/100*self.aaa[k2][i]
            ax3.plot(self.T, self.sum2, color=self.generate_100_colors()[1], label='Kuiper')
            self.sum3=0
            for i in range(len(self.r2maxr[k3])):
                self.sum3+=self.r2maxr[k3][i]/100*self.aaa[k3][i]
            ax3.plot(self.T, self.sum3, color=self.generate_100_colors()[2], label='Cross')
            self.sum4=0
            for i in range(len(self.qr2maxr[k4])):
                self.sum4+=self.qr2maxr[k4][i]/100*self.aaa[k4][i]
            ax3.plot(self.T, self.sum4, color=self.generate_100_colors()[3], label='Q-Q')
            self.sum5=0
            for i in range(len(self.simmaxr[k5])):
                self.sum5+=self.simmaxr[k5][i]/100*self.aaa[k5][i]
            ax3.plot(self.T, self.sum5, color=self.generate_100_colors()[4], label='Similarity')            
            self.sum6=0
            for i in range(len(self.likemaxr[k6])):
                self.sum6+=self.likemaxr[k6][i]/100*self.aaa[k6][i]
            ax3.plot(self.T, self.sum6, color=self.generate_100_colors()[5], label='Likeness')            
            ax3.set_xlabel("Zircon U-Pb age (Ma)")
            ax3.set_ylabel("PDF")
            ax3.legend()
                    # 关键：设置x轴间隔为100（每100ma一个刻度）
            ax3.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
            ax3.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
            ax3.set_xlim(min_age, max_age)
            ax3.set_ylim(bottom=0)
##            
##                       
            ax4.plot(self.T, np.cumsum(self.sum1), color=self.generate_100_colors()[0], label='K-S') 
            ax4.plot(self.T, np.cumsum(self.sum2), color=self.generate_100_colors()[1], label='Kuiper')
            ax4.plot(self.T, np.cumsum(self.sum3), color=self.generate_100_colors()[2], label='Cross')
            ax4.plot(self.T, np.cumsum(self.sum4), color=self.generate_100_colors()[3], label='Q-Q')
            ax4.plot(self.T, np.cumsum(self.sum5), color=self.generate_100_colors()[4], label='Similarity')
            ax4.plot(self.T, np.cumsum(self.sum6), color=self.generate_100_colors()[5], label='Likeness')
#
#       
            ax4.set_xlabel("Zircon U-Pb age (Ma)")
            ax4.set_ylabel("CDFs")
            ax4.legend()
            ax4.set_xlim(min_age, max_age)
            ax4.set_ylim(0,1)
            ax4.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
            ax4.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
#            
#            
#            
#            
#                
            self.canvas.figure.set_constrained_layout(True)
                       # 5. 关键优化：调整整个图形的边距和布局
                    #plt.subplots_adjust(left=0.08, right=0.95, top=0.92, bottom=0.2)  # 手动调整边距
            self.canvas.draw()
            model = QStandardItemModel(6, len(self.headers)//2)
        
            # 3. 设置列名（水平表头）
            for i in range ((len(self.headers)-2)//2):
                model.setHeaderData(i, Qt.Horizontal, self.headers[i*2 + 2])
            column_name = "Results"
            model.setHeaderData(len(self.headers)//2-1, Qt.Horizontal, column_name)
            
            # 4. 设置行名（垂直表头）
            row_names = ['K-S','Kupier','Cross','Q-Q','Simlarity','Likeness']
            for row, name in enumerate(row_names):
                model.setHeaderData(row, Qt.Vertical, name)
                
#            # 5. 填充数据
#            data_to_display=[self.ks,self.kut,self.r2,self.qr2,self.sim,self.like]
#                        print(self.ratios[idx_max1])
#            print(max(self.ks))
#                  
#            
            for i in range(len(self.ksmaxr[k1])):
                item = QStandardItem(str("{:.4f}".format(self.ksmaxr[k1][i]/100)))  
                model.setItem(0, i, item)
            item1 = QStandardItem(str("{:.4f}".format(max(self.ksmax)))) 
            model.setItem(0, len(self.ksmaxr[k1]), item1)
            
            for i in range(len(self.kutmaxr[k2])):
                item = QStandardItem(str("{:.4f}".format(self.kutmaxr[k2][i]/100)))  
                model.setItem(1, i, item)
            item2 = QStandardItem(str("{:.4f}".format(max(self.kutmax)))) 
            model.setItem(1, len(self.kutmaxr[k2]), item2)
            
            for i in range(len(self.r2maxr[k3])):
                item = QStandardItem(str("{:.4f}".format(self.r2maxr[k3][i]/100)))  
                model.setItem(2, i, item)
            item3 = QStandardItem(str("{:.4f}".format(max(self.r2max)))) 
            model.setItem(2, len(self.r2maxr[k3]), item3) 
#            
            for i in range(len(self.qr2maxr[k4])):
                item = QStandardItem(str("{:.4f}".format(self.qr2maxr[k4][i]/100)))  
                model.setItem(3, i, item)
            item4 = QStandardItem(str("{:.4f}".format(max(self.qr2max)))) 
            model.setItem(3, len(self.qr2maxr[k4]), item4) 
#            
            for i in range(len(self.simmaxr[k5])):
                item = QStandardItem(str("{:.4f}".format(self.simmaxr[k5][i]/100)))  
                model.setItem(4, i, item)
            item5 = QStandardItem(str("{:.4f}".format(max(self.simmax)))) 
            model.setItem(4, len(self.simmaxr[k5]), item5)         
#            
            for i in range(len(self.likemaxr[k6])):
                item = QStandardItem(str("{:.4f}".format(self.likemaxr[k6][i]/100)))  
                model.setItem(5, i, item)
            item6 = QStandardItem(str("{:.4f}".format(max(self.likemax)))) 
            model.setItem(5, len(self.likemaxr[k6]), item6)  
            
            self.tableView_2.setModel(model)
            
            # 自动调整列宽和行高
            self.tableView_2.resizeColumnsToContents()  # 自动调整所有列宽
            
            # 自动调整行高（基于内容）
            for row in range(model.rowCount()):
                self.tableView_2.resizeRowToContents(row)
            
            # 可选：设置最小行高（避免内容太少时行高太小）
            self.tableView_2.verticalHeader().setDefaultSectionSize(24)  # 设置默认行高
            
            # 可选：设置列宽弹性（允许用户拖动调整）
            self.tableView_2.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
            
            
            
            




        if self.radioButton.isChecked() and self.radioButton_4.isChecked():
            self.lineEdit_4.setEnabled(True)
            self.lineEdit_5.setEnabled(True)
            self.dd=self.data[2:]
            
#            print(self.dd)
            self.min_length = min(len(lst) for lst in self.dd)
            print(self.min_length)
            self.ksmax= []
            self.kutmax= []
            self.r2max= []
            self.qr2max= []
            self.simmax= []
            self.likemax= []
            
            self.ksmaxr= []
            self.kutmaxr= []
            self.r2maxr= []
            self.qr2maxr= []
            self.simmaxr= []
            self.likemaxr= []           


            if self.min_length < int(self.lineEdit_4.text()):
                # 弹出警告框，但继续执行（不报错）
                QMessageBox.warning(
                    self,  # 父窗口（通常是 self）
                    "抽样数量不足",
                    f"最短子列表只有 {self.min_length} 个元素，无法抽取 {int(self.lineEdit_4.text())} 个。"
                )
            else:

                self.canvas.figure.clear()  # 清空 canvas6 画布
                
                
                for i in range(len(self.T)):
                    self.T[i] = min_age + i * dT_value
                self.aaa=[]
                np_sample = self.kde_pdf(self.data[0], self.T, bandwidth=int(self.lineEdit_3.text()))
                outer_grid = gridspec.GridSpec(2, 1, height_ratios=[1, 1], hspace=0.3)
            
                # First row: 1x2 grid with width_ratios=[3, 1] (or [2, 1] if you prefer 2:1)
                first_row = gridspec.GridSpecFromSubplotSpec(1, 2, subplot_spec=outer_grid[0], width_ratios=[3, 1], wspace=0.3)
                ax1 = self.canvas.figure.add_subplot(first_row[0])  # First row, first column (width=3)
                ax2 = self.canvas.figure.add_subplot(first_row[1])  # First row, second column (width=1)
                #            
                # Second row: 1x2 grid with width_ratios=[1, 1] (or [2, 2])
                second_row = gridspec.GridSpecFromSubplotSpec(1, 2, subplot_spec=outer_grid[1], width_ratios=[3, 1], wspace=0.3)
                ax3 = self.canvas.figure.add_subplot(second_row[0])  # Second row, first column (width=1)
                ax4 = self.canvas.figure.add_subplot(second_row[1])  # Second row, second column (width=1)
                
                ax1.plot(self.T, np_sample, color='black', label=self.headers[0])
                ax2.plot(self.T, np.cumsum(np_sample), color='black', label=self.headers[0])
                ax4.plot(self.T, np.cumsum(np_sample), color='black', label=self.headers[0])
                # 循环4次（或根据lineEdit_5的值）
                for j in range(int(self.lineEdit_5.text())):  # 或者 range(int(self.lineEdit_5.text()))
                    # 抽样数据
                    self.ks= []
                    self.kut= []
                    self.r2= []
                    self.qr2= []
                    self.sim= []
                    self.like= []
                    all_sources = []
#                    min_length = min(len(lst) for lst in self.dd)
                    sampled_indices = random.sample(range(self.min_length), int(self.lineEdit_4.text()))
                    self.sampled_data = [
                        [lst[i] for i in sampled_indices]
                        for lst in self.dd
                    ]
                     # 准备数据
                    print(len(self.sampled_data))
                    for a in range (len(self.sampled_data)//2):
                        np_source = self.kde_pdf(self.sampled_data[a*2], self.T, bandwidth=int(self.lineEdit_3.text()))
                        all_sources.append(np_source)
                    self.aaa.append(all_sources)
                    for cc in range(len(all_sources)):
                        ax1.plot(self.T,all_sources[cc],color=self.generate_100_colors()[cc])
                        ax2.plot(self.T, np.cumsum(all_sources[cc]), color=self.generate_100_colors()[cc])  
                    n = int(self.lineEdit_6.text())
                     #            # 计算每组需要的数字个数
                    jj = len(all_sources)   
                    random_combinations = self.generate_random_combinations(n,jj)  
                    self.ratios=[]                    
                    for i, combo in enumerate(random_combinations, 1):
                        self.sum=0
                        self.ratios.append(combo)
                        for a in range (len(combo)):
                            self.sum+=combo[a]/100*all_sources[a]
                #self.aa.append(sim.Similarity(self.np_sample, self.sum))
                
                        self.ks.append(ks.kstest2b_tnc(np_sample, self.sum,0.05,'unequal',len(self.T))[2])           
                        self.kut.append(kut.kuipertest2_tnc(np_sample, self.sum,len(self.T))[1])           
                        self.r2.append(r.calculate_cross_correlation(np_sample, self.sum)[0])                      
                        self.qr2.append(Qr.calculate_qq_plot(np_sample, self.sum,len(self.T))[2])
                        self.sim.append(sim.Similarity(np_sample,self.sum))
                        self.like.append(lk.Likeness(np_sample,self.sum))
                    print(str(j+1)+'次')
                    
                    idx_max1 = np.argmax(self.ks)
                    print(self.ratios[idx_max1])
                    print(max(self.ks))
                    self.ksmaxr.append(self.ratios[idx_max1])
                    self.ksmax.append(max(self.ks))

                    
                    
                    idx_max2 = np.argmax(self.kut)
                    print(self.ratios[idx_max2])
                    print(max(self.kut))
                    self.kutmaxr.append(self.ratios[idx_max2])
                    self.kutmax.append(max(self.kut))
                    
                    
                    idx_max3 = np.argmax(self.r2)
                    print(self.ratios[idx_max3])
                    print(max(self.r2))
                    self.r2maxr.append(self.ratios[idx_max3])
                    self.r2max.append(max(self.r2))
                    
                    idx_max4 = np.argmax(self.qr2)
                    print(self.ratios[idx_max4])
                    print(max(self.qr2))
                    self.qr2maxr.append(self.ratios[idx_max4])
                    self.qr2max.append(max(self.qr2))
                    
                    idx_max5 = np.argmax(self.sim)
                    print(self.ratios[idx_max5])
                    print(max(self.sim))
                    self.simmaxr.append(self.ratios[idx_max5])
                    self.simmax.append(max(self.sim))
                    
              
                    idx_max6 = np.argmax(self.like)
                    print(self.ratios[idx_max6])
                    print(max(self.like))
                    self.likemaxr.append(self.ratios[idx_max6])
                    self.likemax.append(max(self.like))  
                print('*'*100)        
                print('final')
                print(self.aaa)
                k1=np.argmax(self.ksmax)
                print(self.ksmaxr[k1])
                print(max(self.ksmax))   
                
                k2=np.argmax(self.kutmax)
                print(self.kutmaxr[k2])
                print(max(self.kutmax))  
                
                k3=np.argmax(self.r2max)
                print(self.r2maxr[k3])
                print(max(self.r2max))   
                
                k4=np.argmax(self.qr2max)
                print(self.qr2maxr[k4])
                print(max(self.qr2max))  
                
                k5=np.argmax(self.simmax)
                print(self.simmaxr[k5])
                print(max(self.simmax))   
                
                k6=np.argmax(self.likemax)
                print(self.likemaxr[k6])
                print(max(self.likemax))  
#            
#            
#            



#            

            
            ax1.set_xlabel("Zircon U-Pb age (Ma)")
            ax1.set_ylabel("KDE")
            for cc in range(len(all_sources)):
                ax1.plot([],[],color=self.generate_100_colors()[cc],label=self.headers[cc*2 + 2])
            ax1.legend()
                    # 关键：设置x轴间隔为100（每100ma一个刻度）
            ax1.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
            ax1.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
            ax1.set_xlim(min_age, max_age)
            ax1.set_ylim(bottom=0)
            
#            for a in range(self.pair_count):
#                ax2.plot(self.T, np.cumsum(self.np_source[a]), color=self.generate_100_colors()[a], label=self.headers[a*2 + 2])  
##        

            ax2.set_xlabel("Zircon U-Pb age (Ma)")
            ax2.set_ylabel("CDFs")
            for cc in range(len(all_sources)):
                ax2.plot([],[],color=self.generate_100_colors()[cc],label=self.headers[cc*2 + 2])
            ax2.legend()
            ax2.set_xlim(min_age, max_age)
            ax2.set_ylim(0,1)
            ax2.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
            ax2.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
            
            ax3.plot(self.T, np_sample, color='black', label=self.headers[0])


            self.sum1=0
            for i in range(len(self.ksmaxr[k1])):
                self.sum1+=self.ksmaxr[k1][i]/100*self.aaa[k1][i]
            ax3.plot(self.T, self.sum1, color=self.generate_100_colors()[0], label='K-S')
            self.sum2=0
            for i in range(len(self.kutmaxr[k2])):
                self.sum2+=self.kutmaxr[k2][i]/100*self.aaa[k2][i]
            ax3.plot(self.T, self.sum2, color=self.generate_100_colors()[1], label='Kuiper')
            self.sum3=0
            for i in range(len(self.r2maxr[k3])):
                self.sum3+=self.r2maxr[k3][i]/100*self.aaa[k3][i]
            ax3.plot(self.T, self.sum3, color=self.generate_100_colors()[2], label='Cross')
            self.sum4=0
            for i in range(len(self.qr2maxr[k4])):
                self.sum4+=self.qr2maxr[k4][i]/100*self.aaa[k4][i]
            ax3.plot(self.T, self.sum4, color=self.generate_100_colors()[3], label='Q-Q')
            self.sum5=0
            for i in range(len(self.simmaxr[k5])):
                self.sum5+=self.simmaxr[k5][i]/100*self.aaa[k5][i]
            ax3.plot(self.T, self.sum5, color=self.generate_100_colors()[4], label='Similarity')            
            self.sum6=0
            for i in range(len(self.likemaxr[k6])):
                self.sum6+=self.likemaxr[k6][i]/100*self.aaa[k6][i]
            ax3.plot(self.T, self.sum6, color=self.generate_100_colors()[5], label='Likeness')            
            ax3.set_xlabel("Zircon U-Pb age (Ma)")
            ax3.set_ylabel("KDE")
            ax3.legend()
                    # 关键：设置x轴间隔为100（每100ma一个刻度）
            ax3.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
            ax3.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
            ax3.set_xlim(min_age, max_age)
            ax3.set_ylim(bottom=0)
#            
#                       
            ax4.plot(self.T, np.cumsum(self.sum1), color=self.generate_100_colors()[0], label='K-S') 
            ax4.plot(self.T, np.cumsum(self.sum2), color=self.generate_100_colors()[1], label='Kuiper')
            ax4.plot(self.T, np.cumsum(self.sum3), color=self.generate_100_colors()[2], label='Cross')
            ax4.plot(self.T, np.cumsum(self.sum4), color=self.generate_100_colors()[3], label='Q-Q')
            ax4.plot(self.T, np.cumsum(self.sum5), color=self.generate_100_colors()[4], label='Similarity')
            ax4.plot(self.T, np.cumsum(self.sum6), color=self.generate_100_colors()[5], label='Likeness')

       
            ax4.set_xlabel("Zircon U-Pb age (Ma)")
            ax4.set_ylabel("CDFs")
            ax4.legend()
            ax4.set_xlim(min_age, max_age)
            ax4.set_ylim(0,1)
            ax4.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
            ax4.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
            
            
            
            
                
            self.canvas.figure.set_constrained_layout(True)
                       # 5. 关键优化：调整整个图形的边距和布局
                    #plt.subplots_adjust(left=0.08, right=0.95, top=0.92, bottom=0.2)  # 手动调整边距
            self.canvas.draw()
            model = QStandardItemModel(6, len(self.headers)//2)
        
            # 3. 设置列名（水平表头）
            for i in range ((len(self.headers)-2)//2):
                model.setHeaderData(i, Qt.Horizontal, self.headers[i*2 + 2])
            column_name = "Results"
            model.setHeaderData(len(self.headers)//2-1, Qt.Horizontal, column_name)
            
            # 4. 设置行名（垂直表头）
            row_names = ['K-S','Kupier','Cross','Q-Q','Simlarity','Likeness']
            for row, name in enumerate(row_names):
                model.setHeaderData(row, Qt.Vertical, name)
                
#            # 5. 填充数据
#            data_to_display=[self.ks,self.kut,self.r2,self.qr2,self.sim,self.like]
#                        print(self.ratios[idx_max1])
#            print(max(self.ks))
#                  
#            
            for i in range(len(self.ksmaxr[k1])):
                item = QStandardItem(str("{:.4f}".format(self.ksmaxr[k1][i]/100)))  
                model.setItem(0, i, item)
            item1 = QStandardItem(str("{:.4f}".format(max(self.ksmax)))) 
            model.setItem(0, len(self.ksmaxr[k1]), item1)
            
            for i in range(len(self.kutmaxr[k2])):
                item = QStandardItem(str("{:.4f}".format(self.kutmaxr[k2][i]/100)))  
                model.setItem(1, i, item)
            item2 = QStandardItem(str("{:.4f}".format(max(self.kutmax)))) 
            model.setItem(1, len(self.kutmaxr[k2]), item2)
            
            for i in range(len(self.r2maxr[k3])):
                item = QStandardItem(str("{:.4f}".format(self.r2maxr[k3][i]/100)))  
                model.setItem(2, i, item)
            item3 = QStandardItem(str("{:.4f}".format(max(self.r2max)))) 
            model.setItem(2, len(self.r2maxr[k3]), item3) 
#            
            for i in range(len(self.qr2maxr[k4])):
                item = QStandardItem(str("{:.4f}".format(self.qr2maxr[k4][i]/100)))  
                model.setItem(3, i, item)
            item4 = QStandardItem(str("{:.4f}".format(max(self.qr2max)))) 
            model.setItem(3, len(self.qr2maxr[k4]), item4) 
#            
            for i in range(len(self.simmaxr[k5])):
                item = QStandardItem(str("{:.4f}".format(self.simmaxr[k5][i]/100)))  
                model.setItem(4, i, item)
            item5 = QStandardItem(str("{:.4f}".format(max(self.simmax)))) 
            model.setItem(4, len(self.simmaxr[k5]), item5)         
#            
            for i in range(len(self.likemaxr[k6])):
                item = QStandardItem(str("{:.4f}".format(self.likemaxr[k6][i]/100)))  
                model.setItem(5, i, item)
            item6 = QStandardItem(str("{:.4f}".format(max(self.likemax)))) 
            model.setItem(5, len(self.likemaxr[k6]), item6)  
            
            self.tableView_2.setModel(model)
            
            # 自动调整列宽和行高
            self.tableView_2.resizeColumnsToContents()  # 自动调整所有列宽
            
            # 自动调整行高（基于内容）
            for row in range(model.rowCount()):
                self.tableView_2.resizeRowToContents(row)
            
            # 可选：设置最小行高（避免内容太少时行高太小）
            self.tableView_2.verticalHeader().setDefaultSectionSize(24)  # 设置默认行高
            
            # 可选：设置列宽弹性（允许用户拖动调整）
            self.tableView_2.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
    
    @pyqtSlot()
    def on_actionNew_triggered(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.model._data = [["" for _ in range(self.model.cols)] for _ in range(self.model.rows)]
        
        # 2. 重置表头（如果需要）
        self.model._horizontal_header = [f"{i+1}" for i in range(self.model.cols)]
        self.model._vertical_header = [f"{i+1}" for i in range(self.model.rows)]
        
        # 3. 通知视图数据已更改
        self.model.layoutChanged.emit()
        # 设置表格属性
        self.tableView.horizontalHeader().setDefaultSectionSize(100)
        self.tableView.verticalHeader().setDefaultSectionSize(30)
        
        # 4. 可选：显示提示信息
        #QMessageBox.information(self, "提示", "表格已新建")
        QMessageBox.information(self, "Notification", "A new table has been created")
    
    @pyqtSlot()
    def on_actionSave_as_triggered(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save as CSV File",
            "",  # Default path
            "CSV Files (*.csv);;All Files (*)"
        )
        
        # 如果用户取消保存，直接返回
        if not file_path:
            return
        
        # 确保文件以 .csv 结尾
        if not file_path.lower().endswith('.csv'):
            file_path += '.csv'
        
        try:
            # 2. 获取表头和数据
            headers = []
            for col in range(self.model.columnCount()):
                headers.append(str(self.model.headerData(col, Qt.Horizontal, Qt.DisplayRole)))
            
            data = []
            for row in range(self.model.rowCount()):
                row_data = []
                for col in range(self.model.columnCount()):
                    item = self.model.data(self.model.index(row, col), Qt.DisplayRole)
                    row_data.append(str(item) if item is not None else "")
                data.append(row_data)
            
            # 3. 写入 CSV 文件
            with open(file_path, 'w', encoding='utf-8') as file:
                # 写入表头
                file.write(','.join(headers) + '\n')
                # 写入数据
                for row in data:
                    file.write(','.join(row) + '\n')
            
            # 4. 提示保存成功
#            QMessageBox.information(
#                self,
#                "保存成功",
#                f"数据已成功保存到：\n{file_path}"
#            )
            QMessageBox.information(
                self,
                "Save Successful",
                f"Data successfully saved to:\n{file_path}"
            )
            
        except Exception as e:
#            QMessageBox.critical(
#                self,
#                "保存失败",
#                f"保存文件时出错：\n{str(e)}"
#            )
            QMessageBox.critical(
                self,
                "Import Failed",
                f"Error reading CSV file:\n{str(e)}"
            )
    
    @pyqtSlot()
    def on_actionexit_triggered(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.close()
    def closeEvent(self, event):
            """
            重写关闭事件，弹出确认对话框
            """
            # 创建确认对话框
#            reply = QMessageBox.question(
#                self,
#                "确认退出",
#                "确定要退出程序吗？",
#                QMessageBox.Yes | QMessageBox.No,
#                QMessageBox.No
#            )
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
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 设置全局样式，使界面更美观
    app.setStyle("Fusion")
    
    desktopsource = MainBigSource()
    desktopsource.show()
    sys.exit(app.exec_())