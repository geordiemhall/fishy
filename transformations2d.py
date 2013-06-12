''' Various 2D Transform functions  

Created for HIT3046 AI for Games by Clinton Woodward cwoodward@swin.edu.au

'''

from matrix33 import Matrix33

#------------------------------------------------------------------------------
def WorldTransformScale(points, pos, forward, side, scale):
    ''' Transform the given list of points, using the provided position, 
        direction and scale, to object world space. '''
    # make a copy of original points (so we don't trash them)
    tran_points = [ pt.copy() for pt in points ]
    # create a transformation matrix to perform the operations
    matTransform = Matrix33()
    # scale (but only if needed)
    if (scale.x != 1.0) or (scale.y != 1.0):
        matTransform.scale_update(scale.x, scale.y)
    # rotate
    matTransform.rotate_by_vectors_update(forward, side)
    # and translate
    matTransform.translate_update(pos.x, pos.y)
    # now transform all the points (vertices)
    matTransform.transform_vector2d_list(tran_points)
    # done
    return tran_points

#------------------------------------------------------------------------------
def WorldTransform(points, pos, forward, side):
    ''' Transform the given list of points, using the provided position and 
        direction, to objects world space. '''
    # make a copy of original points (so we don't trash them)
    tran_points = [ pt.copy() for pt in points ]
    # create a transformation matrix to perform the operations
    matTransform = Matrix33()
    # rotate
    matTransform.rotate_by_vectors_update(forward, side)
    # and translate
    matTransform.translate_update(pos.x, pos.y)
    # now transform all the points (vertices)
    matTransform.transform_vector2d_list(tran_points)
    # done
    return tran_points

#------------------------------------------------------------------------------
def PointToWorldSpace(point, pos, forward, side):
    ''' Transforms a point from the agent's local space into world space'''
    # make a copy of the point
    TransPoint = point.copy()
    # create a transformation matrix
    matTransform = Matrix33()
    # rotate
    matTransform.rotate_by_vectors_update(forward, side)
    # and translate
    matTransform.translate_update(pos.x, pos.y)  
    # now transform the vertices
    matTransform.transform_vector2d(TransPoint)
    return TransPoint

#------------------------------------------------------------------------------
def VectorToWorldSpace(vec, forward, side):
    ''' Transforms a vector from the agent's local space into world space '''
    # make a copy of the point
    TransVec = vec.copy()
    # create a transformation matrix
    matTransform = Matrix33()
    # rotate
    matTransform.rotate_by_vectors_update(forward, side)
    # now transform the vertices
    matTransform.transform_vector2d(TransVec)
    return TransVec

#------------------------------------------------------------------------------
def PointToLocalSpace(point, pos, forward, side):
    ''' Transform point to local space. '''
    # make a copy of the point
    TransPoint = point.copy() 
    # We'll plug the changes straight in a matrix... save some time (perhaps)
    Tx = -pos.dot(forward)
    Ty = -pos.dot(side)
    m = [forward.x, side.x, 0.0, forward.y, side.y, 0.0, Tx, Ty, 1.0]
    matTransform = Matrix33(m)
    # now transform the vertices
    matTransform.transform_vector2d(TransPoint)
    return TransPoint

#------------------------------------------------------------------------------
def VectorToLocalSpace(vec, forward, side):
    ''' Return a new vector with the translated direction '''
    # make a copy of the point
    TransVec = vec.copy()
    # create the transformation matrix and plug values straight in
    m = [forward.x, side.x, 0.0, forward.y, side.y, 0.0, 0, 0, 1.0]
    matTransform = Matrix33(m)    
    # now transform the vector
    matTransform.transform_vector2d(TransVec)
    return TransVec

#------------------------------------------------------------------------------
def Vec2DRotateAroundOrigin(vec, rads):
    ''' Rotates a vector a given angle (in radians) around the origin. 
        Note: the vec parameter is altered (does not return a new vector. '''
    mat = Matrix33()
    mat.rotate_update(rads)
    mat.transform_vector2d(vec)


