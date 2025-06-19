import scrapy

from scrapy.utils.project import get_project_settings

from hh_task_project.utility import DataParser
from hh_task_project.items import HHTaskProjectItem


class GoodsParserSpider(scrapy.Spider):
    name = "goods_parser"
    allowed_domains = ["alkoteka.com"]
    settings = get_project_settings()

    start_urls = settings['START_URLS']
    BASE_URL = settings['BASE_API_URL']
    BASE_DETAIL_URL = settings['BASE_API_DETAIL_URL']
    city_uuid = settings['CITIES_UUID']['Краснодар']

    category_slug = ""
    per_page = 20
    start_page = 1

    async def start(self):
        headers = {
            "Accept": "application/json"
        }
        
        for url in self.start_urls:
            slug = url.split('/catalog/')[1] # forms an api url
            self.category_slug = slug
            url = self.BASE_URL + \
                f"city_uuid={self.city_uuid}&" + \
                f"page={self.start_page}&per_page={self.per_page}&" + \
                f"root_category_slug={slug}"
            yield scrapy.Request(url=url, callback=self.parse, headers=headers, cb_kwargs={'page': self.start_page})


    def parse(self, response, page):
        response_data = response.json()
        products = response_data.get("results", [])
        self.total_products = response_data.get("meta", {}).get('total', 0) # Total products count needed for later output
        
        if not products:
            return
        
        for product in products:   
            url = product.get("product_url")
            
            if url:
                detail_slug = url.rsplit("/", 1)[-1]
                url_detail = f'{self.BASE_DETAIL_URL}{detail_slug}?city_uuid={self.city_uuid}' # Detail project api url

                yield scrapy.Request(
                    url=url_detail,
                    callback=self.parse_product_page,
                    headers=response.request.headers
                )

        next_page = page + 1
        next_url = (
            f"https://alkoteka.com/web-api/v1/product?"
            f"city_uuid={self.city_uuid}&"
            f"page={next_page}&per_page={self.per_page}&"
            f"root_category_slug={self.category_slug}"
        )
        yield scrapy.Request(next_url, callback=self.parse, headers=response.request.headers, cb_kwargs={'page': next_page})


    def closed(self, reason):
        count = self.crawler.stats.get_value("item_scraped_count")
        self.logger.info(f"Total products parsed: {self.total_products}, Total products saved: {count}")
        self.logger.info("Data saved correctly" if count == self.total_products else f"Data missed {count - self.total_products}")


    def parse_product_page(self, response):
        response_data = response.json()
        results = response_data.get('results', {})

        dp = DataParser()
        parsed_data = dp.parse(results)

        data = HHTaskProjectItem()
        data['timestamp'] = parsed_data['timestamp']
        data['RPC'] = parsed_data['rpc']
        data['title'] = parsed_data['title']
        data['url'] = parsed_data['url']
        data['marketing_tags'] = parsed_data['tags']
        data['brand'] = parsed_data['brand']
        data['section'] = parsed_data['section']
        data['price_data'] = {
                "current": parsed_data['current'],
                "original": parsed_data['original'],
                "sale_tag": parsed_data['sale_tag']
            }
        data['stock'] = {
                "in_stock": parsed_data['in_stock'],
                "count": parsed_data['count']
            }
        data['assets'] = {
                "main_image": parsed_data['image_url'],
                "set_images": [parsed_data['image_url']],
                "view360": [],
                "video": []
            }
        data['variants'] = parsed_data['variants']
        data['metadata'] = parsed_data['metadata']
    
        yield data