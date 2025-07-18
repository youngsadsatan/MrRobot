# playlist.py
import requests
from bs4 import BeautifulSoup
import re

# Série poster (header cover)
poster_url = (
    "https://www.apple.com/br/tv-pr/shows-and-films/t/the-studio/images/"
    "season-01/show-home-graphic-header/key-art-01/4x1/"
    "Apple_TV_The_Studio_key_art_graphic_header_4_1_show_home.jpg.small_2x.jpg"
)

# URLs de Streamtape em ordem de E01 a E10
urls = [
    "https://streamtape.com/v/j6LBmKO9kofLpz/O.Estudio.S01E01.mkv",
    "https://streamtape.com/v/1Wwd2mz9p1FbqM/O.Estudio.S01E02.mkv",
    "https://streamtape.com/v/q9YKVpYJg4T1YB/O.Estudio.S01E03.mkv",
    "https://streamtape.com/v/LLWRxkDDd8CRRV0/O.Estudio.S01E04.mkv",
    "https://streamtape.com/v/lP2VOeJ4JPUdLo/O.Estudio.S01E05.mkv",
    "https://streamtape.com/v/A2zxvY7eOwUZmd/O.Estudio.S01E06.mkv",
    "https://streamtape.com/v/R9JJ7PBR3PudlXG/O.Estudio.S01E07.mkv",
    "https://streamtape.com/v/XPxMR2XjZPtDQmp/O.Estudio.S01E08.mkv",
    "https://streamtape.com/v/vk37MqjzDGc4Xpl/O.Estudio.S01E09.mkv",
    "https://streamtape.com/v/jaBQp89vOOCzRKg/O.Estudio.S01E10.mkv",
]

pattern = re.compile(r"\.S01E(\d{2})")
episodes = [(int(pattern.search(u).group(1)), u) for u in urls if pattern.search(u)]
episodes.sort(key=lambda x: x[0])

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

with open("playlist.m3u", "w", encoding="utf-8") as f:
    # Header Extended M3U
    f.write("#EXTM3U\n")
    f.write("#EXTENC:UTF-8\n")
    f.write("#PLAYLIST:O Estúdio\n")
    f.write(f"#EXTIMG:{poster_url}\n")

    for num, page_url in episodes:
        # Carrega página e extrai link via norobotlink
        resp = requests.get(page_url, headers=headers)
        soup = BeautifulSoup(resp.text, "html.parser")
        link_tag = soup.find(id="norobotlink") or soup.find(id="captchalink")
        if not link_tag:
            print(f"Erro: não encontrou link em {page_url}")
            continue
        src = link_tag.get_text().strip()

        # Normaliza URL
        if src.startswith("//"):
            src = "https:" + src
        elif src.startswith("/"):
            src = "https://streamtape.com" + src
        elif not src.startswith("http"):
            src = "https://" + src

        # Adiciona dl=1 se não existir
        if "dl=1" not in src:
            if "?" in src:
                src += "&dl=1"
            else:
                src += "?dl=1"

        # Resolve redirect para pegar o domínio tapecontent.net
        try:
            head = requests.head(src, headers=headers, allow_redirects=False)
            location = head.headers.get("Location")
            final_url = location if location else src
        except requests.RequestException:
            final_url = src

        # Escreve o episódio
        f.write(f"#EXTINF:0,O Estúdio S01E{num:02d}\n")
        f.write(final_url + "\n")
