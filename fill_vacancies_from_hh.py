#!/usr/bin/env python3

import requests
import re

filename = 'vacancies.txt'
text = 'разработчик'
per_page = 100
pages = 10

vacancy_id_list = []

for page in range(1, pages+1):

    vacancies = requests.get(f'https://api.hh.ru/vacancies?text={text}&per_page={per_page}&page={page}').json()
    vacancy_id_list.extend([item['id'] for item in vacancies['items']])
    print(page)

regex = re.compile(r'<.*?>|&.*?;')

with open(filename, 'w', encoding='utf-8') as docs_file:
    for i, vacancy_id in enumerate(vacancy_id_list):
        vacancy = requests.get('https://api.hh.ru/vacancies/' + vacancy_id).json()
        vacancy_name = vacancy['name']
        vacancy_description = regex.sub(' ', vacancy['description']).strip()
        doc = f'{vacancy_id} • {vacancy_name} • {vacancy_description}'

        docs_file.write(str(doc)+'\n')
        print(i, vacancy_id)

