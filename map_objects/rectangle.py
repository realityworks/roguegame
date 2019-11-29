class Rect:
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)

        return (center_x, center_y)

    def intersect(self, other):
        if (self.x1 >= other.x2 or
            self.x2 <= other.x1 or
            self.y1 >= other.y2 or
            self.y2 <= other.y1):
            return False

        return True

    def intersect_with_distance(self, other, distance):
        if (self.x1 >= other.x2 or self.x2 <= other.x1 or self.y1 >= other.y2 or self.y2 <= other.y1):
            distancex1 = abs(self.x1 - other.x2)
            distancey1 = abs(self.y1 - other.y2)
            distancex2 = abs(self.x2 - other.x1)
            distancey2 = abs(self.y2 - other.y1)
            if distancex1 > distance and distancex2 > distance and distancey1 > distance and distancey2 > distance:
                return False


        return True