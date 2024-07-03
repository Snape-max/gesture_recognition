import pickle

import mediapipe as mp
import cv2
import numpy as np
from sklearn.naive_bayes import GaussianNB, MultinomialNB

from draw_utils import calc_feature, normalization

cap = cv2.VideoCapture(0)

mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1)
mpDraw = mp.solutions.drawing_utils

clf = pickle.load(open("./model/model.pkl", "rb"))
gesture_label_list = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "GOOD", "BAD"]

num_of_angle_fea = 5
num_of_distance_fea = 9

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
            # 找到手掌最大矩形边界
            list_lms = np.array(list_lms, dtype=np.int32)

            feature_set = calc_feature(list_lms)
            angle_fea = feature_set[:num_of_angle_fea]
            distance_fea = feature_set[num_of_angle_fea:]

            angle_fea = normalization(angle_fea)
            distance_fea = normalization(distance_fea)
            fea_data = np.concatenate((angle_fea, distance_fea))
            if True not in np.isnan(fea_data):
                result = clf.predict_proba(fea_data.reshape(1, -1))

                if np.max(result) > 0:
                    cv2.putText(img, gesture_label_list[np.argmax(result)], (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                (0, 0, 255), 2)

    cv2.imshow('hands', img)
    if cv2.waitKey(1) == ord('q'):
        break
