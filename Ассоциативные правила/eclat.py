import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
"""
Класс инициируется 3мя параметрами:
- min_supp - минимальный support  который мы рассматриваем для ItemSet. Рассчитывается как % от количества транзакций
- max_items - максимальное количество елементов в нашем ItemSet
- min_items - минимальное количество элементов ItemSet
"""


class Eclat:
    # инициализация объекта класса
    def __init__(self, min_support=0.01, max_items=5, min_items=2):
        self.min_support = min_support
        self.max_items = max_items
        self.min_items = min_items
        self.item_lst = list()
        self.item_len = 0
        self.item_dict = dict()
        self.final_dict = dict()
        self.data_size = 0

    # создание словаря из ненулевых объектов из всех транзакций (вертикальный датасет)
    def read_data(self, dataset):
        for index, row in dataset.iterrows():
            row_wo_na = row.dropna().unique()
            for item in row_wo_na:
                item = item.strip()
                if item in self.item_dict:
                    self.item_dict[item][0] += 1
                else:
                    self.item_dict.setdefault(item, []).append(1)
                self.item_dict[item].append(index)
        # задаем переменные экземпляра (instance variables)
        self.data_size = dataset.shape[0]
        self.item_lst = list(self.item_dict.keys())
        self.item_len = len(self.item_lst)
        self.min_support = self.min_support * self.data_size
        #print ("min_supp", self.min_support)

    # рекурсивный метод для поиска всех ItemSet по алгоритму Eclat
    # структура данных: {Item: [Supp number, tid1, tid2, tid3, ...]}
    def recur_eclat(self, item_name, tids_array, minsupp, num_items, k_start):
        if tids_array[0] >= minsupp and num_items <= self.max_items:
            for k in range(k_start + 1, self.item_len):
                if self.item_dict[self.item_lst[k]][0] >= minsupp:
                    new_item = item_name + " | " + self.item_lst[k]
                    new_tids = np.intersect1d(tids_array[1:], self.item_dict[self.item_lst[k]][1:])
                    new_tids_size = new_tids.size
                    new_tids = np.insert(new_tids, 0, new_tids_size)
                    if new_tids_size >= minsupp:
                        if num_items >= self.min_items: self.final_dict.update({new_item: new_tids})
                        self.recur_eclat(new_item, new_tids, minsupp, num_items + 1, k)

    # последовательный вызов функций определенных выше
    def fit(self, dataset):
        i = 0
        self.read_data(dataset)
        for w in self.item_lst:
            self.recur_eclat(w, self.item_dict[w], self.min_support, 2, i)
            i += 1
        return self

    # вывод в форме словаря {ItemSet: support(ItemSet)}
    def transform(self):
        return {k: "{0:.4f}%".format((v[0] + 0.0) / self.data_size * 100) for k, v in self.final_dict.items()}

#создадим экземпляр класса с нужными нам параметрами
model = Eclat(min_support = 0.01, max_items = 4, min_items = 3)

dataset = pd.read_csv('Transaction.csv')
#обучим

Transaction = dataset['Transaction'].unique()
clear_data = []

for t in Transaction:
    filter_t = dataset['Transaction'] == t
    clear_data.append(tuple(dataset.loc[filter_t]['Product'].tolist()))


d = pd.DataFrame(clear_data)
print(d)
model.fit(d)

#и визуализируем результаты
print(model.transform())
