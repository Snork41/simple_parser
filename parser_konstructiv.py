"""
Парсим товары с сайта торгового центра строительных и отделочных материалов.
https://konstr-v.ru/
"""

import csv
from random import randint
from time import sleep

import requests
from bs4 import BeautifulSoup

from parser_model import ProductKonstructiv

# Вставляем url необходимой категории товаров, например:
# 'https://konstr-v.ru/catalog/stroymaterialy_/ventilyatsiya_otoplenie/'
# или
# 'https://konstr-v.ru/catalog/stroymaterialy_/lakokrasochnye_materialy/emali/'
url = 'https://konstr-v.ru/catalog/ruchnoy_instrument/yashchiki_i_sumki/'
name_file_csv = url.split('/')[-2]


def parser(url: str, name_file_csv: str, items_max: int):
    page = 1
    count_items = 0
    while items_max > count_items:
        list_products = []
        response = requests.get(f'{url}?PAGEN_1={page}')
        print(f'> Ответ от страницы {page} получен. Код {response.status_code}')
        print(f'>> {response.url}')
        soup = BeautifulSoup(response.text, 'lxml')
        products = soup.find_all('div', class_='inner_wrap TYPE_1')
        for product in products:
            if count_items >= items_max:
                break
            name = product.find('div', class_='item-title').text.strip()
            article = product.find('div', class_='article_block').text.strip()
            link = f"https://konstr-v.ru{product.find('a').get('href')}"
            price = product.find('span', class_='price_value').text
            list_products.append(ProductKonstructiv(
                name=name,
                article=article,
                link=link,
                price=price
            ))
            count_items += 1
        write_csv(name_file_csv, list_products)
        print(f'>>> Страница {page} записана в файл!')
        page += 1
        pause = randint(1, 4)
        print(f'>>>> Пауза {pause} секунды...', end='\n\n')
        sleep(pause)


def create_csv(name_file_csv: str):
    with open(f'{name_file_csv}.csv', 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['name', 'article', 'link', 'price'])


def write_csv(name_file_csv: str, list_products: list[ProductKonstructiv]):
    with open(f'{name_file_csv}.csv', 'a', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        for product in list_products:
            writer.writerow(
                [
                    product.name,
                    product.article,
                    product.link,
                    product.price
                ]
            )


def max_items_in_category(url, name_file_csv: str):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    items_max = int(soup.find('span', class_='element-count-wrapper').text)
    print(f'>> Количество товаров {items_max} в категории {name_file_csv.upper()} <<', end='\n\n')
    return items_max


def main():
    create_csv(name_file_csv)
    try:
        items_max = max_items_in_category(url=url, name_file_csv=name_file_csv)
        parser(url=url, name_file_csv=name_file_csv, items_max=items_max)
        print('^_^ Готово! ^_^')
    except Exception as err:
        print(f'!ОШИБКА! {type(err)}', err, sep='\n')


if __name__ == '__main__':
    main()
