"""Synthetic botanical garden database generator (SQLite).

Creates botanical_garden.db: the plant collection of an invented garden
(Eldermere Botanical Gardens) followed for two years (2024-2025). It holds
families, species, sites, plots, staff, individual plants, daily weather,
monthly growth measurements, care treatments and pest/disease incidents.
Only the Python standard library is used and the random seed is fixed, so
every run produces an identical database.
"""
import math
import random
import sqlite3
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

SEED = 2025
random.seed(SEED)
DB_PATH = Path("botanical_garden.db")
START, END = date(2024, 1, 1), date(2025, 12, 31)
N_DAYS = (END - START).days + 1
N_WEEKS = math.ceil(N_DAYS / 7)
GROWTH_SCALE = 7.0

# family -> (order, flowering plant?)
FAMILIES = {
    "Araceae": ("Alismatales", 1), "Musaceae": ("Zingiberales", 1), "Strelitziaceae": ("Zingiberales", 1),
    "Zingiberaceae": ("Zingiberales", 1), "Marantaceae": ("Zingiberales", 1), "Moraceae": ("Rosales", 1),
    "Orchidaceae": ("Asparagales", 1), "Bromeliaceae": ("Poales", 1), "Arecaceae": ("Arecales", 1),
    "Malvaceae": ("Malvales", 1), "Rubiaceae": ("Gentianales", 1), "Rutaceae": ("Sapindales", 1),
    "Oleaceae": ("Lamiales", 1), "Lauraceae": ("Laurales", 1), "Lamiaceae": ("Lamiales", 1),
    "Geraniaceae": ("Geraniales", 1), "Amaryllidaceae": ("Asparagales", 1), "Proteaceae": ("Proteales", 1),
    "Theaceae": ("Ericales", 1), "Nyctaginaceae": ("Caryophyllales", 1), "Myrtaceae": ("Myrtales", 1),
    "Asphodelaceae": ("Asparagales", 1), "Crassulaceae": ("Saxifragales", 1), "Asparagaceae": ("Asparagales", 1),
    "Cactaceae": ("Caryophyllales", 1), "Euphorbiaceae": ("Malpighiales", 1), "Dryopteridaceae": ("Polypodiales", 0),
    "Athyriaceae": ("Polypodiales", 0), "Aspleniaceae": ("Polypodiales", 0), "Blechnaceae": ("Polypodiales", 0),
    "Osmundaceae": ("Osmundales", 0), "Onocleaceae": ("Polypodiales", 0), "Dicksoniaceae": ("Cyatheales", 0),
    "Ranunculaceae": ("Ranunculales", 1), "Rosaceae": ("Rosales", 1), "Hydrangeaceae": ("Cornales", 1),
    "Paeoniaceae": ("Saxifragales", 1), "Fabaceae": ("Fabales", 1), "Buxaceae": ("Buxales", 1),
    "Plantaginaceae": ("Lamiales", 1), "Iridaceae": ("Asparagales", 1), "Asteraceae": ("Asterales", 1),
    "Saxifragaceae": ("Saxifragales", 1), "Gentianaceae": ("Gentianales", 1), "Caryophyllaceae": ("Caryophyllales", 1),
    "Campanulaceae": ("Asterales", 1), "Primulaceae": ("Ericales", 1), "Poaceae": ("Poales", 1),
    "Papaveraceae": ("Ranunculales", 1), "Caprifoliaceae": ("Dipsacales", 1), "Orobanchaceae": ("Lamiales", 1),
    "Apiaceae": ("Apiales", 1), "Fagaceae": ("Fagales", 1), "Betulaceae": ("Fagales", 1),
    "Sapindaceae": ("Sapindales", 1), "Aquifoliaceae": ("Aquifoliales", 1), "Ericaceae": ("Ericales", 1),
    "Adoxaceae": ("Dipsacales", 1), "Araliaceae": ("Apiales", 1),
}

