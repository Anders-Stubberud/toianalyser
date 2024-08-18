import ekvipasjer_distanse_vekt_turer
import bil_tilhenger_matching
import koordinater_heatmap

if __name__ == '__main__':

    # Bruker posisionsdataen for  finne ut hvilke lastebiler som har dratt på hvilke tilhengere. 
    # Lagrer resultatet i resultater/bil_tilhenger_matching.csv
    # bil_tilhenger_matching.main()

    # Bruker bil-henger kombinasjonene i resultater/ekvipasjer.csv til å finne 
    # samlet distanse, gjennomsnittlig vekt, og antall turer tilbakelagt for de ulike ekvipasjene  for årene 2021-2024 ,
    # lagrer resultatene i resultater/ekvipasjer_distanse_vekt_turer.csv
    ekvipasjer_distanse_vekt_turer.main()

    # Bruker ekvipasjene fra resultater/path_bil_tilhenger_matching sammen med posisjonsdaten for å finne koordinatene hvor ekvipasjene har kjørt.
    # Lagrer resultatene for hver ekvipasje i resultater/koordinater_heatmap[ekvipasje].csv
    # koordinater_heatmap.main()
