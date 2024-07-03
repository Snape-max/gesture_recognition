import pickle
import numpy as np
from sklearn.naive_bayes import GaussianNB

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


