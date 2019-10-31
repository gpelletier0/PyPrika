#!/usr/bin/python3

from scraper import struct, scrape

if __name__ == '__main__':
    """
    Main
    """
    oScrape = scrape(
        name=struct("h1", "hidden-xs"),
        photo=struct("div", "hero-wrapper"),
        notes=struct("div", "recipe-intro"),
        servings=struct("div", "recipe-detail serves"),
        cook_time=struct("div", "recipe-detail time"),
        categories=struct("div", "tags-list"),
        nutritional=struct("ul", "nutrition-list"),
        ingredients=struct("ul", "ingred-list"),
        directions=struct("div", "method-p")
    )

    oScrape.run("jamieoliver")
