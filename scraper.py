#!/usr/bin/python3

import time
import base64
import sql
from requests import get
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from collections import namedtuple
from pyprika_classes import pyprika_files, pyprika_recipe

struct = namedtuple("struct", ["type", "css"])


def ua():
    """
    Fake user agent
    :return: fake user agent chrome
    """
    u = UserAgent()
    return {'User-Agent': u.chrome}


class scrape:
    def __init__(self,
                 name: struct,
                 photo: struct,
                 ingredients: struct,
                 directions: struct,
                 cook_time=None,
                 servings=None,
                 notes=None,
                 nutritional=None,
                 categories=None,
                 photos=None,
                 rating=None):
        self.name = name
        self.photo = photo
        self.ingredients = ingredients
        self.directions = directions
        self.cook_time = cook_time
        self.servings = servings
        self.notes = notes
        self.nutritional = nutritional
        self.categories = categories
        self.photos = photos
        self.rating = rating

        "dictionary of servings strings to replace unwanted elements"
        self.servings_replace_str = {
            "Serves": "",
            " - ": "-"
        }

        "dictionary of cook time strings to replace unwanted elements"
        self.cooktime_replace_str = {
            "Cooks In": ""
        }

        "dictionary of note strings to replace unwanted elements"
        self.notes_replace_str = {
            "“": "",
            "”": ""
        }

    def get_servings(self, soup):
        """
        :param soup: BeautifulSoup element
        :return: serving information or empty string
        """
        if soup.find(self.servings.type, class_=self.servings.css):
            servings = soup.find(self.servings.type, class_=self.servings.css).text
            for key, val in self.servings_replace_str.items():
                servings = servings.lower().replace(key.lower(), val)
            return servings.strip()

        return ""

    def get_cooktime(self, soup):
        """
        :param soup: BeautifulSoup element
        :return: cook time information or empty string
        """
        if soup.find(self.cook_time.type, class_=self.cook_time.css):
            cooktime = soup.find(self.cook_time.type, class_=self.cook_time.css).text
            for key, val in self.cooktime_replace_str.items():
                cooktime = cooktime.lower().replace(key.lower(), val)
            return cooktime.strip()

        return ""

    def get_category(self, soup):
        """
        :param soup: BeautifulSoup element
        :return: category information or empty string
        """
        if soup.find(self.categories.type, class_=self.categories.css):
            return [a.text.title() for a in soup.find(self.categories.type, class_=self.categories.css).find_all("a")]

        return ""

    def get_image_url(self, soup):
        """
        :param soup: BeautifulSoup element
        :return: image url or None
        """
        if soup.find(self.photo.type, class_=self.photo.css):
            return "http:" + soup.find(self.photo.type, class_=self.photo.css).img["src"]

        return None

    def get_photo_data(self, image_url):
        """
        :param image_url: url of image
        :return: base64 encoded string of image
        """
        if image_url:
            return base64.b64encode(get(image_url, headers=ua()).content).decode()

        return ""

    def get_notes(self, soup):
        """
        :param soup: BeautifulSoup element
        :return: note information or empty string
        """
        if soup.find(self.notes.type, class_=self.notes.css):
            notes = soup.find(self.notes.type, class_=self.notes.css).text
            for key, val in self.notes_replace_str.items():
                notes = notes.lower().replace(key.lower(), val)
            return notes.strip()

        return ""

    def get_ingredients(self, soup):
        """
        :param soup: BeautifulSoup element
        :return: ingredients information or empty string
        """
        if soup.find_all(self.ingredients.type, class_=self.ingredients.css):
            return '\n'.join([" ".join(li.text.split()) for li in
                              soup.find(self.ingredients.type, class_=self.ingredients.css).find_all("li")])

        return ""

    def get_directions(self, soup):
        """
        :param soup: BeautifulSoup element
        :return: directions information or empty string
        """
        if soup.find(self.directions.type, class_=self.directions.css):
            return ''.join([" ".join(li.text.split()) + '\n\n' for li in
                            soup.find(self.directions.type, class_=self.directions.css).find_all("li")])

        return ""

    def get_nutritional_info(self, soup):
        """
        :param soup: BeautifulSoup element
        :return: nutritional information or empty string
        """
        if soup.find(self.nutritional.type, class_=self.nutritional.css):
            return '\n'.join([" ".join(li.text.split()) for li in
                              soup.find(self.nutritional.type, class_=self.nutritional.css).find_all("li")])

        return ""

    def run(self, table_name):
        """
        Scrapes recipe data from urls in database and saves information to Paprika App file format
        :param table_name: table name to iterate in database
        """
        db = sql.pyprika_db(table_name)
        pf = pyprika_files()

        if db.get_recipes_count() > 0:
            for row in db.get_recipes_rows():
                pf.recipes_file = row['source']

                try:
                    while True:
                        request = get(row['url'], headers=ua(), timeout=5)
                        soup = BeautifulSoup(request.text, 'lxml')
                        status_code = request.status_code
                        request.close()

                        if status_code == 403:  # error accessing url
                            time.sleep(30)

                        elif (status_code == 200 and
                              soup.find(self.name.type, class_=self.name.css)):

                            rcp = pyprika_recipe()

                            rcp.name = soup.find(self.name.type, class_=self.name.css).text.strip()
                            rcp.source = row['source']
                            rcp.source_url = row['url']
                            rcp.servings = self.get_servings(soup)
                            rcp.cook_time = self.get_cooktime(soup)
                            rcp.categories = self.get_category(soup)
                            rcp.image_url = self.get_image_url(soup)
                            rcp.photo_data = self.get_photo_data(rcp.image_url)
                            rcp.notes = self.get_notes(soup)
                            rcp.ingredients = self.get_ingredients(soup)
                            rcp.directions = self.get_directions(soup)
                            rcp.nutritional_info = self.get_nutritional_info(soup)

                            pf.add_to_pyprikarecipes(rcp.name, rcp.get_dict().encode("utf-8"))
                            db.set_recipe_scraped(row['id'])
                            time.sleep(1)
                            break
                        else:
                            print(f"Error reading : {row['url']}")
                            db.set_recipe_failed(row['id'])
                            break

                except Exception as ex:
                    print(ex)
                    pass
