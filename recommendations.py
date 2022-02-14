import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy import SpotifyOAuth
import pandas as pd

client_id = 'XXXXXXXXXXX'
client_secret = 'XXXXXXXXXXX'
redirect_uri = 'http://localhost/'
scope = 'user-top-read user-library-read playlist-modify-private playlist-modify-public'

creds = SpotifyOAuth(scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)
sp = spotipy.Spotify(auth_manager=creds)


def create_songs_df(subject,item_list,sub_level):

    data = []
    col_id = subject +'_id'
    col_name = subject +'_name'
    l_df = pd.DataFrame(data, columns=[col_id,col_name])


    for l in item_list:
        if sub_level:
            l = l[sub_level]
        l_id = l['id']
        l_name = l['name']

        l_df = l_df.append({
                            col_id: l_id,
                            col_name: l_name
                            },
                           ignore_index=True)
    return l_df


##### Getting recent top tracks

top_results = sp.current_user_top_tracks(limit=50, offset=0, time_range='short_term')

top_df = create_songs_df(subject='top_songs',item_list=top_results['items'],sub_level=None)

top_list = top_df["top_songs_id"].to_list()


##### Get recommendations from these recent top songs

data=[]
recom_df = pd.DataFrame(data,columns=['recomm_id','recomm_name'])

for t in range(5,len(top_list)+1,5):
    recomms = sp.recommendations(seed_tracks = top_list[t-5:t],limit = 25)
    
    temp = create_songs_df(subject='recomm',item_list=recomms['tracks'],sub_level=None)

    recom_df = recom_df.append(temp, ignore_index = True)


recom_df = recom_df.drop_duplicates(subset=None, keep='first', inplace=False)


##### Get all songs saved in the library and remove recommended songs that are present in saved songs

results = sp.current_user_saved_tracks()
tracks = results['items']

while results['next']:
    results = sp.next(results)
    tracks.extend(results['items'])


my_songs_df = create_songs_df(subject='my_songs',item_list=tracks,sub_level='track')

cond = recom_df['recomm_id'].isin(my_songs_df['my_songs_id'])
recom_df.drop(recom_df[cond].index, inplace=True)



## add songs to the playlist

playlist_id='0JMMsCi7Tpri9QRXda2kbt'
items = recom_df["recomm_id"].to_list()

for i in range(100,len(items),100):
    sp.playlist_add_items(playlist_id, items[i-100:i])



## delete songs present in the playlist


playlist_id='0JMMsCi7Tpri9QRXda2kbt'

results = sp.playlist_items(playlist_id, fields=None, limit=100, offset=0, market=None, additional_types=('track', 'episode'))
tracks = results["items"]

while results["next"]:
    results = sp.next(results)
    tracks.extend(results['items'])

to_delete = []  

for t in tracks:
    track = t["track"]
    item_id = track["id"]
    #result = sp.track(item_id, market=None)
    #uri = result["uri"]
    to_delete.append(item_id)

to_delete_number = len(to_delete)
    

while to_delete_number > 0:

    if to_delete_number >100:
        to_delete_1 = to_delete[0:100]
        remaining = to_delete_number - 100
    else:
        to_delete_1 = to_delete[0:remaining]
        to_delete_number = 0

    sp.user_playlist_remove_all_occurrences_of_tracks('lbrechot10', playlist_id,tracks=to_delete_1)


#my_songs_df["date"] = pd.to_datetime(my_songs_df["date"])
#my_songs_df["year-month"] = my_songs_df["date"].dt.strftime('%Y-%m')

#trend = my_songs_df.groupby(["year-month"])["dance_ratio"].mean()
#trend_df = pd.DataFrame(trend, columns=["dance_ratio"])
#trend_df.reset_index()
#trend_df.sort_values(by="year-month", ascending=False)
    
