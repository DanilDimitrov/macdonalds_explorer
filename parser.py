import re

import requests
from bs4 import BeautifulSoup
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


main_url = 'https://www.mcdonalds.com/'

options = Options()
options.headless = True
options.add_argument('headless')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')


def get_urls_from_main_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    urls = []
    for a_tag in soup.select('.cmp-category__row .cmp-category__item .cmp-category__item-link'):
        urls.append(a_tag['href'])
    return urls


def get_nutrition_values(url):
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    li_items = driver.find_elements(By.CSS_SELECTOR, 'li.cmp-nutrition-summary__heading-primary-item')
    nutrition_values = []

    for li in li_items[:4]:
        span_value = li.find_element(By.CSS_SELECTOR, 'span.value')
        span_sr_only_pd = span_value.find_element(By.CSS_SELECTOR, 'span.sr-only.sr-only-pd')
        nutrition_value = span_sr_only_pd.text.strip()
        cleaned_value = re.sub(r'\s+', ' ', nutrition_value)
        nutrition_values.append(cleaned_value)

    driver.quit()
    return nutrition_values


def get_elements(url):
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    div_element = driver.find_element(By.CSS_SELECTOR, 'div.cmp-nutrition-summary__details-column-view-desktop')
    nutrition_values = []

    ul = div_element.find_element(By.TAG_NAME, 'ul')
    li_items = ul.find_elements(By.CSS_SELECTOR, 'li.label-item')
    for li in li_items[:4]:
        span_sr_only = li.find_element(By.CSS_SELECTOR, 'span.sr-only')
        value = span_sr_only.get_attribute('textContent').strip()
        cleaned_value = re.sub(r'\s+', ' ', value)
        nutrition_values.append(cleaned_value.replace('Percent Daily Values', '% DV'))

    driver.quit()
    return nutrition_values


def get_product_info(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        aboutProductUrl = soup.find('div', class_='cmp-accordion__item')['id']

        nutritions = get_nutrition_values(f"{url}#{aboutProductUrl}")
        elements = get_elements(f"{url}#{aboutProductUrl}")

        product_info = {
            'name': soup.find('span', class_='cmp-product-details-main__heading-title').text.strip(),
            'description': soup.find('div', class_='cmp-text').get_text(strip=True),
            'calories': nutritions[0],
            'fats': nutritions[1],
            'carbs': nutritions[2],
            'proteins': nutritions[3],
            'unsaturated fats': elements[0] if elements else 'no value',
            'sugar': elements[1] if elements else 'no value',
            'salt': elements[2] if elements else 'no value',
            'portion': elements[3] if elements else 'no value',
            }
        return product_info
    except:
        return None


def update_products():
    product_infos = []
    product_urls = get_urls_from_main_page(f"{main_url}ua/uk-ua/eat/fullmenu.html")

    for url in product_urls:
        product_info = get_product_info(main_url + url)
        product_infos.append(product_info)

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(product_infos, f, ensure_ascii=False, indent=4)

