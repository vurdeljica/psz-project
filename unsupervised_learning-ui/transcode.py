import numpy as np
import os.path
import pandas as pd
import re
import sqlite3
import time

from datetime import datetime
from sklearn.feature_extraction.text import CountVectorizer
from sklearn import preprocessing

absolute_path_to_script = os.path.abspath(os.path.dirname(__file__))
absolute_path_to_database = os.path.join(absolute_path_to_script, "..\\resources\\discogs.db").replace('\\','/')

cnx = sqlite3.connect(absolute_path_to_database)

albums_df = pd.read_sql_query("SELECT * FROM album", cnx)
songs_df = pd.read_sql_query("SELECT * FROM song", cnx)
artists_df = pd.read_sql_query("SELECT * FROM artist", cnx)
albums_avg_columns = ['year', 'have', 'want', 'avg_rating', 'ratings', 'lowest', 'median', 'highest']
songs_avg_columns = ['duration']
artists_avg_columns = []


def clear_regular_text_column(field_content):
    if (field_content is None) or (field_content == '') or ('Various' in field_content) or (field_content == '--'):
        return 'unknown'

    return field_content


def clear_album_value(field_content):
    if field_content == '--' or field_content == 'Never':
        return '0'

    return re.match('.+?(\d+\.\d{2})$', field_content).group(1)


def clear_avg_rating(field_content):
    match = re.match('.*(\d+\.\d+)', field_content)
    if match is None:
        return '0'

    val = match.group(1)
    if val == '--':
        return '0'

    return val


def clear_numerical_columns(field_content):
    if field_content == '--':
        return '0'

    return field_content


def clear_last_sold(field_content):
    if field_content == '--' or field_content == 'Never':
        return '0'

    return time.mktime(datetime.strptime(field_content, '%d%b%y').timetuple())

def clear_duration(field_content):
    match = re.match('(\d+:\d+)', field_content)
    if match is None:
        return '0'

    return calculate_seconds(match.group(1))

def calculate_seconds(time_text):
    return sum(int(x) * 60 ** i for i,x in enumerate(reversed(time_text.split(":"))))

clear_columns_map = {
    ('album_name', 'artist_names', 'album_id', 'artist_ids',
     'label', 'country', 'format', 'style', 'genre',
     'song_id', 'song_name',
     'artist_id', 'site'): clear_regular_text_column,
    ('year', 'num_of_releases', 'have', 'want', 'ratings',
     'credits', 'vocals', 'arranged_by_cnt', 'lyrics_by_cnt', 'music_by_cnt'): clear_numerical_columns,
    'avg_rating': clear_avg_rating,
    ('lowest', 'median', 'highest'): clear_album_value,
    'last_sold': clear_last_sold,
    'duration': clear_duration
}

def get_cleared_column(column_name, data_frame):
    for key in clear_columns_map:
        if column_name in key:
            return data_frame[column_name].apply(clear_columns_map[key])

    return None


def clear_unknown_data(df):
    df.replace(np.nan, '--', inplace=True)
    columns = list(df.columns.values)

    for column in columns:
        df[column] = get_cleared_column(column, df)


data_frames = [albums_df, songs_df, artists_df]
data_frame_names = ['albums_df', 'songs_df', 'artists_df']
data_frame_avg_columns = [albums_avg_columns, songs_avg_columns, artists_avg_columns]


def copy_generated_columns_from_df2_to_df1(df1, df2, original_column):
    columns = list(df2.columns.values)
    for column in columns:
        if column == '':
            continue
        df1['generated_' + original_column + '_' + column] = df2[column]


def make_bag_of_words(column, min_count=1):
    column = column.fillna('<NAN>')
    if type(column.iloc[0]) != list: column = column.apply(lambda x: [x])
    counter = CountVectorizer(lowercase=False, tokenizer=lambda x: x, dtype=np.uint32, min_df=min_count)
    counter.fit(column)
    counts = pd.DataFrame(counter.transform(column).toarray())
    counts.columns = [str(x) for x in counter.get_feature_names()]
    return counts


def transcode_column_with_separator(column_name, data_frame):
    data_frame[column_name] = data_frame[column_name].str.strip()
    data_splited_by_separator = pd.Series(data_frame[column_name])
    data_splited_by_separator = data_splited_by_separator.str.split(';')

    bag_of_words = make_bag_of_words(data_splited_by_separator)

    return bag_of_words


def transcode_regular_text(column_name, data_frame):
    label_encoder = preprocessing.LabelEncoder()
    label_encoder.fit(data_frame[column_name])
    encoded_data_frame = pd.DataFrame()
    encoded_data_frame[column_name] = label_encoder.transform(data_frame[column_name])
    return encoded_data_frame


def transcode_numerical(column_name, data_frame):
    numerical_data_frame = pd.DataFrame()
    numerical_data_frame[column_name] = data_frame[column_name]

    return numerical_data_frame


transcode_map = {
    ('format', 'style', 'genre'): transcode_column_with_separator,
    ('album_name', 'artist_names', 'album_id', 'artist_ids', 'label', 'country',
     'song_id', 'song_name', 'album_id',
     'artist_id', 'site'): transcode_regular_text,
}


def get_transcoded_columns(column_name, data_frame):
    for key in transcode_map:
        if column_name in key:
            return transcode_map[key](column_name, data_frame)

    return transcode_numerical(column_name, data_frame)


def prepare_data_for_ml(data_frame):
    columns = list(data_frame.columns.values)
    for column in columns:
        data_frame_generated = get_transcoded_columns(column, data_frame)
        copy_generated_columns_from_df2_to_df1(data_frame, data_frame_generated, column)
    return data_frame


def cast_all_generated_columns_to_float(df):
    columns = list(data_frame.columns.values)
    for column in columns:
        if "generated" in column:
            df[column] = df[column].astype(float)


def replace_cleared_data_with_average(data_frame, index):
    avg_columns = data_frame_avg_columns[index]
    for column in avg_columns:
        data_frame[column] = data_frame[column].astype(float)
        temp_column = data_frame[column].replace(0, np.NaN)
        mean_value = temp_column.mean()
        data_frame[column] = data_frame[column].replace(0, mean_value)


for index, data_frame in enumerate(data_frames):
    clear_unknown_data(data_frame)
    replace_cleared_data_with_average(data_frame, index)
    table = prepare_data_for_ml(data_frame)
    cast_all_generated_columns_to_float(table)
    table.to_csv(absolute_path_to_script + '\\results\\' + data_frame_names[index] + '_prepared.csv', encoding="utf-8-sig")

