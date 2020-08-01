from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import datetime
import calendar

input = ''

def createSoup(site):
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = Request(site,headers=hdr)
    page = urlopen(req)
    return BeautifulSoup(page, features="html.parser")

def main(street):
    #input = "dalry road"
    input = street
    input_search = input.replace(" ","+")
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
        bin_colour = "Green bin and Blue box"
    else:
        bin_colour = "Grey bin and Food caddy"
    
    weekdays = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    bin_index = weekdays.index(table['Food collection day'])
    
    d2b = bin_index - weekdays.index(today.strftime('%A'))
    if d2b < 0:
        d2b += 7
    bin_day = today + datetime.timedelta(days=d2b)
    speech = "For {}, the {} are due to go out next on {} {} {}".format(table['Street'],bin_colour,table['Food collection day'],bin_day.strftime('%B'), bin_day.day)
    return speech
    