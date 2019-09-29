class Vertex(object):
    # static variable to ensure that each vertex has a unique
    next_id = 0

    def __init__(self, pos, is_intersection, is_endpoint):
        # the position of the vertex
        self.coordinates = pos

        # information to make removing a vertex from the graph easier
        self.streets = []
        self.is_intersection = is_intersection
        self.is_endpoint = is_endpoint

        # properly store the id and ensure the next vertex created has a
        # proper id
        self.id = Vertex.next_id
        Vertex.next_id += 1

    def add_street(self, street_name):
        # avoid adding the same street twice
        if not self.is_on_street(street_name):
            self.streets.append(street_name)

    def remove_street(self, street_name):
        # avoid value error
        if self.is_on_street(street_name):
            self.streets.remove(street_name)

    def get_streets(self):
        return self.streets

    def set_is_intersection(self, is_intersection):
        self.is_intersection = is_intersection

    def set_is_endpoint(self, is_endpoint):
        self.is_endpoint = is_endpoint

    def get_is_intersection(self):
        return self.is_intersection

    def get_is_endpoint(self):
        return self.is_endpoint

    def is_on_street(self, street_name):
        # check if this vertex lies on the given street
        return street_name in self.streets

    def get_id(self):
        return self.id

    def is_equal_to_point(self, p):
        # check if this vertex lies on, or approximately on, the given point
        return self.coordinates.is_equal_to_point(p)

    def is_equal_to_vertex(self, v):
        # check if this vertex lies on, or approximately on, the given point
        return self.coordinates.is_equal_to_point(v.coordinates)

    def __repr__(self):
        # print the id and position of the vertex
        return "%d: %s" % (self.id, self.coordinates)


def get_y(vertex):
    return vertex.coordinates.y


def get_x(vertex):
    return vertex.coordinates.x


