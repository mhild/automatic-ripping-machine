import sys
import os
import logging
import subprocess

import requests
from bs4 import BeautifulSoup as bs


class KeyNotFound(Exception):
    pass

def check_key():
        logging.debug("Checking MakeMKV key")
        cmd = 'makemkvcon info disc:9999  |grep "MSG:5020,516,0"'

        try:
            mdisc = subprocess.check_output(
                cmd,
                shell=True
            ).decode("utf-8")
            logging.info("msg": " + mdisc.strip())

def get_current_key():
    try:
        r = requests.get('https://www.makemkv.com/forum/viewtopic.php?f=5&t=1053#p3548')
    except:
        raise KeyNotFound("Key not found")

    if r.status_code == 200:
        bs_content = bs(r.content, "lxml")
        key = bs_content.find("code").get_text()

        return key
    else:
        raise KeyNotFound("Key not found")

if __name__ == "__main__":
    #print(get_current_key())
    print(check_key())
