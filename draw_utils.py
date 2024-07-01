import cv2
import numpy as np
 
 
def draw_line(img, width, height,  hand, start_index, stop_index):
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
    return np.linalg.norm(v1)/np.linalg.norm(v2)

 
 
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
    elif len(out_fingers) == 4 and out_fingers[0] == 8 and out_fingers[1] == 12 and out_fingers[2] == 16 and out_fingers[3] == 20:
        str_gesture = '4'
    elif len(out_fingers) == 5:
        str_gesture = '5'
    elif len(out_fingers) == 0:
        str_gesture = '10'
    else:
        str_gesture = ''
    return str_gesture