# -*- coding: utf-8 -*-

from scrapy import Spider, Request, FormRequest
from collections import OrderedDict
import json, csv, re
from scrapy.crawler import CrawlerProcess
import xml.etree.ElementTree
import urllib



class dasoertlicheSpider(Spider):
    name = "mobilityex"
    count = 0
    headers = []
    models = []
    use_selenium = True
    def __init__(self, city=None, keyword=None, *args, **kwargs):
        super(dasoertlicheSpider, self).__init__(*args, **kwargs)
        self.start_url = 'https://www.mobilityex.com/api/_search/service-providerslist?cacheBuster=1536067187355&lat=&lng=&loc=+&page=0&query=q%3D+&range=100&sensor=false&size=30&sort=companylegalname,asc&svc=Moving+Services+Company+'

    def start_requests(self):
        self.use_selenium = False
        yield Request(self.start_url, self.parse, meta={'index':0})

    def parse(self, response):
        data_json = json.loads(response.body)
        for data in data_json:
            try:
                item = OrderedDict()
                item['company name'] = data['companylegalname']
                item['url'] = 'https://www.mobilityex.com/#/search/service-providers/{}'.format(data['id'])
                item['company description'] = data['companydescription']
                item['Year Established'] = data['established']
                if 'serviceproviderAddresses' in data.keys():
                    for address_json in data['serviceproviderAddresses']:
                        item['country'] = address_json['country']
                        item['city'] = address_json['city']
                        item['state'] = address_json['state']
                        item['postalcode'] = address_json['postalcode']
                        item['addressline1'] = address_json['addressline1']
                        item['addressline2'] = address_json['addressline2']
                        item['addressline3'] = address_json['addressline3']

                        item['email'] = address_json['emailaddress']
                        item['phoneNumber'] = address_json['phoneNumber']
                        item['tollfreenumber'] = address_json['tollfreenumber']
                        item['faxnumber'] = address_json['faxnumber']
                        item['website'] = data['website']
                        break


                compliance_text = ''
                if 'compliance' in data.keys():
                    for compliance in data['compliance']:
                        try:
                            name = compliance['certificateType']['lookupvalue']
                            full_name = compliance['certificateType']['flex1']
                            expiredate = compliance['expirydate']
                            if not expiredate:
                                expiredate = compliance['valApprovedDate']
                            compliance_text += (name+ '({}): '.format(full_name)+expiredate +'\n')
                        except:
                            continue
                item['Compliance & Licenses'] = compliance_text

                lang_text = ''
                if 'languageCapabilities' in data.keys():
                    for languageCapabilities in data['languageCapabilities']:
                        try:
                            name = languageCapabilities['capabilityType']['lookupvalue']
                            lang_text += (name + ',')
                        except:
                            continue
                if lang_text != '':
                    lang_text = lang_text[0:-1]
                item['Languages'] = lang_text

                memberAssociations_text = ''
                if 'memberAssociations' in data.keys():
                    for memberAssociations in data['memberAssociations']:
                        try:
                            name = memberAssociations['memberAssociation']['lookupvalue']
                            full_name = memberAssociations['memberAssociation']['flex1']
                            expiredate = memberAssociations['valExpiryDate']
                            if not expiredate:
                                expiredate = memberAssociations['valApprovedDate']
                            memberAssociations_text += (name+ '({}): '.format(full_name)+expiredate +'\n')
                        except:
                            continue
                item['Association Memberships'] = memberAssociations_text

                parent_text = ''
                if 'memberCapabilities' in data.keys():
                    for memberCapabilities in data['memberCapabilities']:
                        try:
                            name = memberCapabilities['capabilityType']['lookupvalue']
                            parent_text += (name + ',')
                        except:
                            continue
                if parent_text != '':
                    parent_text = parent_text[0:-1]
                item['Partner Category'] = parent_text

                moving_text = ''
                if 'movingCapabilities' in data.keys():
                    for memberCapabilities in data['movingCapabilities']:
                        try:
                            name = memberCapabilities['capabilityType']['lookupvalue']
                            moving_text += (name + ',')
                        except:
                            continue
                if moving_text != '':
                    moving_text = moving_text[0:-1]
                item['Moving Capabilities'] = moving_text

                moving_text = ''
                if 'relocationCapabilities' in data.keys():
                    for relocationCapabilities in data['relocationCapabilities']:
                        try:
                            name = relocationCapabilities['capabilityType']['lookupvalue']
                            moving_text += (name + ',')
                        except:
                            continue
                if moving_text != '':
                    moving_text = moving_text[0:-1]
                item['Relocation Capabilities'] = moving_text

                moving_text = ''
                if 'freightServicesCapabilities' in data.keys():
                    for relocationCapabilities in data['freightServicesCapabilities']:
                        try:
                            name = relocationCapabilities['capabilityType']['lookupvalue']
                            moving_text += (name + ',')
                        except:
                            continue
                if moving_text != '':
                    moving_text = moving_text[0:-1]
                item['Freight Services Capabilities'] = moving_text

                moving_text = ''
                if 'usGovtCapabilities' in data.keys() and data['usGovtCapabilities'] != None:

                    for relocationCapabilities in data['usGovtCapabilities']:
                        try:
                            name = relocationCapabilities['capabilityType']['lookupvalue']
                            moving_text += (name + ',')
                        except:
                            continue
                if moving_text != '':
                    moving_text = moving_text[0:-1]
                item['US Government Capabilities'] = moving_text

                memberAssociations_text = ''
                if 'quality' in data.keys():
                    for memberAssociations in data['quality']:
                        try:
                            name = memberAssociations['certificateType']['lookupvalue']
                            full_name = memberAssociations['certificateType']['flex1']
                            expiredate = memberAssociations['expirydate']
                            if not expiredate:
                                expiredate = memberAssociations['valApprovedDate']
                            memberAssociations_text += (name + '({}): '.format(full_name) + expiredate + '\n')
                        except:
                            continue
                item['Quality Certifications'] = memberAssociations_text

                item['contacts'] = ''
                contacts = []
                if 'serviceproviderContacts' in data.keys():
                    for i in range(1, 4):
                        try:
                            contact = data['serviceproviderContacts'][i]
                            item['contat_name{}'.format(i)] = contact['fullName']
                            item['contact_mail{}'.format(i)] = contact['email']
                            item['contact_officephone{}'.format(i)] = contact['officephone']
                        except:
                            item['contat_name{}'.format(i)] = ''
                            item['contact_mail{}'.format(i)] = ''
                            item['contact_officephone{}'.format(i)] = ''



                item['contacts'] = json.dumps(contacts)
                yield item
            except:
                yield item




        current = response.meta.get('index')
        if current < 252:
            # url = 'https://www.mobilityex.com/api/_search/service-providerslist?cacheBuster=1536067555553&lat=&lng=&loc=+&page=185&query=q%3D+&range=100&sensor=false&size=30&sort=companylegalname,asc&svc=Moving+Services+Company+'
            url = 'https://www.mobilityex.com/api/_search/service-providerslist?cacheBuster=1536067555553&lat=&lng=&loc=+&page={}&query=q%3D+&range=100&sensor=false&size=30&sort=companylegalname,asc&svc=Moving+Services+Company+'.format(current+1)
            yield Request(url, self.parse, meta={'index': current+1})


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


