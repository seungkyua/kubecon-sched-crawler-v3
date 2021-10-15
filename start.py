import argparse, os, requests, bs4, lxml
# import webbrowser

"""
$ python start.py -p='kccncna2021' -date='2021-10-14' -start=' 3:00am KST' -end='00:00 KST'
$ python start.py -p='kccncna2021' -date='2021-10-15' -start=' 3:00am KST' -end='00:00 KST'
$ python start.py -p='kccncna2021' -date='2021-10-16' -start=' 3:00am KST' -end='00:00 KST'
"""

def get_args():
    parser = argparse.ArgumentParser(description='Say hello')
    parser.add_argument('-n', '--name', metavar='name', default='World', help='Name to greet')
    parser.add_argument('-p', '--place', metavar='place', default='', help='place and year')
    parser.add_argument('-date', '--date', metavar='date', default='', help='date ex)2021-10-14')
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
    # content_inners = soup.select('.sched-container-inner')
    # if content_inners == []:
    #     print('Could not find schedule content')
    #     return
    #
    # print('length = [%d]' % len(content_inners))
    # print(str(content_inners[7]))


def write_content(sess, base_url, headers, cookies, dir):
    os.makedirs(dir, exist_ok=True)

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

    sess_speaker_elems = sess_soup.select('h2 > a')
    if len(sess_speaker_elems) < 1:
        print('There was no "speaker"')
        return

    sess_speaker_elem = sess_soup.select('h2 > a')[0]
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

    # webbrowser.open('https://inventwithpython.com/')

    headers = {'Content-Type': 'text/html; charset=utf-8'}
    cookies = {'timezone_display': '"Asia/Seoul"'}

    # base_url = 'https://kccncna2021.sched.com/2021-10-14/list?iframe=no'
    base_url = 'https://' + args.place + '.sched.com/'
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


    each_elem = soup.select('h3')
    for i in range(len(each_elem)):
        h3_elem = soup.find('h3')
        sched_a_elem = soup.find('a')
        time_str = h3_elem.get_text().strip()
        time_str = time_str.split(' ')[0]
        time_str = time_str.replace(':', '').replace('am', '')
        if len(time_str) < 4:
            time_str = '0' + time_str

        dir = args.date.replace('-', '') + '_' + time_str
        write_content(sched_a_elem, base_url, headers, cookies, dir)
        soup.h3.decompose()
        soup.div.decompose()


    # session_elem = soup.select('a')
    # for sess in session_elem:
    #     write_content(sess, base_url, headers, cookies, dir)


if __name__ == '__main__':
    main()
