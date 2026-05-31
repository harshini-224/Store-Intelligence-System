# pipeline/events/line_counter.py

class LineCounter:

    def __init__(self, line_start, line_end):
        self.line_start = line_start
        self.line_end = line_end

        # Stores previous side of each visitor
        self.visitor_sides = {}

    def get_side(self, point):
        """
        Determine which side of the line a point lies on.
        Returns:
            >0 : one side
            <0 : other side
        """

        x, y = point

        x1, y1 = self.line_start
        x2, y2 = self.line_end

        return (x2 - x1) * (y - y1) - (y2 - y1) * (x - x1)

    def check_crossing(self, visitor_id, point):
        """
        Detect ENTRY / EXIT
        """

        current_side = self.get_side(point)

        if visitor_id not in self.visitor_sides:
            self.visitor_sides[visitor_id] = current_side
            return None

        previous_side = self.visitor_sides[visitor_id]

        self.visitor_sides[visitor_id] = current_side

        if previous_side < 0 and current_side > 0:
            return "ENTRY"

        if previous_side > 0 and current_side < 0:
            return "EXIT"

        return None