# scientific name, common name, family, form, lifecycle, native region, light need, water need,
# lowest tolerated temperature (C), maximum height (cm), relative growth rate per month, evergreen, toxic to pets,
# habitats ('|' separated) in which the garden grows it
SPECIES = [
    ("Monstera deliciosa", "Swiss cheese plant", "Araceae", "Climber", "Perennial", "Central America", "Medium", "High", 10, 300, .10, 1, 1, "tropical"),
    ("Alocasia macrorrhiza", "Giant taro", "Araceae", "Herb", "Perennial", "Asia", "Medium", "High", 10, 250, .12, 1, 1, "tropical"),
    ("Musa acuminata", "Dwarf Cavendish banana", "Musaceae", "Herb", "Perennial", "Asia", "High", "High", 8, 300, .11, 1, 0, "tropical"),
    ("Strelitzia reginae", "Bird of paradise", "Strelitziaceae", "Herb", "Perennial", "Africa", "High", "Moderate", 3, 150, .07, 1, 1, "tropical"),
    ("Ficus elastica", "Rubber plant", "Moraceae", "Tree", "Perennial", "Asia", "Medium", "Moderate", 8, 600, .06, 1, 1, "tropical"),
    ("Phalaenopsis amabilis", "Moon orchid", "Orchidaceae", "Herb", "Perennial", "Asia", "Low", "Moderate", 12, 60, .05, 1, 0, "tropical"),
    ("Cattleya labiata", "Ruby-lipped cattleya", "Orchidaceae", "Herb", "Perennial", "South America", "Medium", "Moderate", 10, 45, .04, 1, 0, "tropical"),
    ("Aechmea fasciata", "Silver vase plant", "Bromeliaceae", "Herb", "Perennial", "South America", "Medium", "Moderate", 10, 70, .05, 1, 0, "tropical"),
    ("Dypsis lutescens", "Areca palm", "Arecaceae", "Tree", "Perennial", "Africa", "Medium", "Moderate", 8, 500, .05, 1, 0, "tropical"),
    ("Calathea ornata", "Pinstripe calathea", "Marantaceae", "Herb", "Perennial", "South America", "Low", "High", 12, 80, .08, 1, 0, "tropical"),
    ("Hibiscus rosa-sinensis", "Chinese hibiscus", "Malvaceae", "Shrub", "Perennial", "Asia", "High", "High", 5, 300, .08, 1, 0, "tropical"),
    ("Zingiber officinale", "Ginger", "Zingiberaceae", "Herb", "Perennial", "Asia", "Medium", "High", 12, 100, .14, 0, 0, "tropical"),
    ("Coffea arabica", "Arabica coffee", "Rubiaceae", "Shrub", "Perennial", "Africa", "Medium", "High", 8, 300, .05, 1, 1, "tropical"),
    ("Citrus limon", "Lemon", "Rutaceae", "Tree", "Perennial", "Asia", "High", "Moderate", 0, 400, .05, 1, 1, "temperate|walled"),
    ("Olea europaea", "Olive", "Oleaceae", "Tree", "Perennial", "Mediterranean", "High", "Low", -8, 800, .035, 1, 0, "temperate"),
    ("Laurus nobilis", "Bay laurel", "Lauraceae", "Tree", "Perennial", "Mediterranean", "Medium", "Low", -10, 700, .04, 1, 1, "temperate"),
    ("Lavandula angustifolia", "English lavender", "Lamiaceae", "Shrub", "Perennial", "Europe", "High", "Low", -15, 80, .09, 1, 1, "temperate|walled"),
    ("Rosmarinus officinalis", "Rosemary", "Lamiaceae", "Shrub", "Perennial", "Mediterranean", "High", "Low", -12, 150, .08, 1, 0, "temperate"),
    ("Pelargonium graveolens", "Rose geranium", "Geraniaceae", "Shrub", "Perennial", "Africa", "High", "Low", 0, 120, .12, 1, 1, "temperate|walled"),
    ("Agapanthus africanus", "African lily", "Amaryllidaceae", "Herb", "Perennial", "Africa", "High", "Moderate", -3, 90, .08, 1, 1, "temperate|walled"),
    ("Protea cynaroides", "King protea", "Proteaceae", "Shrub", "Perennial", "Africa", "High", "Low", -2, 200, .05, 1, 0, "temperate"),
    ("Camellia japonica", "Japanese camellia", "Theaceae", "Shrub", "Perennial", "Asia", "Medium", "Moderate", -12, 400, .04, 1, 0, "temperate"),
    ("Bougainvillea glabra", "Paper flower", "Nyctaginaceae", "Climber", "Perennial", "South America", "High", "Low", 2, 500, .10, 0, 1, "temperate"),
    ("Jasminum polyanthum", "Pink jasmine", "Oleaceae", "Climber", "Perennial", "Asia", "High", "Moderate", -2, 400, .12, 1, 0, "temperate|walled"),
    ("Eucalyptus gunnii", "Cider gum", "Myrtaceae", "Tree", "Perennial", "Australasia", "High", "Low", -15, 1500, .09, 1, 1, "temperate"),
    ("Aloe vera", "Aloe", "Asphodelaceae", "Succulent", "Perennial", "Africa", "High", "Low", 4, 60, .04, 1, 1, "arid"),
    ("Echeveria elegans", "Mexican snowball", "Crassulaceae", "Succulent", "Perennial", "Central America", "High", "Low", 2, 15, .03, 1, 0, "arid"),
    ("Agave americana", "Century plant", "Asparagaceae", "Succulent", "Perennial", "Central America", "High", "Low", -5, 200, .03, 1, 1, "arid"),
    ("Opuntia ficus-indica", "Prickly pear", "Cactaceae", "Succulent", "Perennial", "Central America", "High", "Low", -5, 300, .04, 1, 0, "arid"),
    ("Echinocactus grusonii", "Golden barrel cactus", "Cactaceae", "Succulent", "Perennial", "Central America", "High", "Low", 0, 80, .02, 1, 0, "arid"),
    ("Euphorbia trigona", "African milk tree", "Euphorbiaceae", "Succulent", "Perennial", "Africa", "High", "Low", 8, 200, .05, 1, 1, "arid"),
    ("Haworthia fasciata", "Zebra haworthia", "Asphodelaceae", "Succulent", "Perennial", "Africa", "Medium", "Low", 2, 15, .02, 1, 0, "arid"),
    ("Sansevieria trifasciata", "Snake plant", "Asparagaceae", "Succulent", "Perennial", "Africa", "Low", "Low", 7, 90, .04, 1, 1, "arid"),
    ("Crassula ovata", "Jade plant", "Crassulaceae", "Succulent", "Perennial", "Africa", "High", "Low", 2, 120, .03, 1, 1, "arid"),
    ("Yucca filamentosa", "Adam's needle", "Asparagaceae", "Shrub", "Perennial", "North America", "High", "Low", -20, 150, .04, 1, 1, "arid"),
    ("Kalanchoe blossfeldiana", "Flaming Katy", "Crassulaceae", "Succulent", "Perennial", "Africa", "High", "Low", 8, 30, .05, 1, 1, "arid"),
    ("Mammillaria elongata", "Gold lace cactus", "Cactaceae", "Succulent", "Perennial", "Central America", "High", "Low", 2, 20, .02, 1, 0, "arid"),
    ("Dryopteris filix-mas", "Male fern", "Dryopteridaceae", "Fern", "Perennial", "Europe", "Low", "High", -25, 100, .10, 0, 0, "fern"),
    ("Athyrium filix-femina", "Lady fern", "Athyriaceae", "Fern", "Perennial", "Europe", "Low", "High", -25, 100, .11, 0, 0, "fern"),
    ("Polystichum setiferum", "Soft shield fern", "Dryopteridaceae", "Fern", "Perennial", "Europe", "Low", "High", -15, 90, .08, 1, 0, "fern"),
    ("Asplenium scolopendrium", "Hart's-tongue fern", "Aspleniaceae", "Fern", "Perennial", "Europe", "Low", "High", -20, 60, .07, 1, 0, "fern"),
    ("Blechnum spicant", "Hard fern", "Blechnaceae", "Fern", "Perennial", "Europe", "Low", "High", -15, 50, .06, 1, 0, "fern"),
    ("Osmunda regalis", "Royal fern", "Osmundaceae", "Fern", "Perennial", "Europe", "Low", "High", -20, 150, .09, 0, 0, "fern"),
    ("Matteuccia struthiopteris", "Ostrich fern", "Onocleaceae", "Fern", "Perennial", "Europe", "Low", "High", -30, 120, .10, 0, 0, "fern"),
    ("Dicksonia antarctica", "Tasmanian tree fern", "Dicksoniaceae", "Fern", "Perennial", "Australasia", "Low", "High", -8, 300, .04, 1, 0, "fern"),
    ("Hosta sieboldiana", "Siebold's hosta", "Asparagaceae", "Herb", "Perennial", "Asia", "Low", "High", -25, 90, .12, 0, 1, "fern"),
    ("Helleborus foetidus", "Stinking hellebore", "Ranunculaceae", "Herb", "Perennial", "Europe", "Low", "Moderate", -20, 80, .08, 1, 1, "fern"),
    ("Rosa gallica", "French rose", "Rosaceae", "Shrub", "Perennial", "Europe", "High", "Moderate", -25, 120, .09, 0, 0, "walled"),
    ("Hydrangea macrophylla", "Bigleaf hydrangea", "Hydrangeaceae", "Shrub", "Perennial", "Asia", "Medium", "High", -15, 200, .08, 0, 1, "walled"),
    ("Paeonia lactiflora", "Chinese peony", "Paeoniaceae", "Herb", "Perennial", "Asia", "High", "Moderate", -30, 90, .10, 0, 1, "walled"),
    ("Clematis montana", "Mountain clematis", "Ranunculaceae", "Climber", "Perennial", "Asia", "Medium", "Moderate", -20, 800, .12, 0, 1, "walled"),
    ("Wisteria sinensis", "Chinese wisteria", "Fabaceae", "Climber", "Perennial", "Asia", "High", "Moderate", -20, 1000, .09, 0, 1, "walled"),
    ("Buxus sempervirens", "Box", "Buxaceae", "Shrub", "Perennial", "Europe", "Medium", "Moderate", -20, 250, .04, 1, 1, "walled"),
    ("Geranium sanguineum", "Bloody cranesbill", "Geraniaceae", "Herb", "Perennial", "Europe", "Medium", "Moderate", -25, 40, .12, 0, 0, "walled"),
    ("Digitalis purpurea", "Foxglove", "Plantaginaceae", "Herb", "Biennial", "Europe", "Medium", "Moderate", -20, 150, .14, 0, 1, "walled"),
    ("Salvia officinalis", "Common sage", "Lamiaceae", "Shrub", "Perennial", "Mediterranean", "High", "Low", -10, 70, .09, 1, 0, "walled"),
    ("Malus domestica", "Apple", "Rosaceae", "Tree", "Perennial", "Europe", "High", "Moderate", -25, 450, .05, 0, 0, "walled"),
    ("Iris germanica", "Bearded iris", "Iridaceae", "Herb", "Perennial", "Europe", "High", "Low", -25, 90, .10, 0, 1, "walled"),
    ("Echinacea purpurea", "Purple coneflower", "Asteraceae", "Herb", "Perennial", "North America", "High", "Low", -30, 100, .12, 0, 0, "walled"),
    ("Alchemilla mollis", "Lady's mantle", "Rosaceae", "Herb", "Perennial", "Europe", "Medium", "Moderate", -30, 50, .12, 0, 0, "walled"),
    ("Tagetes patula", "French marigold", "Asteraceae", "Herb", "Annual", "Central America", "High", "Moderate", 0, 30, .20, 0, 0, "walled"),
    ("Lathyrus odoratus", "Sweet pea", "Fabaceae", "Climber", "Annual", "Europe", "High", "Moderate", -2, 200, .22, 0, 1, "walled"),
    ("Helianthus annuus", "Sunflower", "Asteraceae", "Herb", "Annual", "North America", "High", "Moderate", -2, 250, .25, 0, 0, "walled|meadow"),
    ("Saxifraga paniculata", "Encrusted saxifrage", "Saxifragaceae", "Herb", "Perennial", "Europe", "High", "Low", -30, 25, .05, 1, 0, "alpine"),
    ("Sempervivum tectorum", "Houseleek", "Crassulaceae", "Succulent", "Perennial", "Europe", "High", "Low", -35, 15, .03, 1, 0, "alpine"),
    ("Gentiana acaulis", "Trumpet gentian", "Gentianaceae", "Herb", "Perennial", "Europe", "High", "Moderate", -30, 10, .04, 1, 0, "alpine"),
    ("Dianthus alpinus", "Alpine pink", "Caryophyllaceae", "Herb", "Perennial", "Europe", "High", "Low", -25, 15, .06, 1, 0, "alpine"),
    ("Campanula cochleariifolia", "Fairy's thimble", "Campanulaceae", "Herb", "Perennial", "Europe", "Medium", "Moderate", -25, 12, .07, 0, 0, "alpine"),
    ("Primula auricula", "Auricula", "Primulaceae", "Herb", "Perennial", "Europe", "Medium", "Moderate", -30, 20, .05, 1, 0, "alpine"),
    ("Edraianthus pumilio", "Dwarf grassbells", "Campanulaceae", "Herb", "Perennial", "Europe", "High", "Low", -20, 8, .04, 1, 0, "alpine"),
    ("Erinus alpinus", "Fairy foxglove", "Plantaginaceae", "Herb", "Perennial", "Europe", "High", "Low", -20, 15, .08, 0, 0, "alpine"),
    ("Androsace carnea", "Pink rock-jasmine", "Primulaceae", "Herb", "Perennial", "Europe", "High", "Low", -30, 8, .04, 1, 0, "alpine"),
    ("Dryas octopetala", "Mountain avens", "Rosaceae", "Shrub", "Perennial", "Europe", "High", "Low", -35, 10, .04, 1, 0, "alpine"),
    ("Pulsatilla vulgaris", "Pasqueflower", "Ranunculaceae", "Herb", "Perennial", "Europe", "High", "Low", -25, 30, .06, 0, 1, "alpine"),
    ("Leontopodium alpinum", "Edelweiss", "Asteraceae", "Herb", "Perennial", "Europe", "High", "Low", -30, 20, .05, 0, 0, "alpine"),
    ("Festuca rubra", "Red fescue", "Poaceae", "Grass", "Perennial", "Europe", "High", "Moderate", -30, 60, .14, 1, 0, "meadow"),
    ("Anthoxanthum odoratum", "Sweet vernal grass", "Poaceae", "Grass", "Perennial", "Europe", "High", "Moderate", -30, 70, .14, 0, 0, "meadow"),
    ("Briza media", "Quaking grass", "Poaceae", "Grass", "Perennial", "Europe", "High", "Low", -25, 60, .13, 0, 0, "meadow"),
    ("Cynosurus cristatus", "Crested dog's-tail", "Poaceae", "Grass", "Perennial", "Europe", "High", "Moderate", -25, 70, .13, 0, 0, "meadow"),
    ("Leucanthemum vulgare", "Oxeye daisy", "Asteraceae", "Herb", "Perennial", "Europe", "High", "Moderate", -25, 80, .16, 0, 0, "meadow"),
    ("Centaurea nigra", "Common knapweed", "Asteraceae", "Herb", "Perennial", "Europe", "High", "Moderate", -25, 90, .16, 0, 0, "meadow"),
    ("Papaver rhoeas", "Common poppy", "Papaveraceae", "Herb", "Annual", "Europe", "High", "Low", -10, 70, .22, 0, 1, "meadow"),
    ("Centaurea cyanus", "Cornflower", "Asteraceae", "Herb", "Annual", "Europe", "High", "Low", -10, 80, .20, 0, 0, "meadow"),
    ("Achillea millefolium", "Yarrow", "Asteraceae", "Herb", "Perennial", "Europe", "High", "Low", -30, 80, .14, 0, 1, "meadow"),
    ("Knautia arvensis", "Field scabious", "Caprifoliaceae", "Herb", "Perennial", "Europe", "High", "Low", -25, 100, .14, 0, 0, "meadow"),
    ("Lotus corniculatus", "Bird's-foot trefoil", "Fabaceae", "Herb", "Perennial", "Europe", "High", "Moderate", -25, 40, .15, 0, 0, "meadow"),
    ("Rhinanthus minor", "Yellow rattle", "Orobanchaceae", "Herb", "Annual", "Europe", "High", "Moderate", -25, 40, .20, 0, 0, "meadow"),
    ("Primula veris", "Cowslip", "Primulaceae", "Herb", "Perennial", "Europe", "Medium", "Moderate", -25, 25, .09, 0, 0, "meadow"),
    ("Daucus carota", "Wild carrot", "Apiaceae", "Herb", "Biennial", "Europe", "High", "Low", -20, 120, .16, 0, 1, "meadow"),
    ("Quercus robur", "English oak", "Fagaceae", "Tree", "Perennial", "Europe", "Medium", "Moderate", -30, 2500, .05, 0, 1, "woodland"),
    ("Fagus sylvatica", "European beech", "Fagaceae", "Tree", "Perennial", "Europe", "Low", "Moderate", -30, 2800, .05, 0, 0, "woodland"),
    ("Betula pendula", "Silver birch", "Betulaceae", "Tree", "Perennial", "Europe", "High", "Moderate", -35, 2000, .08, 0, 0, "woodland"),
    ("Acer campestre", "Field maple", "Sapindaceae", "Tree", "Perennial", "Europe", "Medium", "Moderate", -30, 1500, .06, 0, 0, "woodland"),
    ("Corylus avellana", "Hazel", "Betulaceae", "Shrub", "Perennial", "Europe", "Medium", "Moderate", -30, 500, .08, 0, 0, "woodland"),
    ("Ilex aquifolium", "Holly", "Aquifoliaceae", "Tree", "Perennial", "Europe", "Low", "Moderate", -25, 1200, .035, 1, 1, "woodland"),
    ("Crataegus monogyna", "Hawthorn", "Rosaceae", "Tree", "Perennial", "Europe", "Medium", "Moderate", -30, 800, .06, 0, 0, "woodland"),
    ("Rhododendron yakushimanum", "Yaku rhododendron", "Ericaceae", "Shrub", "Perennial", "Asia", "Low", "High", -25, 150, .04, 1, 1, "woodland"),
    ("Hyacinthoides non-scripta", "Bluebell", "Asparagaceae", "Herb", "Perennial", "Europe", "Low", "Moderate", -25, 40, .10, 0, 1, "woodland"),
    ("Anemone nemorosa", "Wood anemone", "Ranunculaceae", "Herb", "Perennial", "Europe", "Low", "Moderate", -25, 20, .09, 0, 1, "woodland"),
    ("Sambucus nigra", "Elder", "Adoxaceae", "Shrub", "Perennial", "Europe", "Medium", "Moderate", -30, 600, .10, 0, 1, "woodland"),
    ("Hedera helix", "Common ivy", "Araliaceae", "Climber", "Perennial", "Europe", "Low", "Moderate", -25, 1200, .09, 1, 1, "woodland"),
]

