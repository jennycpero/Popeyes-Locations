# Web scraping popeyes restaurant locations

import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import re

URL = "https://locations.popeyes.com/"
page = requests.get(URL)

soup = bs(page.content, "html.parser")
results = soup.find(attrs="Directory-listLinks")
location_elements = soup.find_all("li", attrs="Directory-listItem")
state = []
city = []
num = []

for a in soup.find_all('a', attrs="Directory-listLink", href=True):
    state.append(a['href'])

for i in range(len(state)): #for each state page
    req = requests.get(URL + str(state[i]))
    soup = bs(req.text, 'html.parser')

    if state[i] == "dc/washington": #Since DC is a district and not a state with several cities, the page is formatted differently
        listTeasers = soup.find('ul', attrs='Directory-listTeasers')
        loc_dc = soup.find_all('li', attrs="Directory-listTeaser")
        count = len(loc_dc)
        city.append("Washington, DC")
        num.append(count)

    else:
        loc_el = soup.find_all("li", attrs="Directory-listItem")
        for j in loc_el:
            cityName = j.find("span", attrs="Directory-listLinkText")
            camelCase = state[i].title()
            if (", " + camelCase) in cityName.text:
                city.append(cityName.text.replace((", " + camelCase), (", " + camelCase.upper())))
            else:
                city.append(cityName.text + ", " + state[i].upper())
        for a in soup.find_all('a', attrs="Directory-listLink", href=True):
            num.append(re.sub("[()]", "", a['data-count']))

#turn data into csv file
df = pd.DataFrame({'Location': city, 'Count': num})
df = df.astype({'Count': 'int64'})
df2 = df.groupby(['Location'], as_index=False, sort=False).sum()
df2.to_csv('popeyes.csv', index=False, encoding='utf-8')
