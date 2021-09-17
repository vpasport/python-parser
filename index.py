from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import json

driver = webdriver.Chrome('./chromedriver.exe')


def get_page(url):
    driver.get(url)

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'search-results')))

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    return soup


def parse_page(soup):
    list = soup.find('ul', {'class': 'list'}).findAll('li')

    articles = []

    for el in list:
        article = {}

        article['link'] = 'https://cyberleninka.ru/' + el.find('a', href=True)['href']
        article['name'] = el.find('h2', {'class': 'title'}).get_text()
        article['year'], article['journalName'] = el.find('span', {'class': 'span-block'}).get_text().split(' / ')

        print(f"Parsing: {article['name']}")

        driver.get(article['link'])

        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'infoblock')))
        # WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'full abstract')))

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        article['author'] = []
        authors = soup.find('ul', {'class': 'author-list'}).findAll('li')
        for author in authors:
            article['author'].append(author.get_text())

        article['description'] = ''
        description = soup.find('div', {'class': 'full abstract'})
        try:
            article['description'] = description.get_text()
        except:
            pass

        article['keywords'] = []
        keywords = soup.find('i', {'itemprop': 'keywords'})
        try:
            keywords = keywords.findAll('span')
            for word in keywords:
                article['keywords'].append(word.get_text())

            article['branch'] = soup.find('div', {'class': 'half-right'}).find('a').get_text()
        except:
            pass

        articles.append(article)

    return articles


try:
    articles = []

    for i in range(1, 11):
        page = get_page(
            f'https://cyberleninka.ru/search?q=%D0%B2%D0%B5%D0%B1-%D1%82%D0%B5%D1%85%D0%BD%D0%BE%D0%BB%D0%BE%D0%B3%D0%B8%D0%B8&page={i}'
        )

        articles = articles + parse_page(page)

    with open('data.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(articles, indent=4, ensure_ascii=False))
finally:
    driver.close()
