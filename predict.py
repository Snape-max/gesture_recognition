import pickle

import cv2
import numpy as np
from sklearn.naive_bayes import GaussianNB

from utils import get_angle, calc_feature, calc_angle_feature

GESTURE_LIST = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "GOOD", "BAD"]


class Model:
    """
    贝叶斯分类器模型
    """

    def __init__(self, model_path, num_of_pred_frame):
        """

        :param model_path: 模型路径
        :param num_of_pred_frame: 每次检测取几帧
        """
        self.model = pickle.load(open(model_path, 'rb'))
        self.num_of_pred_frame = num_of_pred_frame
        self.feature_set = []

    def __collect_feature(self, feature):
        """
        收集特征值
        :param feature:
        :return:
        """
        self.feature_set.append(calc_feature(feature))
        if len(self.feature_set) == self.num_of_pred_frame:
            return True
        return False

    def predict(self, feature):
        """
        预测手势
        :param feature: 手势特征
        :return: 是否预测完成，预测结果
        """
        flag = self.__collect_feature(feature)
        if flag:
            fea_data = np.array(self.feature_set)
            self.feature_set = []
            if True not in np.isnan(fea_data):
                result = self.model.predict(fea_data)
                ans = np.argmax(np.bincount(result))
                return True, GESTURE_LIST[ans]
            else:
                return True, ""
        return False, ""


class Decision:
    """
    决策类, 根据预测结果判断手势
    """

    def __init__(self, num_of_pred_frame):
        """

        :param num_of_pred_frame: 每次检测取几帧
        """
        self.num_of_pred_frame = num_of_pred_frame
        self.result_set = []

    def find_out_fingers(self, list_lms):
        """
        查找手指外部点坐标
        :param list_lms: 手指坐标
        :return: 手指坐标
        """
        hull_index = [0, 1, 2, 3, 6, 10, 14, 19, 18, 17]
        hull = cv2.convexHull(list_lms[hull_index], True)

        # 查找外部的点数
        ll = [4, 8, 12, 16, 20]
        out_fingers = []
        for i in ll:
            pt = (int(list_lms[i][0]), int(list_lms[i][1]))
            dist = cv2.pointPolygonTest(hull, pt, True)
            if dist < 0:
                out_fingers.append(i)
        return out_fingers

    def get_str_gesture(self, out_fingers, list_lms):
        """
        根据手指坐标判断手势
        :param out_fingers: 手指坐标
        :param list_lms: 手指坐标
        :return: 手势字符串
        """
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

    def predict(self, list_lms):
        """
        预测， 返回预测结果和是否完成预测
        :param list_lms:
        :return: True, ans or False, ""
        """
        if len(self.result_set) == self.num_of_pred_frame:
            # 找到result_set中重复最多的元素
            ans = max(set(self.result_set), key=self.result_set.count)
            self.result_set = []
            return True, ans
        else:
            self.result_set.append(self.get_str_gesture(self.find_out_fingers(list_lms), list_lms))
            return False, ""


class pose:
    def __init__(self, num_of_pred_frame):
        """

        :param num_of_pred_frame: 每次检测取几帧
        """
        self.num_of_pred_frame = num_of_pred_frame
        self.result_set = []

    def predict(self, list_lms):
        """
        预测， 返回预测结果和是否完成预测
        :param list_lms:
        :return: True, ans or False, ""
        """
        str_pose = ""
        angle_left_arm = calc_angle_feature([14, 12, 24], list_lms)
        angle_right_arm = calc_angle_feature([13, 11, 23], list_lms)
        angle_left_elow = calc_angle_feature([11, 13, 15], list_lms)
        angle_right_elow = calc_angle_feature([12, 14, 16], list_lms)

        if angle_left_arm < 0 and angle_right_arm < 0:
            str_pose = "LEFT_UP"
        elif angle_left_arm > 0 and angle_right_arm > 0:
            str_pose = "RIGHT_UP"
        elif angle_left_arm < 0 and angle_right_arm > 0:
            str_pose = "ALL_HANDS_UP"
            if abs(angle_left_elow) < 120 and abs(angle_right_elow) < 120:
                str_pose = "TRIANGLE"
        elif angle_left_arm > 0 and angle_right_arm < 0:
            str_pose = "NORMAL"
            if abs(angle_left_elow) < 120 and abs(angle_right_elow) < 120:
                str_pose = "AKIMBO"
        return str_pose