class Graph(object):
    def __init__(self):
        self.vertices = {}
        self.edges = {}

    def get_vertex(self, coords, is_intersection, is_endpoint):
        # OPTIMIZE: an Rtree could speed this up?
        # to keep the state consistent, ensure there is only one vertex for
        # each point in the graph, so search through the existing points to
        # see if a vertex for this point already exists
        for vertex in self.vertices.values():
            if vertex.is_equal_to_point(coords):
                """
                only update the intersection <endpoint> state of the vertex
                if this point is an intersection <endpoint> to prevent
                overwriting the existing state, i.e. marking an endpoint
                as not an endpoint because in this case we are using it as an
                intersection

                --> required for special case of a segment passing intersecting
                with an endpoint of another segment
                """
                if (not vertex.get_is_intersection()) and is_intersection:
                    vertex.set_is_intersection(is_intersection)

                if (not vertex.get_is_endpoint()) and is_endpoint:
                    vertex.set_is_endpoint(is_endpoint)

                return vertex

        # create the vertex since it does not exist in the graph
        vertex = Vertex(coords, is_intersection, is_endpoint)
        self.vertices[vertex.get_id()] = vertex
        return vertex

    def insert_vertex(self, segment, edges, vertex):
        """
        Insert a vertex at the correct spot in the graph, updating the edges as
        required. For example, if v1 and v2 are connected, v1 --- v2, and v3 is
        inserted between them, ensure the corresponding graph is v1 - v3 - v2
        """
        i = 0

        # are the coordinates on this segment ordered by y or x?
        if segment.is_vertical():
            # linter was complaining about assigning a lambda function to a variable
            getter = get_y
            # are the coordinates on this segment ordered in ascending or
            # descending order?
            if segment.is_top_down():
                cmp = lambda v1, v2: getter(v1) > getter(v2)
            else:
                cmp = lambda v1, v2: getter(v1) < getter(v1)
        else:
            # linter was complaining about assigning a lambda function to a variable
            getter = get_x
            # are the coordinates on this segment ordered in ascending or
            # descending order?
            if segment.is_ltr():
                cmp = lambda v1, v2: getter(v1) > getter(v2)
            else:
                cmp = lambda v1, v2: getter(v1) < getter(v2)

        # find the correct position of the vertex
        while cmp(vertex, edges[i]):
            i += 1

        edges.insert(i, vertex)

    def add_vertex(self, intersection):
        # get the corresponding vertex object to this point
        vertex = self.get_vertex(intersection.get("coords"), 1, 0)

        # add the vertex to both streets, keeping the vertices ordered by
        # streets simplifies the removal process
        self.add_vertex_to_segment(
            intersection.get("street1"),
            intersection.get("segment1"),
            vertex
        )
        self.add_vertex_to_segment(
            intersection.get("street2"),
            intersection.get("segment2"),
            vertex
        )

    def add_vertex_to_segment(self, street_name, segment, vertex):
        segment_idx = segment.get_index()

        # mark the vertex as being on this street
        vertex.add_street(street_name)

        # ensure this street exists in the graph
        if street_name not in self.edges:
            self.edges[street_name] = {}

        if segment_idx not in self.edges[street_name]:
            """
            If this street segment does not exist in the graph, then adding it
            should be simply, add the vertex and the endpoints of it to the
            graph

            However, we need to handle the special case of a segment
            intersecting the endpoint of another segment. In this case, the
            intersection vertex and one of the endpoint vertices are the same,
            so we shouldn't add it twice
            """
            # get the vertex objects of the endpoints of the segment
            src = self.get_vertex(segment.get_source(), 0, 1)
            src.add_street(street_name)

            dest = self.get_vertex(segment.get_destination(), 0, 1)
            dest.add_street(street_name)

            # create this segment in the graph, and add the intersection and
            # endpoints ensuring to handle the special case correctly
            self.edges[street_name][segment_idx] = []
            if src != vertex:
                self.edges[street_name][segment_idx].append(src)

            self.edges[street_name][segment_idx].append(vertex)

            if dest != vertex:
                self.edges[street_name][segment_idx].append(dest)

            return

        # the segment exists, add the intersection and update the corresponding
        # edges
        self.insert_vertex(
            segment,
            self.edges[street_name][segment_idx],
            vertex
        )

    def remove_vertex(self, vertex, street_name):
        vertex.remove_street(street_name)

        # if the vertex is only on one street, it can only be an endpoint
        if len(vertex.get_streets()) == 1:
            vertex.set_is_intersection(0)
        # if the vertex is not on a street, it can neither be an intersection
        # or endpoint
        elif len(vertex.get_streets()) == 0:
            vertex.set_is_intersection(0)
            vertex.set_is_endpoint(0)

        # if it is neither an endpoint or intersection, remove it
        if (not vertex.get_is_intersection() and not vertex.get_is_endpoint()
                and vertex.get_id() in self.vertices):
            del self.vertices[vertex.get_id()]

    def remove_street(self, street_name):
        if street_name not in self.edges:
            return

        # remove this street from all of the vertices on it
        for segment in self.edges[street_name]:
            for vertex in self.edges[street_name][segment]:
                self.remove_vertex(vertex, street_name)

        # remove the street
        del self.edges[street_name]

        streets_to_remove = []
        # sanitize the state of the graph, i.e. ensure all of the vertices are
        # in a correct state, remove any that shouldn't be here
        for street in self.edges:
            for segment in self.edges[street]:
                # remove any references to removed vertices
                self.edges[street][segment] = list(filter(
                    lambda v: v.get_id() in self.vertices,
                    self.edges[street][segment]
                ))

            segment_id_to_remove = []
            # remove any segments in an invalid state, i.e. they need to have at
            # least one vertex is both an intersection and endpoint, and an
            # endpoint, or two endpoints and an intersection
            for segment_id, segment in self.edges[street].items():
                # has at least three vertices, so it should be valid
                if len(segment) > 2:
                    continue
                # check that one of the endpoints is an intersection
                elif len(segment) == 2:
                    if segment[0].get_is_intersection() or segment[1].get_is_intersection():
                        continue
                    # if it isn't, remove both endpoint
                    self.remove_vertex(segment[0], street)
                    self.remove_vertex(segment[1], street)
                    segment_id_to_remove.append(segment_id)
                else:
                    # a segment with less than two points isn't valid
                    if len(segment) == 1:
                        self.remove_vertex(segment[0], street)
                    segment_id_to_remove.append(segment_id)

            # remove all of the invalid segments, this prevents us from
            # mutating the dict as we are iterating through it
            for segment_id in segment_id_to_remove:
                del self.edges[street][segment_id]

            # is this street invalid?
            if len(self.edges[street]) == 0:
                streets_to_remove.append(street)

        # remove all of the invalid segments, this prevents us from
        # mutating the dict as we are iterating through it
        for street in streets_to_remove:
            del self.edges[street]

    def __repr__(self):
        # output the vertices
        output = 'V = {\n'
        for vertex in self.vertices.values():
            output += '  %s\n' % vertex

        # output the edges
        output_edges = {}
        output += '}\nE = {\n'
        for segments in self.edges.values():
            for segment in segments.values():
                for i in range(len(segment) - 1):
                    # handle a special case of overlapping segments, where an
                    # edge is added to the graph twice, i.e. make sure each
                    # edge of the graph is only outputted once

                    # Test case: a "T" (1,1) (2,2) (3,1)
                    # Test case: a "S" (3,1) (2,2) (3,3)
                    # --> the segment (3,1) (2,2) exists twice in the graph as
                    # it is a part of two streets, without this check, it would
                    # be outputted twice. Since the output does not include
                    # street names, it would appear as duplicate

                    # removing the duplicate edge from the graph would require
                    # significant overhead, and since it is appears in the
                    # internal state of the graph, it is easier to fix here
                    id1 = segment[i].get_id()
                    id2 = segment[i + 1].get_id()
                    if (not (id1 in output_edges and id2 in output_edges[id1])) and id1 != id2:
                        # TODO: during refractoring, an error, most likely due
                        # to isIntersection and is_intersection method and
                        # variable, was introduced to the code that adds the
                        # same vertex twice
                        output += '  <%d,%d>,\n' % (id1, id2)

                    # mark the edge as being outputted
                    if id1 not in output_edges:
                        output_edges[id1] = {}
                    if id2 not in output_edges:
                        output_edges[id2] = {}

                    output_edges[id1][id2] = 1
                    output_edges[id2][id1] = 1

        # remove the trailing comma from the last edge
        if len(self.edges) > 0:
            output = output[0:-2] + '\n'
        # print automatically will add a \n
        return output + '}'
