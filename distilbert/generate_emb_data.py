import json


# This is extremely ugly. Uses previously generated data and simply replaces all "emotions" with "embeddings"
# or concatenates. GENERATE NRC FIRST.
NRC = "../nrc/nrc_vect.json"
EMBS = "avg_embs_out.json"
OUT = "dist_vect.json"


with open(NRC) as file:
    nrc = json.load(file)

with open(EMBS) as file:
    embs = json.load(file)

res = {
    "genre_order": nrc["genre_order"],
    "movies": [{"genres": m.pop("genres")} for m in nrc["movies"]]
}


for movie, emb in zip(res["movies"], embs):
    movie["embeddings"] = emb

with open(OUT, "w") as file:
    json.dump(res, file, indent=2)
