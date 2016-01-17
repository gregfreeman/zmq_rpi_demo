
import json
from pythreejs import *
import numpy as np
from numpy import array, sqrt
from IPython.display import display
from quaternion import Quaternion


def blenderGeometry(fname, color='blue'):
    geomData = json.load(open(fname))
    nfaces = geomData['metadata']['faces']
    nvertices = geomData['metadata']['vertices']
    vertices = array(geomData['vertices']).reshape(nvertices, 3)
    if geomData['faces'][0] == 0x22:
        """0=type
        1,2,3 = face vertex index
        4 = material index
        5,6,7= normal index """
        faces = array(geomData['faces']).reshape(nfaces, 8)
        faceVerticies = faces[:, 1:4]
        # faceMaterial = faces[:, 4:5]
        # faceNormalIndicies = faces[:, 5:8]
        colors = [color] * nfaces
    else:
        raise('cannot decode geometry')
    return PlainGeometry(faces=faceVerticies.tolist(), vertices=vertices.tolist(), colors=colors)


class addlist(list):
    """
    provide a list with addition redefined as in an array with element wise addition (not appending lists)
    """
    def __add__(self, rhs):
        if len(self) != len(rhs):
            raise('Error in addition')
        return addlist([a + b for a, b in zip(self, rhs)])


def coordinateframe(offset, size):
    """
    This draws a 3d reference coordinate frame with lines and x,y,z text
    offset: the position of the coordinate frame diagram within the true coordinate frame
    size: the size of the diagram
    """
    offset = addlist(offset)
    size = 4
    linesgeom = PlainGeometry(vertices=[[0, 0, 0], [size, 0, 0], [0, 0, 0], [0, size, 0], [0, 0, 0], [0, 0, size]],
                              colors=['red', 'red', 'green', 'green', 'blue', 'blue'])
    axes = Line(geometry=linesgeom,
                material=LineBasicMaterial(linewidth=5, vertexColors='VertexColors'),
                type='LinePieces',
                position=offset)
    x = make_text('X', height=.6, position=offset + [size, 0, 0])
    y = make_text('Y', height=.6, position=offset + [0, size, 0])
    z = make_text('Z', height=.6, position=offset + [0, 0, size])

    return [axes, x, y, z]


def qconvert(q):
    """
    Quaternions can be represented in a number of different ways.
    This converts from the Quaternion class to the convention used in pythreejs
    """
    q = np.asarray(q.q)
    q2 = q[1:].tolist() + [q[0]]
    return q2


def showteapot():
    """
    this creates a threejs screen with a teapot and reference coordinate frame
    the following objects are output to manipulation
    (teapot, qzero, camera, renderer)
    """
    teapotGeom = blenderGeometry('teapot.json')
    material = BasicMaterial(wireframe=True, color='red')
    teapot = Mesh(geometry=teapotGeom, material=material, position=[0, 0, 0])
    coord = coordinateframe([-4, -4, -4], 4)
    scene = Scene(children=[teapot, AmbientLight(color=0x777777)] + coord)
    light = DirectionalLight(color='white',
                             position=[3, 5, 1],
                             intensity=0.5)
    camera = PerspectiveCamera(position=[0, 12, 4], up=[0, 0, 1], children=[light])
    qzero = Quaternion([1/sqrt(2), 1/sqrt(2), 0, 0])
    teapot.quaternion = qconvert(qzero)
    renderer = Renderer(camera=camera, scene=scene, controls=[OrbitControls(controlling=camera)])
    display(renderer)
    return teapot, qzero, camera, renderer
