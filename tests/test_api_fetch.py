import pytest
import requests

from scrapy.utils.project import get_project_settings


settings = get_project_settings()
API_URL = "https://alkoteka.com/web-api/v1/product/caringer-shvarc-bir_29294"
CITY_UUID = '4a70f9e0-46ae-11e7-83ff-00155d026416'


def test_api_returns_json():
    response = requests.get(f"{API_URL}?city_uuid={CITY_UUID}", headers={
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    })

    assert response.status_code == 200, "Status != 200"
    data = response.json()
    assert "results" in data, "No key 'results'"
    product = data["results"]
    assert "name" in product, "No key 'name' in results"
    assert isinstance(product, dict), "Product must be a dictionary"
