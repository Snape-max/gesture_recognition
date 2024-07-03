import pickle
import time

import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB, MultinomialNB

num_of_angle_fea = 5
num_of_distance_fea = 9
data = pickle.load(open("./dataset/data_test_1.pkl", "rb"))
original_fea_data = np.array(data['fea_data'])
angle_fea = original_fea_data[:, :num_of_angle_fea]
distance_fea = original_fea_data[:, num_of_angle_fea:]
label = np.array(data['label'])
label_str = np.array(data['label_str'])

# 数据分别归一化
scaler = MinMaxScaler()  # 实例化
angle_fea = scaler.fit_transform(angle_fea)
distance_fea = scaler.fit_transform(distance_fea)
fea_data = np.concatenate((angle_fea, distance_fea), axis=1)

# fea_data = scaler.fit_transform(original_fea_data)

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(original_fea_data, label, test_size=0.3)

# 训练贝叶斯分类器
clf = MultinomialNB()
clf.fit(X_train, y_train)
print("训练集准确率：", clf.score(X_train, y_train))
print("测试集准确率：", clf.score(X_test, y_test))

clf.predict(X_test)

model = open("./model/model_{}.pkl" .format(str(time.time()).split('.')[0]), "wb")
pickle.dump(clf, model)
model.close()
