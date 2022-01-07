# -*- coding: utf-8 -*-

from scrapy import Spider, Request, FormRequest
from collections import OrderedDict
import json, csv, re
from scrapy.crawler import CrawlerProcess
import xml.etree.ElementTree
import urllib



class dasoertlicheSpider(Spider):
    name = "sirelo"
    count = 0
    headers = []
    models = []
    use_selenium = True
    def __init__(self, city=None, keyword=None, *args, **kwargs):
        super(dasoertlicheSpider, self).__init__(*args, **kwargs)
        self.start_url = 'https://sirelo.com'

    def start_requests(self):
        self.use_selenium = False
        yield Request(self.start_url, self.parse)

    def parse(self, response):

        urls = response.xpath('//div[@id="buttons"]/a/@href').extract()
        for url in urls:
            url = url+'/sitemap.xml'
            yield Request(url, self.parse_urls)

    def parse_urls(self, response):

        urls = re.findall('<loc>(.*?)</loc>', response.body)
        attrs = re.findall('<changefreq>(.*?)</changefreq>', response.body)
        index = 0
        for i, attr in enumerate(attrs):
            if attr == "daily":
                index+=1
            if index == 2:
                url = urls[i]
                yield Request(url, self.parse_total_urls)
                break

    def parse_total_urls(self, response):
        urls = response.xpath('//a[@class="city"]/@href').extract()
        for url in urls:
            yield Request(url, self.parse_list)

    def parse_list(self, response):
        self.use_selenium = True
        urls = response.xpath('//a[@class="logo"]/@href').extract()
        for url in urls:
            yield Request(url, self.parse_products)

    def parse_products(self, response):

        item = OrderedDict()
        item['company name'] = response.xpath('//h1[@class="company_name"]/text()').extract_first()
        if not item['company name']:
            return
        item['rating'] = response.xpath('//span[@itemprop="ratingValue"]/text()').extract_first()
        item['rating'] = response.xpath('//span[@itemprop="reviewCount"]/text()').extract_first()

        pros_tags = response.xpath('//div[@id="details_logo"]//div[@class="pros_cons"]/div')
        pros_text = ''
        for tag in pros_tags:
            pros_text += ''.join(tag.xpath('.//text()').extract())+'\n'
        review_text = response.xpath('//div[@id="details_logo"]//div[@class="recommendation good"]/text()').extract_first()
        if review_text:
            pros_text += review_text
        item['pros and cons'] = pros_text

        item['about company'] = response.xpath('//p[@itemprop="description"]/text()').extract_first()
        services = []
        service_tags = response.xpath('//div[@class="detailblock_services mobile_hide"]//div[@class="service"]')
        for tag in service_tags:
            services.append(''.join(tag.xpath('./text()').extract()))
        for i in range(1, 6):
            try:
                item['service_{}'.format(i)] = services[i-1]
            except:
                item['service_{}'.format(i)] = ''

        associations = ''.join(response.xpath('//div[@class="detailblock_branches mobile_hide clear_after"]/div[@class="branches"]//text()').extract())
        btag_text = response.xpath('//div[@class="detailblock_branches mobile_hide clear_after"]/div[@class="branches"]/div[@class="label"]/h4/text()').extract_first()
        item['associations'] = associations.replace(btag_text, '', 1)

        establish = ''.join(response.xpath('//div[@class="details_block"]/div[@class="established"]/span/text()').extract())
        if establish:
            item['established'] = establish
        else:
            item['established'] = ''

        employees = ''.join(response.xpath('//div[@class="details_block"]/div[@class="employees"]/span/text()').extract())
        if employees :
            item['employing'] = employees
        else:
            item['employing'] = ''

        trucks = response.xpath('//div[@class="details_block"]/div[@class="trucks"]/text()').re(r'[\d]+')
        if trucks :
            item['trucks'] = ''.join(response.xpath('//div[@class="details_block"]/div[@class="trucks"]/text()').extract()).strip()
        else:
            item['trucks'] = ''

        location = response.xpath('//div[contains(@class,"company_details")]/div[@class="location"]/text()').extract()
        if location :
            item['location1'] = location[-2]
            item['location2'] = location[-1]
        else:
            item['location'] = ''

        item['telephone'] = response.xpath('//div[contains(@class,"company_details")]/div[@class="telephone"]/text()').extract_first()
        item['website'] = response.xpath('//div[contains(@class,"company_details")]/div[@class="website"]/a/text()').extract_first()
        item['email'] = response.xpath('//div[contains(@class,"company_details")]/div[@class="email"]/text()').extract_first()
        item['url'] = response.url

        self.count += 1
        print(self.count)
        yield item


