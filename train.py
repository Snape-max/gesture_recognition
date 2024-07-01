import pickle

fea_data_1 = pickle.load(open("./dataset/fea_data_1.pkl", "rb"))
for s in fea_data_1:
    print(s)

