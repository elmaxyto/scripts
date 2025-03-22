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
    """
    Aggiorna la riga #EXTINF: sostituendo il nome del canale (che si trova dopo l'ultima virgola)
    se presente nella mappa. Viene usato .strip() per rimuovere spazi extra e non viene aggiunto
    spazio extra dopo la virgola.
    """
    try:
        idx = line.rindex(",")
        old_name = line[idx+1:].strip()  # Pulisce il nome da spazi extra
        # Cerca una corrispondenza parziale per "TGCOM 24"
        if re.search(r"TGCOM\s*24", old_name, re.IGNORECASE):
            new_name = "TgCom"
        else:
            new_name = mapping.get(old_name, old_name)
        return line[:idx+1] + new_name
    except ValueError:
        return line

def processa_m3u(contenuto, mapping):
    """
    Processa il contenuto del file m3u linea per linea, aggiornando le righe #EXTINF.
    """
    nuove_linee = []
    for line in contenuto.splitlines():
        if line.startswith("#EXTINF:"):
            nuove_linee.append(aggiorna_extinf_line(line, mapping) + "\n")
        else:
            nuove_linee.append(line + "\n")
    return "".join(nuove_linee)

def elimina_gruppi(contenuto):
    """Elimina i gruppi esistenti dai canali."""
    nuove_linee = []
    for line in contenuto.splitlines():
        if line.startswith("#EXTGRP:"):
            continue
        if line.startswith("#EXTINF:"):
            idx = line.find(",")
            if idx != -1:
                nome_canale = line[idx+1:].strip()
                # Rimuovi eventuali gruppi
                if "-" in nome_canale:
                    nome_canale = nome_canale.split("-")[-1].strip()
                line = line[:idx+1] + nome_canale
        nuove_linee.append(line)
    return "\n".join(nuove_linee) + "\n"

def elimina_vecchi_gruppi(contenuto):
    """Elimina i vecchi gruppi dalle righe #EXTINF."""
    nuove_linee = []
    for line in contenuto.splitlines():
        if line.startswith("#EXTINF:"):
            idx = line.find("group-title=")
            if idx != -1:
                idx_end = line.find(",", idx)
                if idx_end == -1:
                    idx_end = len(line)
                line = line[:idx] + line[idx_end:]
        nuove_linee.append(line)
    return "\n".join(nuove_linee) + "\n"

def elimina_extm3u(contenuto):
    """Rimuove le righe #EXTM3U non necessarie."""
    nuove_linee = []
    for line in contenuto.splitlines():
        if line == "#EXTM3U":
            continue
        nuove_linee.append(line)
    return "\n".join(nuove_linee) + "\n"

def aggiungi_group_title(contenuto, nome_gruppo):
    """Aggiunge il campo group-title alle righe #EXTINF."""
    nuove_linee = []
    for line in contenuto.splitlines():
        if line.startswith("#EXTINF:"):
            idx = line.find(",")
            if idx != -1:
                line = line[:idx] + f" group-title=\"{nome_gruppo}\"," + line[idx:]
        nuove_linee.append(line)
    return "\n".join(nuove_linee) + "\n"

def unisci_m3u(contenuto1, contenuto2):
    """Unisce due liste m3u mantenendo l'ordine originale."""
    nuove_linee = contenuto1.splitlines()
    for line in contenuto2.splitlines():
        if line.startswith("#EXTINF:"):
            nuove_linee.append(line)
        else:
            nuove_linee.append(line)
    return "\n".join(nuove_linee) + "\n"

def aggiungi_gruppo(contenuto, nome_gruppo):
    """Aggiunge un nuovo gruppo ai canali."""
    gruppo_line = f"#EXTGRP:{nome_gruppo}\n"
    return gruppo_line + contenuto

def main():
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
        if i == 0:  # Solo per la prima lista
            contenuto_modificato = processa_m3u(contenuto, channel_mapping)
        else:
            contenuto_modificato = contenuto  # Lascia invariati gli altri
        
        contenuto_modificato = elimina_gruppi(contenuto_modificato)
        contenuto_modificato = elimina_vecchi_gruppi(contenuto_modificato)
        contenuto_modificato = elimina_extm3u(contenuto_modificato)
        
        if i == 0:
            contenuto_modificato = aggiungi_group_title(contenuto_modificato, "TV Italiane")
        elif i == 1:
            contenuto_modificato = aggiungi_group_title(contenuto_modificato, "Rakuten TV")
        elif i == 2:
            contenuto_modificato = aggiungi_group_title(contenuto_modificato, "Pluto TV")
        
        contenuti_modificati.append(contenuto_modificato)

    # Aggiungi nuovi gruppi
    contenuto_tv_italiane = aggiungi_gruppo(contenuti_modificati[0], "TV Italiane")
    contenuto_rakuten_tv = aggiungi_gruppo(contenuti_modificati[1], "Rakuten TV")
    contenuto_pluto_tv = aggiungi_gruppo(contenuti_modificati[2], "Pluto TV")

    # Unisce le liste m3u
    contenuto_unito = contenuto_tv_italiane + contenuto_rakuten_tv + contenuto_pluto_tv

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
