import json


# This is extremely ugly. Uses previously generated data and simply replaces all "emotions" with "embeddings"
# or concatenates. GENERATE NRC AND EMB DATA FIRST.
NRC = "../nrc/nrc_vect.json"
EMBS = "dist_vect.json"
OUT = "ob_vect.json"


with open(NRC) as file:
    nrc = json.load(file)

with open(EMBS) as file:
    embs = json.load(file)

res = {
    "genre_order": nrc["genre_order"],
    "movies": [{"genres": m.pop("genres")} for m in nrc["movies"]]
}


for i, movie in enumerate(res["movies"]):
    movie["emotions_embeddings"] = nrc["movies"][i]["emotions"] + embs["movies"][i]["embeddings"]

with open(OUT, "w") as file:
    json.dump(res, file, indent=2)
