from bs4 import BeautifulSoup, Tag
from urllib.request import urlopen

class Episode:
    def getShowTitle(self, episode):
        return episode.h3("a")[0].get_text().strip()

    def getEpisodeTitle(self, episode):
        return episode.h3("a")[1].get_text().strip()

    def getEpisodeId(self, episode):
        url = episode.h3("a")[1]["href"].strip()
        iden = url.split("/")[2]
        return iden

    def getYear(self, episode):
        return episode.h3("span")[2].get_text().strip()[1:-1]

    def getRating(self, episode):
        return episode.find("div", {"class": "ratings-bar"}).div.strong.get_text().strip()

    def getDescription(self, episode):
        desc = episode("p")[1].get_text().strip()
        if "See full summary" in desc:
            for delim in [";", ".", ":", ","]:
                if delim in desc:
                    desc = desc[:desc.rindex(delim)]
                    break
        return desc

    def getExternalData(self):
        url = "https://www.imdb.com/title/" + self.episodeId
        response = urlopen(url)
        epPageSoup = BeautifulSoup(response.read(), "html.parser")
        try:
            imgAlt = self.episodeTitle + " Poster"
            self.imageUrl = epPageSoup.find("img", {"alt": imgAlt})["src"]
            [season, episode] = epPageSoup.find("div", {"class": "button_panel"}).find("div", {"class": "bp_heading"}).get_text().split(" | ")
            self.seasonNumber = season.strip().split(" ")[1]
            self.episodeNumber = episode.strip().split(" ")[1]
        except (KeyError, ValueError) as e:
            print("Malformed data from the web - skipping season / episode info")
            self.seasonNumber = ""
            self.episodeNumber = ""
        except (TypeError) as e:
            print("Malformed image url from the web - skipping season / episode info")
            self.seasonNumber = ""
            self.episodeNumber = ""

    def __init__(self, episode):
        self.showTitle = self.getShowTitle(episode)
        self.episodeTitle = self.getEpisodeTitle(episode)
        self.episodeId = self.getEpisodeId(episode)
        self.rating = self.getRating(episode)
        self.description = self.getDescription(episode)
        self.year = self.getYear(episode)
        self.getExternalData()