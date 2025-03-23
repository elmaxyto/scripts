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
    # Esempio di mappa di corrispondenza
    "Canale1": "Canale Uno",
    "Canale2": "Canale Due"
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

def elimina_vecchi_gruppi(contenuto):
    """Rimuove le righe che iniziano con '#EXTGRP:' (uguale a elimina_gruppi)."""
    return elimina_gruppi(contenuto)

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
    """Aggiunge il campo group-title alle righe #EXTINF senza modificare il nome del canale."""
    nuove_linee = []
    for line in contenuto.splitlines():
        if line.startswith("#EXTINF:"):
            idx = line.find(",")
            if idx != -1:
                # Aggiungi il campo group-title senza modificare il nome del canale
                if "group-title=" not in line:
                    line = line[:idx] + f" group-title=\"{nome_gruppo}\"," + line[idx:]
                else:
                    line = line[:idx] + f"," + line[idx+1:]
        nuove_linee.append(line)
    return "\n".join(nuove_linee) + "\n"

def unisci_m3u(contenuto1, contenuto2):
    """Unisce due liste m3u."""
    return contenuto1 + contenuto2

def aggiungi_gruppo(contenuto, nome_gruppo):
    """Aggiunge un nuovo gruppo (in questo caso, è simile a aggiungi_group_title)."""
    return aggiungi_group_title(contenuto, nome_gruppo)

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
        
        # Non rimuovere i gruppi se non vuoi
        # contenuto_modificato = elimina_gruppi(contenuto_modificato)
        # contenuto_modificato = elimina_vecchi_gruppi(contenuto_modificato)
        contenuto_modificato = elimina_extm3u(contenuto_modificato)
        
        if i == 0:
            contenuto_modificato = aggiungi_group_title(contenuto_modificato, "TV Italiane")
        elif i == 1:
            contenuto_modificato = aggiungi_group_title(contenuto_modificato, "Rakuten TV")
        elif i == 2:
            contenuto_modificato = aggiungi_group_title(contenuto_modificato, "Pluto TV")
        
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
