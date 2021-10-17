import argparse
import os
import requests
import bs4
# import lxml
# import webbrowser

"""
$ python start.py -p 'kccncna2021' -s 'day' -date '2021-10-14' -start '3:00am KST' -end '00:00 KST'
$ python start.py -p 'kccncna2021' -s 'day' -date '2021-10-15' -start '3:00am KST' -end '00:00 KST'
$ python start.py -p 'kccncna2021' -s 'day' -date '2021-10-16' -start '3:00am KST' -end '00:00 KST'
"""


def get_args():
    parser = argparse.ArgumentParser(description='Say hello')
    parser.add_argument('-n', '--name', metavar='name', default='World', help='Name to greet')
    parser.add_argument('-s', '--scope', metavar='scope', default='all', help='scraping scope')
    parser.add_argument('-p', '--place', metavar='place', default='kccncna2021', help='place and year')
    parser.add_argument('-date', '--date', metavar='date', default='', help='date ex)2021-10-14')
    parser.add_argument('-start', '--start-time', metavar='start_time', default='',
                        help='time ex)12:00am KST')
    parser.add_argument('-end', '--end-time', metavar='end_time', default='00:00 KST', help='time ex)00:00 KST')
    return parser.parse_args()


def get_content_with_element_string(text, element, start, end):
    soup = bs4.BeautifulSoup(text, 'html.parser')

    # containers = soup.find('h3', string='12:00am KST')
    # containers = soup.h3.next_tag
    # containers = soup.select('#sched-content-inner .sched-container')
    tags = soup.select(element)
    if len(tags) < 1:
        print('Could not find schedule tags')
        return
    # print('length = [%d]' % len(tags))
    # print(str(tags))

    try:
        first_tag = soup.find(element, string=start)
        start_idx = text.find(str(tags[tags.index(first_tag)]))
    except Exception as exc:
        raise

    # end_idx = 0
    if end != '00:00 KST':
        end_tag = soup.find(element, string=end)
        end_idx = text.find(str(tags[tags.index(end_tag)]))
        # print(tags.index(first_tag))
        # print(tags.index(end_tag))
    else:
        end_tag = soup.find('div', {'class': 'sched-container-bottom'})
        end_tag_string = str(end_tag)
        end_tag_string_idx = end_tag_string.find('>') + 1
        end_idx = text.rindex(end_tag_string[:end_tag_string_idx])

    return text[start_idx:end_idx]


def get_content_date_schedule(text, date):
    start_soup = bs4.BeautifulSoup(text, 'html.parser')

    date_elem = start_soup.find('a', {'id': date})
    start_tag_string = str(date_elem).strip()
    start_tag_string_idx = start_tag_string.find('</a>') + 4
    start_idx = text.index(start_tag_string[:start_tag_string_idx])

    text = text[start_idx:]

    # end_soup = bs4.BeautifulSoup(text, 'lxml')
    # end_tag = end_soup.find('div', {'class': 'sched-container-bottom'})
    # end_tag_string = str(end_tag).strip()
    # end_tag_string_idx = end_tag_string.find('>') + 1

    end_idx = text.find('sched-container-bottom') - 12
    # end_idx = text.find(end_tag_string[:end_tag_string_idx])

    # print(end_idx)
    #
    # if start_idx > 169740:
    #     print(text[start_idx:start_idx + end_idx])

    # end_idx = text.index(end_tag_string[:end_tag_string_idx], start_idx)

    context_string = text[:end_idx]
    date_time_soup = bs4.BeautifulSoup(context_string, 'html.parser')
    date_time_list = date_time_soup.select('h3')
    if len(date_time_list) < 2:
        start_time = date_time_list[0].get_text().strip()
        end_time = '00:00 KST'
    else:
        start_time = date_time_list[0].get_text().strip()
        end_time = date_time_list[len(date_time_list) - 1].get_text().strip()

    return context_string, start_time, end_time


