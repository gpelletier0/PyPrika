#!/usr/bin/python3
import sqlite3


class pyprika_db:
    conn = sqlite3.connect("pyprika.sqlite3")
    conn.row_factory = sqlite3.Row

    def __init__(self, site_name):
        self.site_name = site_name  # table name

    def get_recipes_count(self):
        """
        :return: number of recipes in database that have not been scraped
        """
        return self.conn.execute(
            f"SELECT count(*) FROM {self.site_name}_rcp WHERE scraped = 0"
        ).fetchone()[0]

    def get_recipes_rows(self):
        """
        :return: id, source and url of all recipes that have not been scraped
        """
        return self.conn.execute(
            f"SELECT id, source, url FROM {self.site_name}_rcp WHERE scraped = 0"
        ).fetchall()

    def set_recipe_scraped(self, id):
        """
        Sets recipe scrape value to true (1)
        :param id: id of recipe
        """
        self.conn.execute(
            f"""UPDATE {self.site_name}_rcp SET scraped = ? WHERE id = ?""",
            (1, id)
        )
        self.conn.commit()

    def set_recipe_failed(self, id):
        """
        Sets recipe scrape value to failed (2)
        :param id: id of recipe
        """
        self.conn.execute(
            f"""UPDATE {self.site_name}_rcp SET scraped = ? WHERE id = ?""",
            (2, id)
        )
        self.conn.commit()
