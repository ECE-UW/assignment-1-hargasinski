import sys

from graph import Graph
from street import Street
from parse import parse

streets = {}
graph = Graph()


def throw_error(msg):
    print("Error: %s" % msg)


def add_street(street_name, coordinates):
    # check for any errors in the input
    if not street_name:
        return throw_error('A valid street name is required to add a street.')
    elif street_name in streets:
        return throw_error('Trying to add a street that already exists.')
    elif not coordinates or len(coordinates) < 2:
        return throw_error('A street needs to have 2 or more points.')

    # add the street
    base_add_street(street_name, coordinates)


def base_add_street(street_name, coordinates):
    # create the street
    new_street = Street(street_name, coordinates)

    # check for any intersections with the existing streets
    for street in streets.values():
        intersections = street.find_intersections(new_street)

        # add the intersections to the graph
        for intersection in intersections:
            graph.add_vertex(intersection)

    # add the street to the database (dictionary)
    streets[street_name] = new_street


def change_street(street_name, new_coordinates):
    # check for any errors in the input
    if not street_name:
        return throw_error('A valid street name is required to change a street.')
    elif street_name not in streets:
        return throw_error('Trying to change a street that does not exist.')
    elif not new_coordinates or len(new_coordinates) < 2:
        return throw_error('A street needs to have 2 or more points.')

    # change the street
    base_change_street(street_name, new_coordinates)


def base_change_street(street_name, new_coordinates):
    # a change in a street is equivalent (mostly) to removing a street and then
    # adding it back in
    base_remove_street(street_name, new_coordinates)
    base_add_street(street_name, new_coordinates)


def remove_street(street_name, coordinates):
    # check for any errors in the input
    if not street_name:
        return throw_error('A valid street name is required to remove a street.')
    elif street_name not in streets:
        return throw_error('Trying to remove a street that does not exist.')
    elif coordinates:
        return throw_error('Received coordinates for a street that is being removed.')

    # remove the street
    base_remove_street(street_name, coordinates)


def base_remove_street(street_name, coordinates):
    # remove the street from the graph and database
    graph.remove_street(street_name)
    del streets[street_name]


def generate_graph(street_name, coordinates):
    # check for any errors in the input
    if street_name:
        return throw_error('Did not expect a street name for this command.')
    elif coordinates:
        return throw_error('Did not expect coordinates for this command.')

    print(graph)


def execute_command(command):
    # a command could not be parsed from the given line
    if not command:
        return

    # could be made global
    valid_commands = {
        'a': add_street,
        'c': change_street,
        'r': remove_street,
        'g': generate_graph
    }

    action = command.get('action')

    # Should not reach this condition as we check for a valid command in
    # the parser
    if action not in valid_commands:
        throw_error(
            'Command `%s` not recognized, please enter a valid command' % action
        )
        return

    # execute the command
    valid_commands[action](
        command.get('street_name'),
        command.get('coordinates')
    )


def main():
    # YOUR MAIN CODE GOES HERE

    # sample code to read from stdin.
    # make sure to remove all spurious print statements as required
    # by the assignment
    while True:
        line = sys.stdin.readline()
        if line == '':
            break
        execute_command(parse(line))

    # return exit code 0 on successful termination
    sys.exit(0)


if __name__ == '__main__':
    main()
