import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv


load_dotenv()
SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = "http://example.com"
SCOPE = "playlist-modify-public playlist-modify-private playlist-read-private"


class SpotifyManager:
    def __init__(self):
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                SPOTIFY_CLIENT_ID,
                SPOTIFY_CLIENT_SECRET,
                redirect_uri=REDIRECT_URI,
                scope=SCOPE,
                show_dialog=True,
                cache_path="token.txt",
            ),
        )

    def user_playlists(self):
        """Get playlists created by current user"""
        current_user_id = self.sp.current_user()["id"]
        return [
            {"name": p["name"], "id": p["id"]}
            for p in self.sp.current_user_playlists()["items"]
            if p["owner"]["id"] == current_user_id
        ]

    def create_playlist(self, name):
        """Create a new playlist for the current user"""
        current_user_id = self.sp.current_user()["id"]
        return self.sp.user_playlist_create(current_user_id, name)

    def find_album(self, artist, album_name):
        """Find an album's URI in Spotify by album's name and artist"""
        query = f"{artist} {album_name}"
        try:
            album = self.sp.search(q=query, limit=1, type="album", market="US")[
                "albums"
            ]["items"][0]
        except IndexError:
            print(f"No match for {artist} - {album_name}")
            return None
        album_uri = album["uri"]
        if artist == album["artists"][0]["name"]:
            print(f"Found {artist} - {album_name}")
            return album_uri
        else:
            print(f"No match for {artist} - {album_name}")
            return None

    def get_track_pop(self, track_id):
        """Get track popularity by track's id"""
        return int(self.sp.track(track_id=track_id)["popularity"])

    def get_top_track(self, album_uri):
        """Get the most 'popular' track of the album"""
        try:
            album_tracks = self.sp.album_tracks(album_id=album_uri)["items"]
            first_track = album_tracks[0]
            max_id = first_track["uri"]
            max_pop = self.get_track_pop(max_id)
            for track in album_tracks[1:]:
                pop = self.get_track_pop(track["uri"])
                if pop > max_pop:
                    max_pop = pop
                    max_id = track["uri"]
            return max_id
        except (TypeError, spotipy.SpotifyException):
            return None

    def add_to_playlist(self, playlist_id, tracks):
        """Add a list of tracks to a given playlist id"""
        n_tracks = len(tracks)
        end = n_tracks - n_tracks % 100
        step = 100
        for i in range(0, end, step):
            self.sp.playlist_add_items(
                playlist_id, tracks[int(i / 100 * step): i + step]
            )

        self.sp.playlist_add_items(playlist_id, tracks[end:])
