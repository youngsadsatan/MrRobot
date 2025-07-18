# playlist.py
import re
from yt_dlp import YoutubeDL

# Série poster (header cover)
poster_url = (
    "https://www.apple.com/br/tv-pr/shows-and-films/t/the-studio/images/"
    "season-01/show-home-graphic-header/key-art-01/4x1/"
    "Apple_TV_The_Studio_key_art_graphic_header_4_1_show_home.jpg.small_2x.jpg"
)

# URLs de Streamtape (E01 a E10)
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

# Configuração do YTDLP
ydl_opts = {
    'quiet': True,
    'skip_download': True,
    'nocheckcertificate': True,
    'extract_flat': False,
    'format': 'best',
}

with open("playlist.m3u", "w", encoding="utf-8") as f:
    # Header Extended M3U
    f.write("#EXTM3U\n")
    f.write("#EXTENC:UTF-8\n")
    f.write("#PLAYLIST:O Estúdio\n")
    f.write(f"#EXTIMG:{poster_url}\n")

    with YoutubeDL(ydl_opts) as ydl:
        for num, page_url in episodes:
            try:
                info = ydl.extract_info(page_url, download=False)
            except Exception as e:
                print(f"Erro YTDLP em {page_url}: {e}")
                continue

            # pega a URL direta
            stream_url = info.get('url') or (info.get('formats') and info['formats'][0].get('url'))
            if not stream_url:
                print(f"Não encontrou stream em {page_url}")
                continue

            # adiciona dl=1
            if 'dl=1' not in stream_url:
                sep = '&' if '?' in stream_url else '?'
                stream_url += sep + 'dl=1'

            f.write(f"#EXTINF:0,O Estúdio S01E{num:02d}\n")
            f.write(stream_url + "\n")
