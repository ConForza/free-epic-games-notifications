# imports
import operator
import datetime as dt
import requests
import os
from epicstore_api import EpicGamesStoreAPI

TOKEN = os.environ.get("TOKEN")
DISCORD_URI = os.environ.get("DISCORD_URI")

# Discord header
header = {
    "Content-Type": "application/json",
    "Authorization": f"Bot {TOKEN}"
}

# Initialize Epic API
api = EpicGamesStoreAPI(locale="en-US", country="GB")
free_games = api.get_free_games()['data']['Catalog']['searchStore']['elements']

free_games = sorted(
    filter(lambda g: g.get('promotions'), free_games),
    key=operator.itemgetter('title'),
)

# Iterate free games, getting information about game
for game in free_games:
    game_price = game['price']['totalPrice']['fmtPrice']['originalPrice']
    game_price_promo = game['price']['totalPrice']['fmtPrice']['discountPrice']
    game_title = game['title']
    game_url = ""
    if game["urlSlug"]:
        if game['offerType'] == "BUNDLE":
            game_url = f"https://store.epicgames.com/en-US/bundles/{game['urlSlug']}"
        else:
            game_url = f"https://store.epicgames.com/en-US/p/{game['urlSlug']}"

    game_promotions = game['promotions']['promotionalOffers']

    # Check to see if game is in fact free
    if game_promotions and game['price']['totalPrice']['discountPrice'] == 0:
        start_date = dt.datetime.fromisoformat(game_promotions[0]['promotionalOffers'][0]['startDate'][:-1])
        end_date = dt.datetime.fromisoformat(game_promotions[0]['promotionalOffers'][0]['endDate'][:-1])
        thumbnail_url = game['keyImages'][2]["url"]

        # Only show games that have gone on sale today
        if start_date.date() == dt.date.today():
            message = f'***{game_title} ({game_price}) is FREE now, until {end_date}***\n{game_url}'
            # Initialize Discord message. Contains title, description, price, and thumbnail image
            parameters = {
                "content": f"{message}",
                "embeds": [{
                    "description": game["description"],
                    "image": {
                        "url": thumbnail_url
                    }
                }]
            }

            # Send discord message to server channel, so that all members get notified of new free games
            requests.post(url=DISCORD_URI, json=parameters, headers=header)
