import autobot.helpers as helpers


class Authors(object):
    _authors = None

    @classmethod
    def get(self):
        if not Authors._authors:
            Authors._authors = helpers.bigrobot_config_qa_authors()
        return Authors._authors

