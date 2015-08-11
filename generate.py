#!/usr/bin/env python
# coding=utf-8

from __future__ import print_function  # In case we're running with python2

import argparse
import os
import requests
import re
import sys
import pystache
import random
import shutil


FORMATIONS = [
    ([u'ailier droit', u'ailier gauche', u'arrière droit',
      u'arrière gauche', u'attaquant', u'attaquant',
      u'défenseur central', u'défenseur central',
      u'gardien', u'milieu de terrain', u'milieu de terrain'], 442),
    ([u'arrière droit', u'arrière gauche', u'attaquant', u'attaquant',
      u'attaquant', u'défenseur central', u'défenseur central', u'gardien',
      u'milieu de terrain', u'milieu de terrain', u'milieu de terrain'], 433),
    ([u'ailier droit', u'ailier gauche', u'arrière droit', u'arrière gauche',
      u'attaquant', u'défenseur central', u'défenseur central', u'gardien',
      u'milieu de terrain', u'milieu de terrain', u'milieu de terrain'], 451),
    ([u'arrière droit', u'arrière gauche', u'attaquant', u'défenseur central',
      u'défenseur central', u'défenseur central', u'gardien',
      u'milieu de terrain', u'milieu de terrain', u'milieu droit',
      u'milieu gauche'], 541)
]


class Sheet():
    def __init__(self, key):
        self.__endpoint = 'https://spreadsheets.google.com'
        self.__key = key

        self.__data = list()

        try:
            path = '/feeds/worksheets/{key}/public/basic?alt=json'.format(
                key=key)
            for entry in self.__requestData(path)['feed']['entry']:
                if entry['title']['$t'] != 'Feuille 1':
                    continue
                path = '/feeds/list/{key}/{sheetId}/public/values?alt=json'\
                    .format(key=key,
                            sheetId=entry['link'][len(entry['link']) - 1]
                                         ['href'].split('/').pop())

                self.__setData(self.__formatData([
                    {key[4:]: value['$t']
                        for key, value in entry.items()
                        if key[:4] == 'gsx$'}
                    for entry in self.__requestData(path)['feed']['entry']]))

        except requests.exceptions.RequestException as e:
            print(e, file=sys.stderr)
            sys.exit(1)

    def __requestData(self, path):
        r = requests.get(self.__endpoint + path)
        if r.status_code == 200:
            return r.json()
        raise requests.exceptions.RequestException(
            "Seems we can't find {0}".format(self.__key))

    def __setData(self, data):
        self.__data = data

    def __formatData(self, data):
        def getOrFalse(d, k):
            return len(d[k]) > 0 and dict(value=d[k].encode('utf-8')) or False

        def addNBSPs(s):
            for char in ['?', ':', '!']:
                s = s.replace(' {0}'.format(char), '&nbsp;{0}'.format(char))
            return s

        return [dict(
            id=int(d['id']),
            firstname=d['prenom'].encode('utf-8'),
            lastname=d['nom'].encode('utf-8'),
            place=d['poste'].encode('utf-8'),
            team=d['equipe'].encode('utf-8'),
            description=addNBSPs(d['description']).encode('utf-8'),
            picture=d['photo'].encode('utf-8')
        ) for d in data]

    def getData(self):
        return self.__data

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('key', metavar='key', type=str)
    parser.add_argument('--dest', type=str)
    parser.add_argument('--src', type=str)
    args = parser.parse_args()

    srcDir = os.path.dirname(os.path.realpath(__file__))
    destDir = os.path.join(srcDir, 'dist')

    srcDir = os.path.join(srcDir, 'src')
    if args.src is not None:
        srcDir = os.path.realpath(args.src)

    if args.dest is not None:
        destDir = os.path.realpath(args.dest)
    if not os.path.isdir(destDir):
        os.mkdir(destDir)

    print('Writing {0}...'.format(os.path.join(destDir, 'index.html')))
    with open(os.path.join(destDir, 'index.html'), 'w') as f:
        with open(os.path.join(srcDir, 'template.html'), 'r') as template:
            data = Sheet(args.key).getData()

            formation = 442
            places = sorted([d['place'].decode('utf-8').lower() for d in data])
            for FORMATION in FORMATIONS:
                intersect = [x for x, y in zip(FORMATION[0], places) if x == y]
                if len(intersect) == len(places):
                    formation = FORMATION[1]
                    break

            style = ''
            with open(os.path.join(srcDir, 'style.css')) as styleF:
                style = styleF.read()

            script = ''
            with open(os.path.join(srcDir, 'script.js')) as scriptF:
                script = scriptF.read()

            data = dict(joueurs=data,
                        formation='f{0}'.format(str(formation)),
                        style=style,
                        script=script)
            f.write(pystache.render(template.read(), data))
            print('\t[OK]')
