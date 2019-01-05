#!/usr/bin/python3

import sys # noqa # pylint: disable=unused-import
import argparse
import urllib
import os # noqa # pylint: disable=unused-import
import xmltodict # noqa # pylint: disable=unused-import
import logging
import json
import re

from config import cfg


def entry():
    """ Entry to program, parses arguments"""
    parser = argparse.ArgumentParser(description='Get type of dvd--movie or tv series')
    parser.add_argument('-t', '--title', help='Title', required=True)
    # parser.add_argument('-k', '--key', help='API_Key', dest='omdb_api_key', required=True)

    return parser.parse_args()


def getdvdtype(disc):
    """ Queries OMDbapi.org for title information and parses if it's a movie
        or a tv series """

    dvd_title = disc.videotitle
    year = disc.videoyear
    needs_new_year = False
    omdb_api_key = cfg['OMDB_API_KEY']

    logging.debug("Title: " + dvd_title + " | Year: " + year)

    dvd_title_clean = cleanupstring(dvd_title)

    if year is None:
        year = ""

    logging.debug("Calling webservice with title: " + dvd_title_clean + " and year: " + year)
    dvd_type = callwebservice(omdb_api_key, dvd_title_clean, year)
    logging.debug("dvd_type: " + dvd_type)

    # handle failures
    # this is a little kludgy, but it kind of works...
    if (dvd_type == "fail"):

        # first try submitting without the year
        logging.debug("Removing year...")
        dvd_type = callwebservice(omdb_api_key, dvd_title_clean, "")
        logging.debug("dvd_type: " + dvd_type)

        if dvd_type != "fail":
            # that means the year is wrong.
            needs_new_year = True

        if dvd_type == "fail":
            # second see if there is a hyphen and split it
            if dvd_title.find("-") > -1:
                dvd_title_slice = dvd_title[:dvd_title.find("-")]
                dvd_title_slice = cleanupstring(dvd_title_slice)
                logging.debug("Trying title: " + dvd_title_slice)
                dvd_type = callwebservice(omdb_api_key, dvd_title_slice, year)
                logging.debug("dvd_type: " + dvd_type)

            # if still fail, then try slicing off the last word in a loop
            while dvd_type == "fail" and dvd_title_clean.count('+') > 0:
                dvd_title_clean = dvd_title_clean.rsplit('+', 1)[0]
                logging.debug("Trying title: " + dvd_title_clean)
                dvd_type = callwebservice(omdb_api_key, dvd_title_clean, year)
                logging.debug("dvd_type: " + dvd_type)

    if needs_new_year:
        #     #pass the new year back to bash to handle
        #     global new_year
        #     return dvd_type + "#" + new_year
        return (dvd_type, new_year)
    else:
        #     return dvd_type
        return (dvd_type, year)


def cleanupstring(string):
    # clean up title string to pass to OMDbapi.org
    string = string.strip()
    
    string = re.sub("[^A-Za-z0-9\ _-]+", "+", string)
    
    for pat in cfg['TITLE_IGNORE_WORDS']:
        string = re.sub(pat, "", string)
        
    return string


def callwebservice(omdb_api_key, dvd_title, year=""):
    """ Queries OMDbapi.org for title information and parses if it's a movie
        or a tv series """

    logging.debug("***Calling webservice with Title: " + dvd_title + " and Year: " + year)
    try:
        params = {'t' : dvd_title, 'y' : year, 'plot' : 'short', 'apikey' : omdb_api_key}
        strurl = "http://www.omdbapi.com/?"+urllib.parse.urlencode(params, doseq=False, safe='', encoding=None, errors=None, quote_via=urllib.parse.quote_plus)
        #strurl = "http://www.omdbapi.com/?t={1}&y={2}&plot=short&r=json&apikey={0}".format(omdb_api_key, dvd_title, year)
        logging.debug(strurl.replace(omdb_api_key,'key_hidden'))
        dvd_title_info_json = urllib.request.urlopen(strurl).read()
    except Exception:
        logging.debug("Webservice failed")
        return "fail"
    else:
        doc = json.loads(dvd_title_info_json.decode())
        if doc['Response'] == "False":
            logging.debug("Webservice failed with error: " + doc['Error'])
            return "fail"
        else:
            global new_year
            new_year = doc['Year']
            logging.debug("Webservice successful.  New Year is: " + new_year)
            return doc['Type']


def main(disc):        

    logging.debug("Entering getvideotype module")
    dvd_type, year = getdvdtype(disc)
    return(dvd_type, year)


# 
# dvd_title_clean = "THE DARK KNIGHT"
# year = "2008"
# omdb_api_key = "6ca2f025"
# 
# #dvd_type = callwebservice(omdb_api_key, dvd_title_clean, year)
# 
# 
# 
# #strurl = "http://www.omdbapi.com/?t={1}&y={2}&plot=short&r=json&apikey={0}".format(omdb_api_key, dvd_title_clean, year)
# 
# params = {'t' : dvd_title_clean, 'y' : year, 'plot' : 'short', 'apikey' : omdb_api_key}
# strurl = "http://www.omdbapi.com/?"+urllib.parse.urlencode(params, doseq=False, safe='', encoding=None, errors=None, quote_via=urllib.parse.quote_plus)
# 
# 
# #strurlenc = urllib.parse.urlencode(strurl, doseq=False, safe='', encoding=None, errors=None, quote_via=urllib.parse.quote_plus)
# print(strurl.replace(omdb_api_key,'key_hidden'))
# 
# dvd_title_info_json = urllib.request.urlopen(strurl).read()

print(dvd_title_info_json)
        