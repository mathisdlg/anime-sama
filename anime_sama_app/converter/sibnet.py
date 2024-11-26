import requests, re
from bs4 import BeautifulSoup
from anime_sama_app.converter.const import PARSER

def correct(url):
    return url if url.startswith('https:') else f"https:{url}"

def get_headers(referer):
    return {"Referer": referer}

def http_request_body(url, referer):
    headers = get_headers(referer)
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Failed to fetch from {url}: {e}")
        return None

def http_request(url, referer):
    headers = get_headers(referer)
    try:
        response = requests.get(url, headers=headers, allow_redirects=False)
        return response
    except requests.RequestException as e:
        print(f"Failed to fetch from {url}: {e}")
        return None


def get_location_from_embed(embed):
    intermediaries = []
    real = ""

    def get_intermediary():
        nonlocal intermediaries
        body = http_request_body(embed, embed)
        if not body:
            return False

        soup = BeautifulSoup(body, PARSER)
        scripts = [script.string for script in soup.find_all('script') if script.string and 'player.src' in script.string]

        if not scripts:
            print("No scripts found")
            return False

        script = scripts[0]
        mp4_match = re.search(r"player\.src\(\[{src:\s*['\"]([^'\"]+)['\"]", script)

        if not mp4_match:
            print("No mp4Match found")
            return False

        intermediaries.append(f"https://video.sibnet.ru{mp4_match.group(1)}")
        return True

    def follow_redirection():
        nonlocal intermediaries, real
        if not intermediaries:
            print("No intermediaries found")
            return False

        res = http_request(intermediaries[0], embed)
        if res and res.status_code == 302:
            intermediaries.append(correct(res.headers.get('Location')))
            second_res = http_request(intermediaries[1], None)

            if second_res:
                if second_res.status_code == 302:
                    real = correct(second_res.headers.get('Location'))
                elif second_res.status_code == 200:
                    real = intermediaries.pop()
                else:
                    print("Second response status is not 302 or 200")
                    return False
            else:
                print("Second request failed")
                return False
        else:
            print("First request failed")
            return False

        return True

    get_intermediary()
    follow_redirection()
    return real