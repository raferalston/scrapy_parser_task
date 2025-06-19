import pytest
import requests

from scrapy.utils.project import get_project_settings

from ..hh_task_project.utility import DataParser


settings = get_project_settings()
API_URL = "https://alkoteka.com/web-api/v1/product/caringer-shvarc-bir_29294"
CITY_UUID = '4a70f9e0-46ae-11e7-83ff-00155d026416'


def test_product_extraction():
    response = requests.get(f"{API_URL}?city_uuid={CITY_UUID}")
    response_data = response.json()
    results = response_data.get('results', {})

    dp = DataParser()
    parsed_data = dp.parse(results)

    assert isinstance(parsed_data, dict)
    assert "title" in parsed_data
    assert parsed_data["current"] >= 0
    assert "metadata" in parsed_data
