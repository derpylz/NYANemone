# NYANemone

Adaptable video tracking software created for automated behavioural analyses of sea anemones.

## Features

NYANemone is a video tracking software, implemented in Python, using the openCV API. It is suitable for high throughput analyses, as almost no user interaction is required. In its current iteration, the software is optimised for tracking sea anemones, however, it can be easily adapted to track any moving organism. In fact, NYANemone is an adaptation of my previous tool, zfTracker, created to track the movement of adult and larval zebrafish.

## Getting Started

NYANemone runs across all platforms, which support Python, it was tested on Windows 10, Mac OS X and Linux (Ubuntu).

### Prerequisites

The following Python packages are required, in addition to a standard **Python 3** installation:

*   numpy
*   opencv3
*   imageio

In addition, **ffmpeg** needs to be installed.

### Installing

The easiest method of installing NYANemone is by downloading the latest compressed distribution archive from the dist folder in this repository. The current version is 1.0. After downloading, decompress the archive to any location on your drive.

In the folder nyanemone/external/data/ you will find a text file called ffmpeg_location.txt. If your ffmpeg installation is not in your PATH variable, write the location of the ffmpeg executable into the file.

Open a terminal and move to the location of the root folder (the folder containing the setup.py file, should be called something like: nyanemone-*yourOS*-*version*). Then run the following two commands:

```
python setup.py build
python setup.py install
```

The installed script should now be in the nyanemone/build/scripts-*pythonversion*/ folder.

## Usage

To run the tool, open a terminal and type `python nyanemone_larva.py` followed by a set of arguments.
Running `python nyanemone_larva.py -h` shows you a help message containing the usage and all possible arguments.

The minimal command for standard execution is:

```
python nyanemone_larva.py path/to/videofolder path/to/resultsfolder dateofexperiment symbiont
```

## Troubleshooting

| Problem | Possible solution |
| ------- | ----------------- |
| nyamemone_larva.py not found | cd to the nyanemone/build/scripts-*pythonversion*/ folder and type python ./nyanemone_larva.py |
| ffmpeg not found | Is ffmpeg installed and in your path / did you add its location to the ffmpeg_location.txt file? If yes, check if there is an empty line in the ffmpeg_location.txt file, this sometimes causes problems.
| some error after ffmpeg seems to have run | Check the temporary folder to see if there are converted video files. If not, try to run the ffmpeg command displayed by NYANemone without the `-hide_banner -loglevel panic` options to look for error messages

## Authors

Nils Trost - contact: nils.trost@hotmail.de

## Acknowledgements

* Susana Paredes Zúñiga
* Bruno Gideon Bergheim
