from bs4 import BeautifulSoup

fileObject = open("htmlPrettifierInput.txt", "r")
html = fileObject.read()
fileObject.close()

soup = BeautifulSoup(html, 'html.parser')
pretty = soup.prettify()

fileObject = open("htmlPrettifierOutput.txt", "w")
fileObject.write(pretty)
fileObject.close()