# name, type, climate controlled, habitat, elevation (m), area (ha), established, number of plants
SITES = [("Tropical House", "Glasshouse", 1, "tropical", 52, 0.4, 1998, 200),
         ("Temperate House", "Glasshouse", 1, "temperate", 52, 0.6, 1987, 210),
         ("Arid House", "Glasshouse", 1, "arid", 52, 0.3, 2005, 150),
         ("Fern Gully", "Woodland", 0, "fern", 48, 0.5, 1962, 150),
         ("Walled Garden", "Outdoor Bed", 0, "walled", 55, 0.8, 1904, 230),
         ("Alpine Rock Garden", "Rock Garden", 0, "alpine", 110, 0.3, 1951, 180),
         ("Wildflower Meadow", "Meadow", 0, "meadow", 60, 2.5, 2011, 240),
         ("Ancient Woodland Walk", "Woodland", 0, "woodland", 58, 3.2, 1880, 160)]
SITE_CODE = ["TRO", "TEM", "ARI", "FER", "WAL", "ALP", "MEA", "WOO"]
OUTDOOR_OFFSET = {"fern": -0.5, "walled": 1.0, "alpine": -2.0, "meadow": 0.0, "woodland": -0.8}
RAIN_FACTOR = {"fern": 1.0, "walled": 0.9, "alpine": 1.3, "meadow": 1.0, "woodland": 1.1}
PLOT_RULES = {
    "tropical": (dict(Loam=50, Peat=40, Sandy=10), dict(Drip=45, Sprinkler=35, Manual=20), dict(Partial=55, Full=30, Shade=15)),
    "temperate": (dict(Loam=55, Sandy=20, Gritty=15, Clay=10), dict(Drip=40, Sprinkler=30, Manual=30), dict(Full=55, Partial=45)),
    "arid": (dict(Sandy=50, Gritty=50), dict(Manual=50, Drip=50), dict(Full=85, Partial=15)),
    "fern": (dict(Peat=45, Loam=45, Clay=10), {"Rain-fed": 50, "Sprinkler": 30, "Manual": 20}, dict(Shade=80, Partial=20)),
    "walled": (dict(Loam=50, Clay=25, Chalk=15, Sandy=10), {"Drip": 35, "Manual": 30, "Sprinkler": 15, "Rain-fed": 20}, dict(Full=55, Partial=45)),
    "alpine": (dict(Gritty=55, Chalk=25, Sandy=20), {"Rain-fed": 60, "Manual": 40}, dict(Full=70, Partial=30)),
    "meadow": (dict(Loam=40, Clay=30, Chalk=20, Sandy=10), {"Rain-fed": 85, "Sprinkler": 15}, dict(Full=90, Partial=10)),
    "woodland": (dict(Loam=45, Clay=35, Peat=10, Sandy=10), {"Rain-fed": 90, "Manual": 10}, dict(Shade=50, Partial=45, Full=5)),
}
SOIL_PH = {"Clay": 7.0, "Loam": 6.6, "Sandy": 6.0, "Peat": 4.8, "Chalk": 7.9, "Gritty": 6.8}
RETENTION = {"Clay": 1.15, "Loam": 1.0, "Peat": 1.1, "Chalk": 0.85, "Sandy": 0.75, "Gritty": 0.65}
IRRIGATION = {"Drip": 0.60, "Sprinkler": 0.55, "Manual": 0.45, "Rain-fed": 0.0}
EXPOSURE = {"Shade": 0.3, "Partial": 0.65, "Full": 1.0}
LIGHT_NEED = {"Low": 0.3, "Medium": 0.65, "High": 1.0}
WATER_NEED = {"Low": 0.3, "Moderate": 0.6, "High": 0.9}
# habitat -> optimum weekly mean temperature, tolerance below it, tolerance above it
TEMP_RESPONSE = {"tropical": (26, 7, 7), "temperate": (21, 9, 11), "arid": (27, 9, 12), "fern": (16, 8, 6),
                 "walled": (18, 8, 8), "alpine": (13, 8, 6), "meadow": (17, 8, 8), "woodland": (16, 8, 8)}
