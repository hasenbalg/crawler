import requests
import sys
import re
from multiprocessing import Pool, Manager
from datetime import datetime


class Link:
    def __init__(self, status, url, arguments):
        self.status = status
        self.url = url
        self.arguments = arguments

    def __eq__(self, other):
        if isinstance(other, Link):
            return self.url == other.url and self.arguments == other.arguments
        return False

    def __hash__(self):
        return hash(str(self.url) + str(self.arguments))

    def __str__(self):
        return "{0}, {1}, {2}\n".format(self.status, self.url, self.arguments)


address = sys.argv[1]


manager = Manager()

linksVisited = manager.list()
linksToGo = manager.list()
# linksVisited = set()
# linksToGo = set()


def findLinks(html):
    newUrls = re.findall(r'a href="(.*?)"', html)
    for url in newUrls:
        addressSegments = url.split('?')

        # relative links
        if addressSegments[0].startswith('/'):
            addressSegments[0] = address + addressSegments[0]

        # if link not external
        if address in addressSegments[0]:
            newLink = Link(None, addressSegments[0], addressSegments[1]) if len(
                addressSegments) > 1 else Link(None, addressSegments[0], None)

            if not any(l == newLink for l in linksToGo) and not any(l == newLink for l in linksVisited):
                linksToGo.append(newLink)


def placeRequest(_):
    if len(linksToGo) > 0:
        link = linksToGo.pop(0)
        if link.arguments is not None:
            print('requesting:' + link.url + '?' + link.arguments)
            response = requests.get(link.url + '?' + link.arguments)
        else:
            response = requests.get(link.url)

        link.status = response.status_code

        html = response.text

        findLinks(html)
        linksVisited.append(link)
        print(str(link) + ' visited')


if __name__ == "__main__":
    linksToGo.append(Link(None, address, None))
    placeRequest(None)
    while len(linksToGo) > 0:
        # p = Pool(5)
        # p.map(placeRequest, [None])
        # p.close()
        # p.join()
        print(str(len(linksVisited)) + ' links visited')
        print(str(len(linksToGo)) + ' links 2 go')
        placeRequest(1)

    f = open(datetime.now().strftime('%m-%d-%Y-%H:%M:%S') + '.csv', 'w')
    outout = ''
    for l in linksVisited:
        outout = outout + str(l)
    f.write(outout)
    f.close()


    