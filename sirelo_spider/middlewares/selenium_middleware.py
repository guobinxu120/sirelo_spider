from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from scrapy.http import TextResponse
from scrapy.exceptions import CloseSpider
from scrapy import signals
import time

class SeleniumMiddleware(object):

    def __init__(self, s):
        # self.exec_path = s.get('PHANTOMJS_PATH', './phantomjs.exe')
        self.exec_path = s.get('C:/Users/phantomjs.exe')

###########################################################

    @classmethod
    def from_crawler(cls, crawler):
        obj = cls(crawler.settings)

        crawler.signals.connect(obj.spider_opened,
                                signal=signals.spider_opened)
        crawler.signals.connect(obj.spider_closed,
                                signal=signals.spider_closed)
        return obj

###########################################################

    def spider_opened(self, spider):
        if spider.use_selenium:
            try:
                self.d = init_driver(self.exec_path)
            except TimeoutException:
                CloseSpider('PhantomJS Timeout Error!!!')

###########################################################

    def spider_closed(self, spider):
        self.d.quit()
###########################################################
    
    def process_request(self, request, spider):
        if spider.use_selenium:
            print "############################ Received url request from scrapy #####"

            try:
                self.d.get(request.url)
                

            except TimeoutException as e:
                print "Timeout error"          
                #raise CloseSpider('TIMEOUT ERROR')
            time.sleep(0.5)

            # lastHeight = self.d.execute_script("return document.body.scrollHeight")

            # print "*** Last Height = ", lastHeight
            # while True:
            #     self.d.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            #     time.sleep(2)
            #     newHeight = self.d.execute_script("return document.body.scrollHeight")
            #     if newHeight == lastHeight:
            #         break
            #     lastHeight = newHeight
            # time.sleep(1.5)
            resp = TextResponse(url=self.d.current_url,
                                body=self.d.page_source,
                                encoding='utf-8')
            resp.request = request.copy()
            
            return resp

###########################################################
###########################################################

def init_driver(path):
    d = webdriver.PhantomJS(executable_path='./phantomjs.exe')
    # d = webdriver.Chrome(executable_path='./chromedriver.exe')
    d.set_page_load_timeout(160)

    return d