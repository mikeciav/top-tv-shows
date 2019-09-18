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


def getEpisodeDivs(soup):
    def isListerItemModeAdvanced(tag):
        return tag.has_attr("class") and len(tag["class"]) == 2 and "lister-item" in tag["class"] and "mode-advanced" in tag["class"]
    return soup.find_all(isListerItemModeAdvanced)

def createHtmlPage():
    return """<html>
                <head>
                    <!-- Latest compiled and minified CSS -->
                    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">

                    <!-- jQuery library -->
                    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>

                    <!-- Latest compiled JavaScript -->
                    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
                </head>

                <body>
                    <div class="container">"""


def appendEpisodeToHtmlPage(ep):

    ret = """           <div class="row">
                            <div class="col-md-12 center" style="display:inline">
                                <div class="col-md-12">
                                    <h1 style="display:inline">#{}: {} - <a href="https://imdb.com/title/{}">&quot;{}&quot;</a></h1>
                                    <div class="col-md-4">
                                        <img src="{}/">
                                    </div>
                                    <div class="col-md-8">
                                        <span style="display:inline"><strong>""".format(ep.ranking, ep.showTitle, ep.episodeId, ep.episodeTitle, ep.imageUrl)
    if ep.seasonNumber and ep.seasonNumber != "N/A":
        ret += """                          Season {}, Episode {} &nbsp;""".format(ep.seasonNumber, ep.episodeNumber)
    ret += """                              ({})""".format(ep.year)
    ret += """                          </strong></span>
                                        <span><i>{}</i></span>
                                    </div>
                                </div>
                            </div>
                        </div>""".format(ep.description)
    return ret

def endHtmlPage():
    return """</div></body></html>"""

#Begin main process
showTitleList = set()
rankToEpisodeMap = {}
rank = 1
startAt = 1
while rank < 106:
    url = """https://www.imdb.com/search/title/?title_type=tv_episode&num_votes=1000,&sort=user_rating,desc""" + "&start=" + str(startAt)
    response = urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, "html.parser")


    episodeDivs = getEpisodeDivs(soup)
    for div in episodeDivs:
        episode = Episode(div)
        if episode.showTitle in showTitleList:
            print("Skipping duplicate show: {}".format(episode.showTitle))
            continue
        if((int (episode.year)) < 2000):
            print("Skipping show from before 2000")
            continue
        #if((int (episode.year)) in [2018, 2017, 2016]):
        #   print("Skipping show from after 2016")
        #  continue
        
        episode.ranking = rank
        rankToEpisodeMap[rank] = episode
        rank+=1
        showTitleList.add(episode.showTitle)
        print(episode.showTitle, flush=True)

    startAt+=50

output = createHtmlPage()

for ranking in sorted(rankToEpisodeMap.keys(), reverse=True):
    episode = rankToEpisodeMap[ranking]
    print("#{}".format(episode.ranking))
    print(episode.showTitle)
    print("{}/10".format(episode.rating))
    print("Episode: \"{}\"".format(episode.episodeTitle))
    print("Season{}, Episode{} ({})".format(episode.seasonNumber, episode.episodeNumber, episode.year))
    print("Rating: {}".format(episode.rating))
    print(episode.description)

    output += appendEpisodeToHtmlPage(episode)

output += endHtmlPage()
fileObject = open("episodes.html", "w")
fileObject.write(BeautifulSoup(output, "html.parser").prettify())
fileObject.close()