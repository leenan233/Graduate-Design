# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CrawlpatItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    patent_url = scrapy.Field()
    patent_no = scrapy.Field()
    patent_title = scrapy.Field()
    patent_abstract = scrapy.Field()
    patent_inventors = scrapy.Field()
    patent_applicant_Name = scrapy.Field()
    patent_applicant_State = scrapy.Field()
    patent_applicant_City = scrapy.Field()
    patent_applicant_Country = scrapy.Field()
    patent_assignee = scrapy.Field()
    patent_familyId = scrapy.Field()
    patent_applyNo = scrapy.Field()
    patent_fieldDate = scrapy.Field()
    patent_claims = scrapy.Field()
    patent_description = scrapy.Field()
    patent_references = scrapy.Field()
    patent_date = scrapy.Field()
    patent_otherref = scrapy.Field()
    patent_refurl = scrapy.Field()
    patent_keyword = scrapy.Field()
