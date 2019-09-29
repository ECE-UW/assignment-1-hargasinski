import re

from street import Point


def throw_error(msg):
    print("Error: %s" % msg)


"""
Action and street name regex - matches the action and street name
    ([acrg]) - check for a valid action: a, c, r or g
    (?:
        \s+ - check for one or more spaces after the action
        "([\w\s]+)" - check for word characters or spaces between double quotes
    )? - the street name is optional, not required for `g`
    \s* - check for white space after the street name or command
"""
r_input = re.compile(r'([acrg])(?:\s+"([\w\s]+)")?\s*')

"""
Coordinate regex - matches one set of coordinates followed by optional
whitespace
    \(
        ([\-|\+]?\d+) -
        , - there should be a comma between the numbers
        ([\-|\+]?\d+) -
    \) - coordinates should be enclosed by parentheses
    \s* - optional whitespace following coordinates
"""
r_coordinates = re.compile(r'\(([\-|\+]?\d+),([\-|\+]?\d+)\)\s*')

"""
Ensure there is a space between the street name and coordinate list
    (
        " - the ending double quote of the street name
        \s+ - ensure one or more spaces between the street name and
              start of the coordinates
        \( - the start of the coordinates
    )
"""
r_valid_input = re.compile(r'(\"\s+\()')


def parse(line):
    # parse the action and street name
    line = line.strip()
    command_info = r_input.match(line)

    # ensure the input was valid
    if not command_info:
        return throw_error('Could not parse command and/or street name')
    elif command_info.group(1) in ['a', 'c'] and not r_valid_input.findall(line):
        return throw_error(
            'Expected a space between the street name and start of the coordinates'
        )

    # parse the coordinates, if present
    coordinates = []
    for coord in r_coordinates.finditer(line, command_info.end()):
        coordinates.append(Point(coord.group(1), coord.group(2)))

    # since we do not output the street name anymore, we can simplify the
    # program by changing it to lower case (street name as case insensitive)
    street_name = command_info.group(2) or ""

    return {
        "action": command_info.group(1),
        "street_name": street_name.lower(),
        "coordinates": coordinates
    }
