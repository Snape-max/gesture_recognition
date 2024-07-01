import sys

from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
import time

class WorkerThread(QThread):
    finished = pyqtSignal()  # 线程完成信号
    intReady = pyqtSignal(int)  # 发送整数信号

    def __init__(self):
        super().__init__()

    def run(self):
        for i in range(5):
            time.sleep(1)  # 模拟耗时操作
            self.intReady.emit(i)  # 发射intReady信号
        self.finished.emit()  # 所有任务完成后发射finished信号

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker = WorkerThread()  # 创建WorkerThread实例
        self.label = QLabel("Waiting...", self)
        self.label.move(50, 50)

        # 连接信号和槽函数
        self.worker.intReady.connect(self.update_label)
        self.worker.finished.connect(self.thread_complete)

        # 启动线程
        self.worker.start()

    def update_label(self, val):
        self.label.setText(str(val))

    def thread_complete(self):
        print("Thread complete!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())