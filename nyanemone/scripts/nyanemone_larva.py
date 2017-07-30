#!python
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 2 2016

@author: Nils Jonathan Trost

Script that tracks larvae in circular arenas.

Needs ffmpeg and FIJI to run.
"""

import argparse
import os
from datetime import datetime

import errno

import shutil

from nyanemone.external.runffmpeg import Ffmpeg
from nyanemone.tracking.analyze_tracks import Analysis
from nyanemone.tracking.cv_tracking import Video


def silent_remove(filename):
    """removes file without error on non existing file"""
    try:
        os.remove(filename)
    except OSError as err:
        if err.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
            raise  # re-raise exception if a different error occurred


def prepare_vid(video_name, infile, temp_dir):
    """get FIJI compatible avi from video"""
    ffmpeg = Ffmpeg(infile, temp_dir + video_name)
    ffmpeg.pix_fmt = "nv12"
    ffmpeg.f = "avi"
    ffmpeg.vcodec = "rawvideo"
    ffmpeg.run()


def main():
    """main function to track larvae"""
    args = get_arguments()
    # get all file names and directories ready
    out_dir, temp_dir, video_bases, videos = housekeeping(args)
    for idx in range(len(videos)):

        infile = videos[idx]
        video_name_base = video_bases[idx]

        # make directory for temporary results
        converted_name = video_name_base + "_c.avi"
        # convert video to raw avi format
        prepare_vid(converted_name, infile, temp_dir)
        # track the segmented video
        vid = Video(os.path.join(temp_dir, converted_name))
        tracks = vid.track(args.show_nyan)

        analysis = Analysis(tracks)
        analysis.save_track(out_dir, video_name_base)
        analysis.save_stats(os.path.join(out_dir, 'stats.txt'),
                            video_name_base,
                            args.date,
                            args.symbiont,
                            args.dpf,
                            args.dpi,
                            args.fps,
                            args.end_frame-args.start_frame)

        if args.save_track_image:
            # save track image to file
            analysis.save_track_image(temp_dir, out_dir)

    if not args.keep_temp:
        shutil.rmtree(temp_dir)
        for video_name_base in video_bases:
            silent_remove(os.path.join(out_dir, "SEG_" + video_name_base + ".avi"))


def get_arguments():
    parser = argparse.ArgumentParser(description="Tracks anemones")
    # add options for argument parser
    parser.add_argument("in_path",
                        help="Path to the video directory.")
    parser.add_argument("out_path",
                        help="Directory for results. Should be empty.")
    parser.add_argument("date", help="experiment date as string in quotes")
    parser.add_argument("symbiont", help="Used symbiont")
    parser.add_argument("-x", "--keep_temp", action="store_true",
                        help="Keep temporary folder after execution.")
    parser.add_argument("-i", "--save_track_image", action="store_true",
                        help="Save images of tracked paths.")
    parser.add_argument("--median", action="store_true",
                        help="Use median intensity projection for segmentation.")
    parser.add_argument("-s", "--start_frame", help="first frame of video",
                        default=1, type=int)
    parser.add_argument("-e", "--end_frame", help="last frame of video",
                        default=600, type=int)
    parser.add_argument("--dpf", help="Days post fertilization",
                        default=0, type=int)
    parser.add_argument("--dpi", help="Days post infection",
                        default=0, type=int)
    parser.add_argument("--fps", help="Frames per second",
                        default=1, type=float)
    parser.add_argument("-n", "--show_nyan", action="store_true",
                        help="show nyanemone rainbow while executing.")
    # parse arguments from command line
    args = parser.parse_args()
    return args


def housekeeping(args):
    """creates variables for videos and directories"""
    in_dir = os.path.abspath(args.in_path)
    videos = []
    for f in os.listdir(in_dir):
        if os.path.isfile(os.path.join(in_dir, f)):
            videos.append(os.path.join(in_dir, f))
    video_bases = []
    for v in videos:
        video_bases.append(os.path.splitext(os.path.basename(v))[0])
    out_dir = os.path.abspath(args.out_path)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    with open(os.path.join(out_dir, 'stats.txt'), 'w') as out:
        out.write('video\t')
        out.write('date\t')
        out.write('symbiont\t')
        out.write('dpf\t')
        out.write('dpi\t')
        out.write('average velocity [px/s]\t')
        out.write('total distance\t')
        out.write('average static time\n')
    if not out_dir.endswith('/'):
        out_dir += '/'
    # make directory for temporary results
    temp_dir = os.path.join(out_dir, "temp/")
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    return out_dir, temp_dir, video_bases, videos


if __name__ == '__main__':
    start = datetime.now()
    main()
    end = datetime.now()
    print("\nExecuted in " + str(end - start))
