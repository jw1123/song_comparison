#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import walk, path
from time import sleep
from bregman.suite import os, Chromagram, HighQuefrencyChromagram, \
    HighQuefrencyLogFrequencySpectrum, HighQuefrencyMelSpectrum, \
    LinearFrequencySpectrum, LinearFrequencySpectrumCentroid, \
    LinearFrequencySpectrumSpread, LinearPower, LogFrequencySpectrum, \
    LogFrequencySpectrumCentroid, LogFrequencySpectrumSpread,\
    LowQuefrencyLogFrequencySpectrum, LowQuefrencyMelSpectrum, \
    MelFrequencyCepstrum, MelFrequencySpectrumCentroid, \
    MelFrequencySpectrumSpread, RMS, dBPower
from contextlib import closing
from wave import open as wopen
from numpy import arange, median, mean
from numpy import sum as npsum
from aubio import tempo, source
from ConfigParser import ConfigParser


class Extraction:

    def __init__(self, path_wave, song_collection):
        print "EXTRACTION"
        # List of all the features that can
        # be extracted so that they can be used as functions
        self.features_list = {'Chromagram': Chromagram,
        'HighQuefrencyChromagram': HighQuefrencyChromagram,
        'HighQuefrencyLogFrequencySpectrum': HighQuefrencyLogFrequencySpectrum,
        'HighQuefrencyMelSpectrum': HighQuefrencyMelSpectrum,
        'LinearFrequencySpectrum': LinearFrequencySpectrum,
        'LinearFrequencySpectrumCentroid': LinearFrequencySpectrumCentroid,
        'LinearFrequencySpectrumSpread': LinearFrequencySpectrumSpread,
        'LinearPower': LinearPower, 'LogFrequencySpectrum': LogFrequencySpectrum,
        'LogFrequencySpectrumCentroid': LogFrequencySpectrumCentroid,
        'LogFrequencySpectrumSpread': LogFrequencySpectrumSpread,
        'LowQuefrencyLogFrequencySpectrum': LowQuefrencyLogFrequencySpectrum,
        'LowQuefrencyMelSpectrum': LowQuefrencyMelSpectrum,
        'MelFrequencyCepstrum': MelFrequencyCepstrum,
        'MelFrequencySpectrumCentroid': MelFrequencySpectrumCentroid,
        'MelFrequencySpectrumSpread': MelFrequencySpectrumSpread,
        'RMS': RMS, 'dBPower': dBPower, 'BPM': 'BPM'}

        #__________________________________________________________
        path_data = path.dirname(path.realpath("configure.txt")) + "/configure.txt"
        #_________________________________________________________________

        config = ConfigParser()
        config.read(path_data)
        feat_dic = {}
        # Storing the parameter values and features from the
        # configuration file in a dictionary
        for feat in config.sections():
            i = 0
            for param in config.options(feat):
                if i == 0:
                    feat_dic.update({feat: {param: int(config.get(feat, param))}})
                else:
                    feat_dic[feat].update({param: int(config.get(feat, param))})
                i += 1

        mdbfeat = {}

        for feat in feat_dic:
            a = None
            b = ''
            # Convert parameters into a name,
            # to classify the extracted features
            if len(feat_dic[feat]) > 1:
                for i in feat_dic[feat]:
                    b += self.parameter_short({i: feat_dic[feat][i]})
                mdbfeat.update({feat: b})
            else:
                mdbfeat.update({feat: self.parameter_short(feat_dic[feat])})

        self.so = song_collection
        self.par_short = mdbfeat
        self.features = feat_dic

        self.extract(path_wave)

        # To iterate through the song database
        # and show all the song collections
        for s in self.so.find():
            print s

    def parameter_short(self, a):
        b = ''
        # Check for all the parameters and
        # combine them as abreviations
        for p in a:
            if p == "default" or 0:
                b = "default"
            else:
                if p == "sample_rate":
                    b += "s" + str(a[p])[:len(str(a[p]))-3]
                elif p == "nbpo":
                    b += "nb" + str(a[p])
                elif p == "ncoef":
                    b += "nc" + str(a[p])
                elif p == "lcoef":
                    b += "lc" + str(a[p])
                elif p == "lo":
                    b += "lo" + str(a[p])
                elif p == "hi":
                    b += "hi" + str(a[p])[:len(str(a[p]))-3]
                elif p == "nfft":
                    b += "nf" + str(a[p])
                elif p == "wfft":
                    b += "w" + str(a[p])
                elif p == "nhop":
                    b += "nh" + str(a[p])
                elif p == "log10":
                    b += "l10" + str(a[p])[0]
                elif p == "magnitude":
                    b += "m" + str(a[p])[0]
                elif p == "intensity":
                    b += "i" + str(a[p])[0]
                elif p == "onsets":
                    b += "o" + str(a[p])[0]
                else:
                    b += "v" + str(a[p])
        return b

    def BPM(self, path, param):
        """ Calculate the beats per minute (bpm) as a rhythm feature.
            path: path to the file
            param: dictionary of parameters
        """
        try:
            win_s = param['wfft']
            samplerate = param['sample_rate']
        except:
            win_s = 512                 # fft size
            samplerate = 11000

        hop_s = win_s / 2           # hop size

        s = source(path, samplerate, hop_s)
        samplerate = s.samplerate
        o = tempo("default", win_s, hop_s, samplerate)

        # Tempo detection delay, in samples
        # default to 4 blocks delay to catch up with
        delay = 4. * hop_s

        # List of beats, in samples
        beats = []

        # Total number of frames read
        total_frames = 0
        while True:
            samples, read = s()
            is_beat = o(samples)
            if is_beat:
                this_beat = int(total_frames - delay + is_beat[0] * hop_s)
                beats.append(this_beat)
            total_frames += read
            if read < hop_s:
                break

        # Convert samples to seconds
        beats = map(lambda x: x/float(samplerate), beats)

        bpms = [60./(b-a) for a, b in zip(beats[:-1], beats[1:])]

        if samplerate == 11000:
            b = median(bpms)*4
        elif samplerate == 22000:
            b = median(bpms)*2
        else:
            b = median(bpms)
        return b

    def sliding_window(self, x, coeff):
        """ The principle of the sliding window is the following:
            We have an array that we want to reduce by a certain factor
            (16 by default). We only reduce the array in the column
            dimension, as the row dimension is critical for certain
            features (as the 12 step chromagram). So we take the array
            and average over coeff + coeff/2 cases (50 percent overlapping)
            and store it as a new array.
            Example: if the initial shape of x is (50,1600), after the
            sliding window has been applied, its new shape is (50,100)
        """
        new_array = []
        # Determine the dimensions of x
        if x.shape != (x.shape[0],):
            for i in x:
                template = []
                for j in arange(int(len(i)/coeff)):
                    if(j != 0):
                        # If it is neither the first, nor the last case
                        template.append(float(npsum(i[j*coeff-coeff/2:(j+1)*coeff])/(coeff+coeff/2)))
                    elif j == int(len(i)/coeff)-1:
                        # Last case, filling up
                        template.append(float(npsum(i[j*coeff-coeff/2:])/len(i[j*coeff-coeff/2:])))
                    else:
                        # First case
                        template.append(float(npsum(i[:(j+1)*coeff])/coeff))
                new_array.append(template)
            xshape = (len(new_array),len(new_array[0]))
        else:
            template = []
            for j in arange(int(x.shape[0]/coeff)):
                if(j != 0):
                    template.append(float(npsum(x[j*coeff-coeff/2:(j+1)*coeff])/(coeff+coeff/2)))
                elif j == int(x.shape[0]/coeff)-1:
                    # Last case, filling up
                    template.append(float(npsum(x[j*coeff-coeff/2:])/len(x[j*coeff-coeff/2:])))
                else:
                    # First case
                    template.append(float(npsum(x[:(j+1)*coeff])/coeff))
            new_array = template
            xshape = (len(new_array),1)

        return new_array, xshape

    def extract_features(self, x):
        """ Extract all features and reducing them invoking the wind function.
            x: path to the file
            para: list of parameter dictionaries
        """
        fea_dic = {}

        # Recognize the features and launch their respective functions
        for f in self.features:
            if f != 'BPM':
                if self.features[f] != {"default": 0}:
                    # **para[i] gets the parameter dictionary and uses
                    # it as an argument for the bregman functions
                    fea_dic.update({f: self.features_list[f](x, **self.features[f])})
                else:
                    # Extraction with default values
                    fea_dic.update({f: self.features_list[f](x)})
            else:
                fea_dic.update({f: self.BPM(x, self.features[f])})

        fea_dic1 = {}
        # Convert the numpy arrays into binaries to store them in MongoDB
        # Change the sliding window reduction coefficient to your liking
        for fe in fea_dic:
            if 'Chromagram' in fe:
                d, s = self.sliding_window(fea_dic[fe].CHROMA, 16)
            elif fe == 'MelFrequencyCepstrum':
                d, s = self.sliding_window(fea_dic[fe].MFCC, 16)
            elif 'LinearFrequencySpectrum' in fe:
                d, s = self.sliding_window(fea_dic[fe].STFT, 16)
            elif fe == 'LinearPower' or fe == 'RMS' or fe == 'dBPower':
                d, s = self.sliding_window(fea_dic[fe].POWER, 16)
            elif fe == 'BPM':
                d = fea_dic[fe]
                s = (0, 0)
            else:
                d, s = self.sliding_window(fea_dic[fe].CQFT, 16)
            fea_dic1.update({fe: {"data": d, "row": s[0], "column": s[1],
                "parameters": self.features[fe]}})
        return fea_dic1



    def parameter_name(self, features_diction):
        # Combine the parameter name dictionary with the feature array
        # dictionary so as to have the final dictionary
        mdbfeat = {}
        for feat in self.par_short:
            mdbfeat.update({feat: [{self.par_short[feat]: features_diction[feat]}]})
        return mdbfeat

    def extract(self, direc):
        """ Iterating function, and inserting id, metadata and features to the collection.
            param: list of parameter dictionaries
        """
        i = 0

        for root, dirs, files in os.walk(direc):
            for file1 in files:
                if file1[len(file1)-3:] == "wav":
                    i += 1
                    w = wopen(direc+file1, "r")
                    # Exracting the file length
                    with closing(w) as f:
                        frame = f.getnframes()
                        rate = f.getframerate()

                    # Launch the actual extraction
                    dbfeat = self.parameter_name(self.extract_features(direc+file1))
                    # Split the file name in order to use all the metadata
                    meta = file1.split("-*-")

                    # Assign the metadata informations
                    if len(meta) == 5:
                        tit = meta[0]
                        art = meta[1]
                        alb = meta[2]
                        gen = meta[3]
                        yea = meta[4][:len(meta[4])-4]
                    elif len(meta) == 4:
                        tit = meta[0]
                        art = meta[1]
                        alb = meta[2]
                        gen = meta[3][:len(meta[3])-4]
                        yea = ''

                    if self.so.find({"metadata.title": tit}).count() == 0:
                        # If this particular song's collection does not
                        # exist, insert the dictionary
                        song_dictionary_insert = {
                                        'song_id': i,
                                        'metadata': {
                                        'title': tit,
                                        'artist': art,
                                        'album': alb,
                                        'genre': gen,
                                        'year': yea,
                                        'length': frame/float(rate)},
                                        'features': dbfeat}

                        self.so.insert(song_dictionary_insert)
                    else:
                        # If this particular song's collection already exists,
                        # then only update the feature dictionary
                        for k in dbfeat:
                            for par in dbfeat[k][0]:
                                a = "features."+k
                                self.so.update({"metadata.title": tit, "metadata.artist": art,
                                "metadata.album": alb}, {"$addToSet": {a: {par: dbfeat[k][0][par]}}})

                    w.close()
                    print i

        print "Extraction successfully completed!"