STEM = {"Tree": (0.25, 0.95), "Shrub": (0.5, 0.65), "Herb": (0.3, 0.70), "Grass": (0.1, 0.70),
        "Fern": (0.3, 0.60), "Succulent": (0.8, 0.70), "Climber": (0.35, 0.70)}
LEAF = {"Tree": 5.0, "Shrub": 4.0, "Herb": 3.0, "Grass": 12.0, "Fern": 1.5, "Succulent": 0.8, "Climber": 3.5}
BLOOM = {"Herb": {5, 6, 7, 8}, "Shrub": {4, 5, 6, 7}, "Tree": {4, 5}, "Climber": {5, 6, 7}, "Grass": {6, 7, 8},
         "Succulent": {5, 6, 7, 8}, "Fern": set()}
DIEBACK = {1: .3, 2: .3, 3: .6, 4: .85, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1, 10: .9, 11: .7, 12: .3}
ISSUES = {"Aphids": "pest", "Spider Mite": "pest", "Mealybug": "pest", "Slugs": "pest", "Powdery Mildew": "fungal",
          "Leaf Spot": "fungal", "Root Rot": "fungal", "Frost Damage": "abiotic", "Scorch": "abiotic"}
PENALTY = {"Mild": 0.10, "Moderate": 0.25, "Severe": 0.45}
PRODUCTS = {"Fertiliser": ["Balanced NPK 10-10-10", "Seaweed extract", "High-potash feed", "Slow-release liquid feed"],
            "Pest Control": ["Neem oil spray", "Insecticidal soap", "Biological control (nematodes)", "Pyrethrin spray"],
            "Fungicide": ["Sulphur fungicide", "Copper fungicide", "Bicarbonate spray"],
            "Supplementary Watering": ["Mains water", "Harvested rainwater"]}
STAFF_NAMES = (["Amelia", "Oliver", "Priya", "Tomasz", "Grace", "Marcus", "Hannah", "Rohan", "Isla", "Daniel", "Sofia", "Callum",
                "Mei", "Joseph", "Nadia", "Ethan", "Fatima", "George", "Elena", "Samuel", "Ruth", "Kwame", "Lucy", "Arjun"],
               ["Hartley", "Patel", "Nowak", "Okafor", "Bennett", "Clarke", "Singh", "Morgan", "Reid", "Fraser", "Hughes",
                "Adeyemi", "Walker", "Cooper", "Evans", "Brooks", "Khan", "Taylor", "Murphy", "Foster"])

