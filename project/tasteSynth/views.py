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
    playlist_id1 = request.GET["first_playlist"]
    results1 = sp.playlist_items(playlist_id1,fields="items.item.name,items.item.id,items.item.album.images.url,next")
    tracks1 = results1['items']
    while results1['next']:
        results1 = sp.next(results1)
        tracks1.extend(results1['items'])
    playlist_id2 = request.GET["second_playlist"]
    results2 = sp.playlist_items(playlist_id2,fields="items.item.name,items.item.id,items.item.album.images.url,next")
    tracks2 = results2['items']
    while results2['next']:
        results2 = sp.next(results2)
        tracks2.extend(results2['items'])
    overlapping_tracks = []
    for track in tracks1:
        if track in tracks2:
            overlapping_tracks.append(track)
    return render(request, "PlaylistView.html", {"tracks": overlapping_tracks})
