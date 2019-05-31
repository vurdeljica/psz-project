import scrapy
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
import re
from ..items import DiscogsAlbum
from ..items import DiscogsArtist
from ..items import DiscogsSongs
from ..db_manager import DatabaseManager
from unidecode import unidecode
from urllib.parse import unquote
import requests

from scrapy.crawler import CrawlerProcess


class DiscorgSpider(scrapy.Spider):
    name = "discorg"
    start_urls = [
        'https://www.discogs.com/search/?style_exact=Vocal&style_exact=Easy+Listening&style_exact=Folk&style_exact=Country&style_exact=Swing&genre_exact=Blues'
        #'https://www.discogs.com/search/?decade=2010&country_exact=Yugoslavia',
        #'https://www.discogs.com/search/?decade=2000&country_exact=Yugoslavia',
        #'https://www.discogs.com/search/?decade=1990&country_exact=Yugoslavia', #granica, ukljucuje
        #'https://www.discogs.com/search/?year=1980&decade=1980&country_exact=Yugoslavia',
        #'https://www.discogs.com/search/?year=1981&decade=1980&country_exact=Yugoslavia',
        #'https://www.discogs.com/search/?year=1982&decade=1980&country_exact=Yugoslavia',
        #'https://www.discogs.com/search/?year=1983&decade=1980&country_exact=Yugoslavia',
        #'https://www.discogs.com/search/?year=1984&decade=1980&country_exact=Yugoslavia',
        #'https://www.discogs.com/search/?year=1985&decade=1980&country_exact=Yugoslavia',
        #'https://www.discogs.com/search/?year=1986&decade=1980&country_exact=Yugoslavia'
        #'https://www.discogs.com/search/?year=1987&decade=1980&country_exact=Yugoslavia',
        #'https://www.discogs.com/search/?year=1988&decade=1980&country_exact=Yugoslavia',
        #'https://www.discogs.com/search/?year=1989&decade=1980&country_exact=Yugoslavia',
        #'https://www.discogs.com/search/?year=1970&decade=1970&country_exact=Yugoslavia',
        #'https://www.discogs.com/search/?year=1971&decade=1970&country_exact=Yugoslavia',
        #'https://www.discogs.com/search/?year=1972&decade=1970&country_exact=Yugoslavia',
        #'https://www.discogs.com/search/?year=1973&decade=1970&country_exact=Yugoslavia',
        #'https://www.discogs.com/search/?year=1974&decade=1970&country_exact=Yugoslavia',
        #'https://www.discogs.com/search/?year=1975&decade=1970&country_exact=Yugoslavia',
        #'https://www.discogs.com/search/?year=1976&decade=1970&country_exact=Yugoslavia',
        #'https://www.discogs.com/search/?year=1977&decade=1970&country_exact=Yugoslavia',
        #'https://www.discogs.com/search/?year=1978&decade=1970&country_exact=Yugoslavia',
        #'https://www.discogs.com/search/?year=1979&decade=1970&country_exact=Yugoslavia', #granica, ukljucuje
        #'https://www.discogs.com/search/?decade=1960&country_exact=Yugoslavia',
        #'https://www.discogs.com/search/?decade=1950&country_exact=Yugoslavia',
        #'https://www.discogs.com/search/?decade=1940&country_exact=Yugoslavia',
        #'https://www.discogs.com/search/?decade=1930&country_exact=Yugoslavia',
        #'https://www.discogs.com/search/?decade=1920&country_exact=Yugoslavia',
        #'https://www.discogs.com/search/?year=2010&decade=2010&country_exact=Serbia',
        #'https://www.discogs.com/search/?year=2011&decade=2010&country_exact=Serbia',
        #'https://www.discogs.com/search/?year=2012&decade=2010&country_exact=Serbia',
        #'https://www.discogs.com/search/?year=2013&decade=2010&country_exact=Serbia',
        #'https://www.discogs.com/search/?year=2014&decade=2010&country_exact=Serbia',
        #'https://www.discogs.com/search/?year=2015&decade=2010&country_exact=Serbia',
        #'https://www.discogs.com/search/?year=2016&decade=2010&country_exact=Serbia',
        #'https://www.discogs.com/search/?year=2017&decade=2010&country_exact=Serbia',
        #'https://www.discogs.com/search/?year=2018&decade=2010&country_exact=Serbia',
        #'https://www.discogs.com/search/?year=2019&decade=2010&country_exact=Serbia',
        #'https://www.discogs.com/search/?decade=2000&country_exact=Serbia',
        #'https://www.discogs.com/search/?decade=1990&country_exact=Serbia'
    ]

    def parseLabelContent(self, content):
        labels_list = content.css("::text").extract()
        labels_list = [label.strip() for label in labels_list]
        labels = "".join(labels_list)

        return labels

    def parseFormatContent(self, content):
        format_link_list = content.css("a::text").extract()
        format_link_list = [format.strip() for format in format_link_list]
        format_link_string = ";".join(format_link_list)

        format_div_list = content.css(".content::text").extract()
        for format in format_div_list:
            if format != "":
                format = "".join(format.split())
                format = format.replace(',', ';')
                format_link_string = format_link_string + format

        return format_link_string

    def parseCountryContent(self, content):
        return content.css("a::text").extract_first().strip()

    def parseReleasedContent(self, content):
        full_year = content.css("a::text").extract_first()
        if full_year is not None:
            full_year = full_year.strip()
            year = re.match(r".*?([0-9]{4})$", full_year).group(1)
            return year
        else:
            return None

    def parseGenreContent(self, content):
        genres_list = content.css("a::text").extract()
        genres_list = [genre.strip() for genre in genres_list]
        genres = ";".join(genres_list)

        return genres

    def parseStyleContent(self, content):
        styles_list = content.css("a::text").extract()
        styles_list = [style.strip() for style in styles_list]
        styles = ";".join(styles_list)

        return styles

    def defaultFunction(self, label):
        return None

    def contentAction(self, label):
        return {
            'Label': self.parseLabelContent,
            'Format': self.parseFormatContent,
            'Country': self.parseCountryContent,
            'Released': self.parseReleasedContent,
            'Year': self.parseReleasedContent,
            'Genre': self.parseGenreContent,
            'Style': self.parseStyleContent
        }.get(label, self.defaultFunction)

    def generalStatisticAction(self, statistics, album_item):
        li_statistics = statistics.css("li")
        for statistic in li_statistics:
            statistic_name = statistic.css("h4::text").extract_first().strip()
            statistic_value_list = statistic.css("::text").extract()[2:]
            statistic_value_list = ["".join(value.split()) for value in statistic_value_list]
            statistic_value = "".join(statistic_value_list)

            key = statistic_name.lower()[:-1]
            key = key.replace(' ', '_')
            album_item[key] = statistic_value

            print(statistic_name + " " + statistic_value)

    def getArtistItem(self, artist_id):
        db_manager = DatabaseManager()
        artist_info = db_manager.get_artist_db(artist_id)
        # print(artist_info)
        artist_item = DiscogsArtist()
        if (artist_info is None) or (len(artist_info) == 0):
            artist_item['artist_id'] = artist_id
            artist_item['arranged_by_cnt'] = 0
            artist_item['lyrics_by_cnt'] = 0
            artist_item['music_by_cnt'] = 0
        else:
            artist_item = DiscogsArtist.listToArtist(artist_info)

        return artist_item

    def parse_album(self, response):
            db_manager = DatabaseManager()
            base_url = "https://www.discogs.com"

            album_item = DiscogsAlbum()
            #artist_name and album_name
            artist_names_links = response.css("#profile_title a")
            profile_list = response.css("#profile_title span::text").extract()
            if len(profile_list) != 0:
                album_item['album_name'] = profile_list[-1].strip()

            artist_name_list = []
            artist_link_list = []

            for artist in artist_names_links:
                artist_name = artist.css("::text").extract_first().strip()
                artist_name_list.append(artist_name)
                artist_link = "https://www.discogs.com" + artist.css("::attr(href)").get()
                artist_link_list.append(artist_link)
                # if (artist_id is in database)
                artist_item = self.getArtistItem(artist_link)
                db_manager.store_artist_statistics(artist_item)
                yield response.follow(artist_link, callback=self.parse_artist)
            print(album_item['album_name'])

            artist_names = ";".join(artist_name_list)
            artist_links = " ; ".join(artist_link_list)
            album_item['artist_names'] = artist_names
            print(artist_names)
            print(artist_links)

            #artis_id - popraviti
            album_item['album_id'] = response.request.url
            #album_id - popraviti
            album_item['artist_ids'] = artist_links

            print("")

            # informacije o albumu
            all_div_heads = response.css("div.head::text").extract()
            all_div_heads = [head.replace(':', '') for head in all_div_heads]

            all_div_content = response.css("div.content")

            for index, content in enumerate(all_div_content):
                value = self.contentAction(all_div_heads[index])(content)
                if (value is not None):
                    key = all_div_heads[index].lower()
                    if key == "released":
                        key = "year"
                    album_item[key] = value
                print(value)

            print("")
            # informacije o statistici albuma
            statistics = response.css("#statistics .toggle_section_content ul")
            self.generalStatisticAction(statistics, album_item)

            print("")
            # broj razlicitih verzija albuma

            num_of_versions = response.css("#m_versions .float_fix::text").extract_first()
            if ("/master" in album_item['album_id']):
                num_of_versions = num_of_versions.strip()
                num_of_versions = re.match(".*Versions.?\(.*([0-9]+)\).*", num_of_versions).group(1)
            elif (num_of_versions is None):
                num_of_versions = 1
            else:
                num_of_versions = 0
            album_item['num_of_releases'] = num_of_versions
            print(num_of_versions)

            print("")
            # Ljudi koji su ucestvovali na albumu
            set_of_needed_credits = { "Music By", "Lyrics By", "Arranged By" }
            credits_section = response.css("#credits .toggle_section_content ul li")
            for credits_line in credits_section:
                section_line_name = credits_line.css("span.role::text").extract_first().strip()
                section_line_artists_id = credits_line.css("a::attr(href)")
                for artist_id_link in section_line_artists_id:
                    artist_id = "https://www.discogs.com" + artist_id_link.get()
                    #artist_id = re.match(".*/([0-9]+)-.*", artist_id).group(1)

                    # if (artist_id is not in database)
                        # create artist
                    #

                    #print(artist_id)
                    if artist_id == "/artist/Various?anv=":
                        continue

                    artist_info = db_manager.get_artist_db(artist_id)
                    #print(artist_info)
                    artist_item = self.getArtistItem(artist_id)

                    #print("Artiste_item print ", artist_item)

                    #print(artist_info)

                    # get artist statistics

                    for section_line in section_line_name.split(","):
                        section_line = section_line.strip()
                        if section_line not in set_of_needed_credits:
                            continue

                        print("Artist: ", artist_id, " line: ", section_line)

                        if section_line == "Music By":
                            #print(artist_id)
                            artist_item['music_by_cnt'] += 1
                        elif section_line == "Lyrics By":
                            #print(artist_id)
                            artist_item['lyrics_by_cnt'] += 1
                            #inkrementiraj objekat
                            #continue
                        elif section_line == "Arranged By":
                            #print(artist_id)
                            artist_item['arranged_by_cnt'] += 1
                            #inkrementiraj objekat
                            #continue

                    db_manager.store_artist_statistics(artist_item)

                    yield response.follow("https://www.discogs.com" + artist_id_link.get(), callback=self.parse_artist)

            print("")

            # pesme na albumu
            tracklist_id_section = response.css(".tracklist_track_title > a::attr(href)")
            tracklist_id_section = [re.match(".*/(.*)$", tracklist_id.get()).group(1) for tracklist_id in tracklist_id_section]
            #tracklist_id_section = [requests.get(base_url + tracklist_id.get()).url for tracklist_id in tracklist_id_section]
            tracklist_name_section = response.css(".tracklist_track_title a span::text").extract()
            tracklist_name_section = [tracklist_name.strip() for tracklist_name in tracklist_name_section]
            tracklist_duration_section = response.css(".tracklist_track_duration span::text").extract()
            tracklist_duration_section = [re.match(".*([0-9]+:[0-9]+).*", tracklist_duration).group(1) for tracklist_duration in tracklist_duration_section]

            for index, tracklist_name in enumerate(tracklist_id_section):
                #Ubaci u vezu album_id-pesma_id-duration
                song_item = DiscogsSongs()
                song_item['song_id'] = tracklist_id_section[index]
                song_item['song_name'] = tracklist_name_section[index]
                song_item['album_id'] = album_item['album_id']
                song_item['duration'] = tracklist_duration_section[index] if index < len(tracklist_duration_section) else "--"
                db_manager.store_song_db(song_item)
                print(tracklist_id_section[index], " ", tracklist_name_section[index], " ", tracklist_duration_section[index] if index < len(tracklist_duration_section) else "--")

            print("")


            #print(album_item)


            yield album_item

    def cleanup(self, url):
        try:
            return unquote(url, errors='strict')
        except UnicodeDecodeError:
            return unquote(url, encoding='latin-1')

    def parse_artist(self, response):
        db_manager = DatabaseManager()
        artist_item = DiscogsArtist()

        artist_id = self.cleanup(response.request.url);
        #print(artist_id)
        artist_item['artist_id'] = artist_id

        #print(artist_id)
        print(db_manager.get_artist_db(artist_id))

        header_sections = response.css(".credit_type")
        credits_num = 0
        vocals_num = 0
        for header_section in header_sections:
            header_section_list = [section.strip() for section in header_section.css("a ::text").extract()]
            if header_section_list[2] == "Credits":
                credits_num = header_section_list[1]
            if header_section_list[2] == "Vocals":
                vocals_num = header_section_list[1]
        artist_item['credits'] = credits_num
        artist_item['vocals'] = vocals_num
        print(credits_num, " ", vocals_num)


        print("")

        content_topic = response.css(".head::text").extract()
        content_body = response.css(".content")
        links = []
        for index, topic in enumerate(content_topic):
            if topic == "Sites:":
                links = [link.get() for link in content_body[index].css("a::attr(href)")]
                break

        links = " ; ".join(links) if len(links) != 0 else "--"
        print(links)
        artist_item['site'] = links

        #Azuriraj osobe

        yield artist_item

    def parse2(self, response):
        song_item = DiscogsSongs()

        composition_details = response.css(".TracksTable")
        print("Asfasfafasfg", composition_details)
        for composition in composition_details:
            #print(composition.css('.track-title ::text').extract())
            song_item['song_name'] = composition_details.css('.track-title ::text').extract_first().strip()
            song_item['album_id'] = composition_details.css().extract_first().strip()
            song_item['duration'] = composition_details.css().extract_first().strip()

            #print(song_item['song_name'], " ", song_item['album_id'], " ", song_item['duration'])

        yield song_item


    def parse(self, response):
        next_page = response.css("a.pagination_next::attr(href)").get()
        db_manager = DatabaseManager()
        album_links = [link.get() for link in response.css("h4 a::attr(href)")]
        album_links.remove('/sell/list')
        for link in album_links:
            album_info = db_manager.get_album_db("https://www.discogs.com" + link)
            if (album_info is None) or (len(album_info) == 0):
                yield response.follow(link, callback = self.parse_album)

        if next_page is not None:
            yield response.follow(next_page, callback = self.parse)

#settings = get_project_settings()
#process = CrawlerRunner(settings)
#process = CrawlerProcess()
#process.crawl(DiscorgSpider)
#process.crawl(DiscorgSpider)
#process.start()