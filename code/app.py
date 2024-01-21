from flask import Flask, render_template, redirect, url_for, request, flash
from forms import ReviewForm
import redis
import sqlite3
import pymongo
import os

SECRET_KEY = os.urandom(32)

redis_db = redis.Redis(host="localhost", port=6379, decode_responses=True)

mongo_client = pymongo.MongoClient("mongodb://admin:admin@localhost:27017")
mongo_db = mongo_client["trackrate_db"]
reviews_collection = mongo_db["reviews"]

app = Flask(__name__, template_folder="templates")
app.config["SECRET_KEY"] = SECRET_KEY


def review_check(review_name):
    check_review = ""
    for i in reviews_collection.find({}, {"review_name": review_name}):
        check_review = i["review_name"]
    return check_review


def singer_check(singer_from_review):
    check_singer = ""
    conn = sqlite3.connect("trackrate.db")
    cur = conn.cursor()
    query_check = cur.execute(f"SELECT singer_name FROM singers WHERE singer_name = '{singer_from_review}'")
    for i in query_check:
        for j in i:
            check_singer = j
    return check_singer


def song_check(singer_from_review, song_from_review):
    check_song = ""
    conn = sqlite3.connect("trackrate.db")
    cur = conn.cursor()
    results = cur.execute(f"SELECT singer_name, song_name FROM songs "
                          f"WHERE singer_name = '{singer_from_review}' "
                          f"AND song_name = '{song_from_review}'")
    for result in results:
        for row in result:
            check_song += row
    return check_song


def add_points(username, singer_name, song_name):
    scores = 0
    reviews = reviews_collection.find({"username": username,"singer": singer_name, "song": song_name},
                                      {"_id": 0, "lyrics": 1, "structure": 1, "performance": 1, "mixing": 1,
                                       "individuality": 1, "charisma": 1, "atmosphere": 1, "instrumental": 1})
    for review in reviews:
        for key, value in review.items():
            scores += int(value)

    conn = sqlite3.connect("trackrate.db")
    cur = conn.cursor()
    cur.execute(f"UPDATE singers SET scores = "
                f"(SELECT scores FROM singers WHERE singer_name = '{singer_name}') + {scores} "
                f"WHERE singer_name = '{singer_name}'")
    cur.execute(f"UPDATE songs SET scores = "
                f"(SELECT scores FROM songs WHERE singer_name = '{singer_name}' AND song_name = '{song_name}') "
                f"+ {scores} "
                f"WHERE singer_name = '{singer_name}' AND song_name = '{song_name}'")
    conn.commit()


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/make_review", methods=["GET", "POST"])
def make_review():
    review_form = ReviewForm()
    username = review_form.username.data
    singer = review_form.singer.data
    song = review_form.song.data
    review = review_form.review.data
    lyrics = review_form.lyrics.data
    structure = review_form.structure.data
    performance = review_form.performance.data
    mixing = review_form.mixing.data
    individuality = review_form.individuality.data
    charisma = review_form.charisma.data
    atmosphere = review_form.atmosphere.data
    instrumental = review_form.instrumental.data

    if review_form.validate_on_submit():
        review_name = f"{username}:{singer}:{song}:review"
        redis_db.hset(review_name, "review_name", review_name)
        redis_db.hset(review_name, "username", username)
        redis_db.hset(review_name, "singer", singer)
        redis_db.hset(review_name, "song", song)
        redis_db.hset(review_name, "review", review)
        redis_db.hset(review_name, "lyrics", str(lyrics))
        redis_db.hset(review_name, "structure", str(structure))
        redis_db.hset(review_name, "performance", str(performance))
        redis_db.hset(review_name, "mixing", str(mixing))
        redis_db.hset(review_name, "individuality", str(individuality))
        redis_db.hset(review_name, "charisma", str(charisma))
        redis_db.hset(review_name, "atmosphere", str(atmosphere))
        redis_db.hset(review_name, "instrumental", str(instrumental))
        redis_db.expire(review_name, 3600)

        flash("Your review successfully sent and under consideration")
        return redirect(url_for("make_review"))
    else:
        return render_template("make_review.html", form=review_form)


@app.route("/reviews_suggestions")
def reviews_suggestions():
    suggested_reviews = []
    hashes = redis_db.keys("*:review")
    for review_hash in hashes:
        suggested_reviews.append(redis_db.hgetall(review_hash))
    return render_template("reviews_suggestions.html", suggested_reviews=suggested_reviews)


@app.route("/publish_review", methods=["POST"])
def publish_review():
    suggested_reviews = []
    hashes = redis_db.keys("*:review")
    for review_hash in hashes:
        suggested_reviews.append(redis_db.hgetall(review_hash))

        review_to_publish = request.form.get("review_to_publish")

        for review in suggested_reviews:

            if review["review_name"] == review_to_publish:

                if review["review_name"] == review_check(review["review_name"]):
                    reviews_collection.delete_one({"review_name": review["review_name"]})
                    reviews_collection.insert_one(review)
                    suggested_reviews.remove(review)
                    redis_db.delete(review_hash)
                else:
                    reviews_collection.insert_one(review)
                    suggested_reviews.remove(review)
                    redis_db.delete(review_hash)

                if review["singer"] != singer_check(review["singer"]):
                    conn = sqlite3.connect("trackrate.db")
                    cur = conn.cursor()
                    cur.execute(f"INSERT INTO singers (singer_name, scores) VALUES ('{review['singer']}', 0)")
                    conn.commit()
                    conn.close()

                if review['singer']+review['song'] != song_check(review["singer"], review["song"]):
                    conn = sqlite3.connect("trackrate.db")
                    cur = conn.cursor()
                    cur.execute(f"INSERT INTO songs (singer_name, song_name, scores) "
                                f"VALUES ('{review['singer']}', '{review['song']}', 0)")
                    conn.commit()
                    conn.close()

                add_points(review["username"], review["singer"], review["song"])

    return render_template("reviews_suggestions.html", suggested_reviews=suggested_reviews)


@app.route("/reject_review", methods=["POST"])
def reject_review():
    suggested_reviews = []
    hashes = redis_db.keys("*:review")
    for review_hash in hashes:
        suggested_reviews.append(redis_db.hgetall(review_hash))

        review_to_reject = request.form.get("review_to_reject")
        for review in suggested_reviews:
            if review["review_name"] == review_to_reject:
                suggested_reviews.remove(review)
                redis_db.delete(review_hash)
                break

    return render_template("reviews_suggestions.html", suggested_reviews=suggested_reviews)


@app.route("/all_reviews")
def all_reviews():
    reviews_list = []
    reviews = reviews_collection.find()
    for review in reviews:
        reviews_list.append(review)
    return render_template("all_reviews.html", reviews=reviews_list)


@app.route("/all_singers")
def all_singers():
    conn = sqlite3.connect("trackrate.db")
    singers = conn.execute("SELECT * FROM singers")
    return render_template("all_singers.html", singers=singers)


@app.route("/all_songs")
def all_songs():
    conn = sqlite3.connect("trackrate.db")
    songs = conn.execute("SELECT * FROM songs")
    return render_template("all_songs.html", songs=songs)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
