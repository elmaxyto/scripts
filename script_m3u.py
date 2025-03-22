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
    # ... (la tua mappa di corrispondenza)
}

def aggiorna_extinf_line(line, mapping):
    # ... (la tua funzione per aggiornare le righe #EXTINF)

def processa_m3u(contenuto, mapping):
    # ... (la tua funzione per processare il contenuto m3u)

def elimina_gruppi(contenuto):
    # ... (la tua funzione per eliminare i gruppi esistenti)

def elimina_vecchi_gruppi(contenuto):
    # ... (la tua funzione per eliminare i vecchi gruppi)

def elimina_extm3u(contenuto):
    # ... (la tua funzione per rimuovere le righe #EXTM3U non necessarie)

def aggiungi_group_title(contenuto, nome_gruppo):
    """Aggiunge il campo group-title alle righe #EXTINF."""
    nuove_linee = []
    for line in contenuto.splitlines():
        if line.startswith("#EXTINF:"):
            idx = line.find(",")
            if idx != -1:
                line = line[:idx] + f" group-title=\"{nome_gruppo}\"," + line[idx+1:]
        nuove_linee.append(line)
    return "\n".join(nuove_linee) + "\n"

def unisci_m3u(contenuto1, contenuto2):
    # ... (la tua funzione per unire due liste m3u)

def aggiungi_gruppo(contenuto, nome_gruppo):
    # ... (la tua funzione per aggiungere un nuovo gruppo)

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
