import cv2


class camera:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)

    @property
    def frame(self):
        _, frame = self.cap.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame


class fakeTello:
    RESOLUTION_720P = 1

    def __init__(self):
        self.is_flying = False
        self.camera = camera()

    def connect(self):
        pass

    def set_video_resolution(self, x):
        pass

    def streamon(self):
        pass

    def get_frame_read(self):
        return self.camera

    def takeoff(self):
        self.is_flying = True
        pass

    def move_up(self, x):
        print("move {}cm".format(x))
        pass

    def land(self):
        self.is_flying = False
        pass

    def move_left(self, x):
        print("move {}cm".format(x))
        pass

    def move_right(self, x):
        print("move {}cm".format(x))
        pass


    def move_forward(self, x):
        print("move {}cm".format(x))
        pass

    def move_down(self, x):
        print("move {}cm".format(x))
        pass

    def send_command_without_return(self, x):
        pass

    def move_back(self, x):
        print("move {}cm".format(x))
        pass

    def emergency(self):
        pass

    def get_battery(self):
        return 80

    def get_height(self):
        return 20

    def get_temperature(self):
        return 30

    def flip_right(self):
        pass

    def flip_left(self):
        pass

    def flip_forward(self):
        pass
