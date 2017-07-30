"""tracks larvae on previously segmented video"""

import numpy as np
import imageio
import colorsys
from collections import deque

import cv2


def get_colors(i, pt_buffer):
    color = colorsys.hsv_to_rgb(i / len(pt_buffer), 1.0, 1.0)
    r = int(color[0] * 255)
    g = int(color[1] * 255)
    b = int(color[2] * 255)
    return b, g, r


class Point:
    """class to store points on tracks,
    keeps track of the last detected point to calculate distance"""
    def __init__(self, coords, area, frame, prev=None, norm_area=5, a_weight=4, d_weight=1):
        # coordinates of the center of the detected spot
        self.coords = coords
        # area of the detected spot
        self.area = area
        # standard area for score calculation
        self.norm_area = norm_area
        # frame in video
        self.frame = frame
        self.a_weight = a_weight
        self.d_weight = d_weight
        # if point is first on track, skip distance calculation
        if not prev:
            self.score = 0
            self.distance = 0
        else:
            x_dist = self.coords[0] - prev.coords[0]
            y_dist = self.coords[1] - prev.coords[1]
            self.distance = np.sqrt(x_dist**2 + y_dist**2)
            # score is calculated from area of spot and distance to previous point
            self.score = (self.a_weight * (1 - abs(self.norm_area - self.area)))+(1 - self.d_weight * self.distance)

    # functions to make sorting of spots by score possible
    def __repr__(self):
        return "Point at %i:%i" % self.coords

    def __lt__(self, other):
        return self.score < other.score

    def __le__(self, other):
        return self.score <= other.score

    def __gt__(self, other):
        return self.score > other.score

    def __ge__(self, other):
        return self.score >= other.score

    def __eq__(self, other):
        return self.score == other.score

    def __ne__(self, other):
        return self.score != other.score


class Video:
    """stores the video file and contains tracking method"""
    def __init__(self, path):
        # dictionary for points on the track
        # 'key' is the frame of the video; 'value' is a Point object
        self.pts = {}
        # counts the frame in the video
        self.counter = 0
        # bool for special case on first frame
        self.previous_frame = None
        # read the avi file
        self.video = imageio.get_reader(path, 'ffmpeg')
        # tracks is a list with lists for the individual track points
        self.tracks = [[]]
        self.skipped_frames = 0
        self.segmentation = None

    def segment(self):
        """method to segment video"""
        frames = []
        for i, frame in enumerate(self.video):
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            frames.append(frame)
        frames = np.array(frames)
        avg = frames.mean(axis=0)
        avg_blur = cv2.GaussianBlur(avg, (0, 0), 3)
        segmentation = []
        cv2.startWindowThread()
        cv2.namedWindow("segmentation")
        for frame in frames:
            sub = (avg_blur - 30) - cv2.GaussianBlur(frame, (0, 0), 3)
            segmentation.append(sub)
            cv2.imshow("segmentation", sub)
            cv2.waitKey(1)
        self.segmentation = np.array(segmentation)

    def track(self, show_nyan=False):
        """method to track spots in the video"""
        empty = None
        frames = []
        frames_bw = []
        for i, frame in enumerate(self.video):
            if empty is None:
                empty = np.zeros(frame.shape, np.uint8)
            frame_bw = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            frames.append(frame)
            frames_bw.append(frame_bw)
        frames_bw = np.array(frames_bw)
        avg = frames_bw.mean(axis=0)
        avg_blur = cv2.GaussianBlur(avg, (0, 0), 3)
        if show_nyan:
            cv2.startWindowThread()
            cv2.namedWindow("segmentation")
            pt_buffer = deque(maxlen=1000)
        for idx in range(len(frames_bw)):
            frame = frames_bw[idx]
            sub = (avg_blur - 30) - cv2.GaussianBlur(frame, (0, 0), 3)
            # iterate over frames in video
            if np.array_equal(empty, sub):
                # skip empty frames
                self.counter += 1
                self.skipped_frames += 1
                print(self.skipped_frames)
                continue
            # create mask with the detected spots from the frame
            mask = cv2.inRange(sub, 1, 256)
            mask = cv2.dilate(mask, None, iterations=1)
            mask = cv2.erode(mask, None, iterations=1)
            # find contours in the video
            contours = cv2.findContours(mask.copy(),
                                        cv2.RETR_EXTERNAL,
                                        cv2.CHAIN_APPROX_SIMPLE)[-2]
            if len(contours) > 0:
                if self.previous_frame is None:
                    # for the first frame in the video, just find the largest contour in the mask
                    c = max(contours, key=cv2.contourArea)
                    # compute center point
                    m = cv2.moments(c)
                    try:
                        center = (int(m["m10"] / m["m00"]), int(m["m01"] / m["m00"]))
                    except ZeroDivisionError:
                        continue
                    # add point to the points dictionary
                    self.pts[self.counter] = Point(center, cv2.contourArea(c), self.counter)
                    self.previous_frame = self.counter
                else:
                    # make a list of possible spots and choose the one with the highest score
                    candidate_pts = []
                    for c in contours:
                        m = cv2.moments(c)
                        try:
                            center = (int(m["m10"] / m["m00"]), int(m["m01"] / m["m00"]))
                        except ZeroDivisionError:
                            continue
                        candidate_pts.append(Point(center,
                                                   cv2.contourArea(c),
                                                   self.counter,
                                                   self.pts[self.previous_frame]))
                    if len(candidate_pts) >= 1:
                        # add the best spot to the points dictionary
                        c = sorted(candidate_pts)[-1]
                        self.pts[self.counter] = c
                        self.previous_frame = self.counter
                    else:
                        self.skipped_frames += 1
            if show_nyan:
                try:
                    pt_buffer.append(self.pts[self.counter].coords)
                    cv2.circle(frames[idx], self.pts[self.counter].coords, 15, (0, 0, 255), 1)
                    for j in range(1, len(pt_buffer)):
                        b, g, r = get_colors(j, pt_buffer)
                        if pt_buffer[j - 1] is None or pt_buffer[j] is None:
                            continue
                        cv2.line(frames[idx], pt_buffer[j - 1], pt_buffer[j], (b, g, r), 1, cv2.LINE_AA)
                    cv2.imshow("segmentation", frames[idx])
                    cv2.waitKey(1)
                except KeyError:
                    pass
            self.counter += 1

        # after finding all spots, split tracks with gaps of more than 10 frames
        prev_key = 0
        curr_track = 0
        for key in sorted(self.pts):
            if (key - prev_key) > 10:
                self.tracks.append([])
                curr_track += 1
            self.tracks[curr_track].append(self.pts[key])
            prev_key = key

        # delete tracks with less than 2 points
        tracks = [t for t in self.tracks if len(t) >= 2]
        self.tracks = tracks

        return self.tracks
