# -*- coding: utf-8 -*-
from flask import Flask, render_template, request
import os
import multiprocessing
import time
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

sys.path.append(os.path.join(os.getcwd(), 'word'))
import tackle_word
import pronunciation

each_page_words_num = 10
current_dir = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)

stop = False    # stop quickly review


@app.route('/')
def show_year_list_v1():
	tackle = tackle_word.TackleWords()
	res = tackle.get_classified_lst()
	if len(res) == 0:
		return render_template('congratulation.html')

	year_dict = dict()
	for year, value in res[0].iteritems():
		year_dict[year] = 0
	if len(res) > 1:
		for year, value in res[1].iteritems():
			year_dict[year] = 0
	return render_template('year_list.html', year_lst=sorted(year_dict))


@app.route('/year_list', methods=['GET', 'POST'])
def show_year_list_v2():
	tackle = tackle_word.TackleWords()
	res = tackle.get_classified_lst()
	if len(res) == 0:
		return render_template('congratulation.html')

	year_dict = dict()
	for year, value in res[0].iteritems():
		year_dict[year] = 0
	if len(res) > 1:
		for year, value in res[1].iteritems():
			year_dict[year] = 0
	return render_template('year_list.html', year_lst=sorted(year_dict))


@app.route('/week_list', methods=['GET', 'POST'])
def show_week_list():
	if request.method == 'POST':
		tackle = tackle_word.TackleWords()
		res = tackle.get_classified_lst()

		week_list_from_word_builder = []
		week_list_from_clipboard = []
		year = request.form.keys()[0].split('-')[0]

		if year in res[0]:
			for week, words_dict in res[0][year].iteritems():
				week_list_from_word_builder.append(week)
		if len(res) > 1:
			if year in res[1]:
				for week, words_dict in res[1][year].iteritems():
					week_list_from_clipboard.append(week)
		return render_template('week_list.html', year=year, week_list_from_word_builder=sorted(week_list_from_word_builder), week_list_from_clipboard = sorted(week_list_from_clipboard))
	return render_template('nothing.html')


@app.route('/words_list', methods=['GET', 'POST'])
def show_words_list():
	if request.method == 'POST':
		tackle = tackle_word.TackleWords()
		res = tackle.get_classified_lst()

		lst = request.form.keys()[0].split('-')
		come_from = lst[0]
		year = lst[1]
		week = lst[2]

		return show_page(come_from, year, week, 0)
	return render_template('nothing.html')


@app.route('/specified_page', methods=['GET', 'POST'])
def show_specified_page_words():
	if request.method == 'POST':
		tackle = tackle_word.TackleWords()
		res = tackle.get_classified_lst()

		lst = request.form.keys()[0].split('-')
		come_from = lst[0]
		year = lst[1]
		week = lst[2]
		index = lst[3]

		return show_page(come_from, year, week, index)
	return render_template('nothing.html')


def show_page(cf, y, w, i):
	come_from = cf
	year = y
	week = w
	index = i

	start_index = int(index) * each_page_words_num
	last_index = (int(index) + 1) * each_page_words_num - 1
	i = 0

	tackle = tackle_word.TackleWords()
	res = tackle.get_classified_lst()
	src_dict = dict()
	if come_from == '0':  # from word builder
		src_dict = res[0][year][week]
	elif come_from == '1':  # from clipboard
		src_dict = res[1][year][week]
	else:
		return render_template('nothing.html')

	result_lst = []
	src_lst = [(k, v) for k, v in src_dict.iteritems()]
	for item in sorted(src_lst):
		if start_index <= i <= last_index:
			result_lst.append(item)
		if i > last_index:
			break
		i += 1

	num = len(src_dict)/each_page_words_num + 1
	return render_template('word_verbose_info.html', come_from=come_from, y=year, w=week, result=result_lst, button_num=num, page_index=index)



@app.route('/delete', methods=['GET', 'POST'])
def delete_word():
	if request.method == 'POST':
		lst = request.form.keys()[0].split('-')
		come_from = lst[0]
		year = lst[1]
		week = lst[2]
		index = lst[3]
		word = lst[4]

		tackle = tackle_word.TackleWords()
		tackle.delete(come_from, word)
		res = tackle.get_classified_lst()
		if len(res) == 0:
			return render_template('congratulation.html')

		start_index = int(index) * each_page_words_num - 1
		if start_index < 0:
			start_index = 0
		last_index = (int(index) + 1) * each_page_words_num - 1
		i = 0

		src_dict = dict()
		if come_from == '0':  # from word builder
			if len(res[0]) == 0:
				return render_template('congratulation.html')
			src_dict = res[0][year][week]
		elif come_from == '1':  # from clipboard
			if len(res) <= 1 or len(res[1]) == 0:
				return render_template('congratulation.html')
			src_dict = res[1][year][week]
		else:
			return render_template('nothing.html')

		result_lst = []
		src_lst = [(k, v) for k, v in src_dict.iteritems()]
		for item in sorted(src_lst):
			if start_index <= i <= last_index:
				result_lst.append(item)
			if i > last_index:
				break
			i += 1

		num = len(src_dict)/each_page_words_num + 1
		return render_template('word_verbose_info.html', come_from=come_from, y=year, w=week, result=result_lst, button_num=num, page_index=index)
	return render_template('nothing.html')


@app.route('/quickly_review', methods=['GET', 'POST'])
def quickly_review():
	if request.method == 'POST':
		tackle = tackle_word.TackleWords()
		res = tackle.get_classified_lst()

		lst = request.form.keys()[0].split('-')
		come_from = lst[0]
		year = lst[1]
		week = lst[2]
		index = lst[3]

		start_index = int(index) * each_page_words_num - 1
		if start_index < 0:
			start_index = 0
		last_index = (int(index) + 1) * each_page_words_num - 1
		i = 0

		src_dict = dict()
		if come_from == '0':  # from word builder
			src_dict = res[0][year][week]
		elif come_from == '1':  # from clipboard
			src_dict = res[1][year][week]
		else:
			return render_template('nothing.html')

		result_lst = []
		src_lst = [(k, v) for k, v in src_dict.iteritems()]
		for item in sorted(src_lst):
			if start_index <= i <= last_index:
				result_lst.append(item)
			if i > last_index:
				break
			i += 1

		num = len(src_dict)/each_page_words_num + 1

		global stop
		stop = False
		for word, verbose_info in result_lst:
			if stop:
				break
			time.sleep(1.5)
			pronunciation.show(word)
			time.sleep(1)
			pronunciation.show(word)
		return render_template('word_verbose_info.html', come_from=come_from, y=year, w=week, result=result_lst, button_num=num, page_index=index)
	return render_template('nothing.html')


@app.route('/stop_quickly_review', methods=['GET', 'POST'])
def stop_quickly_review():
	if request.method == 'POST':
		global stop
		stop = True

		tackle = tackle_word.TackleWords()
		res = tackle.get_classified_lst()

		lst = request.form.keys()[0].split('-')
		come_from = lst[0]
		year = lst[1]
		week = lst[2]
		index = lst[3]

		return show_page(come_from, year, week, index)
	return render_template('nothing.html')


if __name__ == '__main__':
	app.run(debug=True, threaded=True)
