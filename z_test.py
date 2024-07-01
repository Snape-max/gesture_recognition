from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal


class WorkerThread(QThread):
    message_received = pyqtSignal(str)  # 定义一个接收字符串信号

    def __init__(self):
        super().__init__()
        self.message = ""

    def run(self):
        while True:
            if self.message != "":
                print(f"Message received: {self.message}")
                self.message_received.emit(self.message)  # 发射信号
                self.message = ""  # 清空消息
            self.msleep(100)  # 防止CPU占用过高

    @pyqtSlot(str)
    def set_message(self, msg):
        self.message = msg  # 设置消息


import sys
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.worker = WorkerThread()
        self.worker.message_received.connect(self.on_message_received)  # 连接子线程的信号到槽

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.send_message)  # 定时发送消息
        self.timer.start(1000)  # 每秒发送一次

        self.worker.start()  # 启动子线程

    def send_message(self):
        self.worker.set_message("Hello from the main process!")  # 调用子线程的slot发送消息

    def on_message_received(self, msg):
        print(f"Main process received: {msg}")  # 主进程收到子线程返回的消息


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())