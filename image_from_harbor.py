import requests
import warnings


def main():
    warnings.filterwarnings("ignore")

    headers = {'Content-Type': 'application/json; charset=utf-8'}
    cookies = {'timezone_display': '"Asia/Seoul"'}

    docker_images = []
    for i in range(1,10):
        # url_image = f"https://harbor-tks.taco-cat.xyz/api/v2.0/repositories?page={i}&page_size=100"
        url_image = f"https://harbor.tks/api/v2.0/repositories?page={i}&page_size=100"
        res_json = get_json_from_url(url_image, headers, cookies)

        for value in res_json:
            name = value["name"].split("/")[1]
            tag_list = get_tag(name, headers, cookies)
            for tag in tag_list:
                if tag is not None:
                    image_name = name + ":" + tag
                    docker_images.append(image_name)

    print(docker_images)


def get_json_from_url(url, headers, cookies):
    res = requests.get(url, headers=headers, cookies=cookies, verify=False)

    try:
        res.raise_for_status()
    except Exception as exc:
        print('There was a problem: %s' % exc)

    try:
        res_json = res.json()
    except Exception as e:
        print(f'Could not get response_json.\n{e}')
        res_json = None

    return res_json


def get_tag(name, headers, cookies):
    # url = f"https://harbor-tks.taco-cat.xyz/api/v2.0//projects/tks/repositories/{name}/artifacts"
    url = f"https://harbor.tks/api/v2.0//projects/tks/repositories/{name}/artifacts"

    tag_list = []
    res_json = get_json_from_url(url, headers, cookies)
    for value in res_json:
        if value["tags"] is None:
            break
        for tags in value['tags']:
            tag_list.append(tags['name'])

    return tag_list


if __name__ == '__main__':
    main()