SCHEMA = """
CREATE TABLE families (
    family_id    INTEGER PRIMARY KEY,
    family_name  TEXT NOT NULL UNIQUE,
    order_name   TEXT NOT NULL,
    is_flowering INTEGER NOT NULL CHECK (is_flowering IN (0,1))
);
CREATE TABLE species (
    species_id      INTEGER PRIMARY KEY,
    family_id       INTEGER NOT NULL REFERENCES families(family_id),
    scientific_name TEXT NOT NULL UNIQUE,
    common_name     TEXT NOT NULL,
    growth_form     TEXT NOT NULL CHECK (growth_form IN ('Tree','Shrub','Herb','Grass','Fern','Succulent','Climber')),
    lifecycle       TEXT NOT NULL CHECK (lifecycle IN ('Annual','Biennial','Perennial')),
    native_region   TEXT NOT NULL CHECK (native_region IN ('Europe','Mediterranean','Asia','Africa','North America',
                                                           'South America','Central America','Australasia')),
    light_need      TEXT NOT NULL CHECK (light_need IN ('Low','Medium','High')),
    water_need      TEXT NOT NULL CHECK (water_need IN ('Low','Moderate','High')),
    min_temp_c      REAL NOT NULL CHECK (min_temp_c BETWEEN -45 AND 20),
    max_height_cm   INTEGER NOT NULL CHECK (max_height_cm BETWEEN 5 AND 4000),
    evergreen       INTEGER NOT NULL CHECK (evergreen IN (0,1)),
    toxic_to_pets   INTEGER NOT NULL CHECK (toxic_to_pets IN (0,1))
);
CREATE TABLE sites (
    site_id            INTEGER PRIMARY KEY,
    site_name          TEXT NOT NULL UNIQUE,
    site_type          TEXT NOT NULL CHECK (site_type IN ('Glasshouse','Outdoor Bed','Woodland','Rock Garden','Meadow')),
    climate_controlled INTEGER NOT NULL CHECK (climate_controlled IN (0,1)),
    elevation_m        INTEGER NOT NULL CHECK (elevation_m BETWEEN 0 AND 1500),
    area_ha            REAL NOT NULL CHECK (area_ha > 0),
    established_year   INTEGER NOT NULL CHECK (established_year BETWEEN 1800 AND 2020)
);
CREATE TABLE staff (
    staff_id           INTEGER PRIMARY KEY,
    first_name         TEXT NOT NULL,
    last_name          TEXT NOT NULL,
    birth_year         INTEGER NOT NULL CHECK (birth_year BETWEEN 1960 AND 2004),
    role               TEXT NOT NULL CHECK (role IN ('Gardener','Horticulturist','Botanist','Technician')),
    qualification      TEXT NOT NULL CHECK (qualification IN ('Certificate','Diploma','Degree','Doctorate')),
    years_experience   INTEGER NOT NULL CHECK (years_experience BETWEEN 0 AND 45)
);
CREATE TABLE plots (
    plot_id              INTEGER PRIMARY KEY,
    site_id              INTEGER NOT NULL REFERENCES sites(site_id),
    plot_code            TEXT NOT NULL UNIQUE,
    area_m2              REAL NOT NULL CHECK (area_m2 > 0),
    soil_type            TEXT NOT NULL CHECK (soil_type IN ('Clay','Loam','Sandy','Peat','Chalk','Gritty')),
    soil_ph              REAL NOT NULL CHECK (soil_ph BETWEEN 3 AND 10),
    irrigation           TEXT NOT NULL CHECK (irrigation IN ('Drip','Sprinkler','Manual','Rain-fed')),
    sun_exposure         TEXT NOT NULL CHECK (sun_exposure IN ('Shade','Partial','Full')),
    responsible_staff_id INTEGER NOT NULL REFERENCES staff(staff_id)
);
CREATE TABLE plants (
    plant_id          INTEGER PRIMARY KEY,
    species_id        INTEGER NOT NULL REFERENCES species(species_id),
    plot_id           INTEGER NOT NULL REFERENCES plots(plot_id),
    tag_code          TEXT NOT NULL UNIQUE,
    planted_date      TEXT NOT NULL,
    origin            TEXT NOT NULL CHECK (origin IN ('Seed','Cutting','Nursery','Division')),
    initial_height_cm REAL NOT NULL CHECK (initial_height_cm > 0),
    status            TEXT NOT NULL CHECK (status IN ('Alive','Dead','Removed')),
    end_date          TEXT,
    CHECK ((status = 'Alive' AND end_date IS NULL) OR (status <> 'Alive' AND end_date IS NOT NULL AND end_date >= planted_date))
);
CREATE TABLE weather_daily (
    site_id        INTEGER NOT NULL REFERENCES sites(site_id),
    obs_date       TEXT NOT NULL,
    temp_min_c     REAL NOT NULL CHECK (temp_min_c BETWEEN -20 AND 45),
    temp_max_c     REAL NOT NULL CHECK (temp_max_c BETWEEN -20 AND 50),
    rainfall_mm    REAL NOT NULL CHECK (rainfall_mm >= 0),
    sunshine_hours REAL NOT NULL CHECK (sunshine_hours BETWEEN 0 AND 17),
    humidity_pct   INTEGER NOT NULL CHECK (humidity_pct BETWEEN 0 AND 100),
    PRIMARY KEY (site_id, obs_date),
    CHECK (temp_max_c >= temp_min_c)
);
CREATE TABLE growth_measurements (
    measurement_id   INTEGER PRIMARY KEY,
    plant_id         INTEGER NOT NULL REFERENCES plants(plant_id),
    staff_id         INTEGER NOT NULL REFERENCES staff(staff_id),
    measure_date     TEXT NOT NULL,
    height_cm        REAL NOT NULL CHECK (height_cm > 0),
    stem_diameter_mm REAL NOT NULL CHECK (stem_diameter_mm > 0),
    leaf_count       INTEGER NOT NULL CHECK (leaf_count >= 0),
    chlorophyll_spad REAL NOT NULL CHECK (chlorophyll_spad BETWEEN 0 AND 80),
    health_score     INTEGER NOT NULL CHECK (health_score BETWEEN 1 AND 5),
    in_flower        INTEGER NOT NULL CHECK (in_flower IN (0,1)),
    UNIQUE (plant_id, measure_date)
);
CREATE TABLE treatments (
    treatment_id   INTEGER PRIMARY KEY,
    plant_id       INTEGER NOT NULL REFERENCES plants(plant_id),
    staff_id       INTEGER NOT NULL REFERENCES staff(staff_id),
    treatment_date TEXT NOT NULL,
    treatment_type TEXT NOT NULL CHECK (treatment_type IN ('Fertiliser','Pruning','Pest Control','Fungicide','Supplementary Watering')),
    product        TEXT,
    quantity_ml    REAL CHECK (quantity_ml IS NULL OR quantity_ml > 0),
    cost_gbp       REAL NOT NULL CHECK (cost_gbp >= 0)
);
CREATE TABLE incidents (
    incident_id   INTEGER PRIMARY KEY,
    plant_id      INTEGER NOT NULL REFERENCES plants(plant_id),
    reported_by   INTEGER NOT NULL REFERENCES staff(staff_id),
    treatment_id  INTEGER REFERENCES treatments(treatment_id),
    issue_type    TEXT NOT NULL CHECK (issue_type IN ('Aphids','Spider Mite','Mealybug','Slugs','Powdery Mildew',
                                                      'Leaf Spot','Root Rot','Frost Damage','Scorch')),
    severity      TEXT NOT NULL CHECK (severity IN ('Mild','Moderate','Severe')),
    detected_date TEXT NOT NULL,
    resolved_date TEXT,
    CHECK (resolved_date IS NULL OR resolved_date >= detected_date)
);
CREATE INDEX idx_plants_plot ON plants(plot_id);
CREATE INDEX idx_growth_plant ON growth_measurements(plant_id, measure_date);
CREATE INDEX idx_treat_plant ON treatments(plant_id);
CREATE INDEX idx_incident_plant ON incidents(plant_id);
"""


def wchoice(mapping):
    return random.choices(list(mapping), list(mapping.values()))[0]


