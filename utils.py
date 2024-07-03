import cv2
import numpy as np


def draw_line(img, width, height, hand, start_index, stop_index):
    for i in range(start_index, stop_index):
        x1, y1 = int(hand.landmark[i].x * width), int(hand.landmark[i].y * height)
        x2, y2 = int(hand.landmark[i + 1].x * width), int(hand.landmark[i + 1].y * height)
        cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 2)


def draw_hand(img, width, height, hand):
    # 画圆
    for i in range(21):
        pos_x = hand.landmark[i].x * width  # hand.landmark[i].x为归一化后的坐标
        pos_y = hand.landmark[i].y * height
        cv2.circle(img, (int(pos_x), int(pos_y)), 5, (0, 0, 255), -1)
    # 画线
    draw_line(img, width, height, hand, 0, 4)
    draw_line(img, width, height, hand, 5, 8)
    draw_line(img, width, height, hand, 9, 12)
    draw_line(img, width, height, hand, 13, 16)
    draw_line(img, width, height, hand, 17, 20)
    index = [0, 5, 9, 13, 17, 0]
    for i in range(5):
        pt1 = (int(hand.landmark[index[i]].x * width), int(hand.landmark[index[i]].y * height))
        pt2 = (int(hand.landmark[index[i + 1]].x * width), int(hand.landmark[index[i + 1]].y * height))
        cv2.line(img, pt1, pt2, (255, 255, 255), 2)


def get_angle(v1, v2):
    """
    计算两个向量的夹角
    :param v1: 向量1
    :param v2: 向量2
    :return: 夹角（度）
    """
    angle = np.dot(v1, v2) / (np.sqrt(np.sum(v1 * v1)) * np.sqrt(np.sum(v2 * v2)))
    angle = np.arccos(angle) * 180 / np.pi
    return angle


def get_distance_ratio(v1, v2):
    """
    计算两个向量的距离比
    :param v1: 向量1
    :param v2: 向量2
    :return: 距离比
    """
    return np.linalg.norm(v1) / np.linalg.norm(v2)


def get_str_gesture(out_fingers, list_lms):
    if len(out_fingers) == 1 and out_fingers[0] == 8:
        v1 = list_lms[6] - list_lms[7]
        v2 = list_lms[8] - list_lms[7]
        angle = get_angle(v1, v2)
        if angle < 160:
            str_gesture = '9'
        else:
            str_gesture = '1'
    elif len(out_fingers) == 1 and out_fingers[0] == 4:
        str_gesture = 'Good'
    elif len(out_fingers) == 1 and out_fingers[0] == 20:
        str_gesture = 'Bad'
    elif len(out_fingers) == 2 and out_fingers[0] == 8 and out_fingers[1] == 12:
        str_gesture = '2'
    elif len(out_fingers) == 2 and out_fingers[0] == 4 and out_fingers[1] == 20:
        str_gesture = '6'
    elif len(out_fingers) == 2 and out_fingers[0] == 4 and out_fingers[1] == 8:
        str_gesture = '8'
    elif len(out_fingers) == 3 and out_fingers[0] == 8 and out_fingers[1] == 12 and out_fingers[2] == 16:
        str_gesture = '3'
    elif len(out_fingers) == 3 and out_fingers[0] == 4 and out_fingers[1] == 8 and out_fingers[2] == 12:
        str_gesture = '7'
    elif len(out_fingers) == 4 and out_fingers[0] == 8 and out_fingers[1] == 12 and out_fingers[2] == 16 and \
            out_fingers[3] == 20:
        str_gesture = '4'
    elif len(out_fingers) == 5:
        str_gesture = '5'
    elif len(out_fingers) == 0:
        str_gesture = '10'
    else:
        str_gesture = ''
    return str_gesture


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


def calc_feature(list_lms):
    """
    :param list_lms:
    :return:
    """
    feature_set = []
    dis_feature_points = [
        [17, 2, 4],
        [0, 6, 8],
        [0, 10, 12],
        [0, 14, 16],
        [0, 8, 20],
        [4, 20, 0]
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
        [5, 6, 7],
        [6, 7, 8]
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
    return feature_set


def normalization(data):
    """
    数据归一化
    :param data:
    :return:
    """
    min_data = np.min(data, axis=0)
    max_data = np.max(data, axis=0)
    norm_data = (data - min_data) / (max_data - min_data)
    return norm_data


def normalization_feature(feature_set, num_of_distance_fea):
    """
    分别归一化特征值
    :param feature_set:
    :param num_of_distance_fea:
    :return:
    """
    feature_set = np.array(feature_set)
    distance_fea = feature_set[:, :num_of_distance_fea]
    angle_fea = feature_set[:, num_of_distance_fea:]
    angle_fea = normalization(angle_fea)
    distance_fea = normalization(distance_fea)
    fea_data = np.concatenate((distance_fea, angle_fea), axis=1)
    return fea_data
