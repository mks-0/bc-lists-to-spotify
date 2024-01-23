import requests
import math
from bs4 import BeautifulSoup
from daily_list import DailyList
from spotify_manager import SpotifyManager


URL = "https://daily.bandcamp.com"


def get_bandcamp_lists_page(page_n):
    # Get the bandcamp lists BeautifulSoup object
    bandcamp_lists_html = requests.get(f"{URL}/lists?page={page_n}").text
    return BeautifulSoup(bandcamp_lists_html, "html.parser")


if __name__ == "__main__":
    bc_lists = get_bandcamp_lists_page(page_n=1)  # Get the first page of lists

    num_results = (
        bc_lists.find(id="num-results").getText().replace(" ", "").replace("\n", "")
    )
    n_lists = int(num_results[-3:])  # Overall number of lists
    lists_per_page = int(num_results[-7:-5])  # Number of lists per page

    n_pages = math.ceil(n_lists / 30)  # Number of bandcamp lists pages
    page = int(input(f"Choose a page (from 1 to {n_pages}) to scrape lists from: "))
    if not (0 < page < n_pages):
        print("Not a valid page number")
    else:
        if page != 1:
            bc_lists = get_bandcamp_lists_page(
                page_n=page
            )  # Get the nth page of bandcamp lists

        links = [
            a.get("href")
            for a in bc_lists.select(selector="#p-daily-franchise .list-article .title")
        ]  # List of links to each bandcamp list
        n_lists = 0
        while not (0 < n_lists <= lists_per_page):
            try:
                n_lists = int(
                    input(
                        f"Choose a number of  lists (from 1 to {lists_per_page}) to scrape: "
                    )
                )
            except ValueError:
                print("Not a number")

        print("Scraping lists...")
        lists = [
            DailyList(link) for link in links[:n_lists]
        ]  # list of Daily List objects

        albums = []
        [
            albums.extend(dlist.albums) for dlist in lists
        ]  # List of albums (album name and artist dict) of all the lists

        sm = SpotifyManager()  # Initialize Spotify API Manager

        if input("Create a new playlist to add tracks to? (y/n): ") == "y":
            new_playlist_name = input("Enter the new playlist name: ")
            p_list_id = sm.create_playlist("List")[
                "id"
            ]  # Creates new playlist for user with a given name
        else:
            playlists = sm.user_playlists()
            print("Your Playlists:")
            [print(p["name"]) for p in playlists]  # Prints all the user's playlists

            def choose_playlist(playlist_name):
                # Choose a playlist to add tracks to by name
                playlist_id = next(
                    (p["id"] for p in playlists if p["name"] == playlist_name), None
                )
                if playlist_id is not None:
                    print(f"Playlist ID: {playlist_id}")
                    return playlist_id
                else:
                    choose_playlist(
                        input("Not a valid playlist name. Choose another one: ")
                    )

            p_list_id = choose_playlist(
                input("Choose a playlist name to add track to: ")
            )

        tracks = []
        tracks_found = 0
        tracks_not_found = 0

        # with open('albums.txt') as file:
        #     albums = file.read().split()
        # with open('tracks.txt') as file:
        #     tracks = file.read().split()[:5]

        print("Searching tracks...")
        for album in albums:
            album_uri = sm.find_album(
                artist=album["artist"], album_name=album["album_name"]
            )
            top_track = sm.get_top_track(
                album_uri
            )  # The most "popular" track of the album
            if top_track is not None:
                tracks.append(top_track)
                tracks_found += 1
            else:
                tracks_not_found += 1

        print(f"Tracks found:{tracks_found}\nTracks not found: {tracks_not_found}")

        print("Adding tracks...")
        sm.add_to_playlist(p_list_id, tracks)
        print("Tracks added.")
