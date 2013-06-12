''' Useful 2D geometry functions 

Created for HIT3046 AI for Games by Clinton Woodward cwoodward@swin.edu.au

'''

from vector2d import Vector2D
from transformations2d import PointToLocalSpace
from math import pi, sqrt, cos, sin, acos, asin

#------------------------------------------------------------------------------
def DistanceToRayPlaneIntersection(ray_origin, ray_heading, plane_point, plane_normal):
    ''' Given a plane and a ray, determine how far along the ray an 
        intersection occurs. Return -1.0 if ray is parallel. Parameters
        must be all Vector2D objects. '''
    d = - plane_normal.dot(plane_point)
    numer = plane_normal.dot(ray_origin) + d
    denom = plane_normal.dot(ray_heading)
    if -0.000001 < denom < 0.000001:
        return -1.0
    else:
        return -(numer/denom)

#------------------------------------------------------------------------------
# define result values for WhereIsPoint()
PLANE_FRONT = 0; PLANE_BACKSIDE = 1; ON_PLANE = 2

def WhereIsPoint(point, point_on_plane, plane_normal):
    dir = point_on_plane - point
    d = dir.dot(plane_normal)
    if d < -0.000001:
       return PLANE_FRONT
    elif d > 0.000001:
       return PLANE_BACKSIDE
    else:
       return ON_PLANE 

#------------------------------------------------------------------------------
def GetRayCircleIntersect(ray_origin, ray_heading, circle_origin, radius):
    ''' '''
    to_circle = circle_origin - ray_origin
    length = to_circle.length()
    v = to_circle.dot(ray_heading)
    d = radius*radius - (length*length - v*v)
    # if there was no intersection, return -1
    if d < 0.0:
        return -1.0
    # return the distance to the (first) intersection point
    else:
        return (v - sqrt(d))
    
#------------------------------------------------------------------------------
def doRayCircleIntersect(ray_origin, ray_heading, circle_origin, radius):
    ''' '''
    to_circle = circle_origin - ray_origin
    length = to_circle.length()
    v = to_circle.dot(ray_heading)
    d = radius*radius - (length*length - v*v) 
    return d < 0.0  

#------------------------------------------------------------------------------
def GetTangentPoints(vCentre, radius, vPoint): 
    ''' Given a point P and a circle of radius R centered at C, determine the 
        two points T1, T2 on the circle that intersect with the tangents from P
        to the circle. Returns False if P is within the circle '''
    PmC = vPoint - vCentre
    sqr_len = PmC.lengthSq()
    r_sqr = radius*radius
    # Quick check for P inside the circle, return False if so
    if sqr_len <= r_sqr:
        return False, None, None # tangent objects are not returned.
    # time to work out the real tangent points then
    T1 = Vector2D()
    T2 = Vector2D()
    inv_sqr_len = 1.0 / sqr_len
    root = sqrt(abs(sqr_len - r_sqr))  
    
    T1.x = vCentre.x + radius*(radius*PmC.x - PmC.y*root)*inv_sqr_len;
    T1.y = vCentre.y + radius*(radius*PmC.y + PmC.x*root)*inv_sqr_len;
    T2.x = vCentre.x + radius*(radius*PmC.x + PmC.y*root)*inv_sqr_len;
    T2.y = vCentre.y + radius*(radius*PmC.y - PmC.x*root)*inv_sqr_len;
    # return tuple of True and two Tangent points  
    return True, T1, T2
        
#------------------------------------------------------------------------------
def DistToLineSegment(A, B, P):
    ''' Given line AP and point P, calculate the perpendicular distance.'''
    # If angle between PA and AB is obtuse, closest AB line point is end A
    dotA = (P.x - A.x)*(B.x - A.x) + (P.y - A.y)*(B.y - A.y)
    if dotA <= 0:
        return A.distance(P)
    # If angle between PB and AB is obtuse, closest AB line point is end B
    dotB = (P.x - B.x)*(A.x - B.x) + (P.y - B.y)*(A.y - B.y)
    if dotB <= 0:
        return B.distance(P)
    # Okay, get the point along AB that is closest (perpendicular to AB)
    Q = A + ((B - A) * dotA)/(dotA + dotB)
    # and the distance
    return P.distance(Q)
    
#------------------------------------------------------------------------------
def DistToLineSegmentSq(A, B, P):
    ''' As above, but avoiding the sqrt operation returning squared values. '''
    # If angle between PA and AB is obtuse, closest AB line point is end A
    dotA = (P.x - A.x)*(B.x - A.x) + (P.y - A.y)*(B.y - A.y)
    if dotA <= 0:
        return A.distanceSq(P)
    # If angle between PB and AB is obtuse, closest AB line point is end B
    dotB = (P.x - B.x)*(A.x - B.x) + (P.y - B.y)*(A.y - B.y)
    if dotB <= 0:
        return B.distanceSq(P)
    # Okay, get the point along AB that is closest (perpendicular to AB)
    Q = A + ((B - A) * dotA)/(dotA + dotB)
    # and the distance
    return P.distanceSq(Q)


