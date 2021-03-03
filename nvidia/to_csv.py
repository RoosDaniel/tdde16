import json


MOVIES = "../all_movies_filtered.json"

with open(MOVIES) as file:
    movies = json.load(file)


for i, movie in enumerate(movies):
    print(i)
    to_csv = "sentence" + "\n" + "\n".join([s for s in movie["script"].split(". ")])

    with open("movies/%s_%s.csv" % (str(i).zfill(3), movie["title"].replace(" ", "_").replace(":", "")), "w", encoding="utf-8") as file:
        file.write(to_csv)
