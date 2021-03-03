import numpy as np
from sklearn.preprocessing import normalize

import sys, json, os


np.set_printoptions(threshold=sys.maxsize)


def _count_genres(data):
    genres = {}

    for movie in data:
        for genre in movie["genres"]:
            count = genres.get(genre, 0)
            genres[genre] = count + 1
    return genres


def get_vector(movie_vectors):
    avg = np.average(movie_vectors, axis=0)
    return normalize([avg], norm="l1")[0]


def vectorize():
    with open("../all_movies_filtered.json") as file:
        data = json.load(file)
    
    genres = sorted([g.lower() for g in _count_genres(data)])

    vectorized = {
        "emotion_order": [
            "anger",
            "anticipation",
            "disgust",
            "fear",
            "joy",
            "sadness",
            "surprise",
            "trust"
        ],
        "genre_order": genres,
        "movies": []
    }

    for file in os.listdir("output"):
        movie = None
        for mo in data:
            if mo["title"].replace(" ", "_") == file[4:-4]:
                movie = mo

        with open("output\\%s" % file, "rb") as f:
            emotions = np.load(f)
        vector = get_vector(emotions)

        gs = []

        m_gs = [g.lower() for g in movie["genres"]]

        for g in genres:
            if g in m_gs:
                gs.append(1)
            else:
                gs.append(0)

        vectorized["movies"].append({
            "title": file[:-4],
            "genres": list(gs),
            "vector": list(vector)
        })
    
    with open("nvid_vect.json", "w") as file:
        json.dump(vectorized, file, indent=2)
    

if __name__ == "__main__":
    vectorize()


# set CUDA_VISIBLE_DEVICES=""
# python sd/run_classifier.py --load mlstm_semeval.clf --data test.csv --model "mlstm" --text-key sentence
# anger, anticipation, disgust, fear, joy, sadness, surprise, trust
