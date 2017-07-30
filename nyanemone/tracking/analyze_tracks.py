"""module analyzes tracks generated by cv_tracking.py"""

import colorsys
import os
from collections import deque

import numpy as np

import cv2


def distance(pts):
    """calculates distance between two points"""
    pt1 = pts[0]
    pt2 = pts[1]
    x_dist = pt1[0] - pt2[0]
    y_dist = pt1[1] - pt2[1]
    return np.sqrt(x_dist ** 2 + y_dist ** 2)


def mean(pts):
    """calculates mean coordinates of track points"""
    avg = []
    for i in zip(*pts):
        avg.append(int(np.mean(i)))
    return tuple(avg)


def median(pts):
    """calculates median coordinates of track points"""
    mdn = []
    for i in zip(*pts):
        mdn.append(int(np.median(i)))
    return tuple(mdn)


def smooth_track(track, method=mean):
    """smooths the track dynamically depending on the distance traveled within the window"""
    wd = deque(maxlen=10)
    smoothed_track = []
    for pt in track:
        if len(wd) == 10:
            d_pts = deque(maxlen=2)
            dist = 0
            for d_pt in wd:
                if len(d_pts) == 2:
                    dist += distance(d_pts)
                d_pts.append(d_pt)
            if dist < 10:
                smoothed_track.append(method(wd))
            else:
                smoothed_track += list(wd)
            wd.clear()
        wd.append(pt.coords)
    if 10 >= len(wd) > 0:
        smoothed_track.append(method(wd))
    return smoothed_track


class Analysis:
    """class contains inner and outer tracks,
    methods for computing the distance and times on tracks
    and to save an image of the tracks"""
    def __init__(self, tracks, fps=1, px_size=0.006):
        self.fps = fps
        self.px_size = px_size
        self.tracks = tracks

    def save_track_image(self, temp_dir, out_dir):
        """saves tracks to image of mask"""
        image = cv2.imread(os.path.join(temp_dir, 'crop.tiff'))
        for i in range(len(self.tracks)):
            color = colorsys.hsv_to_rgb(i / len(self.tracks), 1.0, 1.0)
            r = int(color[0] * 255)
            g = int(color[1] * 255)
            b = int(color[2] * 255)
            for idx in range(1, len(self.tracks[i])):
                if self.tracks[i][idx - 1] is None or self.tracks[i][idx] is None:
                    continue
                cv2.line(image, self.tracks[i][idx - 1], self.tracks[i][idx], (r, g, b), 1)
        cv2.imwrite(os.path.join(out_dir, "tracks.tiff"), image)

    def save_stats(self, path, name, date, sym, dpf, dpi, fps, frames):
        """saves stats to meta output"""
        all_tracks = {}
        tot_dist = 0
        for idx in range(len(self.tracks)):
            for point in self.tracks[idx]:
                # list of Point object and index of track
                pts_at_frame = all_tracks.get(point.frame, [])
                pts_at_frame.append([point, idx])
                all_tracks[point.frame] = pts_at_frame
        static_time_l = []
        is_static = False
        static_time = 0
        first = True
        for frame in sorted(all_tracks):
            for pt in all_tracks[frame]:
                tot_dist += pt[0].distance
                if first:
                    first = False
                    static_pt = pt
                    continue
                dist_to_static = distance([static_pt[0].coords, pt[0].coords])
                if dist_to_static <= 15:
                    if is_static:
                        static_time += 1
                    else:
                        is_static = True
                        static_time = 1
                else:
                    if static_time == 0:
                        continue
                    static_time_l.append(static_time)
                    static_time = 0
                    is_static = False
                    static_pt = pt

        time = frames / fps
        avg_speed = tot_dist / time
        avg_stat_time = 0
        if len(static_time_l) > 0:
            avg_stat_time = np.mean(static_time_l) / fps

        with open(path, 'a') as out:
            out.write(str(name) + '\t')
            out.write(str(date) + '\t')
            out.write(str(sym) + '\t')
            out.write(str(dpf) + '\t')
            out.write(str(dpi) + '\t')
            out.write(str(avg_speed) + '\t')
            out.write(str(tot_dist) + '\t')
            out.write(str(avg_stat_time) + '\n')

    def save_track(self, out_dir, video_name):
        """saves track points to file"""
        all_tracks = {}
        for idx in range(len(self.tracks)):
            for point in self.tracks[idx]:
                # list of Point object and index of track
                pts_at_frame = all_tracks.get(point.frame, [])
                pts_at_frame.append([point, idx])
                all_tracks[point.frame] = pts_at_frame

        # for header
        first = True
        with open(os.path.join(out_dir, "{}_track_points.txt".format(video_name)), 'w') as out:
            for frame in sorted(all_tracks):
                if first:
                    out.write("frame\ttrack\tx\ty\tdistance\n")
                    first = False
                for pt in all_tracks[frame]:
                    out.write(str(frame) + '\t')
                    out.write(str(pt[1]) + '\t')
                    out.write(str(pt[0].coords[0]) + '\t')
                    out.write(str(pt[0].coords[1]) + '\t')
                    out.write(str(pt[0].distance) + '\n')
