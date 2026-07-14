# tasteSynth

A Django web app that logs into your Spotify account, finds the tracks that
**multiple playlists have in common**, and lets you save that overlap as a new
private playlist.

## How it works

1. Authorize the app against your Spotify account (OAuth).
2. Browse your playlists — the app separates ones you own from ones you only
   collaborate on.
3. Select two or more playlists to merge; the app computes the set of tracks
   present in **every** selected playlist.
4. Save the result as a new private playlist (auto-named `Merged Playlist N`).

## Tech stack

- **Python 3.12**, **Django 6.x**
- **[Spotipy](https://spotipy.readthedocs.io/)** for the Spotify Web API + OAuth
- SQLite (default Django DB, used for the session store that caches OAuth tokens)

## Prerequisites

- Python 3.12+
- A Spotify account
- A Spotify developer app (see [Spotify credentials](#spotify-credentials) below)

## Setup

```bash
# From the repo root
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cd project
python manage.py migrate           # sets up the sqlite session store
```

### Spotify credentials

The app reads its Spotify API credentials from a `.env` file in the `project/`
directory (loaded at startup via `python-dotenv`).

1. Create an app at the
   [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).
2. Add `http://127.0.0.1:8000/auth_success` as a **Redirect URI** in the app
   settings.
3. Copy the template and fill in your app's Client ID and Client Secret:

   ```bash
   cd project
   cp .env.example .env
   # then edit .env:
   #   SPOTIPY_CLIENT_ID=...
   #   SPOTIPY_CLIENT_SECRET=...
   ```

Your real `.env` is gitignored and stays local. Only `.env.example` is committed.

> **Note:** Spotify apps start in *development mode*, which limits access to up
> to 25 users you explicitly add to the app's allow-list. Add each tester's
> Spotify account under the app's **User Management** settings.

## Running

```bash
cd project
python manage.py runserver         # serves at http://127.0.0.1:8000
```

Open **http://127.0.0.1:8000** and click **Authorize Spotify**.

> If you change `.env`, restart the server — credentials are read once at
> startup and `.env` edits don't trigger Django's auto-reload.

## Project structure

```
project/
├── manage.py
├── project/            # Django project config
│   ├── settings.py
│   └── urls.py         # includes tasteSynth.urls
└── tasteSynth/         # the app
    ├── urls.py         # route definitions
    ├── views.py        # all view logic + Spotify OAuth helpers
    └── templates/
        ├── SynthTemplate.html   # landing page ("Authorize Spotify")
        ├── PlaylistList.html    # grid of the user's playlists
        └── PlaylistView.html    # track list (+ "Save Playlist" when merged)
```

### Routes

| Path                     | View                    | Purpose                                          |
| ------------------------ | ----------------------- | ------------------------------------------------ |
| `/`                      | `SynthView`             | Landing page                                     |
| `/authorization`         | `SpotifyAuthorization`  | Redirects to Spotify's OAuth consent screen      |
| `/auth_success`          | `SuccessfulAuthorization` | OAuth callback; stores the token in the session |
| `/playlist_list`         | `PlaylistList`          | Lists the user's owned and collaborative playlists |
| `/playlist_view/<id>`    | `PlaylistView`          | Shows the tracks of a single playlist            |
| `/merge_view`            | `MergeView`             | Computes the track intersection of N playlists   |
| `/save_playlist`         | `SavePlaylist`          | Creates a new private playlist from the overlap  |

OAuth scopes requested: `playlist-read-private`, `playlist-modify-public`,
`playlist-modify-private`.

## Troubleshooting

- **`SpotifyOauthError: No client_id`** — `.env` is missing or empty, or the
  server was started before `.env` existed. Create `project/.env` (see above)
  and restart the server.
- **Redirect URI mismatch** — the URI registered in the Spotify dashboard must
  exactly match `http://127.0.0.1:8000/auth_success`.
- **403 / user not registered** — add the Spotify account to the app's
  allow-list while it's in development mode.
