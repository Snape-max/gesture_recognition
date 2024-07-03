"""
创建数据集程序，需要设置采集手势的标签gesture_label_list和每种手势采集数据num_per_label的数量
按 s 键采集手势，保存到变量中
按 d 键删除上一条数据
按 f 键写入文件 位于 dataset/下
数据为一个字典，包含手势的数据以及对应的标签
按 q 键退出程序
"""
import cv2
import numpy as np
import mediapipe as mp
from draw_utils import calc_feature
import pickle
import os

# 采集手势标签
gesture_label_list = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "GOOD", "BAD"]

# 每种手势采集数量
num_per_label = 5

# 计数器
num_cnt = 0
label_cnt = 0

# 特征数据
fea_data = []
# 标签
label = []




# Hand Detection
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1)
mpDraw = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)

# 检查是否存在dataset文件夹
if not os.path.exists("dataset"):
    os.mkdir("dataset")

while True:
    key = cv2.waitKey(1)
    # 读取一帧图像
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
            max_x = np.max(list_lms, axis=0)[0]
            max_y = np.max(list_lms, axis=0)[1]
            min_x = np.min(list_lms, axis=0)[0]
            min_y = np.min(list_lms, axis=0)[1]
            cv2.rectangle(img, (min_x, min_y), (max_x, max_y), (0, 255, 0), 2)
            # 计算手势特征点
            if key == ord('s'):
                feature_set = calc_feature(list_lms)
                # 添加到特征列表
                fea_data.append(feature_set)
                # 添加手势标签
                label.append(label_cnt)
                print("手势 {}，已保存特征点数：{}".format(gesture_label_list[label_cnt], num_cnt + 1))

                # 提示信息
                num_cnt += 1
                if num_cnt == num_per_label:
                    print("手势 {}，数据采集完成".format(gesture_label_list[label_cnt]))
                    label_cnt += 1
                    num_cnt = 0

                if label_cnt == len(gesture_label_list):
                    print("手势数据采集完成")

                # 删除上一条数据
            if key == ord('d'):
                num_cnt -= 1
                if num_cnt == 0:
                    num_cnt = num_per_label
                    label_cnt -= 1

                if label_cnt == -1:
                    raise ValueError("删到头了兄弟")
                fea_data.pop()
                label.pop()
                print("已删除上一特征点，手势 {} 现有特征点数：{}".format(gesture_label_list[label_cnt], num_cnt))



    cv2.imshow('hands', img)
    if key == ord('f'):
        # 保存到文件
        data = {
            'fea_data': fea_data,
            'label': label,
            'label_str': gesture_label_list,
        }

        fea_file = open('./dataset/data_test.pkl', 'wb')
        pickle.dump(data, fea_file)
        fea_file.close()

    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
