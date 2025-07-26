# playlist.py
import os
import json
import time
import re
import subprocess
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

OUTPUT_FILE = "playlist.m3u"
COOKIES_FILE = "cookies.txt"

# --- Cookies do GitHub Secrets ---
raw = os.environ.get("VISIONCINE_COOKIES", "")
with open(COOKIES_FILE, "w") as f:
    f.write(raw.strip())

# --- Sessão requests com cookies e headers padrão ---
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0",
    "Referer": "http://www.playcinevs.info/"
})
session.verify = False
with open(COOKIES_FILE, "r") as f:
    for line in f:
        if not line.strip().startswith("#") and "\t" in line:
            parts = line.strip().split("\t")
            if len(parts) >= 7:
                session.cookies.set(parts[5], parts[6])

# --- Lista de episódios ---
EPISODES = [
    ("S01E01", "http://www.playcinevs.info/s/116734"),
    ("S01E02", "http://www.playcinevs.info/s/116735"),
    ("S01E03", "http://www.playcinevs.info/s/116736"),
    ("S01E04", "http://www.playcinevs.info/s/116737"),
    ("S01E05", "http://www.playcinevs.info/s/116738"),
    ("S01E06", "http://www.playcinevs.info/s/116739"),
    ("S01E07", "http://www.playcinevs.info/s/116740"),
    ("S01E08", "http://www.playcinevs.info/s/116741"),
    ("S01E09", "http://www.playcinevs.info/s/116742"),
    ("S01E10", "http://www.playcinevs.info/s/116743"),
    ("S01E11", "http://www.playcinevs.info/s/116744"),
    ("S01E12", "http://www.playcinevs.info/s/116745"),
    ("S01E13", "http://www.playcinevs.info/s/116746"),
    ("S01E14", "http://www.playcinevs.info/s/116747"),
    ("S01E15", "http://www.playcinevs.info/s/116748"),
    ("S01E16", "http://www.playcinevs.info/s/116749"),
    ("S01E17", "http://www.playcinevs.info/s/116750"),
    ("S01E18", "http://www.playcinevs.info/s/116751"),
    ("S01E19", "http://www.playcinevs.info/s/116752"),
    ("S01E20", "http://www.playcinevs.info/s/116753"),
    ("S01E21", "http://www.playcinevs.info/s/116754"),
    ("S01E22", "http://www.playcinevs.info/s/116755"),

    ("S02E01", "http://www.playcinevs.info/s/116756"),
    ("S02E02", "http://www.playcinevs.info/s/116757"),
    ("S02E03", "http://www.playcinevs.info/s/116758"),
    ("S02E04", "http://www.playcinevs.info/s/116759"),
    ("S02E05", "http://www.playcinevs.info/s/116760"),
    ("S02E06", "http://www.playcinevs.info/s/116761"),
    ("S02E07", "http://www.playcinevs.info/s/116762"),
    ("S02E08", "http://www.playcinevs.info/s/116763"),
    ("S02E09", "http://www.playcinevs.info/s/116764"),
    ("S02E10", "http://www.playcinevs.info/s/116765"),
    ("S02E11", "http://www.playcinevs.info/s/116766"),
    ("S02E12", "http://www.playcinevs.info/s/116767"),
    ("S02E13", "http://www.playcinevs.info/s/116768"),
    ("S02E14", "http://www.playcinevs.info/s/116769"),
    ("S02E15", "http://www.playcinevs.info/s/116770"),
    ("S02E16", "http://www.playcinevs.info/s/116771"),
    ("S02E17", "http://www.playcinevs.info/s/116772"),
    ("S02E18", "http://www.playcinevs.info/s/116773"),
    ("S02E19", "http://www.playcinevs.info/s/116774"),
    ("S02E20", "http://www.playcinevs.info/s/116775"),
    ("S02E21", "http://www.playcinevs.info/s/116776"),
    ("S02E22", "http://www.playcinevs.info/s/116777"),

    ("S03E01", "http://www.playcinevs.info/s/116778"),
    ("S03E02", "http://www.playcinevs.info/s/116779"),
    ("S03E03", "http://www.playcinevs.info/s/116780"),
    ("S03E04", "http://www.playcinevs.info/s/116781"),
    ("S03E05", "http://www.playcinevs.info/s/116782"),
    ("S03E06", "http://www.playcinevs.info/s/116783"),
    ("S03E07", "http://www.playcinevs.info/s/116784"),
    ("S03E08", "http://www.playcinevs.info/s/116785"),
    ("S03E09", "http://www.playcinevs.info/s/116786"),
    ("S03E10", "http://www.playcinevs.info/s/116787"),
    ("S03E11", "http://www.playcinevs.info/s/116788"),
    ("S03E12", "http://www.playcinevs.info/s/116789"),
    ("S03E13", "http://www.playcinevs.info/s/116790"),
    ("S03E14", "http://www.playcinevs.info/s/116791"),
    ("S03E15", "http://www.playcinevs.info/s/116792"),
    ("S03E16", "http://www.playcinevs.info/s/116793"),
    ("S03E17", "http://www.playcinevs.info/s/116794"),
    ("S03E18", "http://www.playcinevs.info/s/116795"),
    ("S03E19", "http://www.playcinevs.info/s/116796"),
    ("S03E20", "http://www.playcinevs.info/s/116797"),

    ("S04E01", "http://www.playcinevs.info/s/116798"),
    ("S04E02", "http://www.playcinevs.info/s/116799"),
    ("S04E03", "http://www.playcinevs.info/s/116800"),
    ("S04E04", "http://www.playcinevs.info/s/116801"),
    ("S04E05", "http://www.playcinevs.info/s/116802"),
    ("S04E06", "http://www.playcinevs.info/s/116803"),
    ("S04E07", "http://www.playcinevs.info/s/116804"),
    ("S04E08", "http://www.playcinevs.info/s/116805"),
    ("S04E09", "http://www.playcinevs.info/s/116806"),
    ("S04E10", "http://www.playcinevs.info/s/116807"),
    ("S04E11", "http://www.playcinevs.info/s/116808"),
    ("S04E12", "http://www.playcinevs.info/s/116809"),
    ("S04E13", "http://www.playcinevs.info/s/116810"),
    ("S04E14", "http://www.playcinevs.info/s/116811"),
    ("S04E15", "http://www.playcinevs.info/s/116812"),
    ("S04E16", "http://www.playcinevs.info/s/116813"),
    ("S04E17", "http://www.playcinevs.info/s/116814"),
    ("S04E18", "http://www.playcinevs.info/s/116815"),
    ("S04E19", "http://www.playcinevs.info/s/116816"),
    ("S04E20", "http://www.playcinevs.info/s/116817"),
    ("S04E21", "http://www.playcinevs.info/s/116818"),
    ("S04E22", "http://www.playcinevs.info/s/116819"),
    ("S04E23", "http://www.playcinevs.info/s/116820"),
    ("S04E24", "http://www.playcinevs.info/s/116821"),

    ("S05E01", "http://www.playcinevs.info/s/116822"),
    ("S05E02", "http://www.playcinevs.info/s/116823"),
    ("S05E03", "http://www.playcinevs.info/s/116824"),
    ("S05E04", "http://www.playcinevs.info/s/116825"),
    ("S05E05", "http://www.playcinevs.info/s/116826"),
    ("S05E06", "http://www.playcinevs.info/s/116827"),
    ("S05E07", "http://www.playcinevs.info/s/116828"),
    ("S05E08", "http://www.playcinevs.info/s/116829"),
    ("S05E09", "http://www.playcinevs.info/s/116830"),
    ("S05E10", "http://www.playcinevs.info/s/116831"),
    ("S05E11", "http://www.playcinevs.info/s/116832"),
    ("S05E12", "http://www.playcinevs.info/s/116833"),
    ("S05E13", "http://www.playcinevs.info/s/116834"),
    ("S05E14", "http://www.playcinevs.info/s/116835"),
    ("S05E15", "http://www.playcinevs.info/s/116836"),
    ("S05E16", "http://www.playcinevs.info/s/116837"),
    ("S05E17", "http://www.playcinevs.info/s/116838"),
    ("S05E18", "http://www.playcinevs.info/s/116839"),
    ("S05E19", "http://www.playcinevs.info/s/116840"),
    ("S05E20", "http://www.playcinevs.info/s/116841"),
    ("S05E21", "http://www.playcinevs.info/s/116842"),
    ("S05E22", "http://www.playcinevs.info/s/116843"),
    ("S05E23", "http://www.playcinevs.info/s/116844"),
    ("S05E24", "http://www.playcinevs.info/s/116845"),

    ("S06E01", "http://www.playcinevs.info/s/175497"),
    ("S06E02", "http://www.playcinevs.info/s/175498"),
    ("S06E03", "http://www.playcinevs.info/s/175499"),
    ("S06E04", "http://www.playcinevs.info/s/175500"),
    ("S06E05", "http://www.playcinevs.info/s/175501"),
    ("S06E06", "http://www.playcinevs.info/s/175502"),
    ("S06E07", "http://www.playcinevs.info/s/175503"),
    ("S06E08", "http://www.playcinevs.info/s/175504"),
    ("S06E09", "http://www.playcinevs.info/s/175505"),
    ("S06E10", "http://www.playcinevs.info/s/175506"),
    ("S06E11", "http://www.playcinevs.info/s/175507"),
    ("S06E12", "http://www.playcinevs.info/s/175508"),
    ("S06E13", "http://www.playcinevs.info/s/175509"),
    ("S06E14", "http://www.playcinevs.info/s/175510"),
    ("S06E15", "http://www.playcinevs.info/s/175511"),
    ("S06E16", "http://www.playcinevs.info/s/175512"),
    ("S06E17", "http://www.playcinevs.info/s/175513"),
    ("S06E18", "http://www.playcinevs.info/s/175514"),
    ("S06E19", "http://www.playcinevs.info/s/175515"),
    ("S06E20", "http://www.playcinevs.info/s/175516"),
    ("S06E21", "http://www.playcinevs.info/s/175517"),
    ("S06E22", "http://www.playcinevs.info/s/175518"),
    ("S06E23", "http://www.playcinevs.info/s/175519"),
    ("S06E24", "http://www.playcinevs.info/s/175520"),

    ("S07E01", "http://www.playcinevs.info/s/175521"),
    ("S07E02", "http://www.playcinevs.info/s/175522"),
    ("S07E03", "http://www.playcinevs.info/s/175523"),
    ("S07E04", "http://www.playcinevs.info/s/175524"),
    ("S07E05", "http://www.playcinevs.info/s/175525"),
    ("S07E06", "http://www.playcinevs.info/s/175526"),
    ("S07E07", "http://www.playcinevs.info/s/175527"),
    ("S07E08", "http://www.playcinevs.info/s/175528"),
    ("S07E09", "http://www.playcinevs.info/s/175529"),
    ("S07E10", "http://www.playcinevs.info/s/175530"),
    ("S07E11", "http://www.playcinevs.info/s/175531"),
    ("S07E12", "http://www.playcinevs.info/s/175532"),
    ("S07E13", "http://www.playcinevs.info/s/175533"),
    ("S07E14", "http://www.playcinevs.info/s/175534"),
    ("S07E15", "http://www.playcinevs.info/s/175535"),
    ("S07E16", "http://www.playcinevs.info/s/175536"),
    ("S07E17", "http://www.playcinevs.info/s/175537"),
    ("S07E18", "http://www.playcinevs.info/s/175538"),
    ("S07E19", "http://www.playcinevs.info/s/175539"),
    ("S07E20", "http://www.playcinevs.info/s/175540"),
    ("S07E21", "http://www.playcinevs.info/s/175541"),
    ("S07E22", "http://www.playcinevs.info/s/175542"),
    ("S07E23", "http://www.playcinevs.info/s/175543"),
    ("S07E24", "http://www.playcinevs.info/s/175544"),

    ("S08E01", "http://www.playcinevs.info/s/116846"),
    ("S08E02", "http://www.playcinevs.info/s/116847"),
    ("S08E03", "http://www.playcinevs.info/s/116848"),
    ("S08E04", "http://www.playcinevs.info/s/116849"),
    ("S08E05", "http://www.playcinevs.info/s/116850"),
    ("S08E06", "http://www.playcinevs.info/s/116851"),
    ("S08E07", "http://www.playcinevs.info/s/116852"),
    ("S08E08", "http://www.playcinevs.info/s/116853"),
    ("S08E09", "http://www.playcinevs.info/s/116854"),
    ("S08E10", "http://www.playcinevs.info/s/116855"),
    ("S08E11", "http://www.playcinevs.info/s/116856"),
    ("S08E12", "http://www.playcinevs.info/s/116857"),
    ("S08E13", "http://www.playcinevs.info/s/116858"),
    ("S08E14", "http://www.playcinevs.info/s/116859"),
    ("S08E15", "http://www.playcinevs.info/s/116860"),
    ("S08E16", "http://www.playcinevs.info/s/116861"),
    ("S08E17", "http://www.playcinevs.info/s/116862"),
    ("S08E18", "http://www.playcinevs.info/s/116863"),
    ("S08E19", "http://www.playcinevs.info/s/116864"),
    ("S08E20", "http://www.playcinevs.info/s/116865"),
    ("S08E21", "http://www.playcinevs.info/s/116866"),
    ("S08E22", "http://www.playcinevs.info/s/116867"),
    ("S08E23", "http://www.playcinevs.info/s/116868"),
    ("S08E24", "http://www.playcinevs.info/s/116869"),

    ("S09E01", "http://www.playcinevs.info/s/175545"),
    ("S09E02", "http://www.playcinevs.info/s/175546"),
    ("S09E03", "http://www.playcinevs.info/s/175547"),
    ("S09E04", "http://www.playcinevs.info/s/175548"),
    ("S09E05", "http://www.playcinevs.info/s/175549"),
    ("S09E06", "http://www.playcinevs.info/s/175550"),
    ("S09E07", "http://www.playcinevs.info/s/175551"),
    ("S09E08", "http://www.playcinevs.info/s/175552"),
    ("S09E09", "http://www.playcinevs.info/s/175553"),
    ("S09E10", "http://www.playcinevs.info/s/175554"),
    ("S09E11", "http://www.playcinevs.info/s/175555"),
    ("S09E12", "http://www.playcinevs.info/s/175556"),
    ("S09E13", "http://www.playcinevs.info/s/175557"),
    ("S09E14", "http://www.playcinevs.info/s/175558"),
    ("S09E15", "http://www.playcinevs.info/s/175559"),
    ("S09E16", "http://www.playcinevs.info/s/175560"),
    ("S09E17", "http://www.playcinevs.info/s/175561"),
    ("S09E18", "http://www.playcinevs.info/s/175562"),
    ("S09E19", "http://www.playcinevs.info/s/175563"),
    ("S09E20", "http://www.playcinevs.info/s/175564"),
    ("S09E21", "http://www.playcinevs.info/s/175565"),
    ("S09E22", "http://www.playcinevs.info/s/175566"),
    ("S09E23", "http://www.playcinevs.info/s/175567"),
    ("S09E24", "http://www.playcinevs.info/s/175568"),
]

