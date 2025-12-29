
def clockwise_cross(ab, cd, ef):
    return - (((cd[1] - ab[1]) * (ef[0] - ab[0])) - ((ef[1] - ab[1]) * (cd[0] - ab[0])))

def convex_hull(points: list[tuple]): #monotone chain method
    points = sorted(points, key=lambda p: p[0]) #sort points from left to right (x - values)
    
    #split into 2 halves to glue together later
    #left -> right (bottom half)
    lower = []
    for p in points:
        while len(lower) >= 2 and clockwise_cross(lower[-2], lower[-1], p) <= 0:
            lower.pop(0)
        lower.append(p)

    #right -> left (top half)
    upper = []
    for p in points[::-1]:
        while len(upper) >= 2 and clockwise_cross(upper[-2], upper[-1], p) <= 0:
            upper.pop(0)
        upper.append(p)

    return lower[:-1] + upper[:-1] #return the points (already ordered), removing the end points that would be repeated