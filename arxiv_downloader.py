# -*- coding=utf-8 -*-
#! /mnt/lustre/huanggengshi/anaconda3/bin/python
import os


def get_name_from_line(line):
    return line.split('>')[1].split('<')[0]


def get_authors(html_str):
    try:
        author_lines = html_str.split('<div class="authors"><span class="descriptor">Authors:</span>')[1].split('<div class="dateline">')[0]
        author_lines = author_lines.strip().splitlines()[:1]
        authors = [get_name_from_line(line) for line in author_lines][0]
        # authors = authors.replace(' ', '')
        return authors
    except:
        return ''


def get_title(html_str):
    try:
        from bs4 import BeautifulSoup
        html = BeautifulSoup(html_str, 'html.parser')
        title = str(html.title)
        return ''.join(title.split('] ')[1].split('<')[0].splitlines())
    except:
        return ''


def get_date(html_str):
    try:
        date_str = html_str.split('<div class="submission-history">')[1].split('</div>')[0].split('<b>')[-1].split('>')[1].split('<')[0]
        day, month, year = date_str.split()[1:4]
        import calendar
        abbr2num = {v: k for k,v in enumerate(calendar.month_abbr)}
        month = abbr2num[month]
        return int(year), int(month), int(day)
    except:
        return []


def get_comment(html_str):
    try:
        if '<td class="tablecell label">Comments:' in html_str:
            line = html_str.split('<td class="tablecell label">Comments:')[1].split('tablecell comments">')[1].split('<')[0].lower().strip()

            if 'accepted by' in line:
                line = line.split('accepted by')[1].replace(' ', '').upper()
                line = f'[{line}]'
            else:
                line = ''
        else:
            line = ''
    except:
        line = ''
    return line


def get_attributes(number):
    import urllib.request
    url = r'http://xxx.itp.ac.cn/abs/%s'%number
    res = urllib.request.urlopen(url)
    html_str = res.read().decode('utf-8')
    title = get_title(html_str)
    authors = get_authors(html_str)
    date = get_date(html_str)
    comment = get_comment(html_str)
    return comment, title, authors, date


def change_file_time(target_name, date):
    import datetime
    now = datetime.datetime.now().timetuple()
    access_date = datetime.datetime(now[0],now[1],now[2])
    modified_date = datetime.datetime(date[0], date[1],date[2])
    import time
    access_date = time.mktime(access_date.timetuple())
    modified_date = time.mktime(modified_date.timetuple())
    os.utime(target_name, (access_date, modified_date))


def clear_filename(file_name):
    invalid_characters = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    file_name = file_name.replace(' ', '-')
    for c in invalid_characters:
        file_name = file_name.replace(c, '')
    return file_name


def parse_number(number_like):

    for i in range(len(number_like)):
        if number_like[i].isdigit():
             number_like = number_like[i:]
             break
    if '.pdf' in number_like:
        number_like = number_like.strip()[:-4]

    return number_like


def download_chg_time(target_name, date):
    os.system('wget http://xxx.itp.ac.cn/pdf/%s -O %s' % (number, target_name))
    if date:
        change_file_time(target_name, date)


import time
if __name__ == '__main__':
    import sys
    argument = sys.argv
    target_directory = r'C:\Users\sensetime\Documents\论文集\刚下载的论文/'
    while True:
        try:
            number = input('请输入要下载的arxiv论文编号：')
            number = parse_number(number)
            comment, title, authors, date = get_attributes(number)
            name = f'{comment}{title}_{authors}'

            name = clear_filename(name)
            target_name = '%s/%s.pdf'%(target_directory, name)
            download_chg_time(target_name, date)

            to_try = 3
            while os.stat(target_name).st_size < 50*1024 and to_try > 0:
                print('file size < 50kb, retrying...')
                time.sleep(1)
                download_chg_time(target_name, date)
                to_try -= 1
            if os.stat(target_name).st_size < 50*1024:
                raise Exception('文件下载失败：获得的文件大小太小，可能是空文件')
        except Exception as e:
            print('出了一点错误呢..')
            print(e)