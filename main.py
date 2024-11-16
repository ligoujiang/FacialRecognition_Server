import io
import struct
import sys

from PIL import Image
from PyQt5.QtCore import Qt
from facenet import Facenet
import numpy as np
from PyQt5.QtCore import QDataStream, QByteArray
from PyQt5.QtGui import QPixmap
from PyQt5.QtNetwork import QTcpServer, QTcpSocket, QHostAddress
from PyQt5.QtSql import QSqlDatabase, QSqlQueryModel, QSqlQuery
from PyQt5.QtWidgets import QApplication, QMainWindow
from main_UI import Ui_MainWindow
from enter_face import enter_face
from information_manage import  information_manage

#关闭异常信息
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

#窗口类
class MyApp(QMainWindow,Ui_MainWindow):
    def __init__(self):
        super(MyApp, self).__init__()
        self.setupUi(self)

        #Ui_page_1(self.page_1)

        self.page_2=enter_face(self.page_2)
        self.page_3=information_manage(self.page_3)
        self.stackedWidget.setCurrentIndex(0)

        self.menuBtn_1.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.menuBtn_2.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.menuBtn_3.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(2))

        # facenet模型
        self.facenet = Facenet()
        # 创建套接字
        self.server=QTcpServer() #用于处理连接
        self.socket=QTcpSocket() #用于发送数据
        # 监听，启动服务器
        self.server.listen(QHostAddress.Any, 9999)
        # qtcpServer当有客户端连接会发送newConnection信号
        self.server.newConnection.connect(self.accept_client)

        self.bsize = 0  # 默认没有接收到数据

    #响应客户端连接
    def accept_client(self):
        # 获取与客户端通信的套接字
        self.socket=self.server.nextPendingConnection()
        # 当客户端有数据到达会发送readyRead信号
        self.socket.readyRead.connect(self.read_data)

    # 从客户端接收人脸图像数据
    def read_data(self):
        stream=QDataStream(self.socket) # 把套接字绑定到数据流
        stream.setVersion(QDataStream.Qt_5_15) # 设置Qt版本

        #容错判断
        if self.bsize==0:
            if self.socket.bytesAvailable()<struct.calcsize('q'): # 当数据小于8字节时，返回等待 q=int64
                return
            else:
                self.bsize=stream.readInt64() # 数据大于8字节时，采集数据的大小

        if self.socket.bytesAvailable()<self.bsize: # 当数据小于bsize时，说明数据还没有发送完成，返回继续等待
            return

        byte_array=QByteArray() # Qt二进制数组类型
        stream>>byte_array # 写入数据
        self.bsize = 0 # 置为0，重新开始接收数据
        if byte_array.size()==0:# 读取到数据为0时，直接返回
           return
        py_bytes=byte_array.data() # 将QByteArray类型转为bytes类型，方便后续处理 #py_bytes = bytes(byte_array.data())
        #print(py_bytes)

        #界面显示图片
        mmp=QPixmap()
        mmp.loadFromData(py_bytes,"jpg") # 加载二进制数据，以jpg格式
        # mmp = mmp.scaled(self.label.size()) # 根据界面尺寸调整图像大小
        mmp=mmp.scaled(96,112) # 调整为96x112,方便识别
        mmp.save("./face.jpg") # 保存图片
        #
        # 使用io.BytesIO将二进制数据图像转换为文件对象
        image_file = io.BytesIO(py_bytes)
        self.image = Image.open(image_file)

        output=self.facenet.detect_image_v1(self.image)

        # 从数据表中检索数据
        self.query_database(output)

        self.label.setPixmap(mmp)

    #遍历数据表中的人脸特征向量
    def query_database(self,output):
        self.tableView.setModel(self.query_model)
        self.query_model.setQuery("select * from facialrecognition")  # 查询人脸特征表
        self.threshold = 0.85  # 阈值
        self.min_value = 1.5  # 记录最小距离值
        self.emp_id = -1  # 记录员工id
        self.output=output

        # 循环获取人脸特征表的特征向量列
        for row in range(self.query_model.rowCount()):
            record = self.query_model.record(row)  # 获取当前行的数据
            str = record.value(4)  # 获取128位人脸特征向量字符串类型
            if str == "":  # 当字符串为空时，直接返回
                break
            # 字符串类型转矩阵类型
            rows = [list(map(float, row.split(','))) for row in str.split('\n')]
            # 使用numpy.array将这个二维列表转换成NumPy矩阵
            matrix = np.array(rows)
            #计算欧氏距离
            l1 = np.linalg.norm(matrix - self.output, axis=1)
            # print(matrix.shape)
            if l1 < self.min_value:  # 依次判断最小距离
                self.min_value = l1
                self.emp_id = record.value(2)
                print("最小距离:", self.min_value)  # 浮点数
                print("员工号:", self.emp_id)

        print("距离:", l1)  # 浮点数
        if self.min_value >= self.threshold: #大于等于阈值，说明没有此人脸的特征向量
            print("查无此人")
        else:
            print("存在此人")
            print("最小距离:", self.min_value)  # 浮点数
            self.send_data()

    #给客户端发送个人信息
    def send_data(self):
        query2=QSqlQuery()
        query2.exec_("select * from employee where emp_id=%s"%self.emp_id)
        # 处理查询结果
        while query2.next():
            id_value = query2.value(0)  # 获取第一列的值
            name_value = query2.value(1)  # 获取第二列的值
            # dept_id_value=query2.value(8)
            print(f"工号: {id_value}, 姓名: {name_value}")

#主程序入口
if __name__ == "__main__":
    app = QApplication(sys.argv)
    db = QSqlDatabase.addDatabase("QMYSQL")
    db.setHostName("localhost")
    db.setPort(3306)
    db.setDatabaseName("test")
    db.setUserName("root")
    db.setPassword("123456")
    if db.open():
        print("数据库连接成功！")
    else:
        print(db.lastError().text())
    main_ui=MyApp()
    main_ui.show()
    sys.exit(app.exec_())