def write_content(sess, base_url, headers, cookies, save_dir):
    os.makedirs(save_dir, exist_ok=True)

    # sess.span.extract()
    sess_url = sess.get('href')
    sess_title = sess.get_text().strip().replace('/', '')
    print('session url = [%s]' % sess_url)
    print('session title = [%s]' % sess_title)

    sess_full_url = base_url + sess_url
    sess_res = requests.get(sess_full_url, headers=headers, cookies=cookies)
    try:
        sess_res.raise_for_status()
    except Exception as exc:
        print('There was a problem: %s' % exc)

    sess_soup = bs4.BeautifulSoup(sess_res.text, 'lxml')
    sess_desc_elem = sess_soup.find('div', {'class': 'tip-description'})
    if sess_desc_elem is None:
        print('There was no "tip-description"')
        return

    sess_speaker_elems = sess_soup.select('h2 > a')
    if len(sess_speaker_elems) < 1:
        sess_role_str = ''
        sess_speaker_str = ''
        print('There was no "speaker"')
    else:
        sess_speaker_elem = sess_soup.select('h2 > a')[0]
        sess_role_elem = sess_soup.find('div', {'class': 'sched-event-details-role-company'})
        sess_role_str = sess_role_elem.get_text()
        sess_speaker_str = sess_speaker_elem.get_text()

    text_filename = save_dir + '_' + sess_title + '.txt'
    sess_desc_file = open(os.path.join(save_dir, text_filename), 'w')
    sess_desc_file.write(sess_desc_elem.get_text().strip() + '\n\n')
    sess_desc_file.write('Speaker Role: ' + sess_role_str + '\n')
    sess_desc_file.write('Speaker Name: ' + sess_speaker_str + '\n')
    sess_desc_file.close()

    sess_file_elem = sess_soup.select('.file-uploaded')
    if len(sess_file_elem) > 0:
        uploaded_file_url = sess_file_elem[0].get('href')
        file_res = requests.get(uploaded_file_url)
        try:
            file_res.raise_for_status()
        except Exception as exc:
            print('There was a problem: %s' % exc)

        _, file_extension = os.path.splitext(uploaded_file_url)
        bin_filename = save_dir + '_' + sess_title + file_extension
        sess_upload_file = open(os.path.join(save_dir, bin_filename), 'wb')
        for chunk in file_res.iter_content(100000):
            sess_upload_file.write(chunk)
        sess_upload_file.close()


def main():
    args = get_args()
    print('Hello, ' + args.name + '!')

    # webbrowser.open('https://inventwithpython.com/')

    headers = {'Content-Type': 'text/html; charset=utf-8'}
    cookies = {'timezone_display': '"Asia/Seoul"'}

    if args.scope == 'all':
        # base_url = 'https://kccncna2021.sched.com/list?iframe=no'
        base_url = 'https://' + args.place + '.sched.com/'
        res = requests.get(base_url + "/list?iframe=no", headers=headers, cookies=cookies)
    else:
        # base_url = 'https://kccncna2021.sched.com/2021-10-14/list?iframe=no'
        base_url = 'https://' + args.place + '.sched.com/'
        res = requests.get(base_url + args.date + "/list?iframe=no", headers=headers, cookies=cookies)

    try:
        res.raise_for_status()
    except Exception as exc:
        print('There was a problem: %s' % exc)

    soup = bs4.BeautifulSoup(res.text, 'lxml')
    date_list_elem = soup.select(".sched-container-anchor")
    # for anchor in date_list_elem:
    #     date = anchor.get("id")
    #     content_string, start_time, end_time = get_content_date_schedule(res.text, date)
    #     main_loop(content_string, base_url, headers, cookies, date, start_time, end_time)

    for anchor in date_list_elem:
        date = anchor.get("id")
        if args.date != '' and args.date != date:
            continue

        content_string, start_time, end_time = get_content_date_schedule(res.text, date)
        if args.start_time != '':
            start_time = args.start_time
        if args.end_time != '':
            end_time = args.end_time
        main_loop(content_string, base_url, headers, cookies, date, start_time, end_time)


def main_loop(text, base_url, headers, cookies, date, start_time, end_time):
    # schedFile = open('2021-10-12.txt', 'wb')
    # for chunk in res.iter_content(100000):
    #     schedFile.write(chunk)
    # schedFile.close()

    # content = get_content_with_element_string(res.text, 'h3', ' 3:00am KST', ' 3:30am KST')
    start_hour_str = start_time.split(':')[0]
    if len(start_hour_str) < 2:
        start_time = ' ' + start_time

    end_hour_str = end_time.split(':')[0]
    if len(end_hour_str) < 2:
        end_time = ' ' + end_time
    try:
        content = get_content_with_element_string(text, 'h3', start_time, end_time)
    except Exception as exc:
        print('There was a problem: %s' % exc)
        return

    soup = bs4.BeautifulSoup(content.strip(), 'lxml')

    time_list_elem = soup.select('h3')
    for i in range(len(time_list_elem)):
        h3_elem = soup.find('h3')
        time_str = h3_elem.get_text().strip()
        hour_str = time_str.split(':')[0]
        if len(hour_str) < 2:
            time_str = '0' + time_str
        # 1200am 은 0000am 으로 수정
        time_str = time_str.replace(' KST', '').replace(':', '').replace('1200am', '0000am')
        save_dir = date.replace('-', '') + '_' + time_str
        sched_a_elem = soup.find('a')
        write_content(sched_a_elem, base_url, headers, cookies, save_dir)
        soup.h3.decompose()
        soup.div.decompose()


if __name__ == '__main__':
    main()
