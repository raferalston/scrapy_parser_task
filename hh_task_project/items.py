import scrapy


class HHTaskProjectItem(scrapy.Item):
    timestamp = scrapy.Field(serializer=int)

    RPC = scrapy.Field(serializer=str)
    url = scrapy.Field(serializer=str)
    title = scrapy.Field(serializer=str)

    marketing_tags = scrapy.Field(serializer=list)  # list of str
    brand = scrapy.Field(serializer=str)
    section = scrapy.Field(serializer=str)  # list of str

    price_data = scrapy.Field()  # dict: current, original, sale_tag

    stock = scrapy.Field()  # dict: in_stock, count

    assets = scrapy.Field()  # dict: main_image, set_images, view360, video

    metadata = scrapy.Field()  # dict: __description + ключи характеристик

    variants = scrapy.Field(serializer=int)
