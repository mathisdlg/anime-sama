from bs4 import BeautifulSoup
import os, requests, time, re, pycurl
from anime_sama_app.converter.sibnet import get_location_from_embed
from anime_sama_app.converter.const import PARSER, SITE, SEARCH_QUERY_BASE, SAVE_DIR


def available(series):
    return requests.get(f"https://{SITE}/{SEARCH_QUERY_BASE}/{series}").status_code == 200


def get_seasons_link(series):
    response = requests.get(f"https://{SITE}/{SEARCH_QUERY_BASE}/{series}")
    soup = BeautifulSoup(response.text, PARSER)
    content_div = soup.find("div", {"id": "sousBlocMilieu"}).find_all("div")[0]
    scripts = content_div.find_all("script")
    seasons = []
    for script in scripts:
        if "saison" in script.text or "film" in script.text:
            seasons = script.text.split("panneauAnime")[2:]
    if not seasons:
        return []
    for i in range(len(seasons)):
        seasons[i] = seasons[i].strip().split(",")[1].replace('"', "").strip()[:-2]
    return seasons


def get_ep_file(series, season):
    request = requests.get(f"https://{SITE}/{SEARCH_QUERY_BASE}/{series}/{season}/episodes.js")
    result = request.text.split("'")
    new_result = []
    for i in range(len(result)):
        result[i] = result[i].strip()
        if result[i].startswith("http") and "sibnet" in result[i]:
            new_result.append(result[i])
    return new_result


def get_anime_urls():
    urls = {}
    while True:
        anime = input("Enter the anime name [e - exit]: ")
        if anime == "e":
            break
        elif available(anime):
            seasons = get_seasons_link(anime)
            if seasons == []:
                print("No seasons found for this anime")
                continue
            print([f"{i + 1}. {season.split('/')[0]}" for i, season in enumerate(seasons)])
            choice = input("Enter the season number [a - all]: ")
            if choice.isdigit():
                choice = int(choice)
                if 1 <= choice <= len(seasons):
                    seasons = [f"{seasons[choice - 1]}"]
                else:
                    print("Invalid choice, please try again.")
                    continue
            urls[anime] = {}
            for s in seasons:
                season_vf = f"{s.split('/')[0]}/vf"
                if available(f"{anime}/{season_vf}"):
                    vf_ep = get_ep_file(anime, season_vf)
                    urls[anime][season_vf] = [get_location_from_embed(ep) for ep in vf_ep]
                else:
                    print("Season not available in VF")
                    if input("Do you want to download it in vostfr? [Y/n]").lower() != "n":
                        if available(f"{anime}/{s}"):
                            vostfr_ep = get_ep_file(anime, s)
                            urls[anime][season_vostfr] = [get_location_from_embed(ep) for ep in vostfr_ep]
        else:
            print("Anime not found, please try again.")
    return urls


def convert_files(anime, season, episode, index):
    print(f"Downloading {anime} {season} episode {index+1}")
    with open(f"{SAVE_DIR}/{anime}/{season}/{index+1}.mp4", 'wb') as f:
        c = pycurl.Curl()
        c.setopt(c.URL, episode)
        c.setopt(c.WRITEDATA, f)
        c.setopt(c.NOPROGRESS, False)
        c.setopt(c.XFERINFOFUNCTION, lambda dl_total, dl_now, *_: print(f"\rDownloading: {round(dl_now*100/dl_total, 2) if dl_total != 0 else "..."} %", end=""))
        c.setopt(c.VERBOSE, False)
        c.perform()
        c.close()


def get_all_anime():
    resp = requests.get("https://anime-sama.fr/catalogue/listing_all.php")
    resp = resp.text.lower()
    soup = BeautifulSoup(resp, PARSER)

    index = {}
    alias_index = {}
    anime = soup.find_all("div", {"class": ["anime", "anime,"]})
    for a in anime:
        real_title = a.find("h1").text
        link = a.find("a")["href"]
        index[real_title] = {
            "link": link,
            "img": a.find("img")["src"],
            "tags": [ tag.replace(",", "") for tag in a["class"] if "cardlistanime" not in tag and tag != "-" ],
            "slug": link.split("/")[-1] if not link.endswith("/") else link.split("/")[-2]
        }
        for alias in a.find("p").text.split(", "):
            alias_index[alias] = real_title
        alias_index[real_title.strip()] = real_title

    return index, alias_index


def get_info(anime):
    resp = requests.get(f"https://{SITE}/{SEARCH_QUERY_BASE}/{anime}")
    soup = BeautifulSoup(resp.text, PARSER)

    info = {}
    info["title"] = soup.find(id="titreOeuvre").text
    info["img"] = soup.find(id="coverOeuvre")["src"]
    info["alts"] = soup.find(id="titreAlter").text
    for title2 in soup.findAll('h2'):
        if title2.text.lower() == "synopsis":
            info["synopsis"] = title2.find_next("p").text
            break
    for title2 in soup.findAll('h2'):
        if title2.text.lower() == "genres":
            info["tags"] = title2.find_next("a").text
            break
    
    return info


def main():
    print("What anime do you want to convert?")
    list_anime_url = get_anime_urls()
    print(list_anime_url)

    chrono = time.time()
    for anime in list_anime_url:
        for season in list_anime_url[anime]:
            os.makedirs(f"{SAVE_DIR}/{anime}/{season}", exist_ok=True)
            for index, episode in enumerate(list_anime_url[anime][season]):
                convert_files(anime, season, episode, index)

    print(f"Convert time: {time.time() - chrono}")


if __name__ == "__main__":
    # anime-sama.fr/catalogue/listing_all.php
    print("Please wait while we fetch the anime list...")
    index, alias = get_all_anime()
    print("Done!")
    main(index, alias)