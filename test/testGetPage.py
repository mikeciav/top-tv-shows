from urllib.request import urlopen
from bs4 import BeautifulSoup, Tag

response = urlopen("""https://www.imdb.com/title/tt3230908/""")
data = response.read()
soup = BeautifulSoup(data, "html.parser")
print(soup.prettify())

image = soup.find("img", {"alt": "Mizumono Poster"})["src"]
print(image)

[season, episode] = soup.find("div", {"class": "button_panel"}).find("div", {"class": "bp_heading"}).get_text().split(" | ")
print(season.strip())
print(episode.strip())
