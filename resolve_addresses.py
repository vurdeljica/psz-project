import sqlite3
import pandas as pd
import random
import requests
from threading import Thread
import sys
from queue import Queue
from time import sleep
import numpy
import threading
import time

concurrent = 150
LOCK = threading.Lock()

cnx = sqlite3.connect('C:/Users/igvu/Desktop/discogs_baze/bazeTestiranje/discogs_new_all.db',
                          check_same_thread=False)

song_df = pd.read_sql_query("SELECT * FROM song", cnx)

list_of_translated_addresses = []
list_of_jobs = []


proxies_list = []
with open('C:/Users/igvu/Desktop/Fakultet/Drugi semestar/PSZ\psz-project/discorg_scraper/discorg_scraper/proxy.txt') as f:
    proxies_list = f.read().splitlines()

list_of_song_id = []

total = 0

def doWork():
    list_of_translated_addresses_per_thread = []
    list_of_jobs_per_thread = []
    start = time.time()

    LOCK.acquire()
    global list_of_jobs
    list_of_jobs_per_thread = list_of_jobs.pop(0)
    LOCK.release()


    while len(list_of_jobs_per_thread) > 0:
        time_now = time.time()
        if (time_now - start > 60 * 60):
            break
    #while not q.empty():
        #url_base = q.get()
        url_base = list_of_jobs_per_thread.pop(0)
        num_of_exceptions = 0

        url_full = '--'
        status_code = 0
        while num_of_exceptions < 100:
            try:
                headers = {
                    'User-Agent': "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36"}

                proxies = {
                    'https': random.choice(proxies_list)
                }

                url_full = requests.get('https://www.discogs.com/track/' + url_base, proxies=proxies, headers=headers, timeout=3)
                status_code = url_full.status_code

                if status_code == 429:
                    raise ValueError('429 Error')

                conn = url_full
                url_full = url_full.url
                conn.close()

                break
            except Exception as e:
                #print(e)
                #print(num_of_exceptions)

                if num_of_exceptions == 100 and status_code == 429:
                    print("going to sleep...")
                    sleep(61)
                    num_of_exceptions = 0

                # print("exception")
                num_of_exceptions = num_of_exceptions + 1

        LOCK.acquire()

        global total
        total = total + 1
        print(url_full, "total done: ", total, " remaining by thread: ", len(list_of_jobs_per_thread))

        LOCK.release()

        if (url_full != '--') and ("/track" not in url_full):
            list_of_translated_addresses_per_thread.append((url_base, url_full))
            start = time.time()
            #updateDatabase(url_full, url_base)
        elif (url_full != '--') and (status_code == 404):
            continue
        else:
            #q.put(url_base)
            list_of_jobs_per_thread.append(url_base)

        #q.task_done()

    LOCK.acquire()
    global list_of_translated_addresses
    list_of_translated_addresses += list_of_translated_addresses_per_thread
    LOCK.release()

#def updateDatabase(url, url_base):
#    LOCK.acquire()
#
#    list_of_translated_addresses.append((url_base, url))
#
#    LOCK.release()

#q = Queue(concurrent * 2)
#q = Queue(1_000_000)

for song_id in song_df['song_id']:
    list_of_song_id.append(song_id)
    #q.put(song_id)
list_of_jobs = list(numpy.array_split(numpy.array(list_of_song_id), concurrent * 2))
list_of_jobs = [list(x) for x in list_of_jobs]

thread_list = []
for i in range(2 * concurrent):
    t = Thread(target=doWork)
    t.daemon = True
    thread_list.append(t)
    t.start()

for thread in thread_list:
    thread.join()

#q.join()



for translated_address in list_of_translated_addresses:
    url_base = translated_address[0]
    url = translated_address[1]
    song_df.loc[song_df['song_id'] == url_base, ['song_id']] = url

song_df.to_sql('song', cnx, if_exists='replace', index=False)