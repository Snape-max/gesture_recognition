import sys
import time
import cv2
import mediapipe as mp
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal, QThread, pyqtSlot
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtWidgets import QGridLayout, QWidget, QLabel, QPushButton
from djitellopy import Tello
from predict import Decision, Model

mpHands = mp.solutions.hands
hands = mpHands.Hands(min_detection_confidence=0.60,
                      min_tracking_confidence=0.60,
                      max_num_hands=1)
mpDraw = mp.solutions.drawing_utils

mp_holistic = mp.solutions.holistic
holistic = mp_holistic.Holistic(min_detection_confidence=0.60,
                                min_tracking_confidence=0.60)

# method = Decision(num_of_pred_frame=6)
method = Model(model_path='./model/model_G_new.pkl', num_of_pred_frame=6)

from faketello import fakeTello

# 真Tello
# tello = Tello()
# 假Tello 调试用
tello = fakeTello()
tello.connect()
tello.set_video_resolution(fakeTello.RESOLUTION_720P)
tello.streamon()
frame_read = tello.get_frame_read()


class ControlThread(QThread):
    """
    控制线程
    """
    control_message = pyqtSignal(str)  # 定义一个接收字符串信号

    def __init__(self):
        super().__init__()
        self.message = ""
        # 控制字典
        self.key_dict = {
            '10': 'land',
            '4': 'move_backward',
            '2': 'move_left',
            '3': 'move_right',
            '1': 'take_off',
            '5': 'move_up',
            '6': 'move_forward',
            '7': 'move_down',

            '8': 'stop',
            '9': 'flip',
            'GOOD': 'Good',
            'BAD': 'Bad',
            '': ''
        }
        self.reversed_key_dict = {v: k for k, v in self.key_dict.items()}
        self.keep_alive_frame = 200
        self.cnt = 0
        self.bcnt = 0
        self.ccnt = 0
        self.command1 = ""
        self.command2 = ""

    def send(self, msg):
        self.control_message.emit(msg)

    def run(self):
        """
        手势控制
        1: 降落
        2: 后退
        3: 左移
        4: 右移
        5: 起飞
        Good: 上升
        6: 前进
        Bad: 下降

        :return:
        """
        while True:
            self.keep_alive(200)
            ret, command = self.get_command_with_gap(10)
            if ret:
                print(command)
            self.carry_out_with_gap(command, 70)
            time.sleep(0.033)

    @pyqtSlot(str)
    def set_message(self, msg):
        self.message = msg  # 设置消息

    def carry_out_with_gap(self, command, frames):
        if self.cnt == 0:
            ret = self.carry_out(command)
            if ret:
                self.cnt += 1
        else:
            self.cnt += 1
            self.cnt %= frames
            print("\r延时%d帧" % self.cnt, end="")

    def carry_out(self, command):
        ret = True
        if not tello.is_flying:
            if command == "take_off":
                tello.takeoff()
                print("\r\n起飞\n", end="")
            else:
                ret = False

        else:
            if command == 'move_up':
                tello.move_up(30)
                print("\r\n上升\n", end="")

            elif command == 'land':
                tello.land()
                print("\r\n降落\n", end="")

            elif command == 'move_left':
                tello.move_left(30)
                print("\r\n左移\n", end="")

            elif command == 'move_right':
                tello.move_right(30)
                print("\r\n右移\n", end="")

            elif command == 'move_backward':
                tello.move_backward(30)
                print("\r\n后退\n", end="")

            elif command == 'move_forward':
                tello.move_forward(30)
                print("\r\n前进\n", end="")

            elif command == 'move_down':
                tello.move_down(30)
                print("\r\n下降\n", end="")
            else:
                ret = False
        if ret:
            self.send(command)
        return ret

    def keep_alive(self, frames):
        self.bcnt += 1
        self.bcnt %= frames
        if self.bcnt == frames - 1:
            tello.send_command_without_return("keepalive")
            print("keepalive")

    def get_command(self):
        ret = False
        command = self.key_dict[self.message]
        if command != "":
            ret = True
        return ret, command

    def get_command_with_gap(self, frames):
        ret = False
        command = ""
        if self.ccnt == 0:
            self.ccnt += 1
            ret, tep_command = self.get_command()
            if ret:
                self.command1 = tep_command
        else:
            self.ccnt += 1
            self.ccnt %= frames
            if self.ccnt == frames - 1:
                ret, tep_command = self.get_command()
                if ret:
                    self.command2 = tep_command
                # print("command1={}, command2={}".format(self.command1, self.command2))
                if self.command1 == self.command2 and (self.command1 != ""):
                    command = self.command1
                    self.command1 = ""
                    self.command2 = ""
                    ret = True
        return ret, command


class WorkerThread(QThread):
    def __init__(self):
        super().__init__()
        self.message = ""

    def run(self) -> None:
        while 1:
            if self.message == "take_off":
                tello.takeoff()
            elif self.message == "land":
                tello.land()
            elif self.message == "move_up":
                tello.move_up(30)
            elif self.message == "move_down":
                tello.move_down(30)
            elif self.message == "move_forward":
                tello.move_forward(30)
            elif self.message == "move_left":
                tello.move_left(30)
            elif self.message == "move_right":
                tello.move_right(30)
            elif self.message == "move_back":
                tello.move_back(30)
            elif self.message == "emergency":
                tello.emergency()
            else:
                pass
            self.message = ""
            time.sleep(0.5)

    def send(self, message):
        self.message = message


