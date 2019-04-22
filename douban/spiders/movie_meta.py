#!/usr/bin/env python
# -*- coding: utf-8 -*-


import string
import random
import douban.database as db
import douban.validator as validator

from scrapy import Request, Spider
from douban.items import MovieMeta


cursor = db.connection.cursor()


class MovieMetaSpider(Spider):
    name = 'movie_meta'
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
                  (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36'
    allowed_domains = ["movie.douban.com"]
    sql = 'SELECT * FROM subjects WHERE type="movie" AND douban_id NOT IN \
(SELECT douban_id FROM movies) ORDER BY douban_id DESC'
    cursor.execute(sql)
    movies = cursor.fetchall()
    start_urls = (
        'https://movie.douban.com/subject/%s/' % i['douban_id'] for i in movies
    )

    def start_requests(self):
        for url in self.start_urls:
            bid = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(11))
            cookies = {
                'bid': bid,
                'dont_redirect': True,
                'handle_httpstatus_list': [302],
            }
            yield Request(url, cookies=cookies)

    def get_douban_id(self, meta, response):
        meta['douban_id'] = response.url[33:-1]
        return meta

    def get_name(self, meta, response):
        regx = '//title/text()'
        data = response.xpath(regx).extract()
        if data:
            meta['name'] = data[0][:-5].strip()
        return meta

    def get_year(self, meta, response):
        regx = '//span[@class="year"]/text()'
        data = response.xpath(regx).extract()
        if data:
            meta['year'] = validator.match_year(data[0])
        return meta

    def get_genres(self, meta, response):
        regx = '//span[@property="v:genre"]/text()'
        genres = response.xpath(regx).extract()
        meta['genres'] = '/'.join(genres)
        return meta

    def get_regions(self, meta, response):
        regx = '//text()[preceding-sibling::span[text()="制片国家/地区:"]][fo\
llowing-sibling::br]'
        data = response.xpath(regx).extract()
        if data:
            meta['regions'] = data[0]
        return meta

    def get_release_date(self, meta, response):
        regx = '//span[@property="v:initialReleaseDate"]/@content'
        data = response.xpath(regx).extract()
        if data:
            release_date = validator.str_to_date(validator.match_date(data[0]))
            if release_date:
                meta['release_date'] = release_date
        return meta

    def get_runtime(self, meta, response):
        regx = '//span[@property="v:runtime"]/@content'
        data = response.xpath(regx).extract()
        if data:
            meta['mins'] = data[0]
        return meta

    def get_score(self, meta, response):
        regx = '//strong[@property="v:average"]/text()'
        data = response.xpath(regx).extract()
        if data:
            meta['douban_score'] = data[0]
        return meta

    def get_votes(self, meta, response):
        regx = '//span[@property="v:votes"]/text()'
        data = response.xpath(regx).extract()
        if data:
            meta['douban_votes'] = data[0]
        return meta

    def parse(self, response):
        if 35000 > len(response.body):
            print(response.body)
            print(response.url)
        elif 404 == response.status:
            print(response.url)
        else:
            meta = MovieMeta()
            self.get_douban_id(meta, response)
            self.get_name(meta, response)
            self.get_year(meta, response)
            self.get_genres(meta, response)
            self.get_regions(meta, response)
            self.get_release_date(meta, response)
            self.get_runtime(meta, response)
            self.get_score(meta, response)
            self.get_votes(meta, response)
            return meta
