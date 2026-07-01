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
    results = sp.current_user_playlists(limit=50)
    playlists = results["items"]
    while results["next"]:
        results = sp.next(results)
        playlists.extend(results["items"])
    print(playlists)
    return render(request, "PlaylistDisplay.html", {"playlists": playlists})
    