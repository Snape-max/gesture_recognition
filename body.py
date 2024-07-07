import cv2
import mediapipe as mp
import numpy as np

from utils import calc_angle_feature


cap = cv2.VideoCapture(0)

mp_pose = mp.solutions.pose
mp_holistic = mp.solutions.holistic
drawing = mp.solutions.drawing_utils

pose = mp_pose.Pose(model_complexity=2,  # 选择人体姿态关键点检测模型，0性能差但快，2性能好但慢，1介于之间
                    smooth_landmarks=True,  # 是否选择平滑关键点
                    min_detection_confidence=0.5,  # 置信度阈值
                    min_tracking_confidence=0.5)  # 追踪阈值

from predict import body_recon

decision = body_recon(num_of_pred_frame=10)

res = ""

while True:
    ret, frame = cap.read()
    if ret:
        result = pose.process(frame)
        if result.pose_landmarks:
            landmark = result.pose_landmarks.landmark
            list_lms = []
            for i in range(33):
                list_lms.append([landmark[i].x, landmark[i].y])
            list_lms = np.array(list_lms)
            ret, ans = decision.predict(list_lms)
            if ans != "":
                res = ans
            cv2.putText(frame, res, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            drawing.draw_landmarks(frame, result.pose_landmarks, mp_holistic.POSE_CONNECTIONS)
        cv2.imshow('body', frame)
        key = cv2.waitKey(1)
        if key == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
