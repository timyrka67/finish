import numpy as np
import math
import cv2


class Track:
    tracks_count = 0

    def __init__(self, point):
        self.points = np.atleast_2d(np.array(point))
        self.id = Track.tracks_count
        Track.tracks_count += 1

    def add_point(self, point):
        self.points = np.vstack((self.points, np.array(point)))

    def dist_to_point(self, point):
        return  np.linalg.norm(self.points[-1] - point)

    def angle_to_point(self, point):
        v0 = np.array(self.points[-1]) - np.array(self.points[-2])
        v1 = np.array(point - np.array(self.points[-2]))
        angle = np.math.atan2(np.linalg.det([v0, v1]), np.dot(v0, v1))
        return math.fabs(np.degrees(angle))


class Tracking:
    def __init__(self):
        self.tracks = []
        self.finishers = []

    def clean(self):
        self.tracks = []

    def add_point(self, frame, point):
        if len(self.tracks) == 0:
            self.tracks.append(Track(point))
            if point[0]<40:
                self.finishers.append(point)
                self.tracks = []
            return;
        max_dist = 50
        best_id = 0
        for id, elem in enumerate(self.tracks):
            if(elem.dist_to_point(point)<max_dist):
                max_dist = elem.dist_to_point(point)
                best_id = id
        if(max_dist >= 50):
            if point[0]<40:
                self.finishers.append(point)
            else:
                self.tracks.append(Track(point))
        else:
            if point[0]<40:
                self.finishers.append(point)
                self.tracks.pop(best_id)
            else:
                self.tracks[best_id].add_point(point)

    def drawLines(self, frame):
        for elem in self.tracks:
            if(len(elem.points)>=2):
                cv2.line(frame, tuple(elem.points[-1]), tuple(elem.points[-2]), (255, 0, 0), 5)

    def drawFinishLine(self,frame, p1, p2):
        cv2.line(frame, tuple(p1), tuple(p2), (44, 44, 44), 2)

    def addFinisher(self, point):
        self.finishers =np.atleast_2d(self.finishers.append(point))

    def drawFinisher(self, frame):
        for point in self.finishers:
            cv2.putText(frame, "finish", tuple(point),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

