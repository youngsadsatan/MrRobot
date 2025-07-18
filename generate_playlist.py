# generate_playlist.py
import subprocess
import re

# Lista de URLs Streamtape
urls = [
    "https://streamtape.com/v/q9YKVpYJg4T1YB/O.Estudio.S01E03.mkv",
    "https://streamtape.com/v/1Wwd2mz9p1FbqM/O.Estudio.S01E02.mkv",
    "https://streamtape.com/v/lP2VOeJ4JPUdLo/O.Estudio.S01E05.mkv",
    "https://streamtape.com/v/LLWRxkDDd8CRRV0/O.Estudio.S01E04.mkv",
    "https://streamtape.com/v/j6LBmKO9kofLpz/O.Estudio.S01E01.mkv",
    "https://streamtape.com/v/XPxMR2XjZPtDQmp/O.Estudio.S01E08.mkv",
    "https://streamtape.com/v/jaBQp89vOOCzRKg/O.Estudio.S01E10.mkv",
    "https://streamtape.com/v/R9JJ7PBR3PudlXG/O.Estudio.S01E07.mkv",
    "https://streamtape.com/v/A2zxvY7eOwUZmd/O.Estudio.S01E06.mkv",
    "https://streamtape.com/v/vk37MqjzDGc4Xpl/O.Estudio.S01E09.mkv"
]

# Extrair número do episódio e ordenar
pattern = re.compile(r"\.S01E(\d{2})")
episodes = []
for u in urls:
    m = pattern.search(u)
    if m:
        num = int(m.group(1))
        episodes.append((num, u))
episodes.sort(key=lambda x: x[0])

# Gera playlist m3u em docs/
with open("docs/O_Estudio_S01_playlist.m3u", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    for num, u in episodes:
        # yt-dlp -g retorna a URL de streaming
        res = subprocess.run(["yt-dlp", "-g", u], capture_output=True, text=True, check=True)
        stream_url = res.stdout.strip()
        f.write(f"#EXTINF:-1,O Estúdio S01E{num:02d}\n")
        f.write(stream_url + "\n")
