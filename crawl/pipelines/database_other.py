# -*- coding: utf-8 -*-
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import logging, datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_, or_, func
from crawl.models.util import db_connect, create_news_table
from crawl.Common.Util import session_scope
from crawl.models.crawl_weixin_search import Crawl_Weixin_Search
from crawl.models.crawl_weibo_hotkey import Crawl_Weibo_Hotkey
from crawl.models.crawl_baidu_hotkey import Crawl_Baidu_Hotkey
from crawl.models.crawl_weixin_article_detail import CrawlWeixinArticleDetail
from crawl.models.crawl_weibo import Crawl_Weibo
from crawl.models.crawl_sentence import Sentence
from crawl.items import CrawlWexinArticleItem

class OtherPipeline(object):

    def __init__(self):
        engine = db_connect()
        create_news_table(engine)
        self.sess = sessionmaker(bind=engine)
        self.recent_newsid = None

    def open_spider(self, spider):
        """This method is called when the spider is opened."""
        logging.info('Other pipeline open spider')

    def process_item(self, item, spider):
        """process news item"""
        if spider.name in ['crawl_weixin_search']:
            self.parse_weixin_search(item)
        elif spider.name in ['crawl_weixin_detail']:
            self.parse_weixin_detail(item)
        elif spider.name in ['crawl_weibo_search']:
            self.parse_weibo_seach(item)
        elif spider.name in ['crawl_baidu_search']:
            self.parse_baidu_seach(item)
        elif spider.name in ['crawl_weibo_hot']:
            self.parse_weibo(item)
        elif spider.name in ['crawl_sentence']:
            self.parse_sentence(item)

    def parse_weibo(self, item):
        with session_scope(self.sess) as session:
            query = session.query(Crawl_Weibo.id).filter(
                Crawl_Weibo.source_id == item['source_id']
            ).one_or_none()

            if not query:
                weibo = Crawl_Weibo(**item)
                session.add(weibo)

    def parse_sentence(self, item):
        with session_scope(self.sess) as session:
            sentence = Sentence(**item)
            query = session.query(Sentence.id).filter(
                Sentence.source_id == sentence.source_id
            ).one_or_none()

            if query is None:
                session.add(sentence)
            else:
                session.query(Sentence).filter(
                    Sentence.id == query[0]
                ).update(item)


    def parse_weixin_search(self, item):
        with session_scope(self.sess) as session:
            all_item = []
            for i in item:
                article = Crawl_Weixin_Search(**item[i])
                query = session.query(Crawl_Weixin_Search.id).filter(
                    Crawl_Weixin_Search.source_id == article.source_id
                ).one_or_none()

                if query is None:
                    all_item.append(article)

            if all_item:
                session.add_all(all_item)

    def parse_weixin_detail(self, item):
        with session_scope(self.sess) as session:
            query = session.query(Crawl_Weixin_Search.id).filter(
                Crawl_Weixin_Search.source_id == item['source_id']
            ).one_or_none()

            if query:
                article_detail = CrawlWeixinArticleDetail()
                article_detail.id = query[0]
                article_detail.body = item['body']

                session.add(article_detail)

    def parse_weibo_seach(self, item):
        with session_scope(self.sess) as session:
            hotkey = Crawl_Weibo_Hotkey(**item)
            query = session.query(Crawl_Weibo_Hotkey.id).filter(
                Crawl_Weibo_Hotkey.source_id == hotkey.source_id
            ).one_or_none()

            if query is None:
                session.add(hotkey)

    def parse_baidu_seach(self, item):
        with session_scope(self.sess) as session:
            hotkey = Crawl_Baidu_Hotkey(**item)
            query = session.query(Crawl_Baidu_Hotkey.id).filter(
                Crawl_Baidu_Hotkey.source_id == hotkey.source_id
            ).one_or_none()

            if query is None:
                session.add(hotkey)



    def close_spider(self, spider):
        """close spider"""
        logging.info('Other pipeline close spider')