#------------------------------------------------------------------------------
def LineIntersection2D(A, B, C, D):  
    ''' Given two lines AB and CD, return True is they intersect. '''
    rTop = (A.y-C.y)*(D.x-C.x)-(A.x-C.x)*(D.y-C.y);
    sTop = (A.y-C.y)*(B.x-A.x)-(A.x-C.x)*(B.y-A.y);
    
    Bot = (B.x-A.x)*(D.y-C.y)-(B.y-A.y)*(D.x-C.x);
    # parallel?
    if Bot == 0: 
        return False

    r = rTop / Bot;
    s = sTop / Bot;
    # lines intersect?
    if  (r > 0) and (r < 1) and (s > 0) and (s < 1) :
        return True;

    # fall-through - lines do not intersect
    return False;

#------------------------------------------------------------------------------
def LineIntersection2DDist(A, B, C, D):  
    ''' Given two lines AB and CD, return True is they intersect. 
        and the distance to intersection'''
    rTop = (A.y-C.y)*(D.x-C.x)-(A.x-C.x)*(D.y-C.y);
    sTop = (A.y-C.y)*(B.x-A.x)-(A.x-C.x)*(B.y-A.y);
    
    Bot = (B.x-A.x)*(D.y-C.y)-(B.y-A.y)*(D.x-C.x);

    # parallel?
    if Bot == 0: 
        return False, 0.0

    r = rTop / Bot;
    s = sTop / Bot;
    # lines intersect?
    if  (r > 0) and (r < 1) and (s > 0) and (s < 1) :
        dist = A.distance(B) * r
        return True, dist;

    # fall-through - lines do not intersect
    return False, 0.0; 

#------------------------------------------------------------------------------
def LineIntersection2DDistPoint(A, B, C, D):  
    ''' Given two lines AB and CD, return True is they intersect. 
        the distance to intersection, and the point of intersection. '''
    rTop = (A.y-C.y)*(D.x-C.x)-(A.x-C.x)*(D.y-C.y);
    sTop = (A.y-C.y)*(B.x-A.x)-(A.x-C.x)*(B.y-A.y);
    
    Bot = (B.x-A.x)*(D.y-C.y)-(B.y-A.y)*(D.x-C.x);

    # parallel?
    if Bot == 0: 
        return False, None, 0.0

    r = rTop / Bot;
    s = sTop / Bot;
    # lines intersect?
    if  (r > 0) and (r < 1) and (s > 0) and (s < 1) :
        dist = A.distance(B) * r
        point = A + r * (B - A)
        return True, dist, point;

    # fall-through - lines do not intersect
    return False, None, 0.0;  

#------------------------------------------------------------------------------
def ObjectIntersection2D(obj1, obj2):
    ''' Test if two polygon intersect. Does not test for enclosure. '''
    for i in range(len(obj1)-1):
        for j in range(len(obj2)-1):
            if LineIntersection2D(obj2[j],obj2[j+1],obj1[i],obj1[i+1]):
                return True
    return False 

#------------------------------------------------------------------------------
def SegmentObjectIntersection2D(A, B, obj):
    ''' Test a line segment for intersection against a polygon object. '''
    for i in range(len(obj)-1):
        if LineIntersection2D(A, B, obj[i], obj[i+1]):
            return True
    return False

#------------------------------------------------------------------------------
def TwoCirclesOverlapped(x1,y1,r1,x2,y2,r2):
    ''' Return True if two circles overlap '''
    dx = x1-x2
    dy = y1-y2
    d_centres = sqrt( dx*dx + dy*dy )
    return (d_centres < (r1+r2) or d_centres < abs(r1-r2))

#------------------------------------------------------------------------------
def TwoCirclesOverlappedVec(c1,r1,c2,r2):
    ''' Return True if two circles overlap '''
    dx = c1.x-c2.x
    dy = c1.y-c2.y
    d_centres = sqrt( dx*dx + dy*dy )
    return (d_centres < (r1+r2) or d_centres < abs(r1-r2))

#------------------------------------------------------------------------------
def TwoCirclesOverlapped(x1,y1,r1,x2,y2,r2):
    ''' Return True if circles enclose each other '''
    dx = x1-x2
    dy = y1-y2
    d_centres = sqrt( dx*dx + dy*dy )
    return d_centres < abs(r1-r2)

