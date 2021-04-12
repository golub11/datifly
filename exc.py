import textdistance

textdistance.jaro_winkler("messi","mess")

# poredjenje i dokaz primera koji smo koristili pri definisanju sličnosti u 2. poglavlju
textdistance.jaro_winkler("automobil","auiotobil")
# vraca 0.9074074074074073
textdistance.jaro_winkler("automobil","auiomobtl")
# vraca 0.8814814814814814