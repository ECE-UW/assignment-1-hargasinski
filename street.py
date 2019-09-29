POS_ELIPSON = 0.0001
ELIPSON = 1e-9

# numerical accuracies and positional accuracies are different, so we need two
# different functions to compare them. A different in 0.0001 of a slope is
# reasonable, while if two points are within that range, we can assume they are
# equivalent
def isFloatEqual(a, b):
    return abs(a - b) <= ELIPSON

def isPosEqual(x1, x2):
    return abs(x1 - x2) <= POS_ELIPSON

class Point(object):
    def __init__(self, x, y):
        # ensure all of our arithmetic happens as floating points by
        # converting to floats right away
        self.x = float(x)
        self.y = float(y)

    def isEqualToPoint(self, p):
        # check if two points are, or close to, equivalent
        return isPosEqual(self.x, p.x) and isPosEqual(self.y, p.y)

    def __repr__(self):
        # print points are (x, y)
        return "(%.2f, %.2f)" % (self.x, self.y)

class StreetSegment(object):
    def __init__(self, idx, src, dest):
        # the start and destination define the line segment
        self.src = src
        self.dest = dest

        # a segment having access to it's index in the street simplifies adding
        # and removing it from the graph
        self.idx = idx

        # precalculate some values that will make finding the intersection
        # easier
        x1 = src.x
        y1 = src.y
        x2 = dest.x
        y2 = dest.y

        self.rise = y2 - y1
        self.run = x2 - x1

        # calculate the slope and y-intercept to find the equation of this
        # line in the form y = mx + b
        self.m = 0
        self.b = 0
        if self.isVertical():
            self.m = float("inf")
        else:
            self.m = self.rise/self.run
            self.b = y1 - (self.m * x1)

    def getIndex(self):
        return self.idx

    def getSource(self):
        return self.src

    def getDestination(self):
        return self.dest

    def isVertical(self):
        # check if this line has an infinite slope (helps avoid divison by 0)
        # since the src and dest coordinates will be integers, as stated in
        # the assignment, we can compare them directly
        return (self.src.x == self.dest.x)

    def isTopDown(self):
        # will points on this segment be ordered in descending order according
        # to their y coordinate?
        return (self.rise >= 0)

    def isLtr(self):
        # will points on this segment be ordered in ascending order ("left to
        # right") according to their x coordinate
        return (self.run >= 0)

    def findIntersection(self, street_name, street):
        # find all the intersections of this segment with the given street
        intersections = []
        # we need to compare this segment aginst all of the segments in the
        # given street
        for segment in street.getSegments():
            # look for an intersection between the two segments
            intersection = self.findIntersectionWithSegment(segment)

            # if there is an intersection, add all of the additional info
            # we need to store it in the graph
            if (intersection):
                intersections.append({
                    'street1': street_name,
                    'segment1': self,
                    'street2': street.name,
                    'segment2': segment,
                    'coords': intersection
                })

        return intersections

    def contains(self, p):
        # assuming p is on the infinite line given by y = mx + b, is it in the
        # segment defined by src and des
        if (self.isLtr()):
            return (p.x >= self.src.x and p.x <= self.dest.x)
        else:
            return (p.x >= self.dest.x and p.x <= self.src.x)

    def isParallelTo(self, segment):
        # check if this segment is parallel to the given segment
        return (self.isVertical() and segment.isVertical()) or (isFloatEqual(self.b, segment.b))

    def findIntersectionWithSegment(self, segment):
        if (self.isParallelTo(segment)):
            """
            From the assignment FAQ:
            "a coordinate (x, y) is an intersection point only if there are two
            non-overlapping line segments of two different streets that meet at
            (x, y)."
            which means two possibilities if the segments are parallel:
            1) they don't overlap, so no intersection is possible
            2) the line segments overlap, so no intersection by the definition
            above
            """
            return None
        elif (self.isVertical()):
            #TODO: move this out to a function
            """
            If one of the line segments is vertical, it simplifies the
            calculation as we already know the x-coordinate of the intersection.
            We just need to find y and check if it is on the segment
            """
            x = self.src.x
            y = segment.m * x + segment.b
            # check if the intersection is on the segment
            if (self.isTopDown()):
                if (y >= self.src.y and y <= self.dest.y):
                    return Point(x, y)
            else:
                if (y >= self.dest.y and y <= self.src.y):
                    return Point(x, y)
        elif (segment.isVertical()):
            #TODO: move this out to a function
            """
            If one of the line segments is vertical, it simplifies the
            calculation as we already know the x-coordinate of the intersection.
            We just need to find y and check if it is on the segment
            """
            x = segment.src.x
            y = self.m * x + self.b
            # check if the intersection is on the segment
            if (segment.isTopDown()):
                if (y >= segment.src.y and y <= segment.dest.y):
                    return Point(x, y)
            else:
                if (y >= segment.dest.y and y <= segment.src.y):
                    return Point(x, y)
        else:
            # not required as we already check if they are parallel
            if (self.m == segment.m):
                return
            # find the x and y coordinate of the intersection
            x = (segment.b - self.b) / (self.m - segment.m)
            y = self.m * x + self.b
            p = Point(x, y)

            # make sure the intersection is on both segments, the second check
            # is probably not required
            if (self.contains(p) and segment.contains(p)):
                return p

    def __repr__(self):
        return "%d" % self.getIndex()

class Street(object):
    def __init__(self, name, coordinates):
        self.name = name
        self.update(coordinates)

    def update(self, coordinates):
        self.segments = []
        self.addSegments(coordinates)

    def addSegments(self, coordinates):
        # add all of the segments to this street
        for i in range(len(coordinates) - 1):
            self.segments.append(StreetSegment(i, coordinates[i], coordinates[i+1]))

    def getSegments(self):
        return self.segments

    def findIntersections(self, street):
        # find all of the intersections between this street and the given street
        intersections = []
        for segment in self.getSegments():
            intersections += segment.findIntersection(self.name, street)
        return intersections
