# -*- coding: utf-8 -*-
import scrapy
import datetime
from bs4 import BeautifulSoup

class CrawlWeiboHotSpider(scrapy.Spider):
    name = 'crawl_weibo_hot'
    allowed_domains = ['weibo.com']
    start_urls = ['http://weibo.com/']

    custom_settings = {
        'LOG_FILE': 'logs/weibo_hot_{dt}.log'.format(dt=datetime.datetime.now().strftime('%Y%m%d'))
    }

    "https://d.weibo.com/p/aj/v6/mblog/mbloglist?ajwvr=6&domain=102803_ctg1_1760_-_ctg1_1760&pagebar=0&tab=home&current_page=1&pre_page=1&page=1&pl_name=Pl_Core_NewMixFeed__3&id=102803_ctg1_1760_-_ctg1_1760&script_uri=/&feed_type=1&domain_op=102803_ctg1_1760_-_ctg1_1760&__rnd=1513645659822"

    def start_requests(self):
        # 保存cookie，同时模拟浏览器访问过程，设置refer
        return [scrapy.Request("https://passport.weibo.com/visitor/visitor?entry=miniblog&a=enter&url=http%3A%2F%2Fweibo.com%2F&domain=.weibo.com&ua=php-sso_sdk_client-0.6.23&_rand=1504681177.4204",
                               meta={'cookiejar': self.name, 'handle_httpstatus_list': [301, 302]}, callback=self.parse_cookie)]

    def parse_cookie(self, response):
        with open("weibo.html", "w") as fs:
            fs.write(response.body)

        yield scrapy.Request("https://passport.weibo.com/visitor/visitor?a=incarnate&t=ozD4QaZDtghqkBlmJyBrr9BAhFtSZHzidvH18aseoYI%3D&w=2&c=095&gc=&cb=cross_domain&from=weibo&_rand=0.7829101177189541",
                             meta={'cookiejar': self.name, 'handle_httpstatus_list': [301, 302]},
                             callback=self.parse_redirect)

    def parse_redirect(self, response):
        with open("weibo2.html", "w") as fs:
            fs.write(response.body)

        yield scrapy.Request(self.base_url.format(page=self.page_now),
                             meta={'cookiejar': self.name, 'handle_httpstatus_list': [301, 302]}, callback=self.parse_page)

    def parse_content(self, response):
        divs = response.xpath(".//div[@id='PCD_pictext_i_v5']/ul/div[@class='UG_list_b']")

        for div in divs:
            pic = div.xpath(".//div[@class='pic W_piccut_v']/img/@src").extract_first()
            content = div.xpath(".//div[@class='list_des']/h3/div").extract()

            author_info = div.xpath(".//div[@class='list_des']/div[@class='subinfo_box clearfix']")
            author_img = author_info.xpath("./a[1]//img/@src").extract_first()
            author_name = author_info.xpath("./a[2]/span/text()").extract_first()
            author_link = author_info.xpath("./a[1]/@href").extract_first()
            if author_link is not None and not author_link.starts_with("http"):
                author_link = "https://weibo.com" + author_link

            pub_time = author_info.xpath(".//span[@class='subinfo S_txt2']/text()").extract_first()

            print "pic", pic
            print "content", content
            print "author_img", author_img
            print "author_name", author_name
            print "author_link", author_link
            print "pub_time", pub_time
            print "\n\n"