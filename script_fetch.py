import re, json, concurrent.futures

import requests
from bs4 import BeautifulSoup
import pandas as pd


def fetch_script(url):
    soup = BeautifulSoup(requests.get(url).text, features="html.parser")
    if not soup:
        return
    
    try:
        script = soup.find("td", {"class": "scrtext"}).find("pre").get_text(separator=" ")
    except AttributeError:
        return None

    return re.sub(r"\s+", " ", script)


def fetch_from_movie(i, title, href):
    soup = BeautifulSoup(requests.get(href).text, features="html.parser")

    script_details = soup.find("table", {"class": "script-details"})

    if script_details is None:
        return None

    script_url = None
    genres = []
    
    for a in script_details.find_all("a", href=True):
        href = a['href']
        if href.startswith("/scripts/"):
            script_url = "https://imsdb.com" + href
        if href.startswith("/genre"):
            genres.append(a.text)
    
    if not script_url and genres:
        return None
    
    script = fetch_script(script_url)

    if not script:
        return None

    print("Fetched #%s: %s. Genres: %s" % (i+1, title, ", ".join(genres)))

    return {
        "title": title,
        "genres": genres,
        "script": script,
    }


def fetch_all():
    url = "https://imsdb.com/all-scripts.html"
    soup = BeautifulSoup(requests.get(url).text, features="html.parser")
    soup = soup.select_one("#mainbody > table:nth-of-type(2) > tr > td:nth-of-type(1) > td:nth-of-type(2)")

    hrefs = []

    for a in soup.find_all("a", href=True):
        href = a['href']

        if href.startswith("/Movie Scripts"):
            title = a.text
            hrefs.append((title, "https://imsdb.com%s" % href))
    
    print("Total titles found: %s" % len(hrefs))

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        res = []

        for i, (title, href) in enumerate(hrefs):
            res.append(executor.submit(fetch_from_movie, i, title, href))
        
        concurrent.futures.wait(res)
    
    res = [r.result() for r in res]
    res = [r for r in res if r is not None]  # Remove invalid
    
    with open("all_movies.json", "w", encoding="utf-8") as file:
        json.dump(res, file, indent=2)


if __name__ == "__main__":
    fetch_all()
