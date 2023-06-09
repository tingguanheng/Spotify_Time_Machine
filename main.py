from date_input import DATE_INPUT
from spotify import SPOTIFY
from Webscrapper import BILLBOARD_100
import spotipy

input_date = DATE_INPUT()
input_date.enter_date()
billboard100 = BILLBOARD_100(added_date=input_date.converted_date)

# Connect to Spotify
scope = ["playlist-read-private","playlist-read-collaborative","playlist-modify-private","playlist-modify-public"]

auth = spotipy.oauth2.SpotifyOAuth(client_id=[CLIENT_ID], 
                                      client_secret=[CLIENT_SECRET],
                                      redirect_uri="http://localhost:3000",
                                      scope=scope)


sp = spotipy.Spotify(auth_manager=auth)

myself = sp.current_user()


current_playlists = sp.current_user_playlists()

list_of_playlists = {}
for line in current_playlists["items"]:
    list_of_playlists[line["name"]] = line["id"]

# Create new playlist if doesn't exist
if f"{input_date.converted_date} Top 100" not in list_of_playlists:
    sp.user_playlist_create(user=myself["id"],
                            name= f"{input_date.converted_date} Top 100",
                            public=False,
                            collaborative=False)
    
    current_playlists = sp.current_user_playlists()
    new_playlist_id = current_playlists["items"][0]["id"]
    new_playlist_name = current_playlists["items"][0]["name"]
# Else pull out relevant playlist id
else:
    new_playlist_id = list_of_playlists.get(f"{input_date.converted_date} Top 100")

# Search for songs
for entry in range(len(billboard100.list_of_songs)):
    results = sp.search(q=f"{billboard100.list_of_songs[entry]} {billboard100.list_of_artists[entry]}",type="track")
    item_results = results["tracks"]["items"]
    # Data Cleaning segment
    matching_song = billboard100.list_of_songs[entry].lower().replace(" ","").split("feat")[0]
    matching_song = matching_song.split("(")[0]
    matching_song = matching_song.split("&")[0]
    matching_song = matching_song.split("/")[0]
    matching_song = matching_song.split("-")[0]
    matching_song = matching_song.replace("lil","").replace("\*","").replace("\'","").replace("degrees","º").replace("!","").replace(",","").replace("$","s").replace("’","").replace("\.","")

    matching_artist = billboard100.list_of_artists[entry].lower().replace(" ","").split("feat")[0]
    matching_artist = matching_artist.split("(")[0]        
    matching_artist = matching_artist.split("with")[0]
    matching_artist = matching_artist.split("&")[0]
    matching_artist = matching_artist.split("/")[0]
    matching_artist = matching_artist.split("-")[0]
    matching_artist = matching_artist.replace("lil","").replace("\*","").replace("\'","").replace("degrees","º").replace("!","").replace(",","").replace("$","s").replace("’","").replace("\.","")
    # Data Validation segment
    for index in range(len(item_results)):
        search_results = results["tracks"]["items"][index]
        # Data Cleaning segment
        validation_track = search_results["name"].lower().replace(" ","").split("feat")[0]
        validation_track = validation_track.split("(")[0]
        validation_track = validation_track.split("&")[0]
        validation_track = validation_track.split("/")[0]
        validation_track = validation_track.split("-")[0]
        validation_track = validation_track.replace("lil","").replace("\*","").replace("\'","").replace("degrees","º").replace("!","").replace(",","").replace("ñ","n").replace("$","s").replace("’","").replace("á","a").replace("\.","")

        validation_artist1 = search_results["artists"][0]["name"].lower().replace(" ","").split("feat")[0]
        validation_artist1 = validation_artist1.split("(")[0]        
        validation_artist1 = validation_artist1.split("with")[0]
        validation_artist1 = validation_artist1.split("&")[0]
        validation_artist1 = validation_artist1.split("/")[0]
        validation_artist1 = validation_artist1.split("-")[0]
        validation_artist1 = validation_artist1.replace("lil","").replace("\*","").replace("\'","").replace("degrees","º").replace("ý","y").replace("!","").replace("é","e").replace(",","").replace("ñ","n").replace("$","s").replace("’","").replace("\.","")

        try:
            validation_artist2 = search_results["artists"][1]["name"].lower().replace(" ","").split("feat")[0]
            validation_artist2 = validation_artist2.split("(")[0]        
            validation_artist2 = validation_artist2.split("with")[0]
            validation_artist2 = validation_artist2.split("&")[0]
            validation_artist2 = validation_artist2.split("/")[0]
            validation_artist2 = validation_artist2.split("-")[0]
            validation_artist2 = validation_artist2.replace("lil","").replace("\*","").replace("\'","").replace("degrees","º").replace("ý","y").replace("!","").replace("é","e").replace(",","").replace("ñ","n").replace("$","s").replace("’","").replace("\.","")
        except:
            pass
        # Data Validation segment
        if matching_song not in validation_track or matching_artist not in validation_artist1:
            #with open("log.txt",mode = "a") as file:
            #    file.write(f"{entry}.\n{item_results}")
            if matching_song not in validation_track and matching_artist not in validation_artist1:
                print(f"song name {matching_song} does not match with {validation_track}\nartist name {matching_artist} does not match with {validation_artist1}")
                continue
            elif matching_song not in validation_track:
                print(f"song name {matching_song} does not match with {validation_track}")
                continue
            elif matching_artist not in validation_artist1:
                print(f"artist name {matching_artist} does not match with {validation_artist1}")
                try:
                    if matching_artist in validation_artist2:
                        song_id = search_results["id"]
                        print(f"name:{matching_song}   id:{song_id}")
                        break
                    else:
                        print(f"artist name {matching_artist} does not match with {validation_artist2}")
                        continue
                except:
                    pass
            else:
                print(f"There is an issue.\n{matching_song} does not match with {validation_track}\n{matching_artist} does not match with {validation_artist1}")
                continue
        else:
            song_id = search_results["id"]
            print(f"name:{matching_song}   id:{song_id}")
            break

    playlist_songs = []
    playlist_content = sp.playlist_items(playlist_id=new_playlist_id)
    for items in playlist_content["items"]:
        playlist_content = items["track"]["id"]
        playlist_songs.append(playlist_content)

    # Add song to playlist
    if song_id not in playlist_songs:
        sp.user_playlist_add_tracks(user=myself["id"],playlist_id=new_playlist_id,tracks=[song_id]) #Looking for track id,must be in a list
        print(f"{billboard100.list_of_songs[entry]} added")

