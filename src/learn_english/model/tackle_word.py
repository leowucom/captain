# -*- coding: utf-8 -*-
import os
from os.path import dirname, abspath
import datetime
import utility
from datetime import datetime
from get_word_meaning import get_word_meaning
import random
import time
import pronunciation

parent_dir = dirname(dirname(abspath(__file__)))
working_dir = os.getcwd()
absolute_prefix = os.path.join(working_dir, 'asset')
words_dir = os.path.join(parent_dir, 'asset/words')

dict_file = os.path.join(parent_dir, 'asset/dict.json')
clipboard_file = os.path.join(parent_dir, 'asset/clipboard.json')
builder_file = os.path.join(parent_dir, 'asset/builder.json')


'''
all types might appear in result queried from youdao.com.
'basic'           ------>基本释义
'usage'           ------>出现的语句
'phrase'          ------>词组短语
'synonyms'        ------>同近义词
'rel_word_tab'    ------>同根词
'discriminate'    ------>词语辨析
'collins'         ------>柯林斯
'date'            ------>单词录入时间
'index'           ------>index

word-0            represent word from word builder
word-1            represent word from clipboard
'''


class TackleWords:
    def __init__(self):
        self.dict_data = utility.load_json_file(dict_file)
        self.clipboard_data = utility.load_json_file(clipboard_file)

    def query(self, wrapped_word, usage=None, date=None, book=None):
        if wrapped_word in self.dict_data:
            self.dict_data[wrapped_word]['usage'] = self.add_usage_to_collection(
                self.dict_data[wrapped_word]['usage'], usage)
        else:
            result = get_word_meaning(wrapped_word)
            if result is None:
                return
            if usage is not None:
                result[wrapped_word]['usage'] = self.add_usage_to_collection(result[wrapped_word]['usage'], usage)
            if date is not None:
                result[wrapped_word]['date'] = date.strip()
            if book is not None:
                result[wrapped_word]['book'] = book.strip()
            self.dict_data[wrapped_word] = result[wrapped_word]
        self.store(dict_file, wrapped_word, self.dict_data[wrapped_word])

        if wrapped_word.split('-')[1] == '1':
            self.store_clipboard(wrapped_word[:-2], usage)
        return

    def store(self, file_name, key, value):
        if key is None or len(key) == 0 or value is None:
            self.dict_data = utility.load_json_file(dict_file)
            self.clipboard_data = utility.load_json_file(clipboard_file)
            return
        all_data = utility.load_json_file(file_name)
        all_data[key] = value
        utility.write_json_file(file_name, all_data)

    def remove(self, file_name, key):
        if key is None or len(key) == 0:
            self.dict_data = utility.load_json_file(dict_file)
            self.clipboard_data = utility.load_json_file(clipboard_file)
            return
        all_data = utility.load_json_file(file_name)
        del all_data[key]
        utility.write_json_file(file_name, all_data)

    def store_clipboard(self, word, usage):
        if word in self.clipboard_data:
            self.clipboard_data[word]['usage'] = self.add_usage_to_collection(self.clipboard_data[word]['usage'], usage)
        else:
            word_info = dict()
            word_info['usage'] = ''
            word_info['usage'] = self.add_usage_to_collection(word_info['usage'], usage)
            word_info['date'] = str(datetime.now())[:-7]
            self.clipboard_data[word] = word_info
        self.store(clipboard_file, word, self.clipboard_data[word])

    def import_words(self):
        files = [f for f in os.listdir(words_dir) if os.path.isfile(
            os.path.join(words_dir, f))]
        for file_name in files:
            if os.path.splitext(file_name)[1] != '.txt':
                continue
            file_path = os.path.join(words_dir, file_name)
            with open(file_path) as f:
                # All lines including the blank ones
                lines = (line.rstrip() for line in f)
                lines = list(line for line in lines if line)  # Non-blank lines
                for index, line in enumerate(lines):
                    if line[0].isdigit():
                        word = line[line.find('.') + 2:]
                        wrapped_word = word + '-0'
                        if wrapped_word in self.dict_data:
                            continue
                        usage = lines[index +
                                      1][lines[index + 1].find(':') + 1:]
                        book = lines[index +
                                     2][lines[index + 2].find(':') + 1:]
                        self.query(wrapped_word, usage, file_name[:-4], book)
        for word, word_info in self.clipboard_data.iteritems():
            wrapped_word = word + '-1'
            self.query(wrapped_word, word_info['usage'], word_info['date'])
        utility.show_notification(
            'Captain Import Info', 'Importing words completely finished!')

    def delete(self, wrapped_word):
        self.clipboard_data = utility.load_json_file(clipboard_file)
        word_ele = wrapped_word.split('-')
        # delete from dict
        del self.dict_data[wrapped_word]
        self.remove(dict_file, wrapped_word)

        # delete from word builder
        if word_ele[1] == '0':
            for file_name in os.listdir(words_dir):
                if file_name.endswith(".txt"):
                    file_path = os.path.join(words_dir, file_name)
                    if '. ' + word_ele[0] in open(file_path).read():
                        valid_lines_lst = []
                        with open(file_path) as f:
                            # All lines including the blank ones
                            lines = (line.rstrip() for line in f)
                            # Non-blank lines
                            lines = list(line for line in lines if line)
                            for index, line in enumerate(lines):
                                if line[0].isdigit():
                                    wrapped_word = line[line.find(
                                        '.') + 2:].strip()
                                    if wrapped_word == word_ele[0]:
                                        continue
                                    valid_lines_lst.append(line + '\n')
                                    valid_lines_lst.append(
                                        lines[index + 1] + '\n')
                                    valid_lines_lst.append(
                                        lines[index + 2] + '\n')
                                    valid_lines_lst.append(
                                        lines[index + 3] + '\n')
                                    valid_lines_lst.append('\n')
                        with open(file_path, "w") as f:
                            for line in valid_lines_lst:
                                f.write(line)
                        break
        else:
            # delete from clipboard
            if word_ele[0] in self.clipboard_data:
                self.remove(clipboard_file, word_ele[0])
        return

    # lst(key: year->date->word  value: word_info)
    def get_classified_lst(self):
        result = dict()
        result[0] = dict()
        result[1] = dict()
        for wrapped_word, word_info in self.dict_data.iteritems():
            year_and_month = self.get_year_and_month(word_info[u'date'])
            year = year_and_month[0]
            # month = year_and_month[1]

            wrapped_list = wrapped_word.split('-')
            word = wrapped_list[0]
            word_come_from = int(wrapped_list[1])

            if year not in result[word_come_from]:
                result[word_come_from][year] = dict()
            if word_info['date'] not in result[word_come_from][year]:
                result[word_come_from][year][word_info['date']] = dict()
            result[word_come_from][year][word_info['date']][word] = word_info
        return result

    @staticmethod
    def add_usage_to_collection(collection, usage):
        if collection.find(usage) < 0:
            collection += usage
            if not usage.endswith('\n'):
                collection += '\n'
        return collection

    @staticmethod
    def get_year_and_month(date):
        d1 = date.split(' ')[0]
        d2 = d1.split('-')
        return d2[:2]


    # 获取随机单词，用于复习使用
    def emit_random_word(self):
        random_word = random.choice(self.dict_data.keys())[:-2]
        pronunciation.show(random_word)
        time.sleep(1.5)
        pronunciation.show(random_word)
        time.sleep(1.5)
        pronunciation.show(random_word)
        time.sleep(2)


    def memorize_words(self):
        now_minute = utility.get_now_minute()
        if 0 <= now_minute <= 5:
            self.emit_random_word()
        elif 25 <= now_minute <= 30:
            self.emit_random_word()



def p(content):
    utility.append_log('---------------------')
    utility.append_log(content)


if __name__ == "__main__":
    tackle_words = TackleWords()
    tackle_words.import_words()
