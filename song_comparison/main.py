#!/usr/bin/env python
# -*- coding: utf-8 -*-


from sys import argv
from timeit import timeit
from getopt import getopt
from subprocess import call
from pymongo import Connection
from time import sleep

# print timeit("Distance()", setup="from distance import Distance", number=2)

class Main():
    def __init__(self):
        try:
            con = Connection()
        except:
            call(["osascript", "-e", 'tell app "Terminal" to do script "mongod"'])
            sleep(3)
            con = Connection()
        #__________________________________________________________________________
        # Change the name of the database and collections to your liking
        db = con.feature_extraction_test                        # #####REPLACE#####
        song_features = db.song_features_collection             # #####REPLACE#####
        distance_features = db.distance_features_collection     # #####REPLACE#####
        #__________________________________________________________________________

        options, rem = getopt(argv[1:], 'c:e:d:g:h', ['conversion=',
            'extraction=', 'distance', 'graphdist', 'help'])

        for opt, arg in options:
            if opt in ('-c', '--conversion'):
                from conversion import Conversion
                c = Conversion(arg)
            elif opt in ('-e', '--extraction'):
                from extraction import Extraction
                e = Extraction(arg, song_features)
            elif opt in ('-d', '--distance'):
                from distance import Distance
                d = Distance(song_features, distance_features)
            elif opt in ('-g', '--graphdist'):
                from graphdist import Graphdist
                g = Graphdist(song_features, distance_features)
            elif opt in ('-h', '--help'):
                print """The following options are available:
                -c, --conversion mp3/m4a
                =>  conversion of mp4 and mp3 files to wave files

                -e, --extraction
                =>  feature extraction of either a new set or
                    adding features to a set

                -d, --distance
                =>  calculate the distance between each song

                -g, --graphdist
                => creates a graphml file with song nodes and distance edge

                NOTE: If you use conversion or extraction, you have to add
                the path to the file with your mp4/mp3 filesor wave files
                respectively
                EXAMPLE: python main.py -e /Users/myname/Document/wave/
                """

if __name__ == "__main__":
    m = Main()

