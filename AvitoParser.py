import os
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup

def avito_cities_checker():
    http = "https://www.avito.ru/"
    url = str(http)
    request = requests.get(url)
    bs = BeautifulSoup(request.text, "html.parser")
    all_category = bs.find_all("div", class_="category-with-counters-item-HDr9u")
    all_links = bs.find_all("div", class_="category-with-counters-item-HDr9u")
    for i in all_links:
        for j in i:
            print(j)
    # "/lichnye_veschi" = 'Личные вещи'
    # "/transport" = 'Транспорт'
    # "/rabota" = 'Работа'
    # "/zapchasti_i_aksessuary" = 'Автозапчасти и аксессуары'
    # "/dlya_doma_i_dachi" = 'Для дома и дачи'
    # "/nedvizhimost" = 'Недвижимость'
    # "/predlozheniya_uslug" = 'Предложение услуг'
    # "/hobbi_i_otdyh" = 'Хобби и отдых'
    # "/bytovaya_elektronika" = 'Электроника'
    # "/zhivotnye" = 'Животные'
    # "/dlya_biznesa" = 'Готовый бизнес и оборудование'


def avito_product_finder(product="ps vita", region="moskva", start_price=0, pages=1, savedata=None):
    path = f'./avito_parsered_data/'
    product_original_name = product
    product = product.upper().replace(" ", "+")
    http = "https://www.avito.ru/"
    links = []
    titles = []
    prices = []
    dates = []
    for i in range(pages):
        print("обработка " + str(i + 1) + " страницы")
        page = i
        url = str(http) + region + "?p=" + str(page) + "&q=" + str(product)
        request = requests.get(url)
        # print(request)
        if str(request) == "<Response [200]>":
            print("страница ", i + 1, "загружена")
        if str(request) == "<Response [404]>":
            print("страниц больше нет")
            break
        if str(request) == "<Response [429]>":
            print("BANNED")
            break
        bs = BeautifulSoup(request.text, "lxml")
        all_links = bs.find_all("a", class_="title-root-zZCwT")
        all_prices = bs.find_all("span", class_="price-text-_YGDY text-text-LurtD text-size-s-BxGpL")
        all_dates = bs.find_all("div",
                                class_="date-text-KmWDf text-text-LurtD text-size-s-BxGpL text-color-noaccent-P1Rfs")
        for link in all_links:
            links.append("https://www.avito.ru" + link['href'])
            titles.append(link['title'])
        for price in all_prices:
            try:
                prices.append(int(str(price.text).replace(" ", "")[0:-1]))  # Цены превращаем в int
            except:
                prices.append("not_int")  # Остальное помечаем как "not_int"
        for date in all_dates:
            dates.append(str(date.text))
    df = pd.DataFrame(data={
        'links': links,
        'titles': titles,
        'prices': prices,
        'dates': dates
    })
    df.drop(np.where(df['prices'] == "not_int")[0], inplace=True)  # Убираем "not_int"
    df = df.sort_values(by="prices", ascending=True)  # Сортируем по возрастанию
    df.drop_duplicates(inplace=True)  # Убираем дубликаты
    df = df[df.prices > start_price]  # Убираем хлам
    df = df.reset_index(drop=True)  # Переиндексируем ячейки
    avg_price = 0
    for i in range(0, len(df.links), 1):
        print(i + 1, df.prices[i], df.links[i], df.titles[i], df.dates[i])
        avg_price += int(df.prices[i])
    avg_price /= len(df.links) + 1
    print("Средняя цена", int(avg_price) + 1, "на основании", len(df.links), "объявлений")
    # Сохраняем в файл
    if savedata == "csv":
        os.makedirs(path, exist_ok=True)
        df.csv(path + str(product_original_name) + '.csv')
    if savedata in ["exel", 'xls', 'xlsx']:
        os.makedirs(path, exist_ok=True)
        df.to_excel(path + str(product_original_name) + '.xlsx', header=True)
    return df


# name = input("Введите запрос: ")
avito_product_finder(str(input("Введите поисковый запрос: \n")), "moskva", start_price=int(input("Введите стартовую цену")), pages=4, savedata=None)
