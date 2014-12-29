import re
import autobot.helpers as helpers


def sanitize_yaml_string(value):
    if re.search(r':', value):
        # String contains the character ':' which will cause YAML
        # error.
        if re.search("'", value):
            value = '"' + value + '"'
        else:
            value = "'" + value + "'"
    return value


class PseudoYAML(object):
    def __init__(self, infile):
        self._infile = infile
        self._data = None

    def _sanitize_data(self, line):
        line = line.rstrip()
        if re.match(r'^#', line):
            return None
        if re.match(r'^(- name):', line):
            key, value = line.split(':', 1)
            value = value.strip("' ")

            value = sanitize_yaml_string(value)

            key = key.strip(" ")
            line = "%s: %s" % (key, value)
        elif re.match(r'^\s+(product_suite|status):', line):
            key, value = line.split(':', 1)
            value = value.strip("' ")
            key = key.strip(" ")
            line = "  %s: %s" % (key, value)
        elif re.match(r'^(\s+\w+):', line):
            key, value = line.split(':', 1)
            value = value.strip(" ")
            key = key.strip(" ")
            line = "  %s: %s" % (key, value)
        return line

    def load_yaml_file(self):
        yaml_string = ''
        lines = helpers.file_read_once(self._infile, to_list=True)
        for line in lines:
            new_line = self._sanitize_data(line)
            if new_line:
                yaml_string += new_line + "\n"
        self._data = helpers.from_yaml(yaml_string)
        return self._data

    def data(self):
        return self._data
