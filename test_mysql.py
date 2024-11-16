from PyQt5.Qt import QT_VERSION_STR, PYQT_VERSION_STR
from PyQt5.QtSql import QSqlDatabase

print("Qt 版本:",QT_VERSION_STR)
print("PyQt 版本:",PYQT_VERSION_STR)

print(QSqlDatabase.drivers())

db=QSqlDatabase.addDatabase("QMYSQL")
db.setHostName("localhost")
db.setPort(3306)
db.setDatabaseName("attendance_system")
db.setUserName("root")
db.setPassword("123456")

if db.open():
    print("数据库连接成功！")
else:
    print(db.lastError().text())