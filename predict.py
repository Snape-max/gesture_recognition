import pickle

import cv2
import numpy as np
from sklearn.naive_bayes import GaussianNB

from utils import get_angle

GESTURE_LIST = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "GOOD", "BAD"]


class Model:
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
        self.feature_set.append(feature)
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
    def __init__(self, num_of_pred_frame):
        """

        :param num_of_pred_frame: 每次检测取几帧
        """
        self.num_of_pred_frame = num_of_pred_frame
        self.result_set = []

    def find_out_fingers(self, list_lms):
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

        if len(self.result_set) == self.num_of_pred_frame:
            # 找到result_set中重复最多的元素
            ans = max(set(self.result_set), key=self.result_set.count)
            self.result_set = []
            return True, ans
        else:
            self.result_set.append(self.get_str_gesture(self.find_out_fingers(list_lms), list_lms))
            return False, ""
