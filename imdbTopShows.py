from bs4 import BeautifulSoup, Tag
from urllib.request import urlopen
from Episode import Episode
import configparser

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
                        </div>
                        <hr>""".format(ep.description)
    return ret

def endHtmlPage():
    return """</div></body></html>"""

def loadConfig():
    config = configparser.ConfigParser()
    config.read("config.ini")
    return config



#Begin main process
options = loadConfig()
if len(options["DEFAULT"]) == 0:
    print("No defaults - exiting...")
    exit()
else:
    options = options["DEFAULT"]

showTitleList = set()
rankToEpisodeMap = {}
rank = 1
startAt = 1
maxRank = int(options.get("numEntries", 106))
while rank < maxRank:
    url = """https://www.imdb.com/search/title/?title_type=tv_episode&num_votes=1000,&sort=user_rating,desc""" + "&start=" + str(startAt)
    response = urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, "html.parser")


    episodeDivs = getEpisodeDivs(soup)
    for div in episodeDivs:
        episode = Episode(div)
        if options.getboolean('skipDuplicateShows') and (episode.showTitle in showTitleList):
            print("Skipping duplicate show: {}".format(episode.showTitle))
            continue
        if((int (episode.year)) < int(options.get('minYear', 0))):
            print("Skipping show from before {}".format(options.get('minYear', 0)))
            continue
        if((int (episode.year)) > int(options.get('maxYear', 9999))):
            print("Skipping show from after {}".format(options.get('maxYear', 9999)))
            continue
        #if((int (episode.year)) in [2018, 2017, 2016]):
        #   print("Skipping show from after 2016")
        #  continue
        
        episode.ranking = rank
        rankToEpisodeMap[rank] = episode
        rank+=1
        showTitleList.add(episode.showTitle)
        print(episode.showTitle)

        if rank > maxRank:
            break

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
fileObject = open("episodes-2022.html", "w")
fileObject.write(BeautifulSoup(output, "html.parser").prettify())
fileObject.close()