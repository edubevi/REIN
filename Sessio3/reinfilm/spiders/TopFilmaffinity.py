# -*- coding: utf-8 -*-
import scrapy

MAX_FILMS=999999999999 # Constant that sets a limit of films to scrap

#Parse3
class TopfilmaffinitySpider(scrapy.Spider):
    name = 'TopFilmaffinity'
    allowed_domains = ['filmaffinity.com']
    web_url = 'https://www.filmaffinity.com/en/topgen.php?genre=&fromyear=&toyear=&country=&nodoc&notvse'
    start_urls = [web_url]
    num_films = 0

    def parse(self, response):
        """
        Process the information of each page of top films

        :param response:
        :return:
        """
        for item, mark in zip(response.css('li.content'), response.css('li.data')):

            doc = {}
            data = item.css('div.mc-info-container')
            doc['title'] = data.css('div.mc-title a::text').extract_first()
            doc['url'] = response.urljoin(data.css('div.mc-title a::attr(href)').extract_first())
            doc['country'] = data.css('div.mc-title img::attr(title)').extract_first()
            credits = data.css('div.mc-director')
            doc['director'] = credits.css('span.nb a::text').extract_first()
            doc['mark'] = mark.css('div.avg-rating::text').extract_first()
            self.num_films += 1

            yield scrapy.Request(doc['url'], callback=self.parse_detail, meta=doc)

        if self.num_films < MAX_FILMS:
            yield scrapy.FormRequest(url=self.web_url, formdata={'from': str(self.num_films)}, callback=self.parse)


    def parse_detail(self, response):
        """
        Parses the information of the film detailed page

        :param response:
        :return:
        """
        detail = response.meta
        data = response.css('dl.movie-info')
        detail['year'] = data.css('dd[itemprop="datePublished"]::text').extract_first()
        detail['duration'] = data.css('dd[itemprop="duration"]::text').extract_first()
        detail['cast'] = ' '.join(data.css('span.cast a span::text').extract())
        detail['genre'] = ' '.join(data.css('span[itemprop="genre"] a::text').extract())
        detail['synopsis'] = data.css('dd[itemprop="description"]::text').extract_first()
        yield detail







