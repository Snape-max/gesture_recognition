"""
创建数据集程序，每次运行，会生成一个新文件，保存手势特征
! 每次运行需要设置下 gesture_label
"""
import cv2
import numpy as np
import mediapipe as mp
from draw_utils import get_angle, get_distance_ratio
import pickle
import os

# 本次采集手势标签
gesture_label = "1"


def calc_angle_feature(point_list, list_lms):
    """
    计算角度特征
    :param point_list: 待计算特征点索引
    :param list_lms: 手指特征点列表
    :return:
    """
    return get_angle(list_lms[point_list[0]] - list_lms[point_list[1]],
                     list_lms[point_list[2]] - list_lms[point_list[1]])


def calc_distance_feature(point_list, list_lms):
    """
    计算距离特征
    :param point_list: 待计算特征点索引
    :param list_lms: 手指特征点列表
    :return:
    """
    return get_distance_ratio(list_lms[point_list[0]] - list_lms[point_list[1]],
                              list_lms[point_list[2]] - list_lms[point_list[1]])


# Hand Detection
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1)
mpDraw = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)

# 特征数据
fea_data = []
# 标签
label = []

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
                feature_set = []
                # 距离特征点
                dis_feature_points = [
                    [17, 2, 4],
                    [0, 6, 8],
                    [0, 10, 12],
                    [0, 14, 16],
                    [0, 8, 20],
                ]
                # 角度特征点
                angle_feature_points = [
                    [2, 4, 0],
                    [5, 8, 0],
                    [9, 12, 0],
                    [13, 16, 0],
                    [17, 20, 0],
                    [2, 4, 8],
                    [5, 8, 12],
                    [9, 12, 16],
                    [13, 16, 20],
                ]
                # 计算距离特征点
                original_dis_fea = []
                for i in range(len(dis_feature_points)):
                    original_dis_fea.append(calc_distance_feature(dis_feature_points[i], list_lms))
                # 计算角度特征点
                original_angle_fea = []
                for i in range(len(angle_feature_points)):
                    original_angle_fea.append(calc_angle_feature(angle_feature_points[i], list_lms))

                # 合并特征点
                feature_set.extend(original_dis_fea)
                feature_set.extend(original_angle_fea)
                # 添加到特征列表
                fea_data.append(feature_set)
                print("手势 {}，已保存特征点数：{}".format(gesture_label, len(fea_data)))

    cv2.imshow('hands', img)
    if key == ord('f'):
        # 保存到文件
        fea_file = open('./dataset/fea_data_{}.pkl'.format(gesture_label), 'wb')
        pickle.dump(fea_data, fea_file)
        fea_file.close()

    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
