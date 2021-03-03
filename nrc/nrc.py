import pandas as pd, numpy as np, matplotlib.pyplot as plt

import json, time, datetime

from sklearn.preprocessing import normalize
from sklearn.manifold import TSNE


MOVIE_FILE = "../all_movies_filtered.json"
TAGGED_FILE = "nrc_tagged.json"
DATA_FILE = "nrc_data.json"
VECTORIZED_FILE = "nrc_vect.json"

NRC_FILE = "nrc_affect_intensity.csv"


def _count_genres(data):
    genres = {}

    for movie in data:
        for genre in movie["genres"]:
            count = genres.get(genre, 0)
            genres[genre] = count + 1
    return genres


def _strip_punct(word):
    punct = ["\"", "'", ",", ".", "!", "?"]

    if not word:
        return None

    while word[-1] in punct:
        word = word[:-1]

        if not word:
            return None
    
    while word[0] in punct:
        word = word[1:]

        if not word:
            return None

    return word


def _process_one(movie, word_emotions_df):
    emotions = word_emotions_df.emotion.unique()
    emotive_words = word_emotions_df.word.unique()

    movie_emotions = {
        "title": movie["title"],
        "emotions": {
            e: {"count": 0, "sum": 0} for e in emotions
        },
        "total_words": 0
    }

    word_candicates = movie["script"].lower().split(" ")
    
    words = []

    for word in word_candicates:
        processed = _strip_punct(word)
        if not processed:
            continue
        if processed in emotive_words:
            words.append(processed)

    movie_emotions["total_words"] = len(words)

    for word in words:
        for row in word_emotions_df.loc[word_emotions_df.word == word].iterrows():
            emotion = row[1].emotion
            score = row[1].score

            new_count = movie_emotions["emotions"][emotion]["count"] + 1
            new_score = movie_emotions["emotions"][emotion]["sum"] + score

            movie_emotions["emotions"][emotion]["count"] = new_count
            movie_emotions["emotions"][emotion]["sum"] = new_score
    
    with open(TAGGED_FILE) as file:
        json_data = json.load(file)

    json_data.append(movie_emotions)

    with open(TAGGED_FILE, "w") as file:
        json.dump(json_data, file, indent=2)


def process_all_remaining():
    word_emotions_df = pd.read_csv(NRC_FILE, sep="\t").rename(columns={"emotion-intensity-score": "score"})

    with open(MOVIE_FILE) as file:
        all_movies = json.load(file)

    with open(TAGGED_FILE) as file:
        movies_emotions = json.load(file)
    
    to_process = []

    for m in all_movies:
        seen = False
        for processed in movies_emotions:
            if m["title"] == processed["title"]:
                seen = True
                break
        if not seen:
            to_process.append(m)
    
    del all_movies

    total_len = len(to_process)

    start = time.time()
    est_done = None

    for i, movie in enumerate(to_process):
        print("Processing: %s/%s, %s words. Est. done: %s" % (
            i+1, total_len, len(movie["script"].split(" ")), est_done or "Calculating..."
        ) + " "*10, end="\r")
        _process_one(movie, word_emotions_df)
        end = time.time()

        time_p_doc = (end-start)/(i+1)
        est_done = datetime.datetime.fromtimestamp(end+time_p_doc*(len(to_process)-i)).strftime("%H:%M:%S")


def add_scores():
    with open(TAGGED_FILE) as file:
        nrc_tagged = json.load(file)

    for movie in nrc_tagged:
        for _, emotion in movie["emotions"].items():
            if emotion["sum"] > 0:
                score = emotion["sum"] / movie["total_words"]
            else:
                score = 0
            emotion["score"] = score

    with open(TAGGED_FILE, "w") as file:
        json.dump(nrc_tagged, file, indent=2)


def generate_data():
    with open(TAGGED_FILE) as file:
        nrc_tagged = json.load(file)
    
    with open(MOVIE_FILE) as file:
        all_movies = json.load(file)
    
    return_data = []

    for i, movie in enumerate(nrc_tagged):
        genres = []
        emotions = []

        for m in all_movies:
            if m["title"] == movie["title"]:
                genres = [g.lower() for g in m["genres"]]

        for emotion, data in movie["emotions"].items():
            emotions.append({"emotion": emotion.strip(), "score": data["score"]})

        if genres:
            return_data.append({
                "id": i,
                "title": movie["title"],
                "genres": genres,
                "emotions": emotions
            })
    
    with open(DATA_FILE, "w") as file:
        json.dump(return_data, file, indent=2)


def vectorize_data():
    vectorized = {"movies": []}

    with open(DATA_FILE) as file:
        data_file = json.load(file)
    
    genres = sorted(_count_genres(data_file).keys())
    vectorized["genre_order"] = list(genres)

    word_emotions_df = pd.read_csv(NRC_FILE, sep="\t")
    emotions = word_emotions_df.emotion.unique()
    vectorized["emotion_order"] = list(emotions)

    for i, movie in enumerate(data_file):
        m = {
            "title": str(i).zfill(3) + "_" + movie["title"].replace(" ", "_"),
            "genres": [],
            "emotions": [],
        }

        for genre in genres:
            if genre in movie["genres"]:
                m["genres"].append(1)
            else:
                m["genres"].append(0)
        for emotion in emotions:
            movie_emotion = [e for e in movie["emotions"] if e["emotion"] == emotion][0]
            m["emotions"].append(movie_emotion["score"])
        
        m["emotions"] = list(normalize([m["emotions"]], norm="l1")[0])

        vectorized["movies"].append(m)
    
    with open(VECTORIZED_FILE, "w") as file:
        json.dump(vectorized, file, indent=2, sort_keys=True)


if __name__ == "__main__":
    # process_all_remaining()
    # add_scores()
    # generate_data()
    vectorize_data()
