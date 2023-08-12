#!/usr/bin/python3
# utf-8

import math
# Imports
import random
import requests
import sys
import time

from lib.parser import *

# Handling arguments
kw = sys.argv[0]
apiKey = sys.argv[1]
pexels_apiKey = sys.argv[2]
userID = sys.argv[3]

if type or apiKey or pexels_apiKey or userID == None:
    print('''
    [!] Improper usage:
        Script expects four arguments:
            'python3 main.py -type -igApiKey -pexelsApiKey -userID'
    
    Exiting...
    ''')
    time.sleep(4)
    exit()
else:
    pass

# Global variables
instagram_baseUrl = "https://www.instagram.com"
img_baseUrl = "https://api.pexels.com/v1/"
vid_baseUrl = "https://api.pexels.com/videos/"
apiPost_request = instagram_baseUrl + f"/{userID}/media"
login_url = f"https://graph.facebook.com/v17.0/me/accounts?access_token={apiKey}"
rand_int = int(random.choice(1, 10))
rand_int = math.floor(rand_int)


# Scrape hashtags and media for automated post
class scrape:
    def hashtags(self):
        with open('lib/hashtags.txt', 'r') as file:
            caption = file.read().rstrip()

    class media:
        def pic(self):
            picture = requests.post(f"https://api.pexels.com/v1/search?query={kw}&per_page=1",
                                    headers={"Authorization": f"{pexels_apiKey}"})
            pass

        def vid(self):
            video = requests.get(f"https://api.pexels.com/videos/search?query={kw}&per_page=1",
                                 headers={"Authorization": f"{pexels_apiKey}"}
                                 )
            pass


# Interact with Instagram
class apiInterface:
    def login(self, apiKey, userID, login_url):
        pass

    def post_content(self):
        caption = scrape.hashtags(self)
        if rand_int < 5:
            picture = scrape.media.pic(self)
        else:
            video = scrape.media.vid(self)


# Display
class userInterface:
    # Landing Page
    def UI(self):
        print(f'''
             Token: {apiKey}
             Type: {type}
             User ID: {userID}
             
             Initializing...
             
        ''')

        apiInterface.login(apiKey, userID, login_url)


scrape(kw)
userInterface.UI()
