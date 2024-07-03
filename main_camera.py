import sys
import time
import cv2
import mediapipe as mp
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal, QThread, pyqtSlot
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtWidgets import QGridLayout, QWidget, QLabel, QPushButton

from utils import get_str_gesture

mpHands = mp.solutions.hands
hands = mpHands.Hands(min_detection_confidence=0.60,
                      min_tracking_confidence=0.60,
                      max_num_hands=1)
mpDraw = mp.solutions.drawing_utils

mp_holistic = mp.solutions.holistic
holistic = mp_holistic.Holistic(min_detection_confidence=0.60,
                                  min_tracking_confidence=0.60)


# tello = Tello()
# tello.connect()
# tello.set_video_resolution(Tello.RESOLUTION_720P)
# tello.streamon()
# frame_read = tello.get_frame_read()

cap = cv2.VideoCapture(0)


class ControlThread(QThread):
    """
    控制线程
    """
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
                # tello.send_command_without_return("keepalive")
                print("keepalive")
            if cnt == 0:
                if self.message == "5":
                    # tello.takeoff()
                    print("\r\n起飞\n", end="")
                    cnt += 1

                elif self.message == 'Good':
                    # tello.move_up(30)
                    print("\r\n上升\n", end="")
                    cnt += 1

                elif self.message == '1':
                    # tello.land()
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
        """
        初始化
        """
        super(Gesture_Window, self).__init__()

        self.label_info = QLabel(self)
        self.timer_camera = QtCore.QTimer()
        self.timer_state = QtCore.QTimer()

        self.control = ControlThread()

        self.timer_camera.timeout.connect(self.update_frame)
        self.timer_state.timeout.connect(self.update_state)
        self.set_ui()
        self.timer_camera.start(30)  # 设置视频帧率
        self.timer_state.start(5000)
        self.control.start()

    def set_ui(self):
        """
        设置窗口UI
        """
        self.setWindowIcon(QIcon("./main.png"))
        central_widget = QWidget(self)
        # central_widget.setStyleSheet("background-color: #f3f3f3;")  # 红色
        grid = QGridLayout()
        central_widget.setLayout(grid)
        self.setCentralWidget(central_widget)
        self.setWindowTitle("Gesture Recognition")
        self.setGeometry(200, 100, 1150, 620)

        # 添加视频流显示标签
        self.label_video = QLabel(self)
        self.label_video.setStyleSheet("background-color: #FFFAFA")
        self.label_video.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        grid.addWidget(self.label_video, 0, 0, 3, 2)

        # 添加无人机信息显示标签
        self.label_info.setText("Loading...")
        # 设置字体
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label_info.setFont(font)
        self.label_info.setStyleSheet("color: #000000;background-color: #FFFAFA")
        self.label_info.setAlignment(Qt.AlignTop)
        grid.addWidget(self.label_info, 0, 2, 1, 2)

        # 添加控制按钮
        button_layout = QGridLayout()
        takeoff_button = QPushButton("起飞", self)
        land_button = QPushButton("降落", self)
        emergency_button = QPushButton("急停", self)
        move_up_button = QPushButton("上升", self)
        move_down_button = QPushButton("下降", self)
        move_forward_button = QPushButton("前进", self)
        move_backward_button = QPushButton("后退", self)
        move_left_button = QPushButton("左移", self)
        move_right_button = QPushButton("右移", self)

        takeoff_button.clicked.connect(self.takeoff)
        land_button.clicked.connect(self.land)
        emergency_button.clicked.connect(self.emergency_stop)
        move_up_button.clicked.connect(self.move_up)
        move_down_button.clicked.connect(self.move_down)
        move_forward_button.clicked.connect(self.move_forward)
        move_backward_button.clicked.connect(self.move_backward)
        move_left_button.clicked.connect(self.move_left)
        move_right_button.clicked.connect(self.move_right)

        # 设置字体大小
        font.setPointSize(12)
        takeoff_button.setFont(font)
        land_button.setFont(font)
        emergency_button.setFont(font)
        move_up_button.setFont(font)
        move_down_button.setFont(font)
        move_forward_button.setFont(font)
        move_backward_button.setFont(font)
        move_left_button.setFont(font)
        move_right_button.setFont(font)
        takeoff_button.setStyleSheet("height:60px;")
        land_button.setStyleSheet("height:60px;")
        emergency_button.setStyleSheet("height:60px;")
        move_up_button.setStyleSheet("height:60px;")
        move_down_button.setStyleSheet("height:60px;")
        move_forward_button.setStyleSheet("height:60px;")
        move_backward_button.setStyleSheet("height:60px;")
        move_left_button.setStyleSheet("height:60px;")
        move_right_button.setStyleSheet("height:60px;")
        button_layout.setAlignment(Qt.AlignHCenter)
        button_layout.addWidget(takeoff_button, 0, 0)
        button_layout.addWidget(land_button, 0, 2)
        button_layout.addWidget(emergency_button, 1, 1)
        button_layout.addWidget(move_up_button, 2, 0)
        button_layout.addWidget(move_down_button, 2, 2)
        button_layout.addWidget(move_forward_button, 0, 1)
        button_layout.addWidget(move_left_button, 1, 0)
        button_layout.addWidget(move_backward_button, 2, 1)
        button_layout.addWidget(move_right_button, 1, 2)
        grid.addLayout(button_layout, 1, 2, 2, 2)

    def update_frame(self):
        """
        更新视频流
        """
        ret = 1
        ret, frame = cap.read()
        str_gesture = ""
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channels = frame.shape
            # 得到检测结果
            holistic_result = holistic.process(frame)
            mpDraw.draw_landmarks(frame, holistic_result.pose_landmarks, mp_holistic.POSE_CONNECTIONS)
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
        """
        更新无人机状态
        """
        # battery = tello.get_battery()
        # altitude = tello.get_height()
        # temperature = tello.get_temperature()
        # isfly = tello.is_flying
        battery = 80
        altitude = 10
        temperature = 20
        isfly = True
        isfly_str = ""
        if isfly:
            isfly_str = "True"
        else:
            isfly_str = "False"

        if battery < 20:
            self.label_info.setText(
                "无人机信息:\n"
                "状态: Low Battery\n"
                "高度: {}cm\n"
                "电量: {}%\n"
                "温度:{}°\n"
                "飞行: {}"
                .format(altitude, battery, temperature, isfly_str))
        else:
            self.label_info.setText(
                "无人机信息:\n"
                "状态: Ready\n"
                "高度: {}cm\n"
                "电量: {}%\n"
                "温度: {}°\n"
                "飞行: {}"
                .format(altitude, battery, temperature, isfly_str))

    def takeoff(self):
        # tello.takeoff()
        print("Taking off...")

    def land(self):
        # tello.land()
        print("Landing...")

    def emergency_stop(self):
        # tello.emergency()
        print("Emergency stop!")

    def move_up(self):
        # tello.move_up(20)
        print("Move up 20cm")

    def move_down(self):
        # tello.move_down(20)
        print("Move down 20cm")

    def move_forward(self):
        # tello.move_forward(20)
        print("Move forward 20cm")

    def move_backward(self):
        # tello.move_backward(20)
        print("Move backward 20cm")

    def move_left(self):
        # tello.move_left(20)
        print("Move left 20cm")

    def move_right(self):
        # tello.move_right(20)
        print("Move right 20cm")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = Gesture_Window()
    main.show()
    sys.exit(app.exec_())
