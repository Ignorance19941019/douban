#!/usr/bin/env python
# -*- coding: utf-8 -*-

from scrapy import Item, Field


class Subject(Item):
    douban_id = Field()
    type = Field()


class MovieMeta(Item):
    name = Field()
    votes = Field()
    genres = Field()
    regions = Field()
    release_date = Field()
    runtime = Field()
    year = Field()
    score = Field()
