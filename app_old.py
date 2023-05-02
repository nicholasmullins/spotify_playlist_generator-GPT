import openai
import json
import spotipy
import pprint
import argparse

from dotenv import dotenv_values
config = dotenv_values(".env")
openai.api_key = config["API_KEY"]

parser = argparse.ArgumentParser(description="Simple command line playlist type request")
parser.add_argument("-p", type=str, default="untitled playlist", help="the prompt to describe the type of playlist you want")
parser.add_argument("-n", type=int, default=8, help="the number of songs you want")

args = parser.parse_args()

def get_playlist(prompt, count):
    example_json = """
    [
    {"song": "Everybody Hurts", "artist": "R.E.M."},
    {"song": "Nothing Compares 2 U", "artist": "Sinead O'Connor"},
    {"song": "Hurt", "artist": "Johnny Cash"},
    {"song": "Tears in Heaven", "artist": "Eric Clapton"},
    {"song": "My Heart Will Go On", "artist": "Celine Dion"}
    ]

    """
    messages = [
        {"role":"system", "content": """ You are a helpful playlist generating assistant. You should generate a playlist or a list of songs and their artists according to a text prompt. You should return a JSON array where each element follows this format: {"song": <song_title>, "artist": <artist_name>} """},
        {"role":"user", "content": "Generate a playlist of 5 songs based on this prompt: super sad songs"},
        {"role":"assistant", "content": example_json},
        {"role":"user", "content": f"Generate a playlist of {count} songs based on this prompt: {prompt}"}
    ]

    res = openai.ChatCompletion.create(
        messages=messages,
        model="gpt-3.5-turbo",
        max_tokens=400
    )


    playlist = json.loads(res["choices"][0]["message"]["content"])
    return playlist

playlist = get_playlist(args.p, args.n)
print(playlist)

spot_call = spotipy.Spotify(
    auth_manager=spotipy.SpotifyOAuth(
        client_id=config["SPOTIFY_CLIENT_ID"],
        client_secret=config["SPOTIFY_CLIENT_SECRET"],
        redirect_uri="http://localhost:9999",
        scope="playlist-modify-private"
    )
)

current_user = spot_call.current_user()

track_ids = []
assert current_user is not None

for item in playlist:
    artist, song = item["artist"], item["song"]
    query = f"{song} {artist}"
    search_results = spot_call.search(q=query, type="track", limit=10)
    track_ids.append(search_results["tracks"]["items"][0]["id"])

created_playlist = spot_call.user_playlist_create(
    current_user["id"],
    public=False,
    name=args.p
)

spot_call.user_playlist_add_tracks(current_user["id"], created_playlist["id"], track_ids )