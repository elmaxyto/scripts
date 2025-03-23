import os
import requests
import re

# URL delle liste m3u da scaricare
m3u_urls = [
    "https://raw.githubusercontent.com/Tundrak/IPTV-Italia/main/iptvitaplus.m3u",
    "https://raw.githubusercontent.com/pandvan/rakuten-m3u-generator/refs/heads/master/output/rakuten.m3u",
    "https://raw.githubusercontent.com/Brenders/Pluto-TV-Italia-M3U/main/PlutoItaly.m3u"
]

# URL dell'EPG
epg_url = "https://raw.githubusercontent.com/elmaxyto/epg-update/refs/heads/main/epg.xml"

# Mappa di corrispondenza tra il nome nella m3u e il nome corretto (EPG)
channel_mapping = {
    "Rai 1": "Rai1",
    "Rai 2": "Rai2",
    "Rai 3": "Rai3",
    "Rete 4": "Rete 4",
    "Canale 5": "Canale 5",
    "Italia 1": "Italia 1",
    "LA7": "LA7 HD",
    "TV8": "TV8 HD",
    "NOVE": "Nove",
    "20 Mediaset": "20",
    "Rai 4": "Rai4",
    "Iris": "Iris",
    "Rai 5": "Rai5",
    "Rai Movie": "RaiMovie",
    "Rai Premium": "RaiPremium",
    "Cielo": "cielo",
    "Twenty Seven": "27 Twentyseven",
    "TV2000": "TV2000",
    "LA7d": "LA7D",
    "La 5": "La 5",
    "Real Time": "Real Time",
    "QVC": "QVC",
    "Food Network": "Food Network",
    "Cine34": "Cine34",
    "FOCUS": "FOCUS",
    "RTL 102.5": "RTL 102.5 HD",
    "Warner TV": "Warner TV",
    "Giallo": "Giallo TV",
    "Top Crime": "Top Crime",
    "Boing": "Boing",
    "K2": "K2",
    "Rai Gulp": "RaiGulp",
    "Rai Yoyo": "RaiYoyo",
    "Frisbee": "-frisbee-",
    "Cartoonito": "Cartoonito",
    "Super!": "Super!",
    "Rai News 24": "RaiNews24",
    "Italia 2": "Italia 2",
    "Sky TG24": "Sky TG24",
    "TGCOM 24": "TgCom",
    "TGCom": "TgCom",
    # Corrispondenze mancanti
    "DMAX": "DMAX",
    "RaiStoria": "RaiStoria",
    "Mediaset Extra": "Mediaset Extra",
    "HGTV - Home&Garden": "HGTV",
    "Rai Scuola": "RaiScuola",
    "Rai Sport + HD": "RaiSport",
    "Motor Trend": "Motor Trend",
    "Sportitalia": "Sportitalia",
    "Donna TV": "Donna TV",
    "Supertennis": "SuperTennis HD",
    "ALMA TV": "Alma TV",
    "Radio 105 TV": "Radio 105 TV",
    "R101 TV": "R101tv",
    "BOM CHANNEL": "Bom Channel",
    "RadiolitaliaTV": "Radio Italia TV HD",
    "Rai 4K (HbbTV)": "Rai4K",
    "Padre Pio TV": "Padre Pio TV",
    "RADIO KISS KISS TV": "Radio Kiss Kiss TV",
    "Rai Radio 2 Visual": "Rai Radio 2 Visual",
    "RTL 102.5 News": "RTL 102.5 News",
    "VIRGIN RADIO": "Virgin Radio",
    "RADIOFRECCIA": "RADIOFRECCIA HD",
    "Byoblu": "Byoblu",
    "RDS Social TV": "RDS Social TV",
    "RADIO ZETA": "Radio Zeta",
    "Radio Capital TV": "Radio Capital TV",
}

def aggiorna_extinf_line(line, mapping):
    """Aggiorna il nome del canale in base alla mappa di corrispondenza."""
    for old_name, new_name in mapping.items():
        if old_name in line:
            line = line.replace(old_name, new_name)
    return line

def processa_m3u(contenuto, mapping):
    """Processa il contenuto della lista m3u aggiornando i nomi dei canali."""
    nuove_linee = []
    for line in contenuto.splitlines():
        if line.startswith("#EXTINF:"):
            line = aggiorna_extinf_line(line, mapping)
        nuove_linee.append(line)
    return "\n".join(nuove_linee) + "\n"

def elimina_gruppi(contenuto):
    """Rimuove le righe che iniziano con '#EXTGRP:'."""
    nuove_linee = []
    for line in contenuto.splitlines():
        if not line.startswith("#EXTGRP:"):
            nuove_linee.append(line)
    return "\n".join(nuove_linee) + "\n"

def elimina_extm3u(contenuto):
    """Rimuove le righe che iniziano con '#EXTM3U' tranne la prima."""
    nuove_linee = []
    extm3u_trovato = False
    for line in contenuto.splitlines():
        if line.startswith("#EXTM3U"):
            if not extm3u_trovato:
                nuove_linee.append(line)
                extm3u_trovato = True
        else:
            nuove_linee.append(line)
    return "\n".join(nuove_linee) + "\n"

def aggiungi_group_title(contenuto, nome_gruppo):
    """Sostituisce il campo group-title nelle righe #EXTINF con il nuovo valore."""
    nuove_linee = []
    for line in contenuto.splitlines():
        if line.startswith("#EXTINF:"):
            # Rimuovi qualsiasi group-title esistente
            if "group-title=" in line:
                line = re.sub(r'group-title="[^"]*"', f'group-title="{nome_gruppo}"', line)
            else:
                # Se non esiste, aggiungilo prima della virgola
                idx = line.find(",")
                if idx != -1:
                    line = line[:idx] + f' group-title="{nome_gruppo}"' + line[idx:]
        nuove_linee.append(line)
    return "\n".join(nuove_linee) + "\n"

def main():
    print("Current working directory:", os.getcwd())

    # Scarica le liste m3u dagli URL
    print("Scaricando le liste m3u...")
    contenuti = []
    for url in m3u_urls:
        try:
            response = requests.get(url)
            response.raise_for_status()
            contenuti.append(response.text)
        except requests.exceptions.RequestException as e:
            print(f"Errore nel download della lista m3u da {url}: {e}")
            continue

    # Processa il contenuto delle liste m3u
    contenuti_modificati = []
    for i, contenuto in enumerate(contenuti):
        contenuto_modificato = elimina_gruppi(contenuto)  # Rimuove i gruppi ereditati
        if i == 0:
            contenuto_modificato = processa_m3u(contenuto_modificato, channel_mapping)
            contenuto_modificato = aggiungi_group_title(contenuto_modificato, "TV Italiane")
        elif i == 1:
            contenuto_modificato = aggiungi_group_title(contenuto_modificato, "Rakuten TV")
        elif i == 2:
            contenuto_modificato = aggiungi_group_title(contenuto_modificato, "Pluto TV")
        
        contenuto_modificato = elimina_extm3u(contenuto_modificato)
        contenuti_modificati.append(contenuto_modificato)

    # Unisce le liste m3u
    contenuto_unito = ""
    for contenuto in contenuti_modificati:
        contenuto_unito += contenuto

    # Aggiungi la riga per l'EPG
    epg_line = "#EXTM3U url-tvg=\"{}\"\n".format(epg_url)
    contenuto_unito = epg_line + contenuto_unito

    # Salva il file unico
    output_file = "iptvitaplus.m3u"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(contenuto_unito)
        print(f"Il file m3u unificato è stato salvato in '{output_file}'.")

if __name__ == "__main__":
    main()
