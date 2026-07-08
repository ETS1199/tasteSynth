from django.shortcuts import render, redirect
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import DjangoSessionCacheHandler
from spotipy.exceptions import SpotifyException
import os
import regex
from dotenv import load_dotenv

load_dotenv()

def get_auth_manager(request):
    auth_manager = SpotifyOAuth(
            client_id=os.environ.get("SPOTIPY_CLIENT_ID"),
            client_secret=os.environ.get("SPOTIPY_CLIENT_SECRET"),
            redirect_uri="http://127.0.0.1:8000/auth_success",
            scope="playlist-read-private playlist-modify-public playlist-modify-private",
            cache_handler = DjangoSessionCacheHandler(request)
        )
    return auth_manager

# Create your views here.
def SynthView(request):
    return render(request,"SynthTemplate.html")

def SpotifyAuthorization(request):
    auth_url = get_auth_manager(request).get_authorize_url()
    return redirect(auth_url)

def SuccessfulAuthorization(request):
    current_url = request.build_absolute_uri()
    auth_manager = get_auth_manager(request)
    code = auth_manager.parse_response_code(current_url)
    auth_token = auth_manager.get_access_token(code, as_dict=False)
    request.session["auth_token"] = auth_token
    return redirect("playlist_list")

def PlaylistList(request):
    sp = spotipy.Spotify(auth_manager=get_auth_manager(request))
    results = sp.current_user_playlists()
    playlists = results["items"]
    user_id = sp.current_user().get("id")
    while results["next"]:
        results = sp.next(results)
        playlists.extend(results["items"])
    user_owned_playlists = []
    external_owned_playlists = []
    # Runs checks to split the playlists the user owns from the ones they are a colaborator on
    for playlist in playlists:
        if playlist.get("owner",{}).get("id") == user_id:
            user_owned_playlists.append(playlist)
        else:
            external_owned_playlists.append(playlist)
    return render(request, "PlaylistList.html", {"playlists": user_owned_playlists,"shared_playlists": external_owned_playlists})

def PlaylistView(request,id):
    sp = spotipy.Spotify(auth_manager=get_auth_manager(request))
    results = sp.playlist_items(id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return render(request, "PlaylistView.html", {"tracks": tracks})

def MergeView(request):
    sp = spotipy.Spotify(auth_manager=get_auth_manager(request))
    # Gets the amount of playlists we are looking at
    num_of_playlists = int(request.GET["num_of_playlists"])
    playlists = []
    for playlist in range(1,num_of_playlists + 1):
        playlist_id = request.GET["playlist" + str(playlist)]
        results = sp.playlist_items(playlist_id,fields="items.item.name,items.item.id,items.item.uri,items.item.album.images.url,next")
        tracks = results['items']
        while results['next']:
            results = sp.next(results)
            tracks.extend(results['items'])
        playlists.append(tracks)
    overlapping_tracks = []
    # Gets the playlist with the least songs and removes it from the list to use to find overlapping songs
    least_song_playlist = min(playlists,key=len)
    playlists.remove(least_song_playlist)
    for track in least_song_playlist:
        track_valid = True
        for playlist in playlists:
            if track not in playlist:
                track_valid = False
                break
        if track_valid:
            overlapping_tracks.append(track)
    return render(request, "PlaylistView.html", {"tracks": overlapping_tracks,"merged_playlist": True})

def get_spotify_auth(request):
    cache_handler = DjangoSessionCacheHandler(request)
    return SpotifyOAuth(
        client_id=os.environ.get("SPOTIPY_CLIENT_ID"),
        client_secret=os.environ.get("SPOTIPY_CLIENT_SECRET"),
        redirect_uri="http://127.0.0.1:8000/auth_success",
        scope="playlist-read-private playlist-modify-public playlist-modify-private",
        cache_handler=cache_handler,
    )

def SavePlaylist(request):
    if request.method == "POST":
        auth_manager = get_spotify_auth(request)
        sp = spotipy.Spotify(auth_manager=auth_manager)
        playlist = request.POST.get("playlist")
        # Gets the list of the URIS of the tracks
        print(playlist)
        track_uris = regex.findall(r"'uri': '(spotify:track:[^']+)'",playlist)
        # Gets the users playlists to find a name that is not currently in use
        results = sp.current_user_playlists()
        playlists = results["items"]
        while results["next"]:
            results = sp.next(results)
            playlists.extend(results["items"])
        # Creates a list of all taken names
        playlist_names = []
        for existing_playlist in playlists:
            playlist_names.append(existing_playlist.get("name"))
        # Loops until a name for the playlist is valid
        playlist_num = 1
        new_playlist_name = ""
        while True:
            if "Merged Playlist " + str(playlist_num) not in playlist_names:
                new_playlist_name = "Merged Playlist " + str(playlist_num)
                break
            else:
                playlist_num += 1
        # Creates the new playlist by posting directly to the API (Avoids problems with user_playlist_create)
        new_playlist = sp._post("me/playlists", payload={"name": new_playlist_name,"public": False})
        new_playlist_id = str(new_playlist.get("id"))
        sp._post("playlists/" + new_playlist_id + "/items",payload={"uris":track_uris})
    return redirect("playlist_list")
