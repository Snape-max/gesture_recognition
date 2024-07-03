import mediapipe as mp
import cv2
import numpy as np
from predict import Model
from utils import calc_feature

cap = cv2.VideoCapture(0)
# 初始化手部检测模型
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1, min_detection_confidence=0.75, min_tracking_confidence=0.75)
# 绘图
mpDraw = mp.solutions.drawing_utils
# 初始化分类模型
model = Model(model_path='./model/model_best.pkl', num_of_pred_frame=15)

ans = None
while True:
    ret, img = cap.read()
    height, width, channels = img.shape
    # 转换为RGB
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # 得到检测结果
    results = hands.process(imgRGB)
    # 检测到手，绘制手部关键点
    if results.multi_hand_landmarks:
        for hand in results.multi_hand_landmarks:
            mpDraw.draw_landmarks(img, hand, mpHands.HAND_CONNECTIONS)
            # 采集所有关键点坐标
            list_lms = []
            for i in range(21):
                pos_x = int(hand.landmark[i].x * width)
                pos_y = int(hand.landmark[i].y * height)
                list_lms.append([pos_x, pos_y])
            list_lms = np.array(list_lms, dtype=np.int32)
            # 计算特征值并预测手势，15帧给一个结果
            ret, result = model.predict(calc_feature(list_lms))
            if ret:
                ans = result
            if ans is not None:
                cv2.putText(img, ans, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow('hands', img)
    if cv2.waitKey(1) == ord('q'):
        break