def make_weather():
    """Daily weather for every site; one shared weather regime plus site offsets."""
    anomaly, wet, series = 0.0, False, []
    for t in range(N_DAYS):
        doy = (START + timedelta(days=t)).timetuple().tm_yday
        anomaly = 0.72 * anomaly + random.gauss(0, 2.2)
        p_wet = (0.60 if wet else 0.22) + 0.06 * math.cos(2 * math.pi * (doy - 355) / 365)
        wet = random.random() < p_wet
        series.append((doy, anomaly, wet))
    wx = []
    for s_idx, (name, stype, glass, habitat, *_rest) in enumerate(SITES):
        rows = []
        for t, (doy, anomaly, wet) in enumerate(series):
            base_max = 15.5 - 8.0 * math.cos(2 * math.pi * (doy - 15) / 365) + anomaly
            daylight = 12 + 4.4 * math.cos(2 * math.pi * (doy - 172) / 365)
            sun = daylight * (random.uniform(0.0, 0.25) if wet else random.uniform(0.35, 0.95))
            if habitat in ("woodland", "fern"):
                sun *= 0.55
            rain = random.gammavariate(0.9, 5.5) * RAIN_FACTOR.get(habitat, 0) if wet and random.random() > 0.08 else 0.0
            if glass:
                rain = 0.0
                if habitat == "tropical":
                    tmax = min(34, 26 + (base_max - 15) * 0.3 + random.gauss(0, 0.8))
                    tmin = 20 + random.gauss(0, 0.6)
                    hum = random.gauss(80, 5)
                elif habitat == "temperate":
                    tmax = max(13, min(40, base_max + 8 + random.gauss(0, 1.0)))
                    tmin = 9 + random.gauss(0, 0.7)
                    hum = random.gauss(60, 7)
                else:
                    tmax = max(16, min(42, base_max + 10 + random.gauss(0, 1.0)))
                    tmin = 12 + random.gauss(0, 0.7)
                    hum = random.gauss(38, 7)
                sun *= 0.8
            else:
                tmax = base_max + OUTDOOR_OFFSET[habitat]
                tmin = tmax - max(3.5, random.gauss(5.5, 1.2))
                hum = 82 - 1.0 * (tmax - 12) + (8 if wet else 0) + random.gauss(0, 5) + (6 if habitat == "fern" else 0)
            tmin = min(tmin, tmax - 1.0)
            rows.append((START + timedelta(days=t), round(tmin, 1), round(tmax, 1), round(rain, 1),
                         round(min(16.9, sun), 1), int(min(100, max(25, round(hum))))))
        wx.append(rows)
    return wx


