import os

from cs50 import SQL
import fileinput
import time
import re

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from os.path import join, dirname, realpath
from werkzeug.utils import secure_filename
from flask_session import Session
from tempfile import mkdtemp, gettempdir
import random
import secrets
import json

# use placenames db
db = SQL("sqlite:///placenames.db")


def searchFunc(filepath, db):
    testdict = {}
    with open(filepath, 'r') as file:
        rows = db.execute("SELECT * FROM PlaceHead")
        data = file.read()
        ## data = file.read().replace('\n', ' ')
        for row in rows:
            string = row["PLACE_NAME"]
            string = string.replace(' ', '.')
            expression = r"{0}\W".format(string)
            ##if len(re.findall(expression,data,flags=re.I)) != 0: (this regex flag looks for case insensitive expression)
            amount = len(re.findall(expression, data))
            if amount != 0:
                testdict[row["PLACE_NAME"]] = amount
            ##if re.search(expression, data):
                ##print("Match!")
        print(testdict)
        return(testdict)

def stringBuilder(PlaceName, Line):
    row = db.execute("SELECT * FROM Placenames WHERE Cleaned_Name = ?", PlaceName)
    try:
        objectid = row[0]["objectid"]
        name = row[0]["Place_Name"]
        hist = row[0]["Historic_County"]
        x = row[0]["lat"]
        y = row[0]["long"]
        line = Line
    except:
        print(PlaceName)

    hist1 = hist.strip()
    line = "Times found:" + str(line)
    temp = '{{"type":"Feature","properties":{{"objectid":{0},"Place_Name":"{1}","Historic_County":"{2}","lat":{3},"long":{4},"Line":"{5}"}},"geometry":{{"type":"Point","coordinates":[{6},{7}]}}}}'.format(objectid, name, hist1, x, y, line, y, x)
    return temp

def insertData(testdict, filepath):
    with open(filepath, 'w') as file:
        openStatement = 'var json_placenameslayer_1 = {"type":"FeatureCollection","name":"placenameslayer_1","crs":{"type":"name","properties":{"name":"urn:ogc:def:crs:OGC:1.3:CRS84"}}, "features":['
        endCap = ']}'
        index = 0
        file.write(openStatement.strip())
        for key in testdict:
            if index == 0:
                temp = stringBuilder(key, testdict[key])
                index += 1
            else:
                temp = ','
                temp += stringBuilder(key, testdict[key])
                index += 1
            temp = temp.strip()
            file.write(temp)
        file.write(endCap.strip())