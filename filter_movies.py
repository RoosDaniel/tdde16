import json
from os import remove


INPUT = "all_movies.json"
OUTPUT = "all_movies_filtered.json"


def _count_genres(data):
    genres = {}

    for movie in data:
        for genre in movie["genres"]:
            count = genres.get(genre, 0)
            genres[genre] = count + 1
    return genres


def remove_outside_genre_threshold(data, upper, lower):
    genres_counts = _count_genres(data)
    
    print("Removing lower than %s and higher than %s" % (lower, upper))
    print("# movies before: %s" % len(data))
    print("Genres before:", json.dumps(genres_counts, indent=2), sep="\n")

    to_return = []
    
    for movie in data:
        genres_to_keep = []
        for genre in movie["genres"]:
            if genres_counts[genre] >= lower and genres_counts[genre] <= upper:
                genres_to_keep.append(genre)

        movie["genres"] = genres_to_keep

        if len(movie["genres"]) != 0:
            to_return.append(movie)
    
    genres_counts = _count_genres(to_return)
    
    print("# movies after: %s" % len(to_return))
    print("Genres after:", json.dumps(genres_counts, indent=2), sep="\n")

    return to_return


def keep_specific_genres(data, to_keep):
    genres_counts = _count_genres(data)
    
    print("Keeping only specific genres")
    print("# movies before: %s" % len(data))
    print("Genres before:", json.dumps(genres_counts, indent=2), sep="\n")

    to_return = []

    for movie in data:
        genres_keep = set(movie["genres"]).intersection(to_keep)
        if genres_keep:
            movie["genres"] = list(genres_keep)
            to_return.append(movie)
    
    genres_counts = _count_genres(to_return)
    
    print("# movies after: %s" % len(to_return))
    print("Genres after:", json.dumps(genres_counts, indent=2), sep="\n")

    return to_return


def transform_genres(data):
    to_return = []

    for movie in data:
        genres = []
        for genre in movie["genres"]:
            if not genre:
                continue
            if "." in genre:
                gs = genre.split(".")
                for g in gs:
                    genres.append(g.strip().lower())
            else:
                genres.append(genre.strip().lower())

        movie["genres"] = genres

        if len(movie["genres"]) != 0:
            to_return.append(movie)

    return to_return


if __name__ == "__main__":
    with open(INPUT) as file:
        data = json.load(file)
    
    data = transform_genres(data)
    data = remove_outside_genre_threshold(data, 400, 200)

    with open(OUTPUT, "w") as file:
        json.dump(data, file)
