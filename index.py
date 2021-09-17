from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import json

driver = webdriver.Chrome('./chromedriver.exe')


def get_page(url):
    driver.get(url)

    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'search-results')))

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    return soup


def parse_page(soup):
    list = soup.find('ul', {'class': 'list'}).findAll('li')

    articles = []

    for el in list:
        articl = {}

        articl['link'] = 'https://cyberleninka.ru/' + el.find('a', href=True)['href']
        articl['name'] = el.find('h2', {'class': 'title'}).get_text()
        articl['author'] = el.find('span').get_text()
        articl['year'], articl['branch'] = el.find('span', {'class': 'span-block'}).get_text().split(' / ')
        articl['description'] = el.find('div').get_text()

        articles.append(articl)

    return articles


articles = []

for i in range(1, 11):
    page = get_page(
        f'https://cyberleninka.ru/search?q=%D0%B2%D0%B5%D0%B1-%D1%82%D0%B5%D1%85%D0%BD%D0%BE%D0%BB%D0%BE%D0%B3%D0%B8%D0%B8&page={i}'
    )

    articles = articles + parse_page(page)

print(json.dumps(articles, indent=4, ensure_ascii=False))
with open('data.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(articles, indent=4, ensure_ascii=False))

driver.close()
