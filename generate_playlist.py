# playlist.py
import subprocess
import re

# Série poster (playlist cover)
poster_url = (
    "https://www.apple.com/br/tv-pr/shows-and-films/t/the-studio/images/"
    "season-01/show-home-graphic-header/key-art-01/4x1/"
    "Apple_TV_The_Studio_key_art_graphic_header_4_1_show_home.jpg.small_2x.jpg"
)

# URLs de Streamtape em ordem
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
episodes = []
for u in urls:
    m = pattern.search(u)
    if m:
        episodes.append((int(m.group(1)), u))
episodes.sort(key=lambda x: x[0])

# Cria playlist M3U na raiz (playlist.m3u)
with open("playlist.m3u", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    f.write("#EXTENC:UTF-8\n")
    f.write("#PLAYLIST:O Estúdio\n")
    f.write(f"#EXTIMG:{poster_url}\n")
    for num, u in episodes:
        res = subprocess.run(["yt-dlp", "-g", u], capture_output=True, text=True, check=True)
        url_direct = res.stdout.strip()
        f.write(
            f'#EXTINF:0 tvg-name="" audio-track="" tvg-logo="" '
            f'group-title="O Estúdio",S01E{num:02d}\n'
        )
        f.write(url_direct + "\n")