def main():
    DB_PATH.unlink(missing_ok=True)
    wx = make_weather()

    fam_names = list(FAMILIES)
    fam_id = {f: i for i, f in enumerate(fam_names, start=1)}
    species = []
    for i, s in enumerate(SPECIES, start=1):
        species.append(dict(id=i, sci=s[0], common=s[1], fam=s[2], form=s[3], life=s[4], native=s[5], light=s[6],
                            water=s[7], minT=s[8], H=s[9], rate=s[10], green=s[11], toxic=s[12],
                            habitats=s[13].split("|")))

    staff = []
    for sid in range(1, 25):
        role = random.choices(["Gardener", "Horticulturist", "Botanist", "Technician"], [9, 6, 5, 4])[0]
        qual = {"Gardener": [60, 30, 8, 2], "Horticulturist": [10, 45, 40, 5], "Botanist": [0, 5, 55, 40],
                "Technician": [20, 50, 28, 2]}[role]
        birth = random.randint(1962, 2001)
        staff.append((sid, STAFF_NAMES[0][sid - 1], random.choice(STAFF_NAMES[1]), birth, role,
                      random.choices(["Certificate", "Diploma", "Degree", "Doctorate"], qual)[0],
                      random.randint(0, min(40, 2024 - birth - 18))))
    care_staff = [s[0] for s in staff if s[4] in ("Gardener", "Horticulturist")]
    survey_staff = [s[0] for s in staff if s[4] in ("Botanist", "Technician", "Horticulturist")]

    sites = [(i, s[0], s[1], s[2], s[4], s[5], s[6]) for i, s in enumerate(SITES, start=1)]
    plots, plot_info = [], {}
    for s_idx, site in enumerate(SITES):
        soils, irrs, suns = PLOT_RULES[site[3]]
        for n in range(1, 9):
            soil = wchoice(soils)
            plot_id = len(plots) + 1
            row = (plot_id, s_idx + 1, f"{SITE_CODE[s_idx]}-{n:02d}", round(random.uniform(18, 140), 1), soil,
                   round(min(8.8, max(4.0, random.gauss(SOIL_PH[soil], 0.3))), 1), wchoice(irrs), wchoice(suns),
                   random.choice(care_staff))
            plots.append(row)
            plot_info[plot_id] = dict(site=s_idx, soil=soil, irr=row[6], sun=row[7], staff=row[8], habitat=site[3],
                                      glass=site[2])

    # ------------------------------------------------------------------ plants
    plant_specs = []
    for s_idx, site in enumerate(SITES):
        site_plots = [p for p, info in plot_info.items() if info["site"] == s_idx]
        pool = [sp for sp in species if site[3] in sp["habitats"]]
        for _ in range(site[7]):
            sp = random.choice(pool)
            if sp["life"] == "Annual":
                year = 2024 if random.random() < 0.7 else 2025
                planted = date(year, 4, 1) + timedelta(days=random.randint(0, 75))
            else:
                u = random.random()
                lo, span = (date(2024, 3, 1), 91) if u < 0.5 else (date(2024, 6, 1), 122) if u < 0.8 else \
                    (date(2024, 1, 1), 59) if u < 0.9 else (date(2024, 10, 1), 60)
                planted = lo + timedelta(days=random.randint(0, span))
            form = sp["form"]
            origin = wchoice({"Nursery": 70, "Seed": 15, "Cutting": 15}) if form in ("Tree", "Shrub", "Climber") else \
                wchoice({"Seed": 40, "Division": 30, "Nursery": 30})
            if sp["life"] == "Annual":
                origin = "Seed"
            frac = {"Seed": (0.01, 0.03), "Cutting": (0.03, 0.07), "Division": (0.08, 0.20), "Nursery": (0.05, 0.15)}[origin]
            if form == "Tree":
                frac = (0.03, 0.08)
            h0 = round(min(0.3 * sp["H"], max(2.0, sp["H"] * random.uniform(*frac))), 1)
            plant_specs.append(dict(sp=sp, plot=random.choice(site_plots), planted=planted, origin=origin, h0=h0))
    plant_specs.sort(key=lambda p: (p["planted"], p["plot"]))
    plants = []
    for i, ps in enumerate(plant_specs, start=1):
        life_days = {"Annual": random.randint(150, 230), "Biennial": random.randint(420, 560)}.get(ps["sp"]["life"])
        plants.append(dict(id=i, **ps, h=ps["h0"], health=0.85, nutrient=0.7, alive=True, end=None, status="Alive",
                           incident=None, indiv=random.lognormvariate(0, 0.2), life_days=life_days,
                           last_prune=None))

    # ------------------------------------------------- weekly simulation
    treatments, incidents, measurements = [], [], []
    surveys = []  # per site: dates every 28 days
    for s_idx in range(len(SITES)):
        first = START + timedelta(days=random.randint(10, 26))
        surveys.append([first + timedelta(days=28 * k) for k in range(30) if first + timedelta(days=28 * k) <= END])
    survey_team = {s: random.sample(survey_staff, 3) for s in range(len(SITES))}
    fert_dates = {}
    for p, info in plot_info.items():
        months = [(2, 15), (4, 15), (6, 15), (8, 15)] if info["glass"] else [(4, 15), (6, 15)]
        fert_dates[p] = [date(y, m, d) for y in (2024, 2025) for m, d in months]

    def add_treatment(plant, when, ttype, product, qty, cost, staff_id):
        treatments.append(dict(plant=plant["id"], staff=staff_id, date=when, type=ttype, product=product, qty=qty,
                               cost=cost, key=len(treatments)))
        return len(treatments) - 1

    for w in range(N_WEEKS):
        d0 = START + timedelta(days=7 * w)
        d6 = min(END, d0 + timedelta(days=6))
        n_days = (d6 - d0).days + 1
        summ = []
        for s_idx in range(len(SITES)):
            days = wx[s_idx][7 * w: 7 * w + n_days]
            summ.append(dict(tmean=sum((d[1] + d[2]) / 2 for d in days) / n_days, tmin=min(d[1] for d in days),
                             rain=sum(d[3] for d in days), sun=sum(d[4] for d in days) / n_days,
                             hum=sum(d[5] for d in days) / n_days, tmax=sum(d[2] for d in days) / n_days))
        plot_m, supp_week = {}, {}
        for p, info in plot_info.items():
            s = summ[info["site"]]
            rain_term = 0.0 if info["glass"] else min(0.8, s["rain"] / 30)
            plot_m[p] = max(0.0, min(1.4, (IRRIGATION[info["irr"]] + random.gauss(0, 0.04) + rain_term)
                                     * RETENTION[info["soil"]]))
        month = d0.month
        for pl in plants:
            if not pl["alive"] or pl["planted"] > d6:
                continue
            sp, info = pl["sp"], plot_info[pl["plot"]]
            s_idx = info["site"]
            s = summ[s_idx]
            age_days = (d0 - pl["planted"]).days
            # scheduled care
            for fd in fert_dates[pl["plot"]]:
                if d0 <= fd <= d6 and age_days > 14 and random.random() < 0.92:
                    qty = round(min(220, 30 + 0.05 * sp["H"]) * random.uniform(0.8, 1.2), 0)
                    add_treatment(pl, fd + timedelta(days=random.randint(0, 4)), "Fertiliser",
                                  random.choice(PRODUCTS["Fertiliser"]), qty, round(qty * 0.012, 2), info["staff"])
                    pl["nutrient"] = min(1.0, pl["nutrient"] + 0.5)
            if sp["form"] in ("Shrub", "Climber", "Tree") and month == 2 and 7 <= d0.day <= 21 and age_days > 60:
                if pl["last_prune"] != d0.year and random.random() < 0.9:
                    pl["last_prune"] = d0.year
                    add_treatment(pl, d0 + timedelta(days=random.randint(0, 6)), "Pruning", None, None,
                                  round(random.uniform(3.5, 9.0), 2), info["staff"])
                    if sp["form"] != "Tree" and pl["h"] > 0.4 * sp["H"]:
                        pl["h"] *= random.uniform(0.80, 0.92)
            supp = 0.0
            if not info["glass"] and info["irr"] in ("Rain-fed", "Manual") and s["rain"] < 5 and s["tmax"] > 20 \
                    and random.random() < 0.4:
                qty = round(random.uniform(500, 3500) * (0.5 + sp["H"] / 600) ** 0.5, 0)
                add_treatment(pl, d0 + timedelta(days=random.randint(0, 6)), "Supplementary Watering",
                              random.choice(PRODUCTS["Supplementary Watering"]), qty, round(qty * 0.0004, 2), info["staff"])
                supp = 0.35
            # growth
            t_opt, w_low, w_high = TEMP_RESPONSE[info["habitat"]]
            f_t = math.exp(-(((s["tmean"] - t_opt) / (w_low if s["tmean"] < t_opt else w_high)) ** 2))
            f_sun = 0.3 + 0.7 * min(1.0, s["sun"] / 9)
            f_expo = math.exp(-(((EXPOSURE[info["sun"]] - LIGHT_NEED[sp["light"]]) / 0.45) ** 2))
            m = min(1.4, plot_m[pl["plot"]] + supp)
            f_w = math.exp(-(((m - WATER_NEED[sp["water"]]) / 0.5) ** 2))
            f_n = 0.6 + 0.4 * pl["nutrient"]
            f_h = 0.3 + 0.7 * pl["health"]
            g = sp["rate"] * GROWTH_SCALE * pl["indiv"] * f_t * f_sun * f_expo * f_w * f_n * f_h * 7 / 30
            pl["h"] = max(1.0, pl["h"] + g * pl["h"] * max(0.0, 1 - pl["h"] / sp["H"]))
            pl["nutrient"] = max(0.0, pl["nutrient"] - 0.02)
            # health
            stress = (0.5 + 0.5 * f_expo) * (0.4 + 0.6 * f_w) * (0.6 + 0.4 * math.sqrt(f_t))
            penalty = 0.0
            if pl["incident"]:
                inc = pl["incident"]
                if d0 > inc["resolve_by"]:
                    inc["rec"]["resolved"] = inc["resolve_by"]
                    pl["incident"] = None
                else:
                    penalty = PENALTY[inc["rec"]["severity"]]
            target = max(0.0, min(1.0, stress ** 0.8)) * (1 - penalty)
            pl["health"] += 0.3 * (target - pl["health"])
            # incidents
            if pl["incident"] is None:
                issue, p_hit = None, random.random()
                cands = []
                form = sp["form"]
                if not info["glass"] and s["tmin"] < sp["minT"]:
                    cands.append(("Frost Damage", min(1.0, 0.4 + 0.15 * (sp["minT"] - s["tmin"]))))
                if form in ("Herb", "Shrub", "Climber") and 4 <= month <= 8:
                    cands.append(("Aphids", 0.004 * (1.6 if pl["nutrient"] > 0.7 else 1.0)))
                if info["glass"] and s["tmax"] > 26 and s["hum"] < 62:
                    cands.append(("Spider Mite", 0.008))
                if info["habitat"] in ("tropical", "temperate", "arid"):
                    cands.append(("Mealybug", 0.002))
                if not info["glass"] and 6 <= month <= 9 and form in ("Herb", "Shrub", "Climber") and s["hum"] > 70:
                    cands.append(("Powdery Mildew", 0.004))
                if m > 1.1:
                    cands.append(("Root Rot", 0.012 * (1.5 if info["soil"] in ("Clay", "Peat") else 1.0)))
                if not info["glass"] and s["rain"] > 25 and month in (3, 4, 5, 9, 10, 11):
                    cands.append(("Leaf Spot", 0.005))
                if not info["glass"] and s["rain"] > 20 and pl["h"] < 0.15 * sp["H"]:
                    cands.append(("Slugs", 0.02))
                if info["sun"] == "Full" and sp["light"] != "High" and s["tmax"] > 25 and s["sun"] > 6:
                    cands.append(("Scorch", 0.01))
                random.shuffle(cands)
                for name, prob in cands:
                    if random.random() < prob:
                        issue = name
                        break
                if issue:
                    deficit = (sp["minT"] - s["tmin"]) if issue == "Frost Damage" else 0
                    if issue == "Frost Damage":
                        sev = "Mild" if deficit < 2 else "Moderate" if deficit < 5 else "Severe"
                    else:
                        sev = random.choices(["Mild", "Moderate", "Severe"],
                                             [60, 30, 10] if pl["health"] > 0.6 else [30, 40, 30])[0]
                    detected = d0 + timedelta(days=random.randint(0, 6))
                    kind = ISSUES[issue]
                    treat_key = None
                    lag = random.randint(0, 5)
                    treated = False
                    if kind == "pest" and random.random() < 0.85:
                        qty = round(random.uniform(30, 150), 0)
                        treat_key = add_treatment(pl, min(END, detected + timedelta(days=lag)), "Pest Control",
                                                  random.choice(PRODUCTS["Pest Control"]), qty, round(qty * 0.05, 2),
                                                  random.choice(care_staff))
                        treated = True
                    elif issue in ("Powdery Mildew", "Leaf Spot") and random.random() < 0.8 or \
                            issue == "Root Rot" and random.random() < 0.4:
                        qty = round(random.uniform(30, 120), 0)
                        treat_key = add_treatment(pl, min(END, detected + timedelta(days=lag)), "Fungicide",
                                                  random.choice(PRODUCTS["Fungicide"]), qty, round(qty * 0.06, 2),
                                                  random.choice(care_staff))
                        treated = True
                    elif issue == "Frost Damage" and random.random() < 0.5:
                        treat_key = add_treatment(pl, min(END, detected + timedelta(days=lag + 7)), "Pruning", None, None,
                                                  round(random.uniform(3.5, 9.0), 2), random.choice(care_staff))
                        treated = True
                    factor = {"Mild": 1.0, "Moderate": 1.4, "Severe": 2.0}[sev]
                    days = (random.randint(7, 21) if treated else random.randint(21, 70)) * factor
                    rec = dict(plant=pl["id"], by=random.choice(survey_staff), treat=treat_key, issue=issue, severity=sev,
                               detected=detected, resolved=None)
                    incidents.append(rec)
                    pl["incident"] = dict(rec=rec, resolve_by=detected + timedelta(days=int(days)))
                    if issue == "Frost Damage" and deficit > 6 and random.random() < 0.5:
                        pl["health"] = 0.0
            # ending of life
            end_day = max(d0 + timedelta(days=random.randint(0, n_days - 1)), pl["planted"] + timedelta(days=1))
            if pl["life_days"] and age_days > pl["life_days"]:
                pl.update(alive=False, status="Removed", end=end_day)
            else:
                p_die = 0.0004 + 0.05 * max(0.0, 0.30 - pl["health"]) + (0.004 if pl["incident"] and
                                                                         pl["incident"]["rec"]["severity"] == "Severe" else 0)
                if pl["health"] < 0.2 and random.random() < 0.10:
                    pl.update(alive=False, status="Removed", end=end_day)
                elif random.random() < p_die:
                    pl.update(alive=False, status="Dead", end=end_day)
            if not pl["alive"] and pl["incident"]:
                pl["incident"] = None
            # monthly survey
            for sd in surveys[s_idx]:
                if d0 <= sd <= d6 and sd > pl["planted"] and (pl["end"] is None or sd < pl["end"]):
                    form = sp["form"]
                    h = pl["h"]
                    if not info["glass"] and not sp["green"] and form in ("Herb", "Fern", "Grass"):
                        h *= DIEBACK[sd.month]
                    h = max(1.0, h * random.gauss(1, 0.01))
                    a, b = STEM[form]
                    leaf = LEAF[form] * h ** 0.9 * max(0.2, pl["health"]) * random.lognormvariate(0, 0.12)
                    if not info["glass"] and not sp["green"] and form in ("Tree", "Shrub", "Climber"):
                        leaf *= {11: 0.4, 12: 0.05, 1: 0.03, 2: 0.03, 3: 0.2, 4: 0.7}.get(sd.month, 1.0)
                    spad = 18 + 38 * max(0.0, pl["health"]) * (0.8 + 0.2 * pl["nutrient"]) + random.gauss(0, 2.0)
                    score = 5 if pl["health"] > 0.85 else 4 if pl["health"] > 0.70 else 3 if pl["health"] > 0.50 else \
                        2 if pl["health"] > 0.30 else 1
                    if random.random() < 0.10:
                        score = min(5, max(1, score + random.choice((-1, 1))))
                    if info["habitat"] in ("tropical", "arid"):
                        bloom = random.random() < 0.30
                    else:
                        bloom = sd.month in BLOOM[form]
                        bloom = bloom and random.random() < 0.8
                    flowering = int(FAMILIES[sp["fam"]][1] and bloom and pl["h"] > 0.3 * sp["H"] and pl["health"] > 0.5)
                    measurements.append((pl["id"], random.choice(survey_team[s_idx]), sd.isoformat(), round(h, 1),
                                         round(a * h ** b * random.gauss(1, 0.04), 1), int(round(leaf)),
                                         round(min(70, max(8, spad)), 1), score, flowering))

    # --------------------------------------------------------- id assignment
    end_of = {p["id"]: p["end"] for p in plants}
    dropped = {t["key"] for t in treatments if end_of[t["plant"]] and t["date"] > end_of[t["plant"]]}
    treatments = [t for t in treatments if t["key"] not in dropped]  # nothing is done to a plant after it has gone
    treatments.sort(key=lambda t: (t["date"], t["plant"], t["type"]))
    t_id = {t["key"]: i for i, t in enumerate(treatments, start=1)}
    treatment_rows = [(i, t["plant"], t["staff"], t["date"].isoformat(), t["type"], t["product"], t["qty"], t["cost"])
                      for i, t in enumerate(treatments, start=1)]
    incidents.sort(key=lambda r: (r["detected"], r["plant"]))
    incident_rows = [(i, r["plant"], r["by"], t_id.get(r["treat"]), r["issue"], r["severity"],
                      r["detected"].isoformat(), r["resolved"].isoformat() if r["resolved"] else None)
                     for i, r in enumerate(incidents, start=1)]
    measurements.sort(key=lambda m: (m[2], m[0]))
    measurement_rows = [(i,) + m for i, m in enumerate(measurements, start=1)]
    plant_rows = [(p["id"], p["sp"]["id"], p["plot"], f"EBG-{p['id']:05d}", p["planted"].isoformat(), p["origin"],
                   p["h0"], p["status"], p["end"].isoformat() if p["end"] else None) for p in plants]
    weather_rows = [(s_idx + 1, d.isoformat(), tmin, tmax, rain, sun, hum)
                    for s_idx, rows in enumerate(wx) for d, tmin, tmax, rain, sun, hum in rows]

    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript(SCHEMA)
    con.executemany("INSERT INTO families VALUES (?,?,?,?)",
                    [(fam_id[f], f, FAMILIES[f][0], FAMILIES[f][1]) for f in fam_names])
    con.executemany("INSERT INTO species VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    [(s["id"], fam_id[s["fam"]], s["sci"], s["common"], s["form"], s["life"], s["native"], s["light"],
                      s["water"], s["minT"], s["H"], s["green"], s["toxic"]) for s in species])
    con.executemany("INSERT INTO sites VALUES (?,?,?,?,?,?,?)", sites)
    con.executemany("INSERT INTO staff VALUES (?,?,?,?,?,?,?)", staff)
    con.executemany("INSERT INTO plots VALUES (?,?,?,?,?,?,?,?,?)", plots)
    con.executemany("INSERT INTO plants VALUES (?,?,?,?,?,?,?,?,?)", plant_rows)
    con.executemany("INSERT INTO weather_daily VALUES (?,?,?,?,?,?,?)", weather_rows)
    con.executemany("INSERT INTO growth_measurements VALUES (?,?,?,?,?,?,?,?,?,?)", measurement_rows)
    con.executemany("INSERT INTO treatments VALUES (?,?,?,?,?,?,?,?)", treatment_rows)
    con.executemany("INSERT INTO incidents VALUES (?,?,?,?,?,?,?,?)", incident_rows)
    con.commit()

    print("Rows per table")
    for t in ("families", "species", "sites", "staff", "plots", "plants", "weather_daily", "growth_measurements",
              "treatments", "incidents"):
        print(f"  {t:<22}{con.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]:>8}")
    print("Integrity check:", con.execute("PRAGMA integrity_check").fetchone()[0])
    print("Foreign key violations:", len(con.execute("PRAGMA foreign_key_check").fetchall()))
    print("Measurements outside a plant's life:", con.execute("""
        SELECT COUNT(*) FROM growth_measurements g JOIN plants p ON p.plant_id = g.plant_id
        WHERE g.measure_date <= p.planted_date OR (p.end_date IS NOT NULL AND g.measure_date >= p.end_date)""").fetchone()[0])

    print("\nPlant status by site")
    print(f"  {'site':<24}{'plants':>7}{'alive':>7}{'dead':>6}{'removed':>9}")
    for row in con.execute("""
        SELECT s.site_name, COUNT(*), SUM(p.status = 'Alive'), SUM(p.status = 'Dead'), SUM(p.status = 'Removed')
        FROM plants p JOIN plots pl ON pl.plot_id = p.plot_id JOIN sites s ON s.site_id = pl.site_id
        GROUP BY s.site_id"""):
        print(f"  {row[0]:<24}{row[1]:>7}{row[2]:>7}{row[3]:>6}{row[4]:>9}")
    con.close()


if __name__ == "__main__":
    main()
