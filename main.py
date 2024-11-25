from bs4 import BeautifulSoup
import os, requests, time, re, pycurl
from sibnet import get_location_from_embed
from const import PARSER, SITE, SEARCH_QUERY_BASE, SAVE_DIR

def check_availability(series):
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
        elif check_availability(anime):
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
                if check_availability(f"{anime}/{season_vf}"):
                    vf_ep = get_ep_file(anime, season_vf)
                    urls[anime][season_vf] = [get_location_from_embed(ep) for ep in vf_ep]
                else:
                    print("Season not available in VF")
                    if input("Do you want to download it in vostfr? [Y/n]").lower() != "n":
                        if check_availability(f"{anime}/{s}"):
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
        c.setopt(c.XFERINFOFUNCTION, lambda dl_total, dl_now, *args: print(f"\rDownloading: {round(dl_now*100/dl_total, 2) if dl_total != 0 else "..."} %", end=""))
        c.setopt(c.VERBOSE, False)
        c.perform()
        c.close()


def main():
    print("Hello world! What anime do you want to convert?")
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
    main()