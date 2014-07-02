import cat_helpers


class QaAuthors(object):
    _authors = None

    @classmethod
    def authors(self):
        if not QaAuthors._authors:
            QaAuthors._authors = cat_helpers.load_config_authors()
        return QaAuthors._authors

