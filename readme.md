### Как использовать
- py -m venv env
- env\Scripts\activate или source env\bin\activate
- pip install requirements.txt

### Тесты
- cd hh_task_project
- pytest

### Запуск парсилки
- scrapy crawl goods_parser -O result.json

### FAQ
- В settings.py указать нужные урлы в переменной START_URLS
- По api собираем данные, поэтому город указывается в виде uuid в переменной CITIES_UUID
- Прокси вкл/выкл в переменной PROXY
