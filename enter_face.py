import os
import sys

import cv2 as cv
from PIL import Image
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtSql import QSqlQuery, QSqlTableModel, QSqlQueryModel, QSqlRecord
from PyQt5.QtWidgets import QWidget, QApplication, QFileDialog, QMessageBox
from facenet import Facenet

from Ui.page_2 import Ui_Form

#窗口类
class enter_face(QWidget, Ui_Form):
    def __init__(self,parent):
        super().__init__(parent=parent)
        self.setupUi(self)

        # facenet实例化
        self.facenet=Facenet()
        # 摄像头
        self.cap=None
        # 创建定时器
        self.cap_timer = QTimer()
        self.cap_timer.timeout.connect(self.update_frame)
        #self.cap_timer.start(30)  # 大约30 FPS (1000 ms / 30 = 33.33 ms)
        #原图像路径
        self.file_path=None
        #人脸图像路径
        self.face_path=None
        self.face_detector=cv.CascadeClassifier("D:/Qt/Projects02/OpenCV/opencv-4.10.0/build/install/etc/haarcascades/haarcascade_frontalface_alt.xml")

        # 数据表模型
        self.table_model=QSqlTableModel()
        self.table_model.setTable("facialrecognition")
        self.table_model.select()

        # on/off摄像头
        self.on_off_camera_Btn.clicked.connect(self.on_off_camera_btn_clicked)
        # 拍照
        self.take_pictures_Btn.clicked.connect(self.take_pictures_btn_clicked)
        # 添加照片
        self.add_photo_Btn.clicked.connect(self.add_photo_Btn_clicked)
        # 查询工号
        self.selectBtn.clicked.connect(self.select_btn_clicked)
        # 录入人脸
        self.enter_face_Btn.clicked.connect(self.enter_face_btn_clicked)
        # 删除人脸
        self.delete_face_Btn.clicked.connect(self.delete_face_btn_clicked)

    # 更新视频帧
    def update_frame(self):
        # 从摄像头采集数据
        ret, frame = self.cap.read()
        if not ret:
            print("Failed to grab frame")
            return
        # 翻转图像（水平）
        frame = cv.flip(frame, 1)
        # 转换颜色空间 BGR 到 RGB
        frame_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

        # 转换为QImage
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        q_img = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        # 转换为QPixmap并设置到QLabel上
        pixmap = QPixmap.fromImage(q_img)
        self.cameraLb.setPixmap(pixmap.scaled(self.cameraLb.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
    # 打开/关闭摄像头
    def on_off_camera_btn_clicked(self):
        if self.on_off_camera_Btn.text() == "打开摄像头":
            self.cap=cv.VideoCapture(0)
            self.on_off_camera_Btn.setText("关闭摄像头")
            self.cap_timer.start(30)
        else:
            self.cap_timer.stop()
            self.on_off_camera_Btn.setText("打开摄像头")
            self.cap.release()
            self.cameraLb.clear()
    # 拍照
    def take_pictures_btn_clicked(self):
        self.cap_timer.stop()
        self.on_off_camera_Btn.setText("打开摄像头")
        self.cap.release()

        # 从 cameraLb 中获取 QPixmap并保存为jpg格式
        pixmap = self.cameraLb.pixmap()
        pixmap.save("facial_data/temp.jpg")
        self.file_path="facial_data/temp.jpg"
    # 添加图片
    def add_photo_Btn_clicked(self):
        print(0)
        # 通过文件对话框，选择图片路径
        self.file_path,_=QFileDialog.getOpenFileName(self, "选择图片", "", "Images (*.png *.jpg *.bmp)")
        # 显示图片
        pix=QPixmap()
        pix.load(self.file_path)
        pix = pix.scaled(self.cameraLb.size())  # 根据界面尺寸调整图像大小
        self.cameraLb.setPixmap(pix)
    # 查询工号
    def select_btn_clicked(self):
        emp_id=self.selectEdit.text() # 获取ID
        query = QSqlQuery()
        query.exec_("select * from employee where emp_id=%s" % emp_id)

        # 处理查询结果
        if query.next():
            id_value = query.value(0)  # 工号
            name_value = query.value(1)  # 姓名
            ept_id_value = query.value(8)  # 部门号
            self.emp_idEdit.setText(str(id_value))
            self.name_Edit.setText(str(name_value))
            self.dept_nameEdit.setText(str(ept_id_value))

            query.exec_("select * from facialrecognition where emp_id=%s" % emp_id)
            while query.next():
                face_img = query.value(1)
                pix = QPixmap()
                pix.load(str(face_img))
                pix = pix.scaled(self.face_imageLb.size())  # 根据界面尺寸调整图像大小
                self.face_imageLb.setPixmap(pix)
        else:
            QMessageBox.information(self, "查询提示", "没有查询到该ID！")
            self.emp_idEdit.clear()
            self.name_Edit.clear()
            self.dept_nameEdit.clear()
            self.face_imageLb.clear()
    # 录入人脸
    def enter_face_btn_clicked(self):
        print("人脸录入")
        # 检测图像中的人脸
        image = cv.imread(self.file_path)
        gray_image=cv.cvtColor(image,cv.COLOR_BGR2GRAY)

        face=self.face_detector.detectMultiScale(gray_image,1.1,1)
        for x,y,w,h in face:
            # 裁剪出人脸区域的图像
            self.face_image = image[y:y + h, x:x + w]
            #cv.rectangle(image,(x,y),(x+w,y+h),(0,0,255),1)
        # 预处理
        self.face_image=cv.resize(self.face_image,(96,112)) # 人脸图像调整为97x112
        self.face_path = "facial_data/%s.jpg"%self.emp_idEdit.text() # 根据查询的工号，以工号命名
        cv.imwrite(self.face_path,self.face_image) # 人脸图像存储为本地

        # 将BGR图像转换为RGB图像（因为PIL使用RGB格式）
        rgb_image = cv.cvtColor(self.face_image, cv.COLOR_BGR2RGB)
        # 将NumPy数组转换为PIL图像对象
        pil_image = Image.fromarray(rgb_image)
        # 提取特征值
        output=self.facenet.detect_image_v1(pil_image)
        # print(output)
        # print(output.shape)

        # 矩阵转字符串类型
        # 将矩阵展平为一维数组
        flattened_array = output.flatten()
        # 使用逗号加空格将数组元素转换为字符串并连接起来
        matrix_string = ', '.join(map(str, flattened_array))

        # 存入数据库
        record=self.table_model.record()
        record.setValue("headfile",self.face_path)
        record.setValue("emp_id",self.emp_idEdit.text())
        record.setValue("action_column"," ")
        record.setValue("tezheng",matrix_string)
        ret = self.table_model.insertRecord(0,record)
        if ret:
            QMessageBox.information(self, "录入提示", "人脸录入成功！")
            self.table_model.submitAll()
        else:
            QMessageBox.information(self, "录入提示", "人脸录入失败！")
            print(self.table_model.lastError().text())
    # 删除人脸
    def delete_face_btn_clicked(self):
        print(1)
        emp_id=self.selectEdit.text()
        print(emp_id)
        # 删除数据表的人脸数据
        query=QSqlQuery()
        query.exec_("delete from facialrecognition where emp_id=%s"%emp_id)
        # 删除本地人脸图像
        file_path = "facial_data/%s.jpg" % emp_id
        os.remove(file_path) # 删除文件
        QMessageBox.information(self, "删除提示", "人脸删除成功！")