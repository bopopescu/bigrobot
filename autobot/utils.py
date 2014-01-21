import re


def strip_empty_lines(input_list):
    """
    Given a list of strings, remove entries which are empty lines.
    """
    return filter(lambda x: not re.match(r'^\s*$', x), input_list)


def strip_table_row_dividers(input_list):
    """
    Remove entries in the format:
        '+---------+--------------+---------------------+'
    """
    return filter(lambda x: not re.match(r'^\+---', x), input_list)


def strip_table_ws_between_columns(input_list):
    """
    Remove white spaces between the columns.
    """
    output_list = []
    for s in input_list:
        s = re.sub(r'(\s+\|\s+|\|\s+|\s+\|)', "|", s)
        output_list.append(s)
    return output_list


def strip_surround_delimiters(input_str):
    """
    Remove the starting '|' and trailing '|'.
    """
    return re.sub(r'(^\||\|$)', '', input_str)


def convert_table_to_dict(input_list):
    output_dict = {}
    # First row is the table header containing field identifiers
    first_row = strip_surround_delimiters(input_list[0])
    fields = [s.lower() for s in first_row.split('|')]

    for s in input_list[1:]:
        out = strip_surround_delimiters(s)
        out_list = out.split('|')
        key = out_list[0]
        output_dict[key] = dict(zip(fields, out_list))

    return output_dict


def end_of_output_marker():
    return '\n\n----'
