"""Game recommendation logic"""

import random
from collections import defaultdict
from sqlalchemy import select
from proekt.models import VideoGame, Review, Collection, DefaultCollection, User

HIGH_RATING = 4
LOW_RATING = 2
RECOM_COUNT = 5
POOL_SIZE = 10

def like_or_dislike_genre(session, user_id):
    user_reviews = session.scalars(select(Review).where(Review.user_id == user_id)).all()

    genre_ratings = defaultdict(list)
    for review in user_reviews:
        for genre in review.game.genres:
            genre_ratings[genre.id].append(review.rating)

    liked_genres = set()
    disliked_genres = set()
    for genre_id, ratings in genre_ratings.items():
        avg = sum(ratings) / len(ratings)
        if avg >= HIGH_RATING:
            liked_genres.add(genre_id)
        elif avg <= LOW_RATING:
            disliked_genres.add(genre_id)

    return (liked_genres, disliked_genres)

def excluded_games(session, user_id):
    playing_and_completed = session.scalars(
        select(Collection).where(
            Collection.user_id == user_id,
            Collection.default_type.in_([DefaultCollection.PLAYING,
                                         DefaultCollection.COMPLETED]))).all()

    excluded = set()
    for collection in playing_and_completed:
        for game in collection.games:
            excluded.add(game.id)

    return excluded

def compute_recommendations(session, user_id):

    user = session.get(User, user_id)
    liked_genres, disliked_genres = like_or_dislike_genre(session, user_id)
    exclude = excluded_games(session, user_id)
    friend_ids = {friend.id for friend in user.friends}

    all_games = session.scalars(select(VideoGame)).all()

    game_weights = []
    for game in all_games:
        if game.id in exclude:
            continue

        rating = game.average_rating
        if rating is None:
            continue

        genre_ids = {genre.id for genre in game.genres}
        has_liked_genre = bool(genre_ids & liked_genres)
        weight = 0

        if has_liked_genre and rating >= HIGH_RATING:
            weight += 3

        friend_ratings = [r for r in game.reviews
                               if r.user_id in friend_ids and r.rating >= HIGH_RATING]
        if friend_ratings:
            weight += 2 * len(friend_ratings)

        is_disliked = bool(genre_ids & disliked_genres)

        if not is_disliked and rating >= HIGH_RATING:
            weight += 1

        if weight > 0:
            game_weights.append((weight, game))

    if not game_weights:
        return []

    game_weights.sort(key=lambda pair: pair[0], reverse=True)
    pool = [game for _, game in game_weights[:POOL_SIZE]]
    random.shuffle(pool)

    return pool[:RECOM_COUNT]