# --- yt-dlp extractor ---
def extract_with_ytdlp(label, page_url):
    try:
        result = subprocess.check_output([
            "yt-dlp",
            "--cookies", COOKIES_FILE,
            "--skip-download",
            "--no-warnings",
            "--print-json",
            page_url
        ], stderr=subprocess.DEVNULL, timeout=15)

        data = json.loads(result)
        return (label, data["url"])
    except Exception:
        return None

# --- Regex fallback extractor ---
def extract_with_regex(label, page_url):
    try:
        resp = session.get(page_url, timeout=10)
        html = resp.text
        m = re.search(r"initializePlayer\(['\"](https?://[^'\"]+)['\"]", html)
        if m:
            return (label, m.group(1))
        m2 = re.search(r'<video[^>]+src=["\']([^"\']+)["\']', html)
        if m2:
            return (label, m2.group(1))
        return (label, None)
    except Exception as e:
        return (label, None)

# --- Main ---
def main():
    print(f"Iniciando extração de {len(EPISODES)} episódios com yt-dlp + fallback...")

    start = time.time()
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {}
        for label, url in EPISODES:
            futures[executor.submit(extract_with_ytdlp, label, url)] = (label, url)

        with open(OUTPUT_FILE, "w") as f:
            f.write("#EXTM3U\n")

            for future in as_completed(futures):
                label, url = futures[future]
                result = future.result()

                if result:
                    f.write(f"#EXTINF:-1,{label}\n{result[1]}\n")
                    print(f"[✓] OK {label} (yt-dlp)")
                else:
                    label, final_url = extract_with_regex(label, url)
                    if final_url:
                        f.write(f"#EXTINF:-1,{label}\n{final_url}\n")
                        print(f"[✓] OK {label} (regex)")
                    else:
                        print(f"[x] ERRO {label}: nada extraído")

    print(f"Concluído em {time.time() - start:.1f}s")

if __name__ == "__main__":
    main()
