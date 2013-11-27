#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import walk
from mutagen.id3 import ID3
from mutagen.mp4 import MP4
from subprocess import call, STDOUT, PIPE


class Conversion():

    def __init__(self, path):

        print "CONVERSION"

        # Create a folder for the wave files
        input_path = path
        call(["mkdir", path + "wave/"])
        output_path = path + "wave/"

        self.any_to_wave(input_path, output_path)

    def any_to_wave(self, inp, out):
        # Browse through all files in directory inp
        for root, dirs, files in walk(inp):
            for fil in files:
                end = fil[len(fil)-3:len(fil)]
                # Check if the file is an audio file
                if end in ["mp3", "mp4", "m4a"]:
                    if end == "mp3":
                        # Extract MP3 tags
                        tag = ID3(inp + fil)
                    elif end == "mp4" or end == "m4a":
                        # Extract MP4 and M4A tags
                        mp4 = MP4(inp + fil)
                        tag = mp4.MP4Tags

                    # Check for tags and assign a variable
                    if "TIT2" in tag:
                        title = str(tag["TIT2"])
                    else:
                        title = ''
                    if "TPE1" in tag:
                        artist = str(tag["TIT2"])
                    else:
                        artist = ''
                    if "TALB" in tag:
                        album = str(tag["TALB"])
                    else:
                        album = ''
                    if "TCON" in tag:
                        genre = str(tag["TCON"])
                    else:
                        genre = ''
                    if "TDRC" in tag:
                        year = str(tag["TDRC"])
                    else:
                        year = ''
                    # Call ffmpeg in the terminal and save the wave file
                    # with the tags as file name (if there is no tag,
                    # use old file name and with empty separators)
                    if title + artist + album + genre + year == '':
                        call(["ffmpeg", "-i", inp + fil, "-ar", "11000",
                            out + fil[:len(fil)-4] + "-*--*--*--*-" + ".wav"],
                            stderr=STDOUT, stdout=PIPE)
                    else:
                        call(["ffmpeg", "-i", inp + fil, "-ar", "11000",
                            out + title
                            + "-*-" + artist
                            + "-*-" + album
                            + "-*-" + genre
                            + "-*-" + year
                            + ".wav"],
                            stderr=STDOUT, stdout=PIPE)

        print "Conversion successfully completed!"
