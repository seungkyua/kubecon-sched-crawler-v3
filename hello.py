import argparse, os, requests, bs4, lxml
# import webbrowser

"""
$ python hello.py -date='2021-10-14' -d='20211014_0300' -start=' 3:00am KST' -end=' 3:30am KST'
$ python hello.py -date='2021-10-14' -d='20211014_0355' -start=' 3:55am KST' -end=' 4:30am KST'
$ python hello.py -date='2021-10-14' -d='20211014_0630' -start=' 6:30am KST' -end=' 7:25am KST'
$ python hello.py -date='2021-10-14' -d='20211014_0725' -start=' 7:25am KST' -end=' 7:30am KST'
$ python hello.py -date='2021-10-14' -d='20211014_0830' -start=' 8:30am KST' -end=' 9:25am KST'
$ python hello.py -date='2021-10-14' -d='20211014_0925' -start=' 9:25am KST' -end=' 9:30am KST'


$ python hello.py -date='2021-10-15' -d='20211015_0300' -start=' 3:00am KST' -end=' 3:30am KST'
$ python hello.py -date='2021-10-15' -d='20211015_0355' -start=' 3:55am KST' -end=' 4:00am KST'
$ python hello.py -date='2021-10-15' -d='20211015_0630' -start=' 6:30am KST' -end=' 7:25am KST'
$ python hello.py -date='2021-10-15' -d='20211015_0725' -start=' 7:25am KST' -end=' 7:30am KST'
$ python hello.py -date='2021-10-15' -d='20211015_0830' -start=' 8:30am KST' -end=' 9:00am KST'
$ python hello.py -date='2021-10-15' -d='20211015_0925' -start=' 9:25am KST' -end=' 9:45am KST'


$ python hello.py -date='2021-10-16' -d='20211016_0300' -start=' 3:00am KST' -end=' 3:30am KST'
$ python hello.py -date='2021-10-16' -d='20211016_0355' -start=' 3:55am KST' -end=' 4:30am KST'
$ python hello.py -date='2021-10-16' -d='20211016_0630' -start=' 6:30am KST' -end=' 7:25am KST'
$ python hello.py -date='2021-10-16' -d='20211016_0725' -start=' 7:25am KST' -end=' 8:00am KST'
$ python hello.py -date='2021-10-16' -d='20211016_0830' -start=' 8:30am KST' -end=' 9:15am KST'
$ python hello.py -date='2021-10-16' -d='20211016_0925' -start=' 9:25am KST' -end='00:00am KST'
"""

def get_args():
    parser = argparse.ArgumentParser(description='Say hello')
    parser.add_argument('-n', '--name', metavar='name', default='World', help='Name to greet')
    parser.add_argument('-date', '--date', metavar='date', default='', help='date ex)2021-10-14')
    parser.add_argument('-d', '--dir', metavar='dir', default='', help='directory')
    parser.add_argument('-start', '--start-time', metavar='start_time', default='12:00am KST', help='time ex)12:00am KST')
    parser.add_argument('-end', '--end-time', metavar='end_time', default=' 1:00am KST', help='time ex) 1:00am KST')
    return parser.parse_args()

def get_content_with_element_string(text, element, start, end):
    soup = bs4.BeautifulSoup(text, 'html.parser')

    # containers = soup.find('h3', string='12:00am KST')
    # containers = soup.h3.next_tag
    # containers = soup.select('#sched-content-inner .sched-container')
    tags = soup.select(element)
    if tags == []:
        print('Could not find schedule tags')
        return

    # print('length = [%d]' % len(tags))
    # print(str(tags))

    first_tag = soup.find(element, string=start)
    start_idx = text.find(str(tags[tags.index(first_tag)]))

    end_idx = 0
    if end != '00:00am KST':
        end_tag = soup.find(element, string=end)
        end_idx = text.find(str(tags[tags.index(end_tag)]))
        # print(tags.index(first_tag))
        # print(tags.index(end_tag))
    else:
        end_tag = soup.find('div', {'class': 'sched-container-bottom'})
        end_tag_string = str(end_tag)
        end_tag_string_idx = end_tag_string.find('>') + 1
        print(end_tag_string[:end_tag_string_idx])
        end_idx = text.rindex(end_tag_string[:end_tag_string_idx])

    return text[start_idx:end_idx]
    # content_inners = soup.select('.sched-container-inner')
    # if content_inners == []:
    #     print('Could not find schedule content')
    #     return
    #
    # print('length = [%d]' % len(content_inners))
    # print(str(content_inners[7]))


