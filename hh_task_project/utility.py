'''
Scheme
{
    "timestamp": int,  # Дата и время сбора товара в формате timestamp.
    "RPC": "str",  # Уникальный код товара.
    "url": "str",  # Ссылка на страницу товара.
    "title": "str",  # Заголовок/название товара (! Если в карточке товара указан цвет или объем, но их нет в названии, необходимо добавить их в title в формате: "{Название}, {Цвет или Объем}").
    "marketing_tags": ["str"],  # Список маркетинговых тэгов, например: ['Популярный', 'Акция', 'Подарок']. Если тэг представлен в виде изображения собирать его не нужно.
    "brand": "str",  # Бренд товара.
    "section": ["str"],  # Иерархия разделов, например: ['Игрушки', 'Развивающие и интерактивные игрушки', 'Интерактивные игрушки'].
    "price_data": {
        "current": float,  # Цена со скидкой, если скидки нет то = original.
        "original": float,  # Оригинальная цена.
        "sale_tag": "str"  # Если есть скидка на товар то необходимо вычислить процент скидки и записать формате: "Скидка {discount_percentage}%".
    },
    "stock": {
        "in_stock": bool,  # Есть товар в наличии в магазине или нет.
        "count": int  # Если есть возможность получить информацию о количестве оставшегося товара в наличии, иначе 0.
    },
    "assets": {
        "main_image": "str",  # Ссылка на основное изображение товара.
        "set_images": ["str"],  # Список ссылок на все изображения товара.
        "view360": ["str"],  # Список ссылок на изображения в формате 360.
        "video": ["str"]  # Список ссылок на видео/видеообложки товара.
    },
    "metadata": {
        "__description": "str",  # Описание товара
        "KEY": "str",
        "KEY": "str",
        "KEY": "str"
        # Также в metadata необходимо добавить все характеристики товара которые могут быть на странице.
        # Например: Артикул, Код товара, Цвет, Объем, Страна производитель и т.д.
        # Где KEY - наименование характеристики.
    }
    "variants": int,  # Кол-во вариантов у товара в карточке (За вариант считать только цвет или объем/масса. Размер у одежды или обуви варинтами не считаются).
}

'''
import time


class DataParser:
    '''This helper class is needed to process parsed data according to specified parameters using special methods.'''
    def __init__(self):
        self._data = None
    
    def next_page_exists(self, data: dict) -> bool:
        '''Checks if a next page exists'''
        return data.get('has_more_pages', False)

    def set_data(self, data: dict) -> bool:
        '''Setting a data to a self object'''
        self._data = data

    def get_time(self) -> int:
        '''Timestamp'''
        return int(time.time())

    def get_title(self) -> str:
        '''Get title'''
        return self._data.get('name')

    def get_rpc(self) -> str:
        '''Get rpc'''
        return str(self._data.get("vendor_code"))

    def get_detail_url(self) -> str:
        '''Get detail url for a specific item'''
        return self._data.get("product_url")

    def get_extra(self) -> list:
        '''Get extra data'''
        extra = []
        for label in self._data.get("filter_labels", []):
            if label["filter"] in ["obem", "color"]:
                extra.append(label.get("title"))
        return extra

    def get_marketing_tags(self) -> list:
        '''Didnt find any marketing tags in a json/html output'''
        tags = []
        if self._data.get("new"):
            tags.append("Новинка")
        if self._data.get("recomended"):
            tags.append("Рекомендуем")
        return tags

    def get_brand(self) -> str:
        '''Get brand'''
        brand = None
        for block in self._data.get("description_blocks", []):
            if block.get("code") == "brend":
                values = block.get("values", [])
                if values:
                    brand = values[0].get("name")
        return brand

    def get_sections(self) -> list:
        '''Get sections'''
        section = []
        if self._data.get("category"):
            if self._data["category"].get("parent"):
                section.append(self._data["category"]["parent"].get("name"))
            section.append(self._data["category"].get("name"))
        return section

    def get_current(self) -> int:
        '''Get current price'''
        return self._data.get("price")

    def get_original(self) -> int:
        '''Set current price if no original exists'''
        return self._data["prev_price"] if self._data["prev_price"] else self.get_current()

    def get_stock(self) -> tuple:
        '''Get stock count'''
        in_stock = self._data.get("available")
        count = self._data.get("quantity_total") if in_stock else 0
        return in_stock, count
    
    def get_metadata(self) -> dict:
        '''Forms metadata'''
        description = ""
        for block in self._data.get("text_blocks", []):
            if block.get("title") == "Описание":
                description = block.get("content", "").strip()

        metadata = {"__description": description}
        for block in self._data.get("description_blocks", []):
            title = block.get("title")
            if block.get("type") == "range":
                min_val = block.get("min")
                max_val = block.get("max")
                unit = block.get("unit", "").strip()
                val = f"{min_val}{unit}" if min_val == max_val else f"{min_val}-{max_val}{unit}"
                metadata[title] = val
            elif block.get("type") == "select":
                values = block.get("values", [])
                if values:
                    metadata[title] = ", ".join(v["name"] for v in values if v.get("enabled"))
        return metadata

    def get_image_url(self) -> str:
        '''Get image url. Didnt find any other images for products'''
        return self._data.get("image_url")
    
    def get_variants(self):
        '''Set variants'''
        variants = 0
        for f in self._data.get("filter_labels", []):
            if f["filter"] in ["obem", "cvet"]:
                variants += 1
        return variants
        
    def get_detail_slug(self, url: str) -> str:
        '''Utility method for parse and form detail url
        Example: Original urls is - https://alkoteka.com/product/pivo-1/caringer-shvarc-bir_29294
        Output: caringer-shvarc-bir_29294
        And used it to form detail url for an product'''
        return url.rsplit("/", 1)[-1]
    
    def parse(self, data: dict) -> dict:
        '''Parsing for creating a final object data'''
        self.set_data(data) # Setting data as inner object

        timestamp = self.get_time()
        title = self.get_title()
        extra = self.get_extra()
        
        if extra:
            title = f"{title}, {' / '.join(extra)}"

        rpc = self.get_rpc()
        url = self.get_detail_url()
        tags = self.get_marketing_tags()
        brand = self.get_brand()
        section = self.get_sections()
        original = self.get_original()
        current = self.get_current()

        sale_tag = None
        if data.get("prev_price"):
            discount = int(round(100 - (current / original * 100)))
            sale_tag = f"Скидка {discount}%"

        in_stock, count = self.get_stock()
        metadata = self.get_metadata()
        image_url = self.get_image_url()
        variants = self.get_variants()

        return {
            'timestamp': timestamp,
            'rpc': rpc,
            'url': url,
            'title': title,
            'tags': tags,
            'brand': brand,
            'section': section,
            'current': float(current),
            'original': float(original),
            'sale_tag': sale_tag,
            'in_stock': in_stock,
            'count': count,
            'metadata': metadata,
            'image_url': image_url,
            'variants': variants
        }
