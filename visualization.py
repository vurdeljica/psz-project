import sqlite3
import pandas as pd
from collections import defaultdict

import collections
import operator
import re
import matplotlib.pyplot as plt

cnx = sqlite3.connect('C:/Users/igvu/Desktop/discogs_baze/t/discogs0.db')

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

genre_dictionary = get_dictionary('genre', albums_df)

#3.a
sorted_genre_dictionary = sorted(genre_dictionary.items(), key = operator.itemgetter(1), reverse=True)
sorted_genre_dictionary = collections.OrderedDict(sorted_genre_dictionary)
sorted_genre_keys = list(sorted_genre_dictionary.keys())[0:6]
sorted_genre_values = list(sorted_genre_dictionary.values())[0:6]
print(sorted_genre_keys)
print(sorted_genre_values)

plt.figure(1, [15, 8])
plt.title('Most common genres')
plt.bar(sorted_genre_keys, sorted_genre_values)
plt.show()

##3.b
def calculate_seconds(time_text):
    return sum(int(x) * 60 ** i for i,x in enumerate(reversed(time_text.split(":"))))

#pretpostavka je da uzimamo jednu pesmu, iako je drugacije vreme trajanja od albuma do albuma
song_df_without_duplicates = song_df.drop_duplicates(subset='song_id', keep="first")

songs_by_duration = [0, 0, 0, 0, 0, 0]
for index, row in song_df_without_duplicates.iterrows():
    songs_duration_text = row['duration']
    if songs_duration_text == '--':
        continue

    songs_duration = calculate_seconds(songs_duration_text)
    if songs_duration in range(0, 91):
        songs_by_duration[0] += 1
    elif songs_duration in range(91, 181):
        songs_by_duration[1] += 1
    elif songs_duration in range(181, 241):
        songs_by_duration[2] += 1
    elif songs_duration in range(241, 301):
        songs_by_duration[3] += 1
    elif songs_duration in range(301, 361):
        songs_by_duration[4] += 1
    elif songs_duration >= 361:
        songs_by_duration[5] += 1

songs_by_duration_index = ["<=90", "(90, 180]", "(180, 240]", "(240, 300]", "(300, 360]", "360>="]

print(songs_by_duration_index)
print(songs_by_duration)

plt.figure(2, [15, 8])
plt.title('Songs by duration')
plt.bar(songs_by_duration_index, songs_by_duration)
plt.show()

#3.c
albums_by_years = [0, 0, 0, 0, 0, 0, 0]
for index, row in albums_df.iterrows():
    year_text = row['year']
    if year_text == '--':
        continue

    year = int(year_text)
    if year in range(1950, 1960):
        albums_by_years[0] += 1
    elif year in range(1960, 1970):
        albums_by_years[1] += 1
    elif year in range(1970, 1980):
        albums_by_years[2] += 1
    elif year in range(1980, 1990):
        albums_by_years[3] += 1
    elif year in range(1990, 2000):
        albums_by_years[4] += 1
    elif year in range(2000, 2010):
        albums_by_years[5] += 1
    elif year >= 2010:
        albums_by_years[6] += 1

albums_by_years_index = ["[1950, 1960)", "[1960, 1970)", "[1970, 1980)", "[1980, 1990)", "[1990, 2000)", "[2000, 2010)", "2010>="]

print(albums_by_years_index)
print(albums_by_years)

plt.figure(3, [15, 8])
plt.title('Albums by years')
plt.bar(albums_by_years_index, albums_by_years)
plt.show()

#3.d
def has_cyrillic(text):
   return bool(re.search('[а-шА-Ш]', text))

latin_cyrilic_album_names = [0, 0]
for index, row in albums_df.iterrows():
    album_name = row['album_name']
    if album_name == '--':
        continue

    if has_cyrillic(album_name):
        latin_cyrilic_album_names[0] += 1
    elif not has_cyrillic(album_name):
        latin_cyrilic_album_names[1] += 1

albums_by_latin_cyrillic_names_index = ["Cyrillic", "Latin"]

print(albums_by_years_index)

print(latin_cyrilic_album_names)
sum_of_latin_cyrilic = sum(latin_cyrilic_album_names)
latin_cyrilic_percentage = [latin_cyrilic_cnt * 100 / sum_of_latin_cyrilic for latin_cyrilic_cnt in latin_cyrilic_album_names]
print(latin_cyrilic_percentage)

plt.figure(4, [15, 8])
plt.title('Albums names by latin/cyrillic')
graph = plt.bar(albums_by_latin_cyrillic_names_index, latin_cyrilic_album_names)

for index, p in enumerate(graph.patches):
    width, height = p.get_width(), p.get_height()
    x, y = p.get_xy()
    plt.annotate('{:.0%}'.format(latin_cyrilic_percentage[index] / 100), (x + 0.375, y + height + 500))

plt.show()

##3.e
genre_percentage = [0, 0, 0, 0]
for index, row in albums_df.iterrows():
    line = row['genre']

    if line == '--':
        continue

    items = line.split(';')
    size = len(items) - 1
    genre_percentage[size if size < 3 else 3] += 1

genre_number_index = ["1", "2", "3", "4>="]
genre_number = genre_percentage
print(genre_number_index)
print(genre_percentage)
sum_of_genres = sum(genre_percentage)
genre_percentage = [genre_cnt * 100 / sum_of_genres for genre_cnt in genre_percentage]
print(genre_percentage)

plt.figure(5, [15, 8])
plt.title('Albums bu number of genres')
graph = plt.bar(genre_number_index, genre_number)

for index, p in enumerate(graph.patches):
    width, height = p.get_width(), p.get_height()
    x, y = p.get_xy()
    plt.annotate('{:.0%}'.format(genre_percentage[index] / 100), (x + 0.360, y + height + 500))

plt.show()