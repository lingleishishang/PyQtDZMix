# -*- coding: utf-8 -*-

"""
Module implementing MainWindow.
"""
import sys
from PyQt5 import QtCore
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtWidgets import (QApplication,  QFileDialog,QMessageBox,QMainWindow, QHeaderView, 
                            QLineEdit, QStyledItemDelegate)
from PyQt5.QtCore import QAbstractTableModel,Qt, QVariant, pyqtSlot

from Ui_PyDZmain import Ui_MainWindow
from PyOriginalData import PyOriData

from PySubData import PyMainSub
class EditableHeaderDelegate(QStyledItemDelegate):
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

class EmptyEditableTableModel(QAbstractTableModel):
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


class MainWindow(QMainWindow, Ui_MainWindow):
    """
    Class documentation goes here.
    """
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Two to four sources") 
        
        # 获取屏幕尺寸并计算2/3大小
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
        
        # 设置窗口不可改变大小
        self.setFixedSize(width, height)
        self.tableView.setGeometry(QtCore.QRect(0, 0, width*4/5, height*95/100))
        self.pushButton.setGeometry(QtCore.QRect(width*5/6, height*2/10, 150, 100))
        self.pushButton_2.setGeometry(QtCore.QRect(width*5/6, height*4/10, 150, 100))
        self.pushButton_3.setGeometry(QtCore.QRect(width*5/6, height*6/10, 150, 100))
        
        # 创建模型并设置
        self.model = EmptyEditableTableModel(rows=3000, cols=10)
        self.tableView.setModel(self.model)
        
        # 设置表头可编辑
        self.header_delegate = EditableHeaderDelegate(self.tableView)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.tableView.horizontalHeader().setSectionsClickable(True)
        self.tableView.horizontalHeader().sectionDoubleClicked.connect(self.edit_header)
        
        # 设置表格属性
        self.tableView.horizontalHeader().setDefaultSectionSize(120)
        self.tableView.verticalHeader().setDefaultSectionSize(30)
        self.actionSave_as.setEnabled(False)  # 空表格时禁用
        
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
        self.tableView.horizontalHeader().setDefaultSectionSize(120)
        self.tableView.verticalHeader().setDefaultSectionSize(30)
        
        # 4. 可选：显示提示信息
        #QMessageBox.information(self, "提示", "表格已新建")
        QMessageBox.information(self, "Notification", "A new table has been created")
        
    
    
    @pyqtSlot()
    def on_actionOpen_triggered(self):
        """
        打开 CSV 文件并导入到 TableView
        """
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
            if num_columns > 10:
#                QMessageBox.critical(
#                    self,
#                    "数据溢出",
#                    f"CSV 文件有 {num_columns} 列，超过最大 10 列限制！\n请重新选择文件。"
#                )
                QMessageBox.critical(
                    self,
                    "Data Overflow",  # or "Column Limit Exceeded" for more precision
                    f"CSV file has {num_columns} columns, exceeding the maximum limit of 10.\nPlease select a different file."
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

        #将 TableView 数据保存为 CSV 文件
    
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

    @pyqtSlot()
    def on_actionAbout_triggered(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        QMessageBox.information(
                self,
                "About",
                f"Copyright © 2025 by Fangbin Liu\nPlease contact the author promptly if you encounter any issues.\nEmail: liufangbin8908@163.com"
            )
    @pyqtSlot()
    def on_pushButton_clicked(self):
        """
        检查表格数据
        """
        # 检查表格是否为空
        
        empty_cells_in_gaps = {}  # 存储不连续的空单元格 {列索引: [(空单元格行索引, 前一个非空行索引)]}
        non_numeric_cells = []    # 存储非数字单元格位置
        column_pairs_mismatch = [] # 存储数字个数不一致的列对
        is_all_empty = True       # 标记表格是否全部为空
        
        # 定义需要检查的列对 (列索引从0开始)
        column_pairs = [(0, 1), (2, 3), (4, 5), (6, 7), (8, 9)]
        
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
        
#        if empty_cells_in_gaps:
#            gap_messages = []
#            for col, gaps in empty_cells_in_gaps.items():
#                gap_details = []
#                for gap in gaps:
#                    empty_row, prev_row = gap
#                    gap_details.append(
#                        f"第{empty_row+1}行(前一个非空是第{prev_row+1}行)"
#                    )
#                gap_messages.append(
#                    f"第{col+1}列存在数据不连续，空单元格位置:\n" + "\n".join(gap_details)
#                )
#            message_parts.append("以下列存在数据不连续:\n" + "\n\n".join(gap_messages))
#        else:
#            message_parts.append("所有列数据连续，没有空单元格间隙")
#        
#        if non_numeric_cells:
#            message_parts.append(
#                "以下单元格包含非数字内容:\n" + "\n".join(non_numeric_cells) + 
#                "\n\n请修改这些单元格的内容为数字"
#            )
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
            self.actionSave_as.setEnabled(True)  # 空表格时禁用
        
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
    def on_pushButton_2_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        headers = []  # 存储非空列的表头
        data = []     # 存储非空列的数据（按列组织）
        
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
                headers.append(header_text)
                data.append(column_data)    
        # 3. 创建子窗口并传数据
        self.sub = PyMainSub(parent=self)
        self.sub.show()
#        self.showMinimized()AA
        self.sub.set_table_data(headers, data)  # <-- 关键调用
        
    
    @pyqtSlot()
    def on_pushButton_3_clicked(self):
        """
        打开原始数据窗口，并传递 tableView 数据
        """
#        # 1. 提取表头
#        headers = []
#        for col in range(self.model.columnCount()):
#            headers.append(str(self.model.headerData(col, Qt.Horizontal, Qt.DisplayRole)))
#    
#        # 2. 提取数据（只导出有内容的行）
#        data = [[] for _ in range(self.model.columnCount())]   # 先建空列桶
#
#        for row in range(self.model.rowCount()):
#            for col in range(self.model.columnCount()):
#                val = self.model.data(self.model.index(row, col), Qt.DisplayRole)
#                str_val = str(val).strip() if val else ""
#                if str_val:                      # 非空才收集
#                    data[col].append(float(str_val) )   # 按列追加
        headers = []  # 存储非空列的表头
        data = []     # 存储非空列的数据（按列组织）
        
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
                headers.append(header_text)
                data.append(column_data)    
        # 3. 创建子窗口并传数据
        self.origin = PyOriData(parent=self)
        self.origin.show()
#        self.showMinimized()AA
        self.origin.set_table_data(headers, data)  # <-- 关键调用

        
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
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    

