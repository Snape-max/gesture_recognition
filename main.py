import time
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import cv2
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QThread, pyqtSlot
from PyQt5.QtWidgets import QGridLayout, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
import mediapipe as mp
import numpy as np
from draw_utils import get_str_gesture
from djitellopy import Tello

mpHands = mp.solutions.hands
hands = mpHands.Hands(min_detection_confidence=0.60,
                      min_tracking_confidence=0.60,
                      max_num_hands=1)

mpDraw = mp.solutions.drawing_utils


tello = Tello()
tello.connect()
tello.set_video_resolution(Tello.RESOLUTION_720P)
tello.streamon()
frame_read = tello.get_frame_read()

class ControlThread(QThread):
    control_message = pyqtSignal(str)  # 定义一个接收字符串信号
    def __init__(self):
        super().__init__()
        self.message = ""

    def run(self):
        cnt = 0
        bcnt = 0
        while True:
            bcnt += 1
            bcnt %= 400
            if bcnt == 399:
                tello.send_command_without_return("keepalive")

            if cnt == 0:
                if self.message == "5":
                    tello.takeoff()
                    print("\r\n起飞\n", end="")
                    cnt += 1

                elif self.message == 'Good':
                    tello.move_up(30)
                    print("\r\n上升\n", end="")
                    cnt += 1

                elif self.message == '1':
                    tello.land()
                    print("\r\n降落\n", end="")
                    cnt += 1
            else:
                cnt += 1
                cnt %= 70
                print("\r延时%d帧" % cnt, end="")
            time.sleep(0.033)

    @pyqtSlot(str)
    def set_message(self, msg):
        self.message = msg  # 设置消息


class Gesture_Window(QtWidgets.QMainWindow):
    def __init__(self):
        super(Gesture_Window, self).__init__()
        self.label_info = QLabel(self)
        self.timer_camera = QtCore.QTimer()
        self.timer_state = QtCore.QTimer()
        # self.cap = cv2.VideoCapture(0)  # 假设使用默认摄像头，如果使用无人机视频流，需要相应的设备ID或URL
        # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
        # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 450)

        self.control = ControlThread()

        self.timer_camera.timeout.connect(self.update_frame)
        self.timer_state.timeout.connect(self.update_state)
        self.set_ui()
        self.timer_camera.start(30)  # 设置视频帧率
        self.timer_state.start(5000)
        self.control.start()

    def set_ui(self):
        central_widget = QWidget(self)
        # central_widget.setStyleSheet("background-color: #ffffff;")  # 红色
        grid = QGridLayout()
        central_widget.setLayout(grid)
        self.setCentralWidget(central_widget)
        self.setWindowTitle("Drone Control Interface")
        self.setGeometry(200, 100, 1000, 700)

        # 添加视频流显示标签
        self.label_video = QLabel(self)
        self.label_video.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        grid.addWidget(self.label_video, 0, 0, 2, 2)

        # 添加无人机信息显示标签
        self.label_info.setText("Loading...")
        self.label_info.setAlignment(Qt.AlignTop)
        grid.addWidget(self.label_info, 0, 2, 2, 2)

        # 添加控制按钮
        button_layout = QHBoxLayout()
        takeoff_button = QPushButton("Take Off", self)
        land_button = QPushButton("Land", self)
        emergency_button = QPushButton("Emergency Stop", self)

        takeoff_button.clicked.connect(self.takeoff)
        land_button.clicked.connect(self.land)
        emergency_button.clicked.connect(self.emergency_stop)

        takeoff_button.setStyleSheet("width: 100px; height: 50px;")
        land_button.setStyleSheet("width: 100px; height: 50px;")
        emergency_button.setStyleSheet("width: 100px; height: 50px;")
        button_layout.setAlignment(Qt.AlignHCenter)
        button_layout.addWidget(takeoff_button)
        button_layout.addWidget(land_button)
        button_layout.addWidget(emergency_button)

        grid.addLayout(button_layout, 2, 0)

    def update_frame(self):
        ret = 1
        frame = frame_read.frame
        str_gesture = ""
        if ret:
            # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channels = frame.shape
            # 得到检测结果
            results = hands.process(frame)
            if results.multi_hand_landmarks:
                for hand in results.multi_hand_landmarks:
                    mpDraw.draw_landmarks(frame, hand, mpHands.HAND_CONNECTIONS)

                # 采集所有关键点坐标
                list_lms = []
                for i in range(21):
                    pos_x = int(hand.landmark[i].x * width)
                    pos_y = int(hand.landmark[i].y * height)
                    list_lms.append([pos_x, pos_y])

                # 构造凸包点
                list_lms = np.array(list_lms, dtype=np.int32)

                hull_index = [0, 1, 2, 3, 6, 10, 14, 19, 18, 17]
                hull = cv2.convexHull(list_lms[hull_index], True)
                # cv2.polylines(img, [hull], True, (0, 255, 0), 2)

                # 查找外部的点数
                ll = [4, 8, 12, 16, 20]
                out_fingers = []
                for i in ll:
                    pt = (int(list_lms[i][0]), int(list_lms[i][1]))
                    dist = cv2.pointPolygonTest(hull, pt, True)
                    if dist < 0:
                        out_fingers.append(i)

                str_gesture = get_str_gesture(out_fingers, list_lms)
                cv2.putText(frame, str_gesture, (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 0), 4, cv2.LINE_AA)
                for i in ll:
                    pos_x = int(hand.landmark[i].x * width)
                    pos_y = int(hand.landmark[i].y * height)
                    cv2.circle(frame, (pos_x, pos_y), 3, (0, 255, 255), -1)
            # frame.resize((800, 450))
            showframe = cv2.resize(frame, (800, 600))
            height, width, channel = showframe.shape
            step = channel * width
            qImg = QImage(showframe.data, width, height, step, QImage.Format_RGB888)
            self.label_video.setPixmap(QPixmap.fromImage(qImg))
            self.control.set_message(str_gesture)

    def update_state(self):
        battery = tello.get_battery()
        altitude = tello.get_height()
        temperature = tello.get_temperature()
        isfly = tello.is_flying
        isfly_str = ""
        if isfly:
            isfly_str = "True"
        else:
            isfly_str = "False"

        if battery < 20:
            self.label_info.setText(
                "Drone Information:\n"
                "Status: Low Battery\n"
                "Altitude: {}cm\n"
                "Battery: {}%\n"
                "Temperature:{}°\nIsfly: {}"
                .format(altitude, battery, temperature, isfly_str))
        else:
            self.label_info.setText(
                "Drone Information:\n"
                "Status: Ready\n"
                "Altitude: {}cm\n"
                "Battery: {}%\n"
                "Temperature:{}°\n"
                "Isfly: {}"
                .format(altitude, battery, temperature, isfly_str))

    def takeoff(self):
        tello.takeoff()
        print("Taking off...")

    def land(self):
        tello.land()
        print("Landing...")

    def emergency_stop(self):
        tello.emergency()
        print("Emergency stop!")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = Gesture_Window()
    main.show()
    sys.exit(app.exec_())
