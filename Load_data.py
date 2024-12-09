import os
import requests
import pandas as pd
from tqdm import tqdm

# Fonction de téléchargement depuis une URL
def download_data(local_path, url):
    """
    Télécharge un fichier depuis une URL et le sauvegarde localement.
    """
    # Créer le dossier si nécessaire
    dir_path = os.path.dirname(local_path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    
    # Vérifier si le fichier existe déjà
    if os.path.exists(local_path):
        print(f"Les données sont déjà téléchargées : {local_path}")
        return

    # Télécharger depuis une URL
    print("Téléchargement depuis l'URL...")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Barre de progression
        total_size = int(response.headers.get('content-length', 0))
        with open(local_path, 'wb') as f, tqdm(
            desc=f"Téléchargement {os.path.basename(local_path)}",
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(chunk_size=1024):
                f.write(data)
                bar.update(len(data))
        print(f"Téléchargement effectué avec succès : {local_path}")
    except requests.RequestException as e:
        print(f"Erreur lors du téléchargement depuis l'URL : {e}")


# Télécharger et lire les fichiers CSV
download_data(
    local_path="data/acces_libre.csv",
    url="https://www.data.gouv.fr/fr/datasets/accessibilite-des-etablissements-recevant-du-public-erp-pour-les-personnes-en-situation-de-handicap/#/resources/5b0f44f2-e6ea-4a58-874d-6fe364b40342"
)
download_data(
    local_path="data/classement_hotels.csv",
    url="https://minio.lab.sspcloud.fr/inesh/hackathon-tourisme/export%20hotels.csv"
)
