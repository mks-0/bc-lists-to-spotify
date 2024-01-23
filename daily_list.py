import requests
from bs4 import BeautifulSoup

URL = "https://daily.bandcamp.com"


class DailyList:
    """Daily List object representing the list's name and albums it contains"""

    def __init__(self, link):
        self.dlist_html = requests.get(f"{URL}{link}").text
        self.dlist = BeautifulSoup(self.dlist_html, "html.parser")
        self.name = self.dlist.find(name="article-title").getText()
        self.albums = self.get_albums()

    def get_albums(self):
        """Get the list's albums (album name and artist)"""
        albums = []
        prev_album_name = ""
        album_info = self.dlist.select(".mpalbuminfo")
        for a in album_info:
            album = a.findAll("a")
            name = album[0].getText()
            artist = album[1].getText()
            if name != prev_album_name:
                albums.append({"album_name": name, "artist": artist})
                prev_album_name = name
        return albums
