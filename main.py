#!/usr/bin/env python3

from sys import argv
import json


def split_string_to_words(string):
    words = []
    word = ''
    for i, letter in enumerate(string):
        if letter.isalpha():
            word += letter
        # C++
        elif letter == '+' and string[i - 1] in '+cCсСи':
            word += letter
        # C#
        elif letter == '#' and string[i - 1] in 'cCсСи':
            word += letter
        else:
            # исключаем одиночные буквы, кроме некоторых
            # if word and (len(word) > 1 or word in 'R'):
            if word:
                words.append(word.lower())
                word = ''
    # Чтобы не потерять последнее слово, если строка заканчивается буквой
    word and words.append(word)

    return words


def fill_index_from_file(index_filename, docs_filename):
    index = {}
    docs_id_list = []
    with open(docs_filename, 'r', encoding='utf-8') as file:
        for doc_id, doc in enumerate(file, start=1):
            docs_id_list.append(doc_id)
            words = split_string_to_words(doc)
            for word_position, word in enumerate(words, start=1):
                if word in index:
                    if doc_id in index[word]:
                        index[word][doc_id].append(word_position)
                    else:
                        index[word][doc_id] = [word_position]
                else:
                    index[word] = {doc_id: [word_position]}

    with open(index_filename, 'w', encoding='utf-8') as index_file:
        if index_filename[-4:] == 'json':
            index['_docs_filename'] = docs_filename
            index['_docs_id_list'] = docs_id_list
            json.dump(index, index_file,
                      # sort_keys=True,
                      # indent=4,
                      ensure_ascii=False
                      )
        else:
            index_file.write(docs_filename + ':' + ','.join(map(str,docs_id_list)) + '\n')
            for keyword in index:
                line = ':'.join([keyword,
                                 ','.join(map(str, index[keyword].keys())),
                                 ';'.join([','.join(map(str, v)) for v in index[keyword].values()])])
                index_file.write(line + '\n')


def load_index_file(index_filename):
    with open(index_filename, "r", encoding='utf-8') as index_file:
        if index_filename[-4:] == 'json':
            return json.load(index_file, object_hook=json_keys_to_int)
        else:
            index = {}
            for i, line in enumerate(index_file):
                if i == 0:
                    _docs_filename, _docs_id_list = line.strip().split(':')
                    index['_docs_filename'] = _docs_filename
                    index['_docs_id_list'] = list(map(int, _docs_id_list.split(',')))
                    continue
                line_parts = line.strip().split(':')
                word = line_parts[0]
                ids = list(map(int, line_parts[1].split(',')))
                positions = [list(map(int, x.split(','))) for x in line_parts[2].split(';')]
                index[word] = dict(zip(ids, positions))

            return index

def search_one_word_with_ranging(index, word):
    result = {}
    for doc_id, word_positions in index.get(word, {}).items():
        if len(word_positions) in result:
            result[len(word_positions)].append(int(doc_id))
        else:
            result[len(word_positions)] = [int(doc_id)]

    ranked_id_list = []
    [ranked_id_list.extend(ids) for _, ids in sorted([(key, value) for key, value in result.items()], reverse=True)]

    return ranked_id_list


def search_one_word(index, word):
    return index.get(word, {})


def get_found_docs(docs_filename, found_id_list):
    with open(docs_filename, 'r', encoding='utf-8') as docs_file:
        doc_list = {doc_id: doc.rstrip() for doc_id, doc in enumerate(docs_file, start=1) if doc_id in found_id_list}
        return ([(doc_id, doc_list[doc_id]) for doc_id in found_id_list])


def show_results(found_docs, words_to_highlight, page=1, per_page=10):
    for doc_id, doc in found_docs[(page - 1) * per_page:page * per_page]:
        print(f'{doc_id:>3}. {doc[:80]}...')


def json_keys_to_int(d):
    if isinstance(d, dict):
        try:
            return {int(k): v for k, v in d.items()}
        except ValueError:
            return d


if __name__ == '__main__':

    if len(argv) > 3:
        work_mode = argv[1]
        index_filename = argv[2]
        if work_mode == '-i':
            docs_filename = argv[3]
        elif work_mode == '-s':
            request = argv[3:]
            request_str = ' '.join(request)
        else:
            print('Unknown mode')
            quit()
    else:
        print("""Usage: 
        Indexing: main.py -i index_file docs_file
        Searching: main.py -s index_file request""")
        quit()

    if work_mode == '-i':
        fill_index_from_file(index_filename, docs_filename)

    if work_mode == '-s':
        index = load_index_file(index_filename)
        result_id_list = index['_docs_id_list']
        logic_op = 'and'
        not_op = False

        for sub in request:
            # Если это фраза
            if ' ' in sub:
                found_id_list = []
                sub_words = sub.lower().split()

                # Находим все id документов, в которых встречаются все слова из фразы
                for i, word in enumerate(sub_words):
                    if i:
                        doc_id_set = doc_id_set.intersection(set(index.get(word, {}).keys()))
                    else:
                        doc_id_set = set(index.get(word, {}).keys())

                # Выбираем id документов, в которых слова идут одно за другим
                for id in doc_id_set:
                    first_word_position_list = index[sub_words[0]][id]
                    for first_word_position in first_word_position_list:
                        for i, next_word in enumerate(sub_words[1:], start=1):
                            if first_word_position + i not in index[next_word][id]:
                                break
                        else:
                            found_id_list.append(id)
                # print(sub, len(found_id_list), found_id_list)

            elif sub.lower() == 'and':
                logic_op = 'and'
                not_op = False
                continue

            elif sub.lower() == 'or':
                logic_op = 'or'
                not_op = False
                continue

            elif sub.lower() == 'not':
                not_op = True
                continue

            else:
                found_id_list = list(index.get(sub.lower(), {}).keys())
                # print(sub, len(found_id_list), found_id_list)

            # Отрабатываем операторы
            if not_op:
                found_id_list = list(set(index['_docs_id_list']).difference(found_id_list))
                not_op = False

            if logic_op == 'and':
                result_id_list = list(set(result_id_list).intersection(set(found_id_list)))

            if logic_op == 'or':
                result_id_list = list(set(result_id_list).union(set(found_id_list)))
                logic_op = 'and'

        # print()
        # print(len(result_id_list), result_id_list)

        if result_id_list:
            docs_filename = index['_docs_filename']
            found_docs = get_found_docs(docs_filename, result_id_list)
            print(f'По запросу \'{request_str}\' документов найдено: {len(found_docs)} ')
            show_results(found_docs, request, page=1, per_page=10)
            if len(result_id_list) > 10:
                print('...')
        else:
            print(f'По запросу \'{request_str}\' документов не найдено.')
