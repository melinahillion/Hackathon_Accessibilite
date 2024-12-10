library(tidyverse)
library(data.table)
library(jsonlite)

liste_commune_blois <- c("Averdon","Blois","Candé-sur-Beuvron","Cellettes","Chailles","Chambon-sur-Cisse",
                         "Champigny-en-Beauce","Chaumont-sur-Loire","Cheverny","Chitenay","Chouzy-sur-Cisse",
                         "Cormeray","Coulanges","Cour-Cheverny","Fossé","Francay","Herbault","La Chapelle-Vendômoise",
                         "La Chaussée Saint-Victor","Lancôme","Landes-le-Gaulois","Les Montils","Marolles","Ménars",
                         "Mesland","Molineuf","Monteaux","Monthou-sur-Bièvre","Onzain","Orchaise","Rilly-sur-Loire",
                         "Saint-Bohaire","Saint-Cyr-du-Gault","Saint-Denis-sur-Loire","Saint-Étienne-des-Guérets","Saint-Gervais-la-Forêt",
                         "Saint-Lubin-en-Vergonnois","Saint-Sulpice-de-Pommeray","Sambin","Seillac","Seur",
                         "Valaire","Valencisse","Valloire-sur-Cisse","Veuves","Veuzain-sur-Loire","Villebarou",
                         "Villefrancœur","Villerbon","Vineuil","Santenay")


#### Base accès libre centré sur l'agglomération de Blois

df_acceslibre <- data.table::fread("../data/input/acceslibre-with-web-url.csv")

df_clean <- df_acceslibre |>
  filter(commune %in% liste_commune_blois)

extract_1 <- df_clean |> select(name,postal_code,commune,numero,voie,lieu_dit,activite,contact_url,site_internet,latitude,longitude)

json_1 <- toJSON(extract_1)

write(json_1, "../data/output/acceslibre_agglo_blois.json")

#### Base Tourisme et Handicap centré sur l'agglomération de Blois

df_tourismeh <- data.table::fread("../data/input/export Tourisme Handicap.csv",encoding = "Latin-1")

df_clean <- df_tourismeh |>
  filter(Ville %in% stringr::str_to_upper(liste_commune_blois))

extract_2 <- df_clean |> select(
  `Nom du professionnel`,
  `Filière du professionnel`,
  `Activité du professionnel`,
  `Ville`,
  `Adresse`,
  `Handicaps attribués`) |>
  rename(
    "name" = `Nom du professionnel`,
    "filiere" = `Filière du professionnel`,
    "activite"=`Activité du professionnel`,
    "ville" = `Ville`,
    "adresse" = `Adresse`,
    "type_handicap" = `Handicaps attribués`
  )

json_2 <- toJSON(extract_2)

write(json_2, "../data/output/tourisme_handicap_agglo_blois.json")



