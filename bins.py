# -*- coding: utf-8 -*-
"""Bins.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1WBhBePpwwcODsACWHR42QmOjm1OY5SVX
"""

from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import datetime
import calendar

#input = "road"
input = "dalry road"
input_search = input.replace(" ","+")

def createSoup(site):
  hdr = {'User-Agent': 'Mozilla/5.0'}
  req = Request(site,headers=hdr)
  page = urlopen(req)
  return BeautifulSoup(page)

directory = "https://www.edinburgh.gov.uk/directory/search?directoryID=10243&showInMap=&keywords=" + input_search + "&search=Search"
soup = createSoup(directory)
search_soup = soup.find_all("ul", class_ = "list--record")
for item in search_soup:
  search_link = item.find("a")['href']

days = "https://www.edinburgh.gov.uk" + search_link
new_soup = createSoup(days)
label_soup = new_soup.find_all("dt")
answer_soup = new_soup.find_all("dd")

label = []
answer = []

for tag in label_soup:
  label.append(tag.contents[0].strip())

for tag in answer_soup:
  answer.append(tag.contents[0].strip())

table = dict(zip(label, answer))

# Determine bin colour
today = datetime.date.today()
if datetime.date(today.year,today.month,today.day).isocalendar()[1] % 2 == 1:
  bin_colour = "Green bin & Blue box"
else:
  bin_colour = "Grey bin & Food caddy"

weekdays = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
bin_index = weekdays.index(table['Food collection day'])

d2b = bin_index - weekdays.index(today.strftime('%A'))
if d2b < 0:
  d2b += 7
bin_day = today + datetime.timedelta(days=d2b)

print("For {}, the {} are due to go out next on {} {} {}".format(table['Street'],bin_colour,table['Food collection day'],bin_day.strftime('%B'), bin_day.day))