def write_content(sess, base_url, headers, cookies, dir):
    # sess.span.extract()
    sess_url = sess.get('href')
    sess_title = sess.get_text().strip().replace('/', '')
    print('session url = [%s]' % sess_url)
    print('session title = [%s]' % sess_title)

    sess_full_url = base_url + sess_url
    sess_res = requests.get(sess_full_url, headers=headers, cookies=cookies)
    try:
        sess_res.raise_for_status()
    except Execption as exc:
        print('There was a problem: %s' % (exc))

    sess_soup = bs4.BeautifulSoup(sess_res.text, 'lxml')
    sess_desc_elem = sess_soup.find('div', {'class': 'tip-description'})
    if sess_desc_elem is None:
        print('There was no "tip-description"')
        return

    sess_speaker_elem = sess_soup.select('h2 > a')[0]
    if sess_speaker_elem is None:
        print('There was no "speaker"')
        return

    sess_role_elem = sess_soup.find('div', {'class': 'sched-event-details-role-company'})

    text_filename = dir + '_' + sess_title + '.txt'
    sess_desc_file = open(os.path.join(dir, text_filename ), 'w')
    sess_desc_file.write(sess_desc_elem.get_text().strip() + '\n\n')
    sess_desc_file.write('Speaker Role: ' + sess_role_elem.get_text() + '\n')
    sess_desc_file.write('Speaker Name: ' + sess_speaker_elem.get_text() + '\n')
    sess_desc_file.close()

    sess_file_elem = sess_soup.select('.file-uploaded')
    if sess_file_elem != []:
        uploaded_file_url = sess_file_elem[0].get('href')
        file_res = requests.get(uploaded_file_url)
        try:
            file_res.raise_for_status()
        except Execption as exc:
            print('There was a problem: %s' % (exc))

        _, file_extension = os.path.splitext(uploaded_file_url)
        bin_filename = dir + '_' + sess_title + file_extension
        sess_upload_file = open(os.path.join(dir, bin_filename), 'wb')
        for chunk in file_res.iter_content(100000):
            sess_upload_file.write(chunk)
        sess_upload_file.close()


def main():
    args = get_args()
    print('Hello, ' + args.name + '!' )

    os.makedirs(args.dir, exist_ok=True)


    # webbrowser.open('https://inventwithpython.com/')

    headers = {'Content-Type': 'text/html; charset=utf-8'}
    cookies = {'timezone_display': '"Asia/Seoul"'}

    # base_url = 'https://kccncna2021.sched.com/2021-10-14/list?iframe=no'
    base_url = 'https://kccncna2021.sched.com/'
    res = requests.get(base_url + args.date + "/list?iframe=no", headers=headers, cookies=cookies)
    try:
        res.raise_for_status()
    except Execption as exc:
        print('There was a problem: %s' % (exc))


    # schedFile = open('2021-10-12.txt', 'wb')
    # for chunk in res.iter_content(100000):
    #     schedFile.write(chunk)
    # schedFile.close()

    # content = get_content_with_element_string(res.text, 'h3', ' 3:00am KST', ' 3:30am KST')
    content = get_content_with_element_string(res.text, 'h3', args.start_time, args.end_time)

    soup = bs4.BeautifulSoup(content.strip(), 'lxml')
    session_elem = soup.select('a')

    for sess in session_elem:
        write_content(sess, base_url, headers, cookies, args.dir)


if __name__ == '__main__':
    main()
