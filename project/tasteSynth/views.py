from django.shortcuts import render, redirect
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

load_dotenv()
auth_manager = SpotifyOAuth(
        client_id=os.environ.get("SPOTIPY_CLIENT_ID"),
        client_secret=os.environ.get("SPOTIPY_CLIENT_SECRET"),
        redirect_uri="http://127.0.0.1:8000/auth_success",
        scope="playlist-read-private"
    )

# Create your views here.
def SynthView(request):
    return render(request,"SynthTemplate.html")

def SpotifyAuthorization(request):
    auth_url = auth_manager.get_authorize_url()
    return redirect(auth_url)

def SuccessfulAuthorization(request):
    current_url = request.build_absolute_uri()
    code = auth_manager.parse_response_code(current_url)
    auth_token = auth_manager.get_access_token(code, as_dict=False)
    request.session["auth_token"] = auth_token
    return redirect("playlist_display")

def PlaylistDisplay(request):
    auth_token = request.session.get("auth_token")
    sp = spotipy.Spotify(auth=auth_token)
    results = sp.current_user_playlists()
    playlists = results["items"]
    while results["next"]:
        results = sp.next(results)
        playlists.extend(results["items"])
    return render(request, "PlaylistDisplay.html", {"playlists": playlists})

def PlaylistView(request,id):
    auth_token = request.session.get("auth_token")
    sp = spotipy.Spotify(auth=auth_token)
    results = sp.playlist_items(id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return render(request, "PlaylistView.html", {"tracks": tracks})
    
def MergeView(request):
    auth_token = request.session.get("auth_token")
    sp = spotipy.Spotify(auth=auth_token)
    # Gets the amount of playlists we are looking at
    num_of_playlists = int(request.GET["num_of_playlists"])
    playlists = []
    for playlist in range(1,num_of_playlists + 1):
        playlist_id = request.GET["playlist" + str(playlist)]
        results = sp.playlist_items(playlist_id,fields="items.item.name,items.item.id,items.item.album.images.url,next")
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
    return render(request, "PlaylistView.html", {"tracks": overlapping_tracks})
