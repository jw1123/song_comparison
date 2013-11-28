===============================
Song Comparison
===============================

.. image:: https://badge.fury.io/py/song_comparison.png
    :target: http://badge.fury.io/py/song_comparison
    
.. image:: https://travis-ci.org/jw1123/song_comparison.png?branch=master
        :target: https://travis-ci.org/jw1123/song_comparison

.. image:: https://pypip.in/d/song_comparison/badge.png
        :target: https://crate.io/packages/song_comparison?version=latest


* This is a script to help extract audio features and to calculate distances between songs with choice parameters.
* All data is stored in a database of MongoDB, so you should download MongoDB.
* The script only works with wave files, being named in a way described later. You can give mp3 or m4a files (ID3 taged!) 
* to the script and it will convert them to wave files with ffmpeg for you. Make sure ffmpeg (file conversion) and mutagen (ID3 tag) are installed.
* For audio feature extraction, this script is using the bregman audio toolbox and aubio toolbox (for the rhythm) 
* which you have to download and install (make sure both work).
* There is also a set of packages for python: you should have installed numpy, matplotlib, pymongo

Prerequisites:

- python 2.7
- bregman
- aubio
- mongoDB
- ffmpeg
- mutagen
- numpy
- pymongo



Note:

To install aubio, download or clone the latest version on https://github.com/piem/aubio. If you are on a OS X 10.9, then open the wscript file and comment line 86 and 87 out. Follow the instructions from the README. If ./waf build does not work, then reconfigure using this command line: ./waf configure —-disable-sndfile —-disable-samplerate (for some reason, these packages are not necessary). Now it should build and install properly. As we are interested in the python bindings, go to the python folder and follow the instructions in the README. To install it type sudo python setup.py install after building is completed.


Features:
---------------------------------------------------------------------------------------

There is a list of features you can chose from to be extracted from your audio files.

Chromagram
HighQuefrencyChromagram
HighQuefrencyLogFrequencySpectrum
HighQuefrencyMelSpectrum
LinearFrequencySpectrum
LinearFrequencySpectrumCentroid
LinearFrequencySpectrumSpread
LinearPower
LogFrequencySpectrum
LogFrequencySpectrumCentroid
LogFrequencySpectrumSpread
LowQuefrencyLogFrequencySpectrum
LowQuefrencyMelSpectrum
MelFrequencyCepstrum (MFCC)
MelFrequencySpectrumCentroid
MelFrequencySpectrumSpread
RMS
dBPower
BPM


Paramaters:
---------------------------------------------------------------------------------------

For every feature, you can choose to set the following parameters to your liking. If you
don't set the values yourself, they will be set to the default values listed here.

'sample_rate': 44100, # The audio sample rate
'nbpo': 12,           # Number of Bands Per Octave for front-end filterbank
'ncoef' : 10,         # Number of cepstral coefficients to use for cepstral features
'lcoef' : 1,          # Starting cepstral coefficient
'lo': 62.5,           # Lowest band edge frequency of filterbank
'hi': 16000,          # Highest band edge frequency of filterbank
'nfft': 16384,        # FFT length for filterbank
'wfft': 8192,         # FFT signal window length
'nhop': 4410,         # FFT hop size
'log10': False,       # Whether to use log output
'magnitude': True,    # Whether to use magnitude (False=power)
'intensify' : False,  # Whether to use critical band masking in chroma extraction
'onsets' : False,     # Whether to use onset-synchronus features
'verbosity' : 1       # How much to tell the user about extraction




Usage of document type toolbox:

The document toolbox uses a configuration file to retrieve the features you want to extract and the parameters to each feature. Edit the configuration file likewise to this model (if you want the default parameters values, just write default=0):

[Feature]
parameter1=x
parameter2=y
etc.

Example:

[MelFrequencyCepstrum]
sample_rate=22000
ncoef=5



Type the following command into your terminal to use the document toolbox: python main.py -(-)option (argument) (path)
The following options are available:
-c, --conversion		    : conversion of mp4 and mp3 files to wave files
-e, --extraction            : feature extraction of either a new set or adding features to a set
-d, --distance              : calculate the distance between each song
-g, --graphdist             : creates a graphml file with song nodes and distance edges
NOTE: If you use conversion or extraction, you have to add the path to the file with your mp4/mp3 files or wave files respectively
EXAMPLE: python main.py -e /Users/myname/Document/wave/




* Free software: BSD license
* Documentation: http://song_comparison.rtfd.org.

Features
--------

* TODO