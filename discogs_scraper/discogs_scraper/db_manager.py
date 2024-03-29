import os
import os.path
import pandas as pd
import sqlite3


absolute_path_to_script = os.path.abspath(os.path.dirname(__file__))
absolute_path_to_database = os.path.join(absolute_path_to_script, '..\\..\\resources\\discogs.db').replace('\\','/')


class DatabaseManager(object):

    instance = None

    def __new__(cls):
        if DatabaseManager.instance is None:
            DatabaseManager.instance = DatabaseManager.__DatabaseManager()
        return DatabaseManager.instance

    class __DatabaseManager(object):
        def __init__(self):
            self.create_connection()
            self.create_table()

        def create_connection(self):
            #self.conn = sqlite3.connect(absolute_path_to_database)
            self.conn = sqlite3.connect(":memory:")
            self.curr = self.conn.cursor()

            conn2 = sqlite3.connect(absolute_path_to_database)
            with conn2:
                for line in conn2.iterdump():
                    if line not in ('BEGIN;', 'COMMIT;'):  # let python handle the transactions
                        self.conn.execute(line)
            conn2.commit()
            conn2.close()

        def save_database_to_disk(self):
            if os.path.exists(absolute_path_to_database):
                os.remove(absolute_path_to_database)

            conn2 = sqlite3.connect(absolute_path_to_database)
            with conn2:
                for line in self.conn.iterdump():
                    if line not in ('BEGIN;', 'COMMIT;'):  # let python handle the transactions
                        conn2.execute(line)
            conn2.commit()
            conn2.close()

        def create_table(self):
            self.curr.execute("""create table if not exists album(
                                    album_name text,
                                    artist_names text,
                                    album_id text,
                                    artist_ids text,
                                    label text,
                                    format text,
                                    genre text,
                                    style text,
                                    country text,
                                    year text,
                                    num_of_releases text,
                                    have text,
                                    want text,
                                    avg_rating text,
                                    ratings text,
                                    last_sold text,
                                    lowest text,
                                    median text,
                                    highest text
                                )""")

            self.curr.execute("""create table if not exists artist(
                                    artist_id text type unique,
                                    credits text,
                                    vocals text,
                                    site text,
                                    arranged_by_cnt integer,
                                    lyrics_by_cnt integer, 
                                    music_by_cnt integer
                                 )""")


            self.curr.execute("""create table if not exists song(
                                    song_id text,
                                    song_name text,
                                    album_id text,
                                    duration text
                                 )""")



        def store_album_db(self, item):
            for field in item.fields:
                item.setdefault(field, '--')

            self.curr.execute("""insert into album values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",(
                                    item['album_name'],
                                    item['artist_names'],
                                    item['album_id'],
                                    item['artist_ids'],
                                    item['label'],
                                    item['format'],
                                    item['genre'],
                                    item['style'],
                                    item['country'],
                                    item['year'],
                                    item['num_of_releases'],
                                    item['have'],
                                    item['want'],
                                    item['avg_rating'],
                                    item['ratings'],
                                    item['last_sold'],
                                    item['lowest'],
                                    item['highest'],
                                    item['median']
                                ))
            self.conn.commit()



        def store_artist_statistics(self, item):
            item.setdefault('artist_id', '--')
            item.setdefault('credits', '--')
            item.setdefault('vocals', '--')
            item.setdefault('site', '--')
            item.setdefault('arranged_by_cnt', 0)
            item.setdefault('lyrics_by_cnt', 0)
            item.setdefault('music_by_cnt', 0)

            try:
                self.curr.execute("""insert into artist values (?,?,?,?,?,?,?)""", (
                    item['artist_id'],
                    item['credits'],
                    item['vocals'],
                    item['site'],
                    item['arranged_by_cnt'],
                    item['lyrics_by_cnt'],
                    item['music_by_cnt']))
            except sqlite3.IntegrityError:
                self.curr.execute("""UPDATE artist SET 
                                        arranged_by_cnt = ?, 
                                        lyrics_by_cnt = ?, 
                                        music_by_cnt = ? 
                                    WHERE artist_id = ? """,
                                 (item['arranged_by_cnt'],
                                  item['lyrics_by_cnt'],
                                  item['music_by_cnt'],
                                  item['artist_id']))

            self.conn.commit()

        def update_artist_info(self, item):
            item.setdefault('artist_id', '--')
            item.setdefault('credits', '--')
            item.setdefault('vocals', '--')
            item.setdefault('site', '--')
            item.setdefault('arranged_by_cnt', 0)
            item.setdefault('lyrics_by_cnt', 0)
            item.setdefault('music_by_cnt', 0)

            self.curr.execute("""UPDATE artist SET 
                                    credits = ?, 
                                    vocals = ?, 
                                    site = ? 
                                WHERE artist_id = ? """,
                            (item['credits'],
                             item['vocals'],
                             item['site'],
                             item['artist_id']))
            self.conn.commit()

        def store_song_db(self, item):
            for field in item.fields:
                item.setdefault(field, '--')

            self.curr.execute("""insert into song values (?,?,?,?)""",(
                                    item['song_id'],
                                    item['song_name'],
                                    item['album_id'],
                                    item['duration']
                              ))
            self.conn.commit()

        def get_artist_db(self, artist_id):
            self.curr.execute("""SELECT * FROM artist WHERE artist_id = (?) """, (artist_id,))

            return self.curr.fetchall()

        def get_album_db(self, album_id):
            self.curr.execute("""SELECT * FROM album WHERE album_id = (?) """, (album_id,))

            return self.curr.fetchall()

        def get_songs_set(self):
            song_df = pd.read_sql_query("SELECT * FROM song", self.conn)
            return set(song_df['song_id'])

        def get_song_db(self, song_id, album_id):
            self.curr.execute("""SELECT * FROM song WHERE song_id = (?) AND album_id = (?) """, (song_id, album_id))

            return self.curr.fetchall()
