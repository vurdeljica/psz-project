import requests
import asyncio
from concurrent.futures import ThreadPoolExecutor
from timeit import default_timer

import sqlite3
import pandas as pd
import random

import threading

LOCK = threading.Lock()

print('1')

cnx = sqlite3.connect('C:/Users/igvu/Desktop/discogs_baze/bazeTestiranje/discogs_1990.db')

print('2')
proxies_list = []

print('3')
with open('C:/Users/igvu/Desktop/Fakultet/Drugi semestar/PSZ\psz-project/discorg_scraper/discorg_scraper/proxy.txt') as f:
    proxies_list = f.read().splitlines()

print('4')

song_df = pd.read_sql_query("SELECT * FROM song", cnx)

print('5')
list_of_translated_addresses = []
list_of_song_id = []

START_TIME = default_timer()
print('6')
def fetch(session, track):
    base_url = 'https://www.discogs.com/track/'

    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36"}

    proxies = {
        'https': random.choice(proxies_list)
    }

    with session.get(base_url + track, proxies=proxies, headers=headers) as response:
        data = response.text

        if response.status_code == 429:
            list_of_song_id.append(track)
        if response.status_code != 200:
            return data

        LOCK.acquire()
        list_of_translated_addresses.append(response.url)
        LOCK.release()


        elapsed = default_timer() - START_TIME
        time_completed_at = "{:5.2f}s".format(elapsed)
        print("{0:<30} {1:>20}".format(response.url, time_completed_at))

        return data

async def get_data_asynchronous():
    global list_of_song_id
    list_of_song_id = []

    for song_id in song_df['song_id']:
        list_of_song_id.append(song_id)

    print("{0:<30} {1:>20}".format("File", "Completed at"))
    with ThreadPoolExecutor(max_workers=300) as executor:
        with requests.Session() as session:
            # Set any session parameters here before calling `fetch`
            loop = asyncio.get_event_loop()
            START_TIME = default_timer()
            tasks = [
                loop.run_in_executor(
                    executor,
                    fetch,
                    *(session, csv) # Allows us to pass in multiple arguments to `fetch`
                )
                for csv in list_of_song_id
            ]
            for response in await asyncio.gather(*tasks):
                pass


loop = asyncio.get_event_loop()
future = asyncio.ensure_future(get_data_asynchronous())
loop.run_until_complete(future)

for translated_address in list_of_translated_addresses:
    url_base = translated_address[0]
    url = translated_address[1]
    song_df.loc[song_df['song_id'] == url_base, ['song_id']] = url

song_df.to_sql('song', cnx, if_exists='replace', index=False)