#------------------------------------------------------------------------------
def TwoCirclesIntersectionPoints(x1,y1,r1, x2,y2,r2):
    ''' Test and find overlap points for two given circles.
        See http://.../~pbourke/geometry/2circle/
    '''
    #first check to see if they overlap
    if not TwoCirclesOverlapped(x1,y1,r1,x2,y2,r2):
        return False, 0, 0, 0, 0

    # calculate the distance between the circle centers
    d = sqrt( (x1-x2) * (x1-x2) + (y1-y2) * (y1-y2))
  
    # calculate the distance from the center of each circle to the center
    # of the line which connects the intersection points.
    a = (r1 - r2 + (d * d)) / (2 * d)
    b = (r2 - r1 + (d * d)) / (2 * d)

    # MAYBE A TEST FOR EXACT OVERLAP? 

    # Calculate the point P2 which is the center of the line which 
    # connects the intersection points
    p2X = x1 + a * (x2 - x1) / d
    p2Y = y1 + a * (y2 - y1) / d

    # calculate first point
    h1 = sqrt((r1 * r1) - (a * a))
    p3X = p2X - h1 * (y2 - y1) / d
    p3Y = p2Y + h1 * (x2 - x1) / d

    # calculate second point
    h2 = sqrt((r2 * r2) - (a * a))
    p4X = p2X + h2 * (y2 - y1) / d
    p4Y = p2Y - h2 * (x2 - x1) / d

    return True, p3X, p3Y, p4X, p4Y

#------------------------------------------------------------------------------
def TwoCirclesIntersectionArea(x1,y1,r1,x2,y2,r2):
    ''' If the two circles overlap, calculate the area of the union.'''
    # first calculate the intersection points
    test, iX1, iY1, iX2, iY2 = TwoCirclesIntersectionPoints(x1, y1, r1, x2, y2, r2)
    if not test:
        return 0.0 # no overlap
    # distance between circle centres
    d = sqrt( (x1-x2) * (x1-x2) + (y1-y2) * (y1-y2))

    # find the angles given that A and B are the two circle centers
    # and C and D are the intersection points
    CBD = 2 * acos((r2*r2 + d*d - r1*r1) / (r2 * d * 2)) 
    CAD = 2 * acos((r1*r1 + d*d - r2*r2) / (r1 * d * 2))

    # Then we find the segment of each of the circles cut off by the 
    # chord CD, by taking the area of the sector of the circle BCD and
    # subtracting the area of triangle BCD. Similarly we find the area
    # of the sector ACD and subtract the area of triangle ACD.
    area = 0.5*CBD*r2*r2 - 0.5*r2*r2*sin(CBD) + 0.5*CAD*r1*r1 - 0.5*r1*r1*sin(CAD)
    return area;


#------------------------------------------------------------------------------
def CircleArea(radius):
    ''' given the radius, calculates the area of a circle '''
    return pi * radius * radius;

#------------------------------------------------------------------------------

def PointInCircle(Pos, radius, p):
    ''' returns True if the point p is within the radius of the given circle '''
    DistFromCenterSquared = (p-Pos).lengthSq();
    return (DistFromCenterSquared < (radius*radius))

#------------------------------------------------------------------------------

def LineSegmentCircleIntersection(A, B, P, radius):
    ''' Returns True if the line segment AB intersects with a circle at
        position P with radius radius. '''
    # first determine the distance from the center of the circle to the line 
    # segment (working in distance squared space)'''
    DistToLineSq = DistToLineSegmentSq(A, B, P);
    return (DistToLineSq < radius*radius)

#------------------------------------------------------------------------------

def GetLineSegmentCircleClosestIntersectionPoint(A, B, pos, radius, vIP):
    ''' Given a line segment AB and a circle position pos and radius, 
        determines if there is an intersection and stores the position of the 
        closest intersection in the reference vIP.

        Returns False if no intersection point is found. '''                                       
    toBNorm = B-A 
    toBNorm.normalise()

    # move the circle into the local space defined by the vector B-A with 
    # origin at A
    locPos = PointToLocalSpace(pos, toBNorm, toBNorm.perp(), A)

    ipFound = False;

    # If the local position + the radius is negative then the circle lays behind
    # point A so there is no intersection possible. If the local x pos minus the 
    # radius is greater than length A-B then the circle cannot intersect the 
    # line segment
    if (locPos.x+radius >= 0) and ((locPos.x-radius)**2 <= B.distanceSq(A)) :
        # if the distance from the x axis to the object's position is less
        # than its radius then there is a potential intersection.
        if (abs(locPos.y) < radius):
            # now to do a line/circle intersection test. The center of the 
            # circle is represented by A, B. The intersection points are 
            # given by the formulae x = A +/-sqrt(r^2-B^2), y=0. We only 
            # need to look at the smallest positive value of x.
            a = locPos.x;
            b = locPos.y;       
    
            ip = a - sqrt(radius*radius - b*b)
    
            if ip <= 0:
                ip = a + sqrt(radius*radius - b*b)
    
            ipFound = True;
    
            vIP = A + toBNorm*ip

    return ipFound;

    