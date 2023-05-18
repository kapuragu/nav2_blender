import struct


def Vector3(f):
    float_x = struct.unpack('<f', f.read(4))[0]
    float_y = struct.unpack('<f', f.read(4))[0]
    float_z = struct.unpack('<f', f.read(4))[0]
    vector3 = [float_x, float_y, float_z]
    return vector3


def Vector4(f):
    float_x = struct.unpack('<f', f.read(4))[0]
    float_y = struct.unpack('<f', f.read(4))[0]
    float_z = struct.unpack('<f', f.read(4))[0]
    float_w = struct.unpack('<f', f.read(4))[0]
    vector4 = [float_x, float_y, float_z, float_w]
    return vector4


def Vertex(f):
    x = struct.unpack('<H', f.read(2))[0]
    y = struct.unpack('<H', f.read(2))[0]
    z = struct.unpack('<H', f.read(2))[0]
    vertex = [x, y, z]
    return vertex


def IndexPair8(f):
    From = struct.unpack('<B', f.read(1))[0]
    To = struct.unpack('<B', f.read(1))[0]
    indexpair8 = [From, To]
    return indexpair8
