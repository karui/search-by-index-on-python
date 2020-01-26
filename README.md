# search-by-index-on-python
Прототип домашки по индексированию и поиску

## Использование:
- Индексирование:   `python main.py -i index_file docs_file`
- Поиск по индексу: `python main.py -s index_file request`

## Что работает:
- Создание индекс-файла по документ-файлу
- Поиск по индексу: по словам, фразам и с логическими операторами AND/OR/NOT

## Пример:
- Индексирование: `python main.py -i index.txt vacancies.txt`
- Поиск одного слова: `python main.py -s index.txt java`
- Поиск нескольких слов `python main.py -s index.txt junior java jeveloper
- Поиск фразы: `python main.py -s index.txt "junior java jeveloper"
- Поиск с логическими операторами: `python main.py -s index.txt junior or java and jeveloper not python"
- Комбинация всего: `python main.py -s index.txt "белая зп" not "один из лидеров" and junior or hh` 
