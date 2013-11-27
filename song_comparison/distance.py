#!/usr/bin/env python
# -*- coding: utf-8 -*-

from numpy import linalg, array, arange, sqrt, concatenate
from time import sleep


class Distance:

    def __init__(self, song_collection, distance_collection):

        print "DISTANCE CALCULATION"
        #___________________________________________________
        # Change the coefficients for the features you chose
        coeff = [0.3, 0.3, 0.1, 0.2]   # ###REPLACE####
        #___________________________________________________
        self.so = song_collection
        self.di = distance_collection

        self.iterating(coeff)

        # To iterate and show all collections
        # of the distance database
        for d in self.di.find():
            print d

    def iterating(self, coeff):
        s = self.so.find(timeout=False)
        r = self.so.find(timeout=False)
        ski = 1
        j = 1
        for song1 in s:
            # Compare a song only to other songs that
            # have a higher song_id, thus skip the
            # songs with a lower id
            r.skip(ski)
            for song2 in r:
                # Check if both songs have the same number of features,
                # if not, they cannot be compared
                if song1['features'].keys().sort() == song2['features'].keys().sort():
                    # Calling the function that runs through all the features
                    # and calls the distance calculation function
                    distance_dict, weight = self.browse_features(song1, song2, coeff)
                    # Only consider pairs that lie beneath a certain threshold
                    if weight < 10.0:
                        # Check if the collection already exists, if not,
                        # insert the dictionary
                        if type(self.di.find_one({"source": song1['song_id']})) != dict or\
                         type(self.di.find_one({"source": song2['song_id']})) != dict:
                            self.insert_dictionary(song1, song2, distance_dict, weight)
                        # Check which song is the source and which song is the target
                        elif self.di.find_one({"source": song1['song_id']})['target'] == song2["song_id"]:
                            self.set_dictionary(song1, song2, distance_dict, weight)
                        elif self.di.find_one({"source": song2['song_id']})['target'] == song1["song_id"]:
                            self.set_dictionary(song2, song1, distance_dict, weight)
                        print j
                        j += 1
                else:
                    print "Songs need to have the same features"
                    print song1['metadata']['title'], ": ", song1['features']
                    print song2['metadata']['title'], ": ", song2['features']
                    break
            ski += 1
            r.rewind()
        print "Distance calculation successfully completed!"

    def insert_dictionary(self, song1, song2, distance_dict, weight):
        # Creating a dictionary that is inserted in
        # the distance database
        distance_insert_dictionary = {
            'source': song1['song_id'],
            'target': song2['song_id'],
            'feature_distance': distance_dict,
            'weight': weight}
        self.di.insert(distance_insert_dictionary)

    def set_dictionary(self, song1, song2, distance_dict, weight):
        # For an existing collection, a query dictionary
        # allows to find the right collection and the
        # set dictionary replaces the existing distance
        # dictionary
        query_dictionary = {
            'source': song1['song_id'],
            'target': song2['song_id']}
        set_dictionary = {
            'feature_distance': distance_dict,
            'weight': weight}
        self.di.update(query_dictionary, {"$set": set_dictionary})

    def browse_features(self, song1, song2, coeff):
        distance_dict = {}
        summe, dd, ddd, ii = 0, 0, 0, 0
        l = max(song1['metadata']['length'],
                song2['metadata']['length'])
        # Browsing through all features
        for i in song1['features']:
            jii = 0
            # Browsing through all parameter names
            for k in arange(len(song1['features'][i])):
                for h in song1['features'][i][k]:
                    a = song1['features'][i][k][h]['data']
                    b = song2['features'][i][k][h]['data']
                    # Checking the type of features a and b
                    # If float => bpm_comparison
                    # If not => array comparison
                    if type(a) == float and type(b) == float:
                        dd = self.bpm_comparison(a, b)/l
                    else:
                        dd = self.distance_calculation(a, b)/l
                    # Assign the correct coefficient to the
                    # matching feature and multiply the
                    # calculated distance with it
                    if i == 'MelFrequencyCepstrum':
                        ddd = coeff[0]*dd
                    elif i == 'LinearPower':
                        ddd = coeff[1]*dd
                    elif i == 'BPM':
                        ddd = coeff[2]*dd
                    elif i == 'Chromagram':
                        ddd = coeff[3]*dd
                    else:
                        ddd = dd
                    # Check if the feature already exists in the dictionary,
                    # if not (jii == 0) then create the field, if yes then
                    # append the parameter dictionary to the existing list
                    if jii == 0:
                        distance_dict.update({i: [{h: dd}]})
                    else:
                        distance_dict[i].append({h: dd})

                    jii += 1
                    summe += ddd
                    ii += 1
        # Return the distance dictionary and the weight
        return distance_dict, summe/ii

    def bpm_comparison(self, x, y):
        # Compare two bpm's, if they are close to each
        # other or close to the multiple of each other,
        # then the bpm distance is reduced by a factor
        # of 4
        if x % y < 6:
            return abs(x-y)*0.25
        else:
            return abs(x-y)

    def distance_calculation(self, x, y):
        # Determine which list is longer and invoking the reshaping function
        # to even their length (otherwise we cannot compare their values)
        p = array(x)
        q = array(y)

        if p.shape > q.shape:
            d = self.reshape(p, q)
            return d
        elif p.shape < q.shape:
            d = self.reshape(q, p)
            return d
        elif p.shape == q.shape:
            d = linalg.norm(p-q)
            return d
        else:
            return 0

    def reshape(self, b, a):
        # Reshaping and filling of the smaller array
        template = array([])
        new_array = []

        # Check if both arrays are unidimensional or not
        # If the first dimension of the arrays are unequal,
        # we have one dimensional arrays
        # This is due to the Bregman extraction tool, which
        # has an already set number of rows for two dimensional
        # arrays (ex. all MFCC have 95 rows)
        if b.shape[0] == a.shape[0]:
            x = b.shape[1]
            l = int(x/a.shape[1])
            # The smaller array has an l-times less columns
            # Run through all rows (for i in a)
            for i in a:
                template = i
                # "Multiply" l times the columns
                for j in arange(l-1):
                    template = concatenate([template, i])
                # Fill up with the rest
                template = concatenate([template, i[:x-len(template)]])
                new_array.append(template)
        else:
            # Same principle as above, only with a one dimensional
            # array
            x = b.shape[0]
            l = int(x/a.shape[0])
            for j in arange(l):
                template = concatenate([template, a])
            template = concatenate([template, a[:x-len(template)]])
            new_array.append(template)

        return linalg.norm(b-array(new_array))
