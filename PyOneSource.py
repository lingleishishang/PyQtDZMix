# -*- coding: utf-8 -*-

"""
Module implementing OneSource.
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
import math
import random
matplotlib.rcParams['font.sans-serif']=['SimHei']
from Ui_PyOneSource import Ui_MainWindow
class EditableHeaderDelegate1(QStyledItemDelegate):
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

class EmptyEditableTableModel1(QAbstractTableModel):
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

class OneSource(QMainWindow, Ui_MainWindow):
    """
    Class documentation goes here.
    """
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super(OneSource, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("One Source")
        screen = QApplication.primaryScreen().availableGeometry()
        width = int(screen.width() * 2 / 3)
        height = int(screen.height() * 2 / 3)
        
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
        self.label_3.setGeometry(width/25,height/10,width/1,height/8)
        self.lineEdit_4.setGeometry(width*4/25,height/10+height/30,width/16,height/20)
        self.label_4.setGeometry(width/25,height/6,width/8,height/8)
        self.lineEdit_5.setGeometry(width*4/25,height/10+height/10,width/16,height/20)
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
        self.model = EmptyEditableTableModel1(rows=3000, cols=4)
        self.tableView.setModel(self.model)
        
        # 设置表头可编辑
        self.header_delegate = EditableHeaderDelegate1(self.tableView)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.tableView.horizontalHeader().setSectionsClickable(True)
        self.tableView.horizontalHeader().sectionDoubleClicked.connect(self.edit_header)
        
        # 设置表格属性
        self.tableView.horizontalHeader().setDefaultSectionSize(60)
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
        self.cdf_value_sample=np.cumsum(self.np_sample)
    
    def calculate_distributions(self):
        """Calculate normal distributions for sources and sample"""
        for m in range(self.pair_count):
            for n in range(len(self.source[m])):
                self.np_source[m] = self.np_source[m] + st.norm.pdf(self.T, self.source[m][n], 2*self.se[m][n])
        
        for i in range(len(self.sample)):
            self.np_sample = self.np_sample + st.norm.pdf(self.T, self.sample[i], 2*self.sample_err[i])
    @pyqtSlot()
    def on_pushButton_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        
                # 检查表格是否为空
        
        empty_cells_in_gaps = {}  # 存储不连续的空单元格 {列索引: [(空单元格行索引, 前一个非空行索引)]}
        non_numeric_cells = []    # 存储非数字单元格位置
        column_pairs_mismatch = [] # 存储数字个数不一致的列对
        is_all_empty = True       # 标记表格是否全部为空
        
        # 定义需要检查的列对 (列索引从0开始)
        column_pairs = [(0, 1), (2, 3)]
        
        # 检查每列数据
        for col in range(self.model.columnCount()):
            prev_non_empty_row = None  # 记录前一个非空行的行索引
            #gaps_in_column = []        # 记录当前列的空单元格间隙
            #has_data_in_column = False # 标记当前列是否有数据
            
            for row in range(self.model.rowCount()):
                value = self.model.data(self.model.index(row, col), Qt.DisplayRole)
                str_value = str(value).strip() if value else ""
                
                # 检查单元格是否为空
                if not str_value:
                    continue  # 空单元格，跳过检查
                    
                # 如果执行到这里，说明表格不是全部为空
                is_all_empty = False
                #has_data_in_column = True
                
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
                    #column_pairs_mismatch.append(f"第{col1+1}列和第{col2+1}列")
                    column_pairs_mismatch.append(f"Column {col1+1} and Column {col2+1}")
                    break  # 每对列只需要报告一次
        
        # 准备消息
        message_parts = []
        
        if is_all_empty:
            #QMessageBox.information(self, "检查结果", "表格为空值")
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
            #message_parts.append("所有单元格数据都是数字格式")
            message_parts.append("✓ Numeric format: All cells validated")
            self.pushButton_2.setEnabled(True)
            self.pushButton_3.setEnabled(True)
            self.pushButton_4.setEnabled(True)
            self.pushButton_5.setEnabled(True)
#            self.actionSave_as.setEnabled(True)  # 空表格时禁用
        
        if column_pairs_mismatch:
            message_parts.append(
                #"以下列对的数字个数不一致:\n" + "\n".join(column_pairs_mismatch)
                "Column pairs with mismatched number counts:\n" + "\n".join(column_pairs_mismatch)
            )
        else:
            #message_parts.append("所有列对的数字个数一致")
            message_parts.append("All column pairs have matching number counts")
        
        # 显示消息框
        QMessageBox.information(self, "Check Results", "\n\n".join(message_parts))
    
    @pyqtSlot()
    def on_radioButton_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.lineEdit_4.setEnabled(True)
        self.lineEdit_5.setEnabled(True)
    
    @pyqtSlot()
    def on_radioButton_2_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.lineEdit_4.setEnabled(False)
        self.lineEdit_5.setEnabled(False)
    
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

#        self.headers = []  # 存储非空列的表头
#        self.data = []     # 存储非空列的数据（按列组织）
#        self.model = QStandardItemModel()
#        self.tableView_2.setModel(self.model)
#
#        self.model.clear()  # 先清空数据
#        self.model.setColumnCount(0)  # 清除列结构
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
        self.sample=self.data[0]
        self.source=self.data[2]
#        print(self.sample)
#        print(self.source)
        if self.radioButton_2.isChecked() and self.radioButton_3.isChecked():
            self.process_data(min_age, max_age, dT_value)
            self.ks=ks.kstest2b_tnc(self.np_sample, self.np_source,0.05,'unequal',len(self.T))[2]
            
            self.kut =kut.kuipertest2_tnc(self.np_sample, self.np_source,len(self.T))[1]
            
            self.r2=r.calculate_cross_correlation(self.np_sample, self.np_source)[0]
            self.slopr2=r.calculate_cross_correlation(self.np_sample, self.np_source)[1]
            self.interceptr2=r.calculate_cross_correlation(self.np_sample, self.np_source)[2]
            
            self.q1=Qr.calculate_qq_plot(self.np_sample, self.np_source,len(self.T))[0]
            self.q2=Qr.calculate_qq_plot(self.np_sample, self.np_source,len(self.T))[1]
            self.qr2=Qr.calculate_qq_plot(self.np_sample, self.np_source,len(self.T))[2]
            self.qslop=Qr.calculate_qq_plot(self.np_sample, self.np_source,len(self.T))[3]
            self.qinterceptr=Qr.calculate_qq_plot(self.np_sample, self.np_source,len(self.T))[4]     
            
            self.sim=sim.Similarity(self.np_sample,self.np_source)
            
            self.like=lk.Likeness(self.np_sample,self.np_source)
            
          
                
            self.canvas.figure.clear()
            # Create a 2-row, 1-column outer grid (each row will have its own subgrid)
            outer_grid = gridspec.GridSpec(2, 1, height_ratios=[1, 1], hspace=0.3)
            
            # First row: 1x2 grid with width_ratios=[3, 1] (or [2, 1] if you prefer 2:1)
            first_row = gridspec.GridSpecFromSubplotSpec(1, 2, subplot_spec=outer_grid[0], width_ratios=[3, 1], wspace=0.3)
            ax1 = self.canvas.figure.add_subplot(first_row[0])  # First row, first column (width=3)
            ax2 = self.canvas.figure.add_subplot(first_row[1])  # First row, second column (width=1)
            
            # Second row: 1x2 grid with width_ratios=[1, 1] (or [2, 2])
            second_row = gridspec.GridSpecFromSubplotSpec(1, 2, subplot_spec=outer_grid[1], width_ratios=[1, 1], wspace=0.3)
            ax3 = self.canvas.figure.add_subplot(second_row[0])  # Second row, first column (width=1)
            ax4 = self.canvas.figure.add_subplot(second_row[1])  # Second row, second column (width=1)
            # 创建1行2列的网格，宽度比例为2:1
            
            for a in range(self.pair_count):
                ax1.plot(self.T, self.np_source[a], color=self.color[a], label=self.headers[a*2 + 2])  
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
                
            # 第二个子图（占据1/3宽度）
            
            for a in range(self.pair_count):
                ax2.plot(self.T, self.cdf_value[a], color=self.color[a], label=self.headers[a*2 + 2])  
#        
            ax2.plot(self.T, self.cdf_value_sample, color='black', label=self.headers[0])
            ax2.set_xlabel("Zircon U-Pb age (Ma)")
            ax2.set_ylabel("CDFs")
            ax2.legend()
            ax2.set_xlim(min_age, max_age)
            ax2.set_ylim(0,1)
            ax2.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
            ax2.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度

            ax3.scatter(self.np_sample, self.np_source, s=30, color='blue', alpha=0.6, marker='d')
            # 添加拟合线
            x_range = np.linspace(0, 1, 100)
            ax3.plot(x_range, self.slopr2 * x_range + self.interceptr2, 
                     'k--', linewidth=2, alpha=0.7, label='拟合线')
            ax3.set_xlabel(self.headers[0], fontsize=12)
            ax3.set_ylabel('Optional model', fontsize=12)
            #ax3.set_aspect("equal") 
            ax3.set_xlim(0,max(np.max(self.np_sample), np.max(self.np_source)))
            ax3.set_ylim(0,max(np.max(self.np_sample), np.max(self.np_source)))
            ax3.set_aspect("equal")  # 关键参数
            #ax3.grid(alpha=0.3)
            ax3.text(np.max(self.np_sample)/2, 4*max(np.max(self.np_sample), np.max(self.np_source))/5, f'R^2 = {self.r2:.2f}', fontsize=12,
                     bbox=dict(facecolor='white', alpha=0.8))
            

            ax4.scatter(self.q1, self.q2, s=30, color='green', alpha=0.6, marker='d')
            # 添加拟合线
            min_val = min(np.array(self.q1).min(), np.array(self.q2).min())
            max_val = max(np.array(self.q1).max(), np.array(self.q2).max())
            ax4.plot([min_val, max_val], [min_val, max_val], 
                            'k--', linewidth=2, alpha=0.7)
            ax4.set_xlabel(self.headers[0], fontsize=12)
            ax4.set_ylabel(self.headers[2], fontsize=12)
            ax4.set_xlim(min_val, max_val)
            ax4.set_ylim(min_val, max_val)
            ax4.set_aspect("equal")  # 关键参数
            ax4.text(max_val/2, 0.9*max_val, f'R^2 = {self.qr2:.2f}', fontsize=12,
                            bbox=dict(facecolor='white', alpha=0.8))
            # 调整子图间距
            self.canvas.figure.set_constrained_layout(True)
            # 5. 关键优化：调整整个图形的边距和布局
            #plt.subplots_adjust(left=0.08, right=0.95, top=0.92, bottom=0.2)  # 手动调整边距
            self.canvas.draw()
            
            model = QStandardItemModel(6, 1)
        
            # 3. 设置列名（水平表头）
            column_name = "Results"
            model.setHeaderData(0, Qt.Horizontal, column_name)
            
            # 4. 设置行名（垂直表头）
            row_names = ['K-S','Kupier','Cross','Q-Q','Simlarity','Likeness']
            for row, name in enumerate(row_names):
                model.setHeaderData(row, Qt.Vertical, name)
                
            # 5. 填充数据
            data_to_display=[self.ks,self.kut,self.r2,self.qr2,self.sim,self.like]
                  
            


            for row, value in enumerate(data_to_display):
                #item = QStandardItem(str("{:.4f}".format(value)))
                item = QStandardItem(str(value))
                model.setItem(row, 0, item)
            self.tableView_2.setModel(model)
            # 7. 自动调整列宽和行高
            self.tableView_2.resizeColumnToContents(0)
            for row in range(model.rowCount()):
                self.tableView_2.resizeRowToContents(row)
        if self.radioButton_2.isChecked() and self.radioButton_4.isChecked():
            self.lineEdit_3.setEnabled(True)
            self.process_data_kde(min_age, max_age, dT_value,int(self.lineEdit_3.text()))
            self.ks=ks.kstest2b_tnc(self.np_sample, self.np_source,0.05,'unequal',len(self.T))[2]
            
            self.kut =kut.kuipertest2_tnc(self.np_sample, self.np_source,len(self.T))[1]
            
            self.r2=r.calculate_cross_correlation(self.np_sample, self.np_source)[0]
            self.slopr2=r.calculate_cross_correlation(self.np_sample, self.np_source)[1]
            self.interceptr2=r.calculate_cross_correlation(self.np_sample, self.np_source)[2]
            
            self.q1=Qr.calculate_qq_plot(self.np_sample, self.np_source,len(self.T))[0]
            self.q2=Qr.calculate_qq_plot(self.np_sample, self.np_source,len(self.T))[1]
            self.qr2=Qr.calculate_qq_plot(self.np_sample, self.np_source,len(self.T))[2]
            self.qslop=Qr.calculate_qq_plot(self.np_sample, self.np_source,len(self.T))[3]
            self.qinterceptr=Qr.calculate_qq_plot(self.np_sample, self.np_source,len(self.T))[4]     
            
            self.sim=sim.Similarity(self.np_sample,self.np_source)
            
            self.like=lk.Likeness(self.np_sample,self.np_source)
            
          
                
            self.canvas.figure.clear()
            # Create a 2-row, 1-column outer grid (each row will have its own subgrid)
            outer_grid = gridspec.GridSpec(2, 1, height_ratios=[1, 1], hspace=0.3)
            
            # First row: 1x2 grid with width_ratios=[3, 1] (or [2, 1] if you prefer 2:1)
            first_row = gridspec.GridSpecFromSubplotSpec(1, 2, subplot_spec=outer_grid[0], width_ratios=[3, 1], wspace=0.3)
            ax1 = self.canvas.figure.add_subplot(first_row[0])  # First row, first column (width=3)
            ax2 = self.canvas.figure.add_subplot(first_row[1])  # First row, second column (width=1)
            
            # Second row: 1x2 grid with width_ratios=[1, 1] (or [2, 2])
            second_row = gridspec.GridSpecFromSubplotSpec(1, 2, subplot_spec=outer_grid[1], width_ratios=[1, 1], wspace=0.3)
            ax3 = self.canvas.figure.add_subplot(second_row[0])  # Second row, first column (width=1)
            ax4 = self.canvas.figure.add_subplot(second_row[1])  # Second row, second column (width=1)
            # 创建1行2列的网格，宽度比例为2:1
            
            for a in range(self.pair_count):
                ax1.plot(self.T, self.np_source[a], color=self.color[a], label=self.headers[a*2 + 2])  
#        
            ax1.plot(self.T, self.np_sample, color='black', label=self.headers[0])
            ax1.set_xlabel("Zircon U-Pb age (Ma)")
            ax1.set_ylabel("KDE")
            ax1.legend()
                    # 关键：设置x轴间隔为100（每100ma一个刻度）
            ax1.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
            ax1.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度
            ax1.set_xlim(min_age, max_age)
            ax1.set_ylim(bottom=0)
                
            # 第二个子图（占据1/3宽度）
            
            for a in range(self.pair_count):
                ax2.plot(self.T, np.cumsum(self.np_source[a]), color=self.color[a], label=self.headers[a*2 + 2])  
#        
            ax2.plot(self.T, np.cumsum(self.np_sample), color='black', label=self.headers[0])
            ax2.set_xlabel("Zircon U-Pb age (Ma)")
            ax2.set_ylabel("CDFs")
            ax2.legend()
            ax2.set_xlim(min_age, max_age)
            ax2.set_ylim(0,1)
            ax2.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
            ax2.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度

            ax3.scatter(self.np_sample, self.np_source, s=30, color='blue', alpha=0.6, marker='d')
            # 添加拟合线
            x_range = np.linspace(0, 1, 100)
            ax3.plot(x_range, self.slopr2 * x_range + self.interceptr2, 
                     'k--', linewidth=2, alpha=0.7, label='拟合线')
            ax3.set_xlabel(self.headers[0], fontsize=12)
            ax3.set_ylabel('Optional model', fontsize=12)
            #ax3.set_aspect("equal") 
            ax3.set_xlim(0,max(np.max(self.np_sample), np.max(self.np_source)))
            ax3.set_ylim(0,max(np.max(self.np_sample), np.max(self.np_source)))
            ax3.set_aspect("equal")  # 关键参数
            #ax3.grid(alpha=0.3)
            ax3.text(np.max(self.np_sample)/2, 4*max(np.max(self.np_sample), np.max(self.np_source))/5, f'R^2 = {self.r2:.2f}', fontsize=12,
                     bbox=dict(facecolor='white', alpha=0.8))
            

            ax4.scatter(self.q1, self.q2, s=30, color='green', alpha=0.6, marker='d')
            # 添加拟合线
            min_val = min(np.array(self.q1).min(), np.array(self.q2).min())
            max_val = max(np.array(self.q1).max(), np.array(self.q2).max())
            ax4.plot([min_val, max_val], [min_val, max_val], 
                            'k--', linewidth=2, alpha=0.7)
            ax4.set_xlabel(self.headers[0], fontsize=12)
            ax4.set_ylabel(self.headers[2], fontsize=12)
            ax4.set_xlim(min_val, max_val)
            ax4.set_ylim(min_val, max_val)
            ax4.set_aspect("equal")  # 关键参数
            ax4.text(max_val/2, 0.9*max_val, f'R^2 = {self.qr2:.2f}', fontsize=12,
                            bbox=dict(facecolor='white', alpha=0.8))
            # 调整子图间距
            self.canvas.figure.set_constrained_layout(True)
            # 5. 关键优化：调整整个图形的边距和布局
            #plt.subplots_adjust(left=0.08, right=0.95, top=0.92, bottom=0.2)  # 手动调整边距
            self.canvas.draw()
            
            model = QStandardItemModel(6, 1)
        
            # 3. 设置列名（水平表头）
            column_name = "Results"
            model.setHeaderData(0, Qt.Horizontal, column_name)
            
            # 4. 设置行名（垂直表头）
            row_names = ['K-S','Kupier','Cross','Q-Q','Simlarity','Likeness']
            for row, name in enumerate(row_names):
                model.setHeaderData(row, Qt.Vertical, name)
                
            # 5. 填充数据
            data_to_display=[self.ks,self.kut,self.r2,self.qr2,self.sim,self.like]
                  
            


            for row, value in enumerate(data_to_display):
                #item = QStandardItem(str("{:.4f}".format(value)))
                item = QStandardItem(str(value))
                model.setItem(row, 0, item)
            self.tableView_2.setModel(model)
            # 7. 自动调整列宽和行高
            self.tableView_2.resizeColumnToContents(0)
            for row in range(model.rowCount()):
                self.tableView_2.resizeRowToContents(row)

        if self.radioButton_3.isChecked() and self.radioButton.isChecked():
            self.lineEdit_4.setEnabled(True)
            self.lineEdit_5.setEnabled(True)
            self.dd=self.data[2:]
            #print(self.dd)
            min_length = min(len(lst) for lst in self.dd)
           

            if min_length < int(self.lineEdit_4.text()):
                # 弹出警告框，但继续执行（不报错）
                QMessageBox.warning(
                    self,  # 父窗口（通常是 self）
                    "抽样数量不足",
                    f"最短子列表只有 {min_length} 个元素，无法抽取 {int(self.lineEdit_4.text())} 个。"
                )
            else:

                all_sources = []
                all_samples = []
                for i in range(len(self.T)):
                    self.T[i] = min_age + i * dT_value
                
                # 循环4次（或根据lineEdit_5的值）
                for j in range(int(self.lineEdit_5.text())):  # 或者 range(int(self.lineEdit_5.text()))
                    # 抽样数据
                    min_length = min(len(lst) for lst in self.dd)
                    sampled_indices = random.sample(range(min_length), int(self.lineEdit_4.text()))
                    self.sampled_data = [
                        [lst[i] for i in sampled_indices]
                        for lst in self.dd
                    ]
                    
                    # 准备数据
                    self.ss = self.sampled_data[0]  # 源数据年龄
                    self.rr = self.sampled_data[1]  # 源数据误差
                    
                    # 初始化数组
                    np_source = np.zeros(len(self.T))
                    np_sample = np.zeros(len(self.T))
                    
                    # 计算概率密度
                    for n in range(len(self.ss)):
                        np_source += st.norm.pdf(self.T, self.ss[n], 2*self.rr[n])
                    
                    for a in range(len(self.data[0])):
                        np_sample += st.norm.pdf(self.T, self.data[0][a], 2*self.data[1][a])
                    
                    # 归一化
                    np_source /= len(self.ss)
                    np_sample /= len(self.data[0])
                    
                    # 存储结果
                    all_sources.append(np_source)
                    all_samples.append(np_sample)
                self.ks= []
                self.kut= []
                self.r2= []
                self.qr2= []
                self.sim= []
                self.like= []
     
                    
                for i in range(len(all_sources)):
                    self.ks.append(ks.kstest2b_tnc(all_samples[-1], all_sources[i],0.05,'unequal',len(self.T))[2])
                    
                    self.kut.append(kut.kuipertest2_tnc(all_samples[-1], all_sources[i],len(self.T))[1])
                    
                    self.r2.append(r.calculate_cross_correlation(all_samples[-1], all_sources[i])[0])
#                    self.slopr2=r.calculate_cross_correlation(all_samples[-1], all_sources[i])[1]
#                    self.interceptr2=r.calculate_cross_correlation(all_samples[-1], all_sources[i])[2]
#                    
#                    self.q1=Qr.calculate_qq_plot(all_samples[-1], all_sources[i],len(self.T))[0]
#                    self.q2=Qr.calculate_qq_plot(all_samples[-1], all_sources[i],len(self.T))[1]
                    self.qr2.append(Qr.calculate_qq_plot(all_samples[-1], all_sources[i],len(self.T))[2])
#                    self.qslop=Qr.calculate_qq_plot(all_samples[-1], all_sources[i],len(self.T))[3]
#                    self.qinterceptr=Qr.calculate_qq_plot(all_samples[-1], all_sources[i],len(self.T))[4]     
                    
                    self.sim.append(sim.Similarity(all_samples[-1], all_sources[i]))
                    
                    self.like.append(lk.Likeness(all_samples[-1], all_sources[i]))                    
                
                # 绘图
                self.canvas.figure.clear()
                
                # 创建画布布局
                outer_grid = gridspec.GridSpec(1, 2, width_ratios=[2, 1], wspace=0.3)
                

                ax1 = self.canvas.figure.add_subplot(outer_grid[0])
                ax2 = self.canvas.figure.add_subplot(outer_grid[1])
                
                # 绘制所有源曲线
                for j, src in enumerate(all_sources):
                    print(src)
                    ax1.plot(self.T, src, color='red')
                    
                    ax2.plot(self.T, np.cumsum(src), color='red')
                
                # 绘制样本曲线（取最后一次）
                ax1.plot([], [], color='red', label='Resample Source')  # 空曲线用于图例
                ax1.plot(self.T, all_samples[-1], color='black', label=self.headers[0])
                
                # 设置图表属性
                ax1.set_xlabel("Zircon U-Pb age (Ma)")
                ax1.set_ylabel("PDF")
                ax1.legend()
                ax1.xaxis.set_major_locator(ticker.MultipleLocator(500))
                ax1.xaxis.set_minor_locator(ticker.MultipleLocator(100))
                ax1.set_xlim(min_age, max_age)
                ax1.set_ylim(bottom=0)
                    
#                # 第二个子图（占据1/3宽度）
#                

    #        
                ax2.plot(self.T, np.cumsum(all_samples[-1]), color='black', label=self.headers[0])
                ax2.plot([], [], color='red', label='Resample Source')  # 空曲线用于图例
                ax2.set_xlabel("Zircon U-Pb age (Ma)")
                ax2.set_ylabel("CDFs")
                ax2.legend()
                ax2.set_xlim(min_age, max_age)
                ax2.set_ylim(0,1)
                ax2.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
                ax2.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度

                
                model = QStandardItemModel(6, 2)
            
                # 3. 设置列名（水平表头）
                column_name1 = "Results"
                column_name2 = "Std_dev"
                model.setHeaderData(0, Qt.Horizontal, column_name1)
                model.setHeaderData(1, Qt.Horizontal, column_name2)
                
                # 4. 设置行名（垂直表头）
                row_names = ['K-S','Kupier','Cross','Q-Q','Simlarity','Likeness']
                for row, name in enumerate(row_names):
                    model.setHeaderData(row, Qt.Vertical, name)
                
                self.ksmean=sum(self.ks) / len(self.ks)
                self.ksstd_dev = math.sqrt(sum((x - self.ksmean) ** 2 for x in self.ks) / len(self.ks))  # 总体标准差
                self.kutmean=sum(self.kut) / len(self.kut)
                self.kutstd_dev = math.sqrt(sum((x - self.kutmean) ** 2 for x in self.kut) / len(self.kut))  # 总体标准差
                self.r2mean=sum(self.r2) / len(self.r2)
                self.r2std_dev = math.sqrt(sum((x - self.r2mean) ** 2 for x in self.r2) / len(self.r2))  # 总体标准差
                self.qr2mean=sum(self.qr2) / len(self.qr2)
                self.qr2std_dev = math.sqrt(sum((x - self.qr2mean) ** 2 for x in self.qr2) / len(self.qr2))  # 总体标准差
                self.simmean=sum(self.sim) / len(self.sim)
                self.simstd_dev = math.sqrt(sum((x - self.simmean) ** 2 for x in self.sim) / len(self.sim))  # 总体标准差
                self.likemean=sum(self.like) / len(self.like)
                self.likestd_dev = math.sqrt(sum((x - self.likemean) ** 2 for x in self.like) / len(self.like))  # 总体标准差
                    
                # 5. 填充数据
                data_to_display=[self.ksmean,self.kutmean,self.r2mean,self.qr2mean,self.simmean,self.likemean]
                data_to_display1=[self.ksstd_dev,self.kutstd_dev,self.r2std_dev,self.qr2std_dev,self.simstd_dev,self.likestd_dev]
                      
                
    
    
                for row, value in enumerate(data_to_display):
                    #item = QStandardItem(str("{:.4f}".format(value)))
                    item = QStandardItem(str("{:.4f}".format(value)))
                    model.setItem(row, 0, item)
                for row, value in enumerate(data_to_display1):
                    #item = QStandardItem(str("{:.4f}".format(value)))
                    item = QStandardItem(str("{:.4f}".format(value)))
                    model.setItem(row, 1, item)
                self.tableView_2.setModel(model)
                # 7. 自动调整列宽和行高
                self.tableView_2.resizeColumnToContents(0)
                for row in range(model.rowCount()):
                    self.tableView_2.resizeRowToContents(row)
        if self.radioButton_4.isChecked() and self.radioButton.isChecked():
            self.lineEdit_4.setEnabled(True)
            self.lineEdit_5.setEnabled(True)
            self.dd=self.data[2:]
            #print(self.dd)
            min_length = min(len(lst) for lst in self.dd)
           

            if min_length < int(self.lineEdit_4.text()):
                # 弹出警告框，但继续执行（不报错）
                QMessageBox.warning(
                    self,  # 父窗口（通常是 self）
                    "抽样数量不足",
                    f"最短子列表只有 {min_length} 个元素，无法抽取 {int(self.lineEdit_4.text())} 个。"
                )
            else:

                all_sources = []
                all_samples = []
                for i in range(len(self.T)):
                    self.T[i] = min_age + i * dT_value
                
                # 循环4次（或根据lineEdit_5的值）
                for j in range(int(self.lineEdit_5.text())):  # 或者 range(int(self.lineEdit_5.text()))
                    # 抽样数据
                    min_length = min(len(lst) for lst in self.dd)
                    sampled_indices = random.sample(range(min_length), int(self.lineEdit_4.text()))
                    self.sampled_data = [
                        [lst[i] for i in sampled_indices]
                        for lst in self.dd
                    ]
                    
                    # 准备数据
                    self.ss = self.sampled_data[0]  # 源数据年龄
                    #self.rr = self.sampled_data[1]  # 源数据误差
                    np_source = self.kde_pdf(self.ss, self.T, bandwidth=int(self.lineEdit_3.text()))
                    np_sample = self.kde_pdf(self.data[0], self.T, bandwidth=int(self.lineEdit_3.text()))
                    

                    
                    # 存储结果
                    all_sources.append(np_source)
                    all_samples.append(np_sample)
                self.ks= []
                self.kut= []
                self.r2= []
                self.qr2= []
                self.sim= []
                self.like= []
     
                    
                for i in range(len(all_sources)):
                    self.ks.append(ks.kstest2b_tnc(all_samples[-1], all_sources[i],0.05,'unequal',len(self.T))[2])
                    
                    self.kut.append(kut.kuipertest2_tnc(all_samples[-1], all_sources[i],len(self.T))[1])
                    
                    self.r2.append(r.calculate_cross_correlation(all_samples[-1], all_sources[i])[0])
#                    self.slopr2=r.calculate_cross_correlation(all_samples[-1], all_sources[i])[1]
#                    self.interceptr2=r.calculate_cross_correlation(all_samples[-1], all_sources[i])[2]
#                    
#                    self.q1=Qr.calculate_qq_plot(all_samples[-1], all_sources[i],len(self.T))[0]
#                    self.q2=Qr.calculate_qq_plot(all_samples[-1], all_sources[i],len(self.T))[1]
                    self.qr2.append(Qr.calculate_qq_plot(all_samples[-1], all_sources[i],len(self.T))[2])
#                    self.qslop=Qr.calculate_qq_plot(all_samples[-1], all_sources[i],len(self.T))[3]
#                    self.qinterceptr=Qr.calculate_qq_plot(all_samples[-1], all_sources[i],len(self.T))[4]     
                    
                    self.sim.append(sim.Similarity(all_samples[-1], all_sources[i]))
                    
                    self.like.append(lk.Likeness(all_samples[-1], all_sources[i]))                    
                
                # 绘图
                self.canvas.figure.clear()
                
                # 创建画布布局
                outer_grid = gridspec.GridSpec(1, 2, width_ratios=[2, 1], wspace=0.3)
                

                ax1 = self.canvas.figure.add_subplot(outer_grid[0])
                ax2 = self.canvas.figure.add_subplot(outer_grid[1])
                
                # 绘制所有源曲线
                for j, src in enumerate(all_sources):
                    print(src)
                    ax1.plot(self.T, src, color='red')
                    
                    ax2.plot(self.T, np.cumsum(src), color='red')
                
                # 绘制样本曲线（取最后一次）
                ax1.plot([], [], color='red', label='Resample Source')  # 空曲线用于图例
                ax1.plot(self.T, all_samples[-1], color='black', label=self.headers[0])
                
                # 设置图表属性
                ax1.set_xlabel("Zircon U-Pb age (Ma)")
                ax1.set_ylabel("KDE")
                ax1.legend()
                ax1.xaxis.set_major_locator(ticker.MultipleLocator(500))
                ax1.xaxis.set_minor_locator(ticker.MultipleLocator(100))
                ax1.set_xlim(min_age, max_age)
                ax1.set_ylim(bottom=0)
                    
#                # 第二个子图（占据1/3宽度）
#                

    #        
                ax2.plot(self.T, np.cumsum(all_samples[-1]), color='black', label=self.headers[0])
                ax2.plot([], [], color='red', label='Resample Source')  # 空曲线用于图例
                ax2.set_xlabel("Zircon U-Pb age (Ma)")
                ax2.set_ylabel("CDFs")
                ax2.legend()
                ax2.set_xlim(min_age, max_age)
                ax2.set_ylim(0,1)
                ax2.xaxis.set_major_locator(ticker.MultipleLocator(500))  # 主刻度间隔100
                ax2.xaxis.set_minor_locator(ticker.MultipleLocator(100))   # 可选：添加50的次刻度

                
                model = QStandardItemModel(6, 2)
            
                # 3. 设置列名（水平表头）
                column_name1 = "Results"
                column_name2 = "Std_dev"
                model.setHeaderData(0, Qt.Horizontal, column_name1)
                model.setHeaderData(1, Qt.Horizontal, column_name2)
                
                # 4. 设置行名（垂直表头）
                row_names = ['K-S','Kupier','Cross','Q-Q','Simlarity','Likeness']
                for row, name in enumerate(row_names):
                    model.setHeaderData(row, Qt.Vertical, name)
                
                self.ksmean=sum(self.ks) / len(self.ks)
                self.ksstd_dev = math.sqrt(sum((x - self.ksmean) ** 2 for x in self.ks) / len(self.ks))  # 总体标准差
                self.kutmean=sum(self.kut) / len(self.kut)
                self.kutstd_dev = math.sqrt(sum((x - self.kutmean) ** 2 for x in self.kut) / len(self.kut))  # 总体标准差
                self.r2mean=sum(self.r2) / len(self.r2)
                self.r2std_dev = math.sqrt(sum((x - self.r2mean) ** 2 for x in self.r2) / len(self.r2))  # 总体标准差
                self.qr2mean=sum(self.qr2) / len(self.qr2)
                self.qr2std_dev = math.sqrt(sum((x - self.qr2mean) ** 2 for x in self.qr2) / len(self.qr2))  # 总体标准差
                self.simmean=sum(self.sim) / len(self.sim)
                self.simstd_dev = math.sqrt(sum((x - self.simmean) ** 2 for x in self.sim) / len(self.sim))  # 总体标准差
                self.likemean=sum(self.like) / len(self.like)
                self.likestd_dev = math.sqrt(sum((x - self.likemean) ** 2 for x in self.like) / len(self.like))  # 总体标准差
                    
                # 5. 填充数据
                data_to_display=[self.ksmean,self.kutmean,self.r2mean,self.qr2mean,self.simmean,self.likemean]
                data_to_display1=[self.ksstd_dev,self.kutstd_dev,self.r2std_dev,self.qr2std_dev,self.simstd_dev,self.likestd_dev]
                      
                
    
    
                for row, value in enumerate(data_to_display):
                    #item = QStandardItem(str("{:.4f}".format(value)))
                    item = QStandardItem(str("{:.4f}".format(value)))
                    model.setItem(row, 0, item)
                for row, value in enumerate(data_to_display1):
                    #item = QStandardItem(str("{:.4f}".format(value)))
                    item = QStandardItem(str("{:.4f}".format(value)))
                    model.setItem(row, 1, item)
                self.tableView_2.setModel(model)
                # 7. 自动调整列宽和行高
                self.tableView_2.resizeColumnToContents(0)
                for row in range(model.rowCount()):
                    self.tableView_2.resizeRowToContents(row)
                    
                    
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
    def on_actionNew_triggered(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
                # 1. 重置数据模型
        self.model._data = [["" for _ in range(self.model.cols)] for _ in range(self.model.rows)]
        
        # 2. 重置表头（如果需要）
        self.model._horizontal_header = [f"{i+1}" for i in range(self.model.cols)]
        self.model._vertical_header = [f"{i+1}" for i in range(self.model.rows)]
        
        # 3. 通知视图数据已更改
        self.model.layoutChanged.emit()
        # 设置表格属性
        self.tableView.horizontalHeader().setDefaultSectionSize(60)
        self.tableView.verticalHeader().setDefaultSectionSize(30)
        
        # 4. 可选：显示提示信息
        #QMessageBox.information(self, "提示", "表格已新建")
        QMessageBox.information(self, "Notification", "A new table has been created")
    
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
            if num_columns > 4:
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
    def on_actionSave_as_triggered(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
                # 1. 弹出文件保存对话框
#        file_path, _ = QFileDialog.getSaveFileName(
#            self,
#            "保存为 CSV 文件",
#            "",  # 默认路径
#            "CSV 文件 (*.csv);;所有文件 (*)"
#        )
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
    def on_actionExit_triggered(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        # 直接调用 close()，closeEvent 会自动处理确认逻辑
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
    
    desktopsource = OneSource()
    desktopsource.show()
    sys.exit(app.exec_())
