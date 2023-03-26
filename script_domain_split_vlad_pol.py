"""скрипт разбивки домена по ключевым словам для кластеризации"""

import pandas as pd
import re


stop_words = {"www", "com", "net", "ru", "xyz", "info", "http", "https"}  # список слов на удаление
#split_words = ("sex", "porn", "prostitut")  # список подслов на добавление

def domain_split(value):
    """функция разбивки домена по ключевым словам"""
    value = str(value[2:-2])
    lst = set(re.split('[-./:]+', value))
    lst -= stop_words
    lst = list(lst)
#    lst = re.split('[-./:]+', value)
    string = ' '.join(str(el) for el in lst)
#    for word in split_words:
#        if word in string:
#            string += f" {word}"
#    print(string)
    return string


# чтение данных
data_patch = "data/vl.csv"
df = pd.read_csv(data_patch, encoding="utf-8")
#print(df.head())


# вывод датафрейма с доменами и рабитыми доменами
df_domains = df['urls']
df_domains_split = df["urls"].apply(domain_split)
df_domains_split = df_domains_split.rename('domains_split')
df_domains = pd.concat([df_domains, df_domains_split], axis= 1)
df_domains.to_csv("data/df_vl_urls.csv", index=False, encoding="utf-8-sig")

print(df_domains.head())