import os.path
import pandas as pd
import sqlite3

from collections import defaultdict

absolute_path_to_script = os.path.abspath(os.path.dirname(__file__))
absolute_path_to_database = os.path.join(absolute_path_to_script, "..\\resources\\discogs.db").replace('\\','/')

cnx = sqlite3.connect(absolute_path_to_database)

albums_df = pd.read_sql_query("SELECT * FROM album", cnx)
artist_df = pd.read_sql_query("SELECT * FROM artist", cnx)
song_df = pd.read_sql_query("SELECT * FROM song", cnx)


def get_dictionary(column, table, separator=';'):
    dictionary = defaultdict(int)
    for index, row in table.iterrows():
        line = row[column]

        if line == '--':
            continue

        items = line.split(separator)
        for item in items:
            dictionary[item] += 1

    return dictionary


#2.a
genre_dictionary = get_dictionary('genre', albums_df)
genre_df = pd.DataFrame(list(genre_dictionary.items()), columns=['genre','count'])
genre_df.to_csv(absolute_path_to_script + "\\results\\2a.csv", index=False, encoding="utf-8-sig")

#2.b
style_dictionary = get_dictionary('style', albums_df)
style_df = pd.DataFrame(list(style_dictionary.items()), columns=['style','count'])
style_df.to_csv(absolute_path_to_script + "\\results\\2b.csv", index=False, encoding="utf-8-sig")

#2.c
albums_df['num_of_releases']=albums_df['num_of_releases'].astype(int)
largest_num_of_releases = albums_df.sort_values(by='num_of_releases', ascending=False)
index = 20
while True:
    if len(set(largest_num_of_releases['num_of_releases'].values[:index])) == 21:
        break

    index += 1

largest_num_of_releases = largest_num_of_releases.head(index-1)
largest_num_of_releases = largest_num_of_releases.groupby(['album_name', 'artist_names', 'artist_ids', 'num_of_releases','country'])
largest_num_of_releases = pd.DataFrame(largest_num_of_releases.size().reset_index(name = "Group_Count"))
largest_num_of_releases = largest_num_of_releases.sort_values(by='num_of_releases', ascending=False)
largest_num_of_releases = largest_num_of_releases.drop(columns=['Group_Count'])
largest_num_of_releases.to_csv(absolute_path_to_script + '\\results\\2c.csv', index=False, encoding="utf-8-sig")

#2.d
artist_sorted_by_credits = artist_df[artist_df['credits'] != '--']
artist_sorted_by_credits = artist_sorted_by_credits.assign(credits=lambda d: d['credits'].astype(int))
artist_sorted_by_credits = artist_sorted_by_credits.sort_values('credits', ascending=False).head(100)

artist_sorted_by_vocals = artist_df[artist_df['vocals'] != '--']
artist_sorted_by_vocals = artist_sorted_by_vocals.assign(vocals=lambda d: d['vocals'].astype(int))
artist_sorted_by_vocals = artist_sorted_by_vocals.sort_values('vocals', ascending=False).head(100)

artist_sorted_by_arranged = artist_df.sort_values('arranged_by_cnt', ascending=False).head(100)
artist_sorted_by_lyrics = artist_df.sort_values('lyrics_by_cnt', ascending=False).head(100)
artist_sorted_by_music = artist_df.sort_values('music_by_cnt', ascending=False).head(100)

artist_sorted_by_credits.to_csv(absolute_path_to_script + '\\results\\2d1.csv', index=False, encoding="utf-8-sig")
artist_sorted_by_vocals.to_csv(absolute_path_to_script + '\\results\\2d2.csv', index=False, encoding="utf-8-sig")
artist_sorted_by_arranged.to_csv(absolute_path_to_script + '\\results\\2d3.csv', index=False, encoding="utf-8-sig")
artist_sorted_by_lyrics.to_csv(absolute_path_to_script + '\\results\\2d4.csv', index=False, encoding="utf-8-sig")
artist_sorted_by_music.to_csv(absolute_path_to_script + '\\results\\2d5.csv', index=False, encoding="utf-8-sig")


#2.e
songs_highest_appearences = song_df.groupby(['song_id']).size().reset_index(name='counts')
songs_highest_appearences = songs_highest_appearences.sort_values('counts', ascending=False).head(100)
columns=['songs_id', 'song_name', 'counts', 'album_id', 'album_name', 'format', 'country', 'year', 'genre', 'style']
songs_with_albums = pd.DataFrame(columns=columns)
for index, row in songs_highest_appearences.iterrows():
    song_id = row['song_id']
    duration = row['counts']
    song_name = song_df[song_df['song_id'] == song_id]['song_name'].values[0]
    albums_with_song_id = song_df[song_df['song_id'] == song_id]
    for song_index, song_row in albums_with_song_id.iterrows():
        new_row = []
        new_row.append(song_id)
        new_row.append(song_name)
        new_row.append(duration)
        album_row = albums_df[albums_df['album_id'] == song_row['album_id']].values[0]
        new_row.append(album_row[2])
        new_row.append(album_row[0])
        new_row.append(album_row[5])
        new_row.append(album_row[8])
        new_row.append(album_row[9])
        new_row.append(album_row[6])
        new_row.append(album_row[7])
        new_df = pd.DataFrame(data=[new_row], columns=columns)
        songs_with_albums = songs_with_albums.append(new_df, ignore_index=True)

songs_with_albums.to_csv(absolute_path_to_script + '\\results\\2e.csv', encoding="utf-8-sig")

#2.f
artist_with_sites = artist_df[artist_df['site'] != '--']
artist_with_sites = artist_with_sites[['artist_id', 'site']]
artist_with_sites.to_csv(absolute_path_to_script + '\\results\\2f.csv', index=False, encoding="utf-8-sig")

