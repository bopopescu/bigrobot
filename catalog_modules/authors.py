import cat_helpers


class Authors(object):
    _authors = None

    @classmethod
    def get(self):
        if not Authors._authors:
            Authors._authors = cat_helpers.load_config_authors()
        return Authors._authors

