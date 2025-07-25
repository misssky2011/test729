import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import os
from os import path


class DfvideospiderSpider(CrawlSpider):
    name = 'DfVideoSpider'
    allowed_domains = ['eastday.com']
    start_urls = ['http://video.eastday.com/']

    rules = (
        Rule(LinkExtractor(allow=r'.*'), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        self.logger.info(f"正在解析页面: {response.url}")
        video_url = response.xpath('//input[@id="mp4Source"]/@value').get()
        video_title = response.xpath('//meta[@name="description"]/@content').get()

        if video_url and video_title:
            self.logger.info(f"获取到的视频链接: {video_url}, 标题: {video_title}")
            video_url = 'http:' + video_url
            yield scrapy.Request(url=video_url, meta={'video_title': video_title}, callback=self.parse_video)
        else:
            self.logger.warning(f"未找到视频链接或标题: {response.url}")

    def parse_video(self, response):
        video_title = response.meta.get('video_title')
        file_name = f"{video_title}.mp4".replace('?', '').replace(':', '').replace('|', '')
        base_dir = path.join(path.curdir, 'VideoDownload')
        video_local_path = path.join(base_dir, file_name)

        if not os.path.exists(base_dir):
            os.mkdir(base_dir)

        with open(video_local_path, "wb") as f:
            f.write(response.body)
            self.logger.info(f"视频已保存到本地: {video_local_path}")
