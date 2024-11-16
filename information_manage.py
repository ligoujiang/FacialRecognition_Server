from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter
from PyQt5.QtSql import QSqlQueryModel
from PyQt5.QtWidgets import QWidget, QStyledItemDelegate, QStyleOptionViewItem, QAbstractItemView

from Ui.page_3 import Ui_page_3

# 表格文字居中
class MyTextCenteredDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(MyTextCenteredDelegate, self).__init__(parent)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: int) -> None:
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        # 设置文本对齐方式为居中
        alignment = Qt.AlignCenter
        # 保存原始的对齐方式
        original_alignment = opt.displayAlignment
        opt.displayAlignment = alignment
        # 调用基类的方法绘制项
        super(MyTextCenteredDelegate, self).paint(painter, opt, index)
        # 恢复原始的对齐方式（如果需要的话）
        opt.displayAlignment = original_alignment

class information_manage(QWidget, Ui_page_3):
    def __init__(self,parent):
        super().__init__(parent=parent)
        self.setupUi(self)

        # 设置表模型和表视图
        self.query_model = QSqlQueryModel()
        self.query_model.setQuery("select * from employee")  # 查询员工表

        # 设置表头
        tb_header_list = ["员工编号", "姓名", "性别", "出生日期", "身份证号", "电话", "教育背景", "入职时间",
                          "部门编号","人脸图像"]
        i = 0
        for tb_header in tb_header_list:
            self.query_model.setHeaderData(i, Qt.Horizontal, tb_header)
            i+=1

        #设置视图/模型
        self.tableView.setModel(self.query_model)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows) # 仅选择行
        # 自适应大小
        self.tableView.resizeRowsToContents()
        self.tableView.horizontalHeader().setStretchLastSection(True)

        #自定义委托
        #表格文字居中
        self.delegate02=MyTextCenteredDelegate(self.tableView)
        self.tableView.setItemDelegate(self.delegate02)

        # 刷新信息表
        self.refresh_Btn.clicked.connect(self.refresh_btn_clicked)
        # 查询员工信息
        self.select_Btn.clicked.connect(self.select_btn_clicked)



    # 刷新信息表
    def refresh_btn_clicked(self):
        self.query_model.setQuery("select * from employee")
    # 查询员工信息
    def select_btn_clicked(self):
        select_value=self.select_Edit.text()
        self.query_model.setQuery("select * from employee where emp_id like '%s' or name like '%s'"%(select_value,select_value))