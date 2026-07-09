from django.urls import path
from . import views

urlpatterns = [
    path("",views.SynthView, name="synth_view"),
    path("authorization",views.SpotifyAuthorization, name="spotify_authorization"),
    path("auth_success",views.SuccessfulAuthorization, name="successful_authorization"),
    path("playlist_list",views.PlaylistList, name="playlist_list"),
    path("playlist_view/<str:id>",views.PlaylistView, name="playlist_view"),
    path("merge_view",views.MergeView, name="merge_view"),
    path("save_playlist",views.SavePlaylist, name="save_playlist"),
]