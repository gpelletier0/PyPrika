#!/usr/bin/python3
import string
import errno
import gzip
from os import path, rename, remove, mkdir
from zipfile import ZipFile
import json


class pyprika_recipe:
    def __init__(self):
        self.name = ""
        self.cook_time = ""
        self.photo = ""
        self.photo_large = ""
        self.photo_hash = ""
        self.photo_data = ""
        self.photos = []
        self.total_time = ""
        self.prep_time = ""
        self.notes = ""
        self.servings = ""
        self.created = ""
        self.source = ""
        self.source_url = ""
        self.rating = 0
        self.uid = ""
        self.image_url = None
        self.directions = ""
        self.nutritional_info = ""
        self.categories = []
        self.source = ""
        self.description = ""
        self.ingredients = ""
        self.difficulty = ""
        self.hash = ""

    def get_dict(self):
        """
        :return: Serialize dictionary to a JSON formatted string
        """
        data = {}
        if self.name:
            data.update({"name": self.name})
        if self.cook_time:
            data.update({"cook_time": self.cook_time})
        if self.photo:
            data.update({"photo": self.photo})
        if self.photo_large:
            data.update({"photo_large": self.photo_large})
        if self.photo_hash:
            data.update({"photo_hash": self.photo_hash})
        if self.photo_data:
            data.update({"photo_data": self.photo_data})
        if self.photos:
            data.update({"photos": self.photos})
        if self.total_time:
            data.update({"total_time": self.total_time})
        if self.prep_time:
            data.update({"prep_time": self.prep_time})
        if self.notes:
            data.update({"notes": self.notes})
        if self.servings:
            data.update({"servings": self.servings})
        if self.created:
            data.update({"created": self.created})
        if self.source:
            data.update({"source": self.source})
        if self.source_url:
            data.update({"source_url": self.source_url})
        if self.rating:
            data.update({"rating": self.rating})
        if self.uid:
            data.update({"uid": self.uid})
        if self.image_url:
            data.update({"image_url": self.image_url})
        if self.directions:
            data.update({"directions": self.directions})
        if self.nutritional_info:
            data.update({"nutritional_info": self.nutritional_info})
        if self.categories:
            data.update({"categories": self.categories})
        if self.source:
            data.update({"source": self.source})
        if self.description:
            data.update({"description": self.description})
        if self.ingredients:
            data.update({"ingredients": self.ingredients})
        if self.difficulty:
            data.update({"difficulty": self.difficulty})
        if self.hash:
            data.update({"hash": self.hash})

        return json.dumps(data)


def get_path():
    """
    :return: Returns relative path of this file's location
    """
    return path.dirname(path.realpath(__file__)) + "/"


def make_dir(fpath):
    """
    Checks if path exists and creates one if it doesn't
    :param fpath:
    """
    if not path.exists(fpath):
        mkdir(path)


def get_filepath(filename):
    """
    :param filename:
    :return: relative path of file
    """
    return get_path() + filename


def format_filename(filename):
    """
    Formats filename to remove invalid characters
    :param filename:
    :return: filename without invalid characters
    """
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    formated_filename = ''.join(char for char in filename if char in valid_chars)
    # formated_filename = filename.replace(' ','_') # remove spaces in filenames.
    return formated_filename


def remove_file(filename):
    """
    Deletes file
    :param filename: file to remove
    """
    try:
        remove(filename)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise


def rename_file(filename, renamed):
    """
    Renames file
    :param filename: file to rename
    :param renamed: string to rename file to
    """
    try:
        rename(filename, renamed)
    except OSError:
        remove_file(filename)


class pyprika_files:
    """
    Paprika App file formats
    """
    __recipe_extension = ".paprikarecipe"
    __recipes_extension = ".paprikarecipes"
    __gzip_extension = ".gz"

    def __init__(self):
        make_dir(get_path())
        self.recipes_file = ""

    def get_recipe_extension(self):
        """
        :return: file extension string for recipe file
        """
        return self.__recipe_extension

    def get_recipes_extension(self):
        """
        :return: file extension string for recipes file
        """
        return self.__recipes_extension

    def get_gzip_extension(self):
        """
        :return: gzip extension string
        """
        return self.__gzip_extension

    def get_gz_file(self, filename):
        """
        :param filename: file name without extension
        :return: file path of filename with gzip extension string
        """
        return get_filepath(filename) + self.__gzip_extension

    def get_paprika_file(self, filename):
        """
        :param filename: file name without extension
        :return: file path of filename with paprika extension string
        """
        return get_filepath(filename) + self.__recipe_extension

    def get_recipes_file(self):
        """
        :return: file path of recipes import file with recipe extension string
        """
        pfile = get_path() + "recipes_import" + self.__recipes_extension
        if self.recipes_file:
            pfile = get_path() + self.recipes_file + self.__recipes_extension
        return pfile

    def add_to_pyprikarecipes(self, name, dic):
        """
        Adds recipe gzip file to paprika recipes zip file
        :param name:
        :param dic:
        """
        filename = format_filename(name)
        gzfile = self.get_gz_file(filename)
        paprikafile = self.get_paprika_file(filename)

        with gzip.GzipFile(gzfile, 'w') as fout:
            fout.write(dic)

        if path.exists(gzfile):
            rename_file(gzfile, paprikafile)

            with ZipFile(self.get_recipes_file(), "a") as fzip:
                if path.basename(paprikafile) not in fzip.namelist():
                    fzip.write(paprikafile, path.basename(paprikafile))
                    print(f"Saved : {name}")
                else:
                    print(f"Skipped : {name}")

            remove_file(paprikafile)
