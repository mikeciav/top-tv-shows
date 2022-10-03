from bs4 import BeautifulSoup, Tag
from urllib.request import build_opener, HTTPCookieProcessor, urlopen

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
        yurr = episode.h3("span")[2].get_text().strip()[1:-1]
        # handle weird edge case with The Morning Show having (I) in its year for some reason
        if "I) (" in yurr:
            yurr = yurr[4:]
        return yurr


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
        url = "https://www.imdb.com/title/" + self.episodeId + "/"
        opener = build_opener(HTTPCookieProcessor())
        response = opener.open(url)
        epPageSoup = BeautifulSoup(response.read(), "html.parser")
        try:
            divClass = "ipc-media--baseAlt"
            self.imageUrl = epPageSoup.find("div", {"class": divClass}).find("img")["src"]
            [season, episode] = epPageSoup.find("div", {"data-testid": "hero-subnav-bar-season-episode-numbers-section"}).get_text().split(".")
            self.seasonNumber = season.strip()[1:]
            self.episodeNumber = episode.strip()[1:]
        except (KeyError, ValueError) as e:
            print("Malformed data from the web - skipping season / episode info")
            self.imageUrl = ""
            self.seasonNumber = ""
            self.episodeNumber = ""
        except (TypeError) as e:
            print("Malformed image url from the web - skipping season / episode info")
            self.imageUrl = ""
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