import sys
import os
import logging
import subprocess

import requests
from bs4 import BeautifulSoup as bs
from pathlib import Path

class KeyNotFound(Exception):
    pass

def check_key_valid():
    logging.info("Checking MakeMKV key")
    cmd = 'makemkvcon -r info disc:9999'

    try:
        out = subprocess.check_output(cmd,shell=True).decode("utf-8")
    except:
        logging.info("makemkvcon failed - assuming invalid key")
        return False

    logging.info("msg: " + out.strip())

    if "MSG:5020,516,0" in out:
        logging.info("MakeMKV key invalid")
        return False
    else:
        logging.info("MakeMKV key valid")
        return True


def write_settings(key):

    home = str(Path.home())
    path = home+"/.MakeMKV/settings.conf"
    path_bak = home+"/.MakeMKV/settings.conf.bak"

    content = ('#\n'
    '# MakeMKV settings file, written by MakeMKV v1.14.3 linux(x64-release)\n'
    '#\n\n'
    'app_Key = "{}"\n'
    'sdf_Stop = ""').format(key)

    logging.info("moving prev settings: {0} --> {1}".format(path,path_bak))
    os.rename(path, path_bak)

    logging.info("makemkvcon - writing settings")


    file_handle = open(path,"w")
    file_handle.write(content)
    file_handle.close()

def get_current_key():

    logging.info("makemkvcon - getting new key")

    try:
        r = requests.get('https://www.makemkv.com/forum/viewtopic.php?f=5&t=1053#p3548')
    except:
        raise KeyNotFound("Key not found")

    if r.status_code == 200:
        bs_content = bs(r.content, "lxml")
        key = bs_content.find("code").get_text()
        logging.info("makemkvcon - got new key")
        logging.debug("makemkvcon - new key is '{}'".format(key))
        return key
    else:
        raise KeyNotFound("Key not found")


def update_key():

    logging.info("Checking MakeMKV-key")
    if not check_key_valid():
        key = get_current_key()
        write_settings(key)


if __name__ == "__main__":
    print(get_current_key())
    #print(check_key_valid())
    #print(write_settings("testkey"))
    #update_key()
