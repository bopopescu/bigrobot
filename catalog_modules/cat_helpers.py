import autobot.helpers


def load_config_catalog(yaml_file=None):
    if yaml_file == None:
        yaml_file = autobot.helpers.bigrobot_configs_path() + "/catalog.yaml"
    if autobot.helpers.file_not_exists(yaml_file):
        autobot.helpers.error_exit("Test Catalog config does not exist (%s)"
                                   % yaml_file,
                                   1)
    return autobot.helpers.load_config(yaml_file)


def load_config_authors(yaml_file=None):
    if yaml_file == None:
        yaml_file = autobot.helpers.bigrobot_configs_path() + "/qa_authors.yaml"
    if autobot.helpers.file_not_exists(yaml_file):
        autobot.helpers.error_exit("Authors config does not exist (%s)"
                                   % yaml_file,
                                   1)
    return autobot.helpers.load_config(yaml_file)

