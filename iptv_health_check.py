import requests
import re
import concurrent.futures
from datetime import datetime

# Configurazione
M3U_FILE = "iptvitaplus.m3u"
REPORT_FILE = "STATUS.md"
TIMEOUT = 10

def check_link(channel):
    """Controlla se un link è ancora attivo."""
    url = channel['url']
    headers = {"User-Agent": channel.get("ua", "Mozilla/5.0")}
    
    try:
        # Usiamo HEAD per velocità, o GET se HEAD non è supportato
        response = requests.get(url, headers=headers, timeout=TIMEOUT, stream=True)
        if response.status_code < 400:
            return True, "Online"
        elif response.status_code == 403:
            # Spesso i 403 sono geoblock, li consideriamo "probabilmente vivi"
            return True, "Geoblocked (Probabile OK)"
        else:
            return False, f"Errore {response.status_code}"
    except Exception as e:
        return False, f"Timeout/Connessione Fallita"

def parse_master_m3u():
    """Legge il file master e prepara i canali per il test."""
    channels = []
    current = None
    try:
        with open(M3U_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("#EXTINF:"):
                    name = line.split(",")[-1]
                    current = {"name": name, "ua": "Mozilla/5.0"}
                elif line.startswith("#EXTVLCOPT:http-user-agent="):
                    if current: current["ua"] = line.split("=")[1]
                elif line.startswith("http"):
                    if current:
                        current["url"] = line
                        channels.append(current)
                        current = None
    except FileNotFoundError:
        print("File m3u non trovato!")
    return channels

def main():
    print(f"🔍 Avvio Health Check IPTV - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    channels = parse_master_m3u()
    print(f"📊 Canali da testare: {len(channels)}")

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        future_to_ch = {executor.submit(check_link, ch): ch for ch in channels}
        for future in concurrent.futures.as_completed(future_to_ch):
            ch = future_to_ch[future]
            is_up, status = future.result()
            results.append({
                "name": ch["name"],
                "is_up": is_up,
                "status": status,
                "url": ch["url"]
            })

    # Generazione Report Markdown
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(f"# 🛰️ IPTV Health Report\n")
        f.write(f"Ultimo controllo: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`\n\n")
        
        f.write("## ❌ Canali da Riparare\n")
        down_count = 0
        for r in sorted(results, key=lambda x: x["name"]):
            if not r["is_up"]:
                f.write(f"- [ ] **{r['name']}** - `{r['status']}`\n")
                down_count += 1
        
        if down_count == 0:
            f.write("✅ Tutti i canali sono online!\n")
        
        f.write(f"\n---\n**Statistiche:** Totale: {len(results)} | Online: {len(results)-down_count} | Down: {down_count}\n")

    print(f"✅ Report generato in {REPORT_FILE}")

if __name__ == "__main__":
    main()