class Gesture_Window(QtWidgets.QMainWindow):
    def __init__(self):
        """
        初始化
        """
        super(Gesture_Window, self).__init__()

        self.str_gesture = ""

        self.label_info = QLabel(self)
        self.timer_camera = QtCore.QTimer()
        self.timer_state = QtCore.QTimer()

        self.takeoff_button = QPushButton("起飞", self)
        self.land_button = QPushButton("降落", self)
        self.emergency_button = QPushButton("急停", self)
        self.move_up_button = QPushButton("上升", self)
        self.move_down_button = QPushButton("下降", self)
        self.move_forward_button = QPushButton("前进", self)
        self.move_backward_button = QPushButton("后退", self)
        self.move_left_button = QPushButton("左移", self)
        self.move_right_button = QPushButton("右移", self)

        self.control = ControlThread()
        self.worker = WorkerThread()

        self.control.control_message.connect(self.update_button)

        self.timer_camera.timeout.connect(self.update_frame)
        self.timer_state.timeout.connect(self.update_state)
        self.set_ui()
        self.timer_camera.start(30)  # 设置视频帧率
        self.timer_state.start(5000)
        self.control.start()
        self.worker.start()

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
        takeoff_button = self.takeoff_button
        land_button = self.land_button
        emergency_button = self.emergency_button
        move_up_button = self.move_up_button
        move_down_button = self.move_down_button
        move_forward_button = self.move_forward_button
        move_backward_button = self.move_backward_button
        move_left_button = self.move_left_button
        move_right_button = self.move_right_button
        # 按钮作用
        takeoff_button.clicked.connect(self.send_worker("take_off"))
        land_button.clicked.connect(self.send_worker("land"))
        emergency_button.clicked.connect(self.send_worker("emergency"))
        move_up_button.clicked.connect(self.send_worker("move_up"))
        move_down_button.clicked.connect(self.send_worker("move_down"))
        move_forward_button.clicked.connect(self.send_worker("move_forward"))
        move_backward_button.clicked.connect(self.send_worker("move_back"))
        move_left_button.clicked.connect(self.send_worker("move_left"))
        move_right_button.clicked.connect(self.send_worker("move_right"))

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
        # 设置按钮大小
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
        frame = frame_read.frame
        ans = ""
        if ret:
            # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
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
                # 转化为numpy
                list_lms = np.array(list_lms, dtype=np.int32)

                # 计算手势, method采用哪种方法看前面定义
                ret, ans = method.predict(list_lms)
                if ret:
                    self.str_gesture = ans

                # 获取结果显示到图像上
                cv2.putText(frame, self.str_gesture, (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 0), 4,
                            cv2.LINE_AA)

            # 显示到PYQT窗口中
            showframe = cv2.resize(frame, (800, 600))
            height, width, channel = showframe.shape
            step = channel * width
            qImg = QImage(showframe.data, width, height, step, QImage.Format_RGB888)
            self.label_video.setPixmap(QPixmap.fromImage(qImg))
            self.control.set_message(ans)

    def update_state(self):
        """
        更新无人机状态
        """
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

    def clear_button_style(self):
        """
        清除按钮样式
        :return:
        """
        self.takeoff_button.setStyleSheet("QPushButton { height:60px;}")
        self.land_button.setStyleSheet("QPushButton { height:60px;}")
        self.emergency_button.setStyleSheet("QPushButton { height:60px;}")
        self.move_up_button.setStyleSheet("QPushButton { height:60px;}")
        self.move_down_button.setStyleSheet("QPushButton { height:60px;}")
        self.move_forward_button.setStyleSheet("QPushButton { height:60px;}")
        self.move_left_button.setStyleSheet("QPushButton { height:60px;}")
        self.move_right_button.setStyleSheet("QPushButton { height:60px;}")
        self.move_backward_button.setStyleSheet("QPushButton { height:60px;}")

    def update_button(self, val):
        """
        更新按钮状态
        """
        self.clear_button_style()
        if val == "take_off":
            # 改变按钮颜色为绿色
            self.takeoff_button.setStyleSheet("QPushButton { background-color: green; height:60px; }")
        elif val == "land":
            self.land_button.setStyleSheet("QPushButton { background-color: green; height:60px; }")
        elif val == "move_up":
            self.move_up_button.setStyleSheet("QPushButton { background-color: green; height:60px; }")
        elif val == "move_down":
            self.move_down_button.setStyleSheet("QPushButton { background-color: green; height:60px; }")
        elif val == "move_forward":
            self.move_forward_button.setStyleSheet("QPushButton { background-color: green; height:60px; }")
        elif val == "move_left":
            self.move_left_button.setStyleSheet("QPushButton { background-color: green; height:60px; }")
        elif val == "move_right":
            self.move_right_button.setStyleSheet("QPushButton { background-color: green; height:60px; }")
        elif val == "move_backward":
            self.move_backward_button.setStyleSheet("QPushButton { background-color: green; height:60px; }")

    def send_worker(self, val):
        return lambda: self.worker.send(val)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = Gesture_Window()
    main.show()
    sys.exit(app.exec_())
