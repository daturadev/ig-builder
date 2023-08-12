#!/usr/bin/python3
# utf-8

import re
from bs4 import BeautifulSoup  # Cursed module
# Imports
from urllib.request import urlopen  # Cursed module

# Parse hashtags//Globals
site = "https://all-hashtag.com/library/contents/ajax_top.php"
page = urlopen(site)
html = page.read().decode("utf-8")
soup = BeautifulSoup(html, 'html.parser')
src = soup.find_all('span')
# Clean junk from list
del src[0]

# Write trending, extracted hashtags to 'hashtags.txt'
# Remove HTML tags                   
class scrape:
    with open('hashtags.txt', 'w') as file:
        for hashtag in src:
            clean = re.compile('<.*?>')
            cleantxt = re.sub(clean, '', str(hashtag))
            print(cleantxt)
            file.write(cleantxt + "\n")
