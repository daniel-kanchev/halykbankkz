import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from halykbank.items import Article


class halykbankSpider(scrapy.Spider):
    name = 'halykbank'
    start_urls = ['https://halykbank.kz/about/press_center/']
    page = 1
    page_limit = -1

    def parse(self, response):
        if self.page_limit == -1:
            self.page_limit = \
                int(response.xpath('//button[@data-url="/ru/about/press_center"]/@data-totalpages').get())

        links = response.xpath('//a[@class="common-block"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)
        if self.page < self.page_limit:
            self.page += 1
            next_page = f'https://halykbank.kz/about/press_center/{self.page}'
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url.lower():
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//div[@class="date"]/text()').get()
        if date:
            date = " ".join(date.split())

        content = response.xpath('//div[@class="text"]//text()').getall()
        content = [text.strip() for text in content if text.strip() and '{' not in text]
        content = " ".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
