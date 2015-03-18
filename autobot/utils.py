import re


def strip_empty_lines(input_list):
    """
    Given a list of strings, remove entries which are empty lines.
    """
    return filter(lambda x: not re.match(r'^\s*$', x), input_list)


def strip_cruds_before_table_begins(input_list):
    """
    For CLI output, the first line(s) may be a command (not part of the
    table), so strip lines before the table starts.
    """
    i = 0
    for s in input_list:
        s = s.rstrip()
        if re.match(r'^[\+-]+$', s):
            break
        i += 1
    return input_list[i:]


def strip_cruds_after_table_ends(input_list):
    """
    For CLI output, the last line(s) may be a prompt or some extraneous
    output which is not part of the table, so strip lines after the table
    ends.
    """
    i = 0
    for s in reversed(input_list):
        s = s.rstrip()
        if re.match(r'^[\+-]+$', s):
            break
        i += 1
    if i == 0:
        return input_list
    else:
        return input_list[:-i]


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
    return '\n\n------'


def marker():
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
