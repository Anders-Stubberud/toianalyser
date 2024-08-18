import os
import fnmatch
import polars as pl

alle_ekvipasjer = (
    '3-akslet trekkvogn med 4-akslet tilhenger',
    '3-akslet trekkvogn med 5-akslet tilhenger',
    '4-akslet trekkvogn med 4-akslet tilhenger',
    '4-akslet trekkvogn med 5-akslet tilhenger',
)

vektgrense_ekvipasjer = {
    '3-akslet trekkvogn med 4-akslet tilhenger': 60000,
    '3-akslet trekkvogn med 5-akslet tilhenger': 65000,
    '4-akslet trekkvogn med 4-akslet tilhenger': 68000,
    '4-akslet trekkvogn med 5-akslet tilhenger': 74000,
}

UTVIKLING_MAKSIMAL_KJØREVEKT = 'utvikling maksimal kjørevekt'
UTVIKLING_KAPASITETSUTNYTTELSE = 'utvikling kapasitetsutnyttelse'
FORDELING_TURER_MED_VEKT = 'fordeling turer med vekt'
UTVIKLINGER_OVER_TID = 'utviklinger over tid'
SEKSJONER = (
    'section1',
    'section2',
    'section3',
    'section4'
)

PROPERTIES_AND_ALIASES = [ # for 'videreutvikling statistikk 2022', fikk ikke lov til å kalle filer det de originale navnene var
    ('AdBluesnitt (l/mil)', 'adblue'),
    ('Snittforbruk totalt (l/mil)', 'snittforbruk totalt'),
    ('Snittforbruk kjøring (l/mil)', 'snittforbruk kjøring'),
    ('Snitthastighet', 'snitthastighet'),
    ('CO₂ snitt (kg/km)', 'co2'),
    ('Snittforbruk (l/time)', 'snittforbruk')
]

current_dir = os.path.dirname(os.path.abspath(__file__))
path_dir_posisjonsdata = os.path.join(current_dir, '..', 'LINX-data', 'posisjonsdata')
paths_posisjonsdata = [os.path.join(path_dir_posisjonsdata, fil) for fil in os.listdir(path_dir_posisjonsdata) if fil.endswith('csv')]
path_dir_kjøretøysdata = os.path.join(current_dir, '..', 'LINX-data', 'kjøretøysdata')
paths_kjøretøysdata = [os.path.join(path_dir_kjøretøysdata, fil) for fil in os.listdir(path_dir_kjøretøysdata) if fil.endswith('csv')]
path_resultater = os.path.join(current_dir, '..', 'resultater')
path_bil_tilhenger_matching = os.path.join(path_resultater, 'bil_tilhenger_matching.csv')
path_ekvipasjer_distanse_vekt_turer = os.path.join(path_resultater, 'ekvipasjer_distanse_vekt_turer.csv')
path_vin_kjøretøytype = os.path.join(current_dir, '..', 'LINX-data', 'vin_kjøretøytype', 'vin_kjøretøytype.csv')
path_bil_henger_combo = os.path.join(current_dir, '..', 'LINX-data', 'kombo_bil_henger', 'bil_henger_kombo.csv')
path_eiendelsdata = os.path.join(current_dir, '..', 'LINX-data', 'eiendelsrapport', 'Eiendelsrapport_20240705063004.csv')
path_dir_resultater_utviklinger = os.path.join(path_resultater, UTVIKLINGER_OVER_TID)
path_dir_resultater_videreutvikling_statistikk_2022 = os.path.join(path_resultater, 'videreutvikling statistikk 2022')
path_dir_wim_data = os.path.join(current_dir, '..', 'WIM-data')

def find_csv_files_with_keywords(keywords, root_dir=os.path.join(current_dir, '..', 'WIM-data')):
    matched_files = []
    for root, dirs, files in os.walk(root_dir):
        for filename in files:
            if fnmatch.fnmatch(filename, '*.csv'):
                for keyword in keywords:
                    if keyword.lower() in filename.lower():
                        matched_files.append(os.path.join(root, filename))
                        break
                else:
                    continue
                break
    return matched_files




