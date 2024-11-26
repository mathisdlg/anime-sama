from django.shortcuts import render, redirect
from anime_sama_app.converter.scraper import get_all_anime, available, get_seasons_link, get_info

# Create your views here.

def index(request):
    animes_index, alias_index = get_all_anime()

    if request.method == "GET":
        search = request.GET.get("search")
        if search:
            new_animes_index = {}
            for alias, anime in alias_index.items():
                if search in alias:
                    real_name = anime
                    if real_name not in new_animes_index:
                        new_animes_index[real_name] = animes_index[real_name]
            animes_index = new_animes_index
    return render(request, "index.html", {"animes": animes_index, "alias": alias_index})

def details(request, anime):
    if available(anime):
        info = get_info(anime)
        seasons = []
        for season in get_seasons_link(anime):
            season_vf = f"{season.split('/')[0]}/vf"
            seasons.append(season)
            if available(f"{anime}/{season_vf}"):
                seasons.append(season_vf)
        return render(request, "details.html", {"seasons": seasons, "info": info})
    else:
        return redirect("index")