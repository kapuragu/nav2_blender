from nav2_blender.common.common import *
from nav2_blender.nav2.nav2_common import *
from nav2_blender.common.utils import *

import os
import struct

navWorlds = dict()
segmentGraphs = dict()
segmentChunks = dict()
navmeshChunks = dict()
section2Entries = []


class Header:
    def __init__(self, f):
        self.magic = struct.unpack('<I', f.read(4))[0]

        self.fileSize = struct.unpack('<I', f.read(4))[0]
        self.endOfHeaderOffset = struct.unpack('<I', f.read(4))[0]
        self.entryCount = struct.unpack('<I', f.read(4))[0]
        self.navSystemOffset = struct.unpack('<I', f.read(4))[0]
        self.fileIndex = struct.unpack('<B', f.read(1))[0]

        self.u0a = struct.unpack('<B', f.read(1))[0]
        self.u0b = struct.unpack('<B', f.read(1))[0]
        self.u0c = struct.unpack('<B', f.read(1))[0]

        self.section2Offset = struct.unpack('<I', f.read(4))[0]
        self.o6 = struct.unpack('<I', f.read(4))[0]
        self.origin = Vector3(f)

        self.section3Offset = struct.unpack('<I', f.read(4))[0]
        self.u1b = struct.unpack('<I', f.read(4))[0]
        self.manifestOffset = struct.unpack('<I', f.read(4))[0]
        self.manifestSize = struct.unpack('<I', f.read(4))[0]

        self.u1c = struct.unpack('<I', f.read(4))[0]
        self.u1d = struct.unpack('<I', f.read(4))[0]

        self.xDivisor = struct.unpack('<H', f.read(2))[0]
        self.yDivisor = struct.unpack('<H', f.read(2))[0]
        self.zDivisor = struct.unpack('<H', f.read(2))[0]

        self.u1h = struct.unpack('<H', f.read(2))[0]

        self.n7 = struct.unpack('<B', f.read(1))[0]
        self.section2EntryCount = struct.unpack('<B', f.read(1))[0]
        self.n8 = struct.unpack('<H', f.read(2))[0]

        self.vals = [struct.unpack('<e', f.read(2))[0] for i in range(8)]


class ManifestSubEntry:
    def __init__(self, f):
        self.groupId = struct.unpack('<B', f.read(1))[0]
        self.u1b = struct.unpack('<B', f.read(1))[0]
        self.u2 = struct.unpack('<H', f.read(2))[0]
        self.payloadOffset = struct.unpack('<I', f.read(4))[0]
        self.entryType = ENTRY_TYPE_UINT8(struct.unpack('<B', f.read(1))[0]).name
        self.entrySize = struct.unpack('<H', f.read(2))[0]
        self.n4 = struct.unpack('<B', f.read(1))[0]

    def __repr__(self):
        return f'ManifestSubEntry : {json.dumps(vars(self), indent=2)}'
    __str__ = __repr__


class ManifestEntry:
    def __init__(self, f):
        self.subentries = [ManifestSubEntry(f) for i in range(3)]

    def __repr__(self):
        return f'ManifestEntry : {vars(self)}'
    __str__ = __repr__


class Manifest:
    def __init__(self, f):
        self.manifestEntryCount = struct.unpack('<I', f.read(4))[0]
        self.manifest = [ManifestEntry(f) for i in range(self.manifestEntryCount)]

    def __repr__(self):
        return f'Manifest : {vars(self)}'
    __str__ = __repr__


class NavWorldPoint:
    def __init__(self, f):
        self.position = Vertex(f)

    def __repr__(self):
        return f'NavWorldPoint : {vars(self)}'
    __str__ = __repr__


class NavWorldSubsection2Entry:
    def __init__(self, f):
        self.NavWorldSubsection3Offset = struct.unpack('<H', f.read(2))[0]
        self.subsection5Index = struct.unpack('<H', f.read(2))[0]
        self.countA = struct.unpack('<B', f.read(1))[0]
        self.countB = struct.unpack('<B', f.read(1))[0]

    def __repr__(self):
        return f'NavWorldSubsection2Entry : {vars(self)}'
    __str__ = __repr__


class NavWorldSubsection2:
    def __init__(self, f, numPoints):
        self.entries = [NavWorldSubsection2Entry(f) for i in range(numPoints)]

    def __repr__(self):
        return f'NavWorldSubsection2 : {vars(self)}'
    __str__ = __repr__


class NavWorldSubsection3Entry:
    def __init__(self, f, countA, countB):
        for j in range(countA):
            self.adjacentNode = struct.unpack('<H', f.read(2))[0]
            self.edgeIndex = struct.unpack('<H', f.read(2))[0]
        for j in range(countB):
            self.u3 = struct.unpack('<H', f.read(2))[0]

    def __repr__(self):
        return f'NavWorldSubsection3Entry : {vars(self)}'
    __str__ = __repr__


class NavWorldEdge:
    def __init__(self, f):
        self.weight = struct.unpack('<H', f.read(2))[0]
        self.subsection5Index = struct.unpack('<H', f.read(2))[0]

        self.u3 = IndexPair8(f)

    def __repr__(self):
        return f'NavWorldEdge : {vars(self)}'
    __str__ = __repr__


class NavWorldSubsection5Entry:
    def __init__(self, f):
        self.flags = struct.unpack('<H', f.read(2))[0]

    def __repr__(self):
        return f'NavWorldSubsection5Entry : {vars(self)}'
    __str__ = __repr__


class NavWorldSubsection5:
    def __init__(self, f, numSubsection5Entries):
        self.entries = [NavWorldSubsection5Entry(f) for i in range(numSubsection5Entries)]

    def __repr__(self):
        return f'NavWorldSubsection5 : {vars(self)}'
    __str__ = __repr__


class NavWorldSubsection6Entry:
    def __init__(self, f):
        self.navmeshSubsection2Index = struct.unpack('<H', f.read(2))[0]

    def __repr__(self):
        return f'NavWorldSubsection6Entry : {vars(self)}'
    __str__ = __repr__


class NavWorldSubsection6:
    def __init__(self, f, numPoints):
        self.entries = [NavWorldSubsection6Entry(f) for i in range(numPoints)]

    def __repr__(self):
        return f'NavWorldSubsection6 : {vars(self)}'
    __str__ = __repr__


class NavWorld:
    def __init__(self, f):
        self.SelfStartPosition = f.tell()
        self.subsection1Offset = struct.unpack('<I', f.read(4))[0]
        assert(self.subsection1Offset == 48)

        self.subsection2Offset = struct.unpack('<I', f.read(4))[0]
        self.subsection4Offset = struct.unpack('<I', f.read(4))[0]

        self.subsection3Offset = struct.unpack('<I', f.read(4))[0]
        self.u1 = struct.unpack('<I', f.read(4))[0]
        assert(self.u1 == 0)

        self.u2 = struct.unpack('<I', f.read(4))[0]
        assert(self.u2 == 0)

        self.subsection5Offset = struct.unpack('<I', f.read(4))[0]
        self.u3 = struct.unpack('<I', f.read(4))[0]
        assert(self.u3 == 0)

        self.subsection6Offset = struct.unpack('<I', f.read(4))[0]

        self.numPoints = struct.unpack('<H', f.read(2))[0]
        self.numEdges = struct.unpack('<H', f.read(2))[0]

        self.probablyPadding1 = struct.unpack('<H', f.read(2))[0]
        self.probablyPadding2 = struct.unpack('<H', f.read(2))[0]
        self.probablyPadding3 = struct.unpack('<H', f.read(2))[0]
        assert(self.probablyPadding1 == 0 & self.probablyPadding2 == 0 & self.probablyPadding3 == 0)

        self.numSubsection5Entries = struct.unpack('<H', f.read(2))[0]

        f.seek(self.SelfStartPosition + self.subsection1Offset)

        self.points = [NavWorldPoint(f) for i in range(self.numPoints)]

        f.seek(self.SelfStartPosition + self.subsection2Offset)

        self.subsection2 = NavWorldSubsection2(f, self.numPoints)

        f.seek(self.SelfStartPosition + self.subsection3Offset)
        self.entries = []
        for i in range(self.numPoints):
            f.seek(self.SelfStartPosition + self.subsection3Offset +
                   (self.subsection2.entries[i].NavWorldSubsection3Offset * 2))
            self.entries.append(NavWorldSubsection3Entry(
                f, self.subsection2.entries[i].countA, self.subsection2.entries[i].countB))

        f.seek(self.SelfStartPosition + self.subsection4Offset)

        self.edges = [NavWorldEdge(f) for i in range(self.numEdges)]

        f.seek(self.SelfStartPosition + self.subsection5Offset)

        self.subsection5 = NavWorldSubsection5(f, self.numSubsection5Entries)

        f.seek(self.SelfStartPosition + self.subsection6Offset)

        self.subsection6 = NavWorldSubsection6(f, self.numPoints)


class NavmeshChunk:
    def __init__(self, f):
        self.SelfStartPosition = f.tell()
        self.subsection1Offset = struct.unpack('<I', f.read(4))[0]
        assert(self.subsection1Offset == 32)

        self.subsection2Offset = struct.unpack('<I', f.read(4))[0]
        self.subsection3Offset = struct.unpack('<I', f.read(4))[0]

        self.uu1 = struct.unpack('<H', f.read(2))[0]
        self.uu2 = struct.unpack('<H', f.read(2))[0]
        self.uu3 = struct.unpack('<H', f.read(2))[0]
        self.uu4 = struct.unpack('<H', f.read(2))[0]
        self.uu5 = struct.unpack('<H', f.read(2))[0]
        self.uu6 = struct.unpack('<H', f.read(2))[0]

        self.numFaces = struct.unpack('<H', f.read(2))[0]
        self.numVertices = struct.unpack('<H', f.read(2))[0]

        self.u4 = struct.unpack('<H', f.read(2))[0]
        self.u5 = struct.unpack('<H', f.read(2))[0]

        f.seek(self.SelfStartPosition + self.subsection1Offset)

        self.vertices = [Vertex(f) for i in range(self.numVertices)]

        f.seek(self.SelfStartPosition + self.subsection2Offset)

        self.faceOffsets = [struct.unpack('<I', f.read(4))[0] for i in range(self.numFaces)]

        f.seek(self.SelfStartPosition + self.subsection3Offset)

        self.faces = []

        for i in range(self.numFaces):
            f.seek(self.SelfStartPosition + self.subsection3Offset + (self.faceOffsets[i] & 0x3ffff) * 2)
            if (self.faceOffsets[i] >> 0x12 & 1 > 0):
                self.adjacentFaces = [struct.unpack('<h', f.read(2))[0] for k in range(4)]
            else:
                self.adjacentFaces = [struct.unpack('<h', f.read(2))[0] for k in range(3)]
            self.v1 = struct.unpack('<b', f.read(1))[0]
            self.v2 = struct.unpack('<b', f.read(1))[0]
            self.v3 = struct.unpack('<b', f.read(1))[0]

            if (self.faceOffsets[i] >> 0x12 & 1 > 0):
                self.v4 = struct.unpack('<b', f.read(1))[0]
                self.faces.append([self.v1, self.v2, self.v3, self.v4])
            else:
                self.faces.append([self.v1, self.v2, self.v3])
            if (self.faceOffsets[i] >> 0x12 & 1 > 0):
                self.edgeIndices = [struct.unpack('<b', f.read(1))[0] for k in range(4)]

            else:
                self.edgeIndices = [struct.unpack('<b', f.read(1))[0] for k in range(3)]


class SegmentChunkSubsection1Entry:
    def __init__(self, f):
        self.a = Vertex(f)
        self.b = Vertex(f)

    def __repr__(self):
        return f'SegmentChunkSubsection1Entry : {vars(self)}'
    __str__ = __repr__


class SegmentChunkSubsection2Entry:
    def __init__(self, f):
        self.vertexIndexOffset = struct.unpack('<h', f.read(2))[0]
        self.navmeshChunkSubsection2EntryIndex = struct.unpack('<h', f.read(2))[0]
        self.u3 = struct.unpack('<h', f.read(2))[0]
        self.u4 = struct.unpack('<h', f.read(2))[0]

        self.verts = struct.unpack('<b', f.read(1))[0]
        self.faces = struct.unpack('<b', f.read(1))[0]
        self.u7 = struct.unpack('<b', f.read(1))[0]
        self.edges = struct.unpack('<b', f.read(1))[0]

    def __repr__(self):
        return f'SegmentChunkSubsection2Entry : {vars(self)}'
    __str__ = __repr__


class SegmentChunk:
    def __init__(self, f):
        self.SelfStartPosition = f.tell()
        self.subsection1Offset = struct.unpack('<I', f.read(4))[0]
        assert(self.subsection1Offset == 16)

        self.subsection2Offset = struct.unpack('<I', f.read(4))[0]

        self.totalSize = struct.unpack('<I', f.read(4))[0]
        self.entryCount = struct.unpack('<I', f.read(4))[0]

        self.subsection1 = [SegmentChunkSubsection1Entry(f) for i in range(self.entryCount)]

        f.seek(self.SelfStartPosition + self.subsection2Offset)

        self.subsection2 = [SegmentChunkSubsection2Entry(f) for i in range(self.entryCount)]


class NavWorldSegmentGraphSubsection1Entry:
    def __init__(self, f):
        self.position = Vertex(f)

    def __repr__(self):
        return f'NavWorldSegmentGraphSubsection1Entry : {vars(self)}'
    __str__ = __repr__


class NavWorldSegmentGraphSubsection2Entry:
    def __init__(self, f):
        self.subsection3Index = [struct.unpack('<B', f.read(1))[0] for i in range(3)]
        self.nEdges = struct.unpack('<B', f.read(1))[0]
        self.u3 = struct.unpack('<h', f.read(2))[0]
        self.u4 = struct.unpack('<H', f.read(2))[0]
        self.u5 = struct.unpack('<b', f.read(1))[0]
        self.u6 = struct.unpack('<b', f.read(1))[0]
        self.offGroupEdges = struct.unpack('<b', f.read(1))[0]
        self.offMeshEdges = struct.unpack('<b', f.read(1))[0]

    def __repr__(self):
        return f'NavWorldSegmentGraphSubsection2Entry : {vars(self)}'
    __str__ = __repr__


class NavWorldSegmentType1Edges:
    def __init__(self, f):
        self.weight = struct.unpack('<H', f.read(2))[0]
        self.adjacentNode = struct.unpack('<H', f.read(2))[0]
        self.adjacentEdgeCount = struct.unpack('<B', f.read(1))[0]
        self.u1 = struct.unpack('<B', f.read(1))[0]

    def __repr__(self):
        return f'NavWorldSegmentType1Edges : {vars(self)}'
    __str__ = __repr__


class NavWorldSegmentType2Edges:
    def __init__(self, f):
        self.groupId = struct.unpack('<H', f.read(2))[0]
        self.weight = struct.unpack('<H', f.read(2))[0]
        self.adjacentNode = struct.unpack('<H', f.read(2))[0]
        self.adjacentEdgeCount = struct.unpack('<B', f.read(1))[0]
        self.u5 = struct.unpack('<B', f.read(1))[0]

    def __repr__(self):
        return f'NavWorldSegmentType2Edges : {vars(self)}'
    __str__ = __repr__


class NavWorldSegmentType3Edges:
    def __init__(self, f):
        self.u1 = struct.unpack('<H', f.read(2))[0]
        self.groupId = struct.unpack('<H', f.read(2))[0]
        self.adjacentNode = struct.unpack('<H', f.read(2))[0]
        self.u4 = struct.unpack('<H', f.read(2))[0]
        self.adjacentEdgeCount = struct.unpack('<B', f.read(1))[0]
        self.u6 = struct.unpack('<B', f.read(1))[0]

    def __repr__(self):
        return f'NavWorldSegmentType3Edges : {vars(self)}'
    __str__ = __repr__


class NavWorldSegmentGraph:
    def __init__(self, f):
        self.SelfStartPosition = f.tell()
        self.subsection1Offset = struct.unpack('<I', f.read(4))[0]
        assert(self.subsection1Offset == 32)

        self.subsection2Offset = struct.unpack('<I', f.read(4))[0]
        self.subsection3Offset = struct.unpack('<I', f.read(4))[0]

        self.uu1 = struct.unpack('<I', f.read(4))[0]
        self.totalSize = struct.unpack('<I', f.read(4))[0]
        self.subsection1EntryCount = struct.unpack('<I', f.read(4))[0]
        self.uu3 = struct.unpack('<H', f.read(2))[0]
        self.totalEdges = struct.unpack('<I', f.read(4))[0]
        self.padding = struct.unpack('<H', f.read(2))[0]

        f.seek(self.SelfStartPosition + self.subsection1Offset)

        self.subsection1 = [NavWorldSegmentGraphSubsection1Entry(f) for i in range(self.subsection1EntryCount)]

        f.seek(self.SelfStartPosition + self.subsection2Offset)

        self.subsection2 = [NavWorldSegmentGraphSubsection2Entry(f) for i in range(self.subsection1EntryCount)]

        if (self.subsection3Offset != self.totalSize):
            f.seek(self.SelfStartPosition + self.subsection3Offset)

            for i in range(self.subsection1EntryCount):
                n = self.subsection2[i].subsection3Index
                offset = (n[0]) + ((n[1]) << 8) + ((n[2]) << 16)
                f.seek(self.SelfStartPosition + self.subsection3Offset + offset*2)
                if (self.subsection2[i].nEdges > 0):
                    self.type1Edges = [NavWorldSegmentType1Edges(f) for i in range(self.subsection2[i].nEdges)]

                if (self.subsection2[i].offGroupEdges > 0):
                    self.type2Edges = [NavWorldSegmentType2Edges(f) for i in range(self.subsection2[i].offGroupEdges)]

                if (self.subsection2[i].offMeshEdges > 0):
                    self.type3Edges = [NavWorldSegmentType3Edges(f) for i in range(self.subsection2[i].offMeshEdges)]

                if (self.subsection2[i].nEdges > 0):
                    self.type1AdjacentEdges = [[struct.unpack('<B', f.read(1))[0] for k in range(
                        self.type1Edges[j].adjacentEdgeCount)]for j in range(self.subsection2[i].nEdges)]

                if (self.subsection2[i].offGroupEdges > 0):
                    self.type2AdjacentEdges = [[struct.unpack('<B', f.read(1))[0] for k in range(
                        self.type2Edges[j].adjacentEdgeCount)]for j in range(self.subsection2[i].offGroupEdges)]

                if (self.subsection2[i].offMeshEdges > 0):
                    self.type3AdjacentEdges = [[struct.unpack('<B', f.read(1))[0] for k in range(
                        self.type3Edges[j].adjacentEdgeCount)]for j in range(self.subsection2[i].offMeshEdges)]


class Entry:
    def __init__(self, f, header, count):
        self.SelfStartPosition = f.tell()
        self.entryType = ENTRY_TYPE(struct.unpack('<H', f.read(2))[0]).name
        self.u1 = struct.unpack('<H', f.read(2))[0]
        assert(self.u1 == 0)

        self.nextEntryRelativeOffset = struct.unpack('<I', f.read(4))[0]
        self.payloadRelativeOffset = struct.unpack('<I', f.read(4))[0]
        self.groupId = struct.unpack('<B', f.read(1))[0]
        self.u2 = struct.unpack('<B', f.read(1))[0]
        self.n3 = struct.unpack('<H', f.read(2))[0]

        if self.entryType == 'NAVWORLD':
            f.seek(self.SelfStartPosition + self.payloadRelativeOffset)
            world = NavWorld(f)
            navWorlds[self.groupId] = world
        elif self.entryType == 'NAVMESH_CHUNK':
            f.seek(self.SelfStartPosition + self.payloadRelativeOffset)
            chunk = NavmeshChunk(f)
            navmeshChunks[self.groupId] = chunk
        elif self.entryType == 'NAVWORLD_SEGMENT_GRAPH':
            f.seek(self.SelfStartPosition + self.payloadRelativeOffset)
            navWorldSegmentGraph = NavWorldSegmentGraph(f)
            segmentGraphs[self.groupId] = navWorldSegmentGraph
        elif self.entryType == 'SEGMENT_CHUNK':
            f.seek(self.SelfStartPosition + self.payloadRelativeOffset)
            segmentChunk = SegmentChunk(f)
            segmentChunks[self.groupId] = segmentChunk
        else:
            pass
        f.seek(self.SelfStartPosition + self.nextEntryRelativeOffset)


class Section2Entry:
    def __init__(self, f):
        self.SelfStartPosition = f.tell()
        self.nextEntryRelativeOffset = struct.unpack('<H', f.read(2))[0]
        self.subsection1RelativeOffset = struct.unpack('<H', f.read(2))[0]
        self.subEntryCount = struct.unpack('<H', f.read(2))[0]
        self.subsection2RelativeOffset = struct.unpack('<H', f.read(2))[0]
        self.subsection3RelativeOffset = struct.unpack('<H', f.read(2))[0]
        self.subsection4RelativeOffset = struct.unpack('<H', f.read(2))[0]
        self.subsection5RelativeOffset = struct.unpack('<H', f.read(2))[0]
        self.subsection6RelativeOffset = struct.unpack('<H', f.read(2))[0]

        f.seek(self.SelfStartPosition + self.subsection1RelativeOffset)

        self.subsection1Entries = [Section2Subsection1(f) for i in range(self.subEntryCount)]

        f.seek(self.SelfStartPosition + self.subsection2RelativeOffset)

        for i in range(self.subEntryCount):
            if (self.subsection1Entries[i].countA >= 0):
                self.aEntries = [AEntries(f) for i in range(self.subsection1Entries[i].countA)]
            if (self.subsection1Entries[i].countB > 0):
                self.bEntries = [BEntries(f) for i in range(self.subsection1Entries[i].countB)]
        f.seek(self.SelfStartPosition + self.subsection3RelativeOffset)
        self.subsection3Entries = [Section2Subsection3(f) for i in range(self.subEntryCount)]
        f.seek(self.SelfStartPosition + self.subsection4RelativeOffset)
        self.subsection4Entries = [Section2Subsection4(f) for i in range(self.subEntryCount)]
        assert(self.subsection6RelativeOffset - self.subsection5RelativeOffset == 24)
        self.subsection5Entries = Section2Subsection5(f)


class Section2Subsection1:
    def __init__(self, f):
        self.SelfStartPosition = f.tell()
        self.position = Vertex(f)
        self.flags = struct.unpack('<H', f.read(2))[0]
        self.subsection2Offset = struct.unpack('<H', f.read(2))[0]
        self.countB = struct.unpack('<H', f.read(2))[0]
        self.countA = struct.unpack('<H', f.read(2))[0]

    def __repr__(self):
        return f'Section2Subsection1 : {vars(self)}'
    __str__ = __repr__


class AEntries:
    def __init__(self, f):
        self.weight = struct.unpack('<H', f.read(2))[0]
        self.adjacentNodeIndex = struct.unpack('<H', f.read(2))[0]

    def __repr__(self):
        return f'AEntries : {vars(self)}'
    __str__ = __repr__


class BEntries:
    def __init__(self, f):
        self.u3 = struct.unpack('<H', f.read(2))[0]

    def __repr__(self):
        return f'BEntries : {vars(self)}'
    __str__ = __repr__


class Section2Subsection3:
    def __init__(self, f):
        self.u1 = struct.unpack('<I', f.read(4))[0]
        self.u5 = struct.unpack('<H', f.read(2))[0]
        self.u7 = struct.unpack('<H', f.read(2))[0]

    def __repr__(self):
        return f'Section2Subsection3 : {vars(self)}'
    __str__ = __repr__


class Section2Subsection4:
    def __init__(self, f):
        self.n1 = struct.unpack('<H', f.read(2))[0]

    def __repr__(self):
        return f'Section2Subsection4 : {vars(self)}'
    __str__ = __repr__


class Section2Subsection5:
    def __init__(self, f):
        self.u1 = [struct.unpack('<B', f.read(1))[0] for i in range(24)]

    def __repr__(self):
        return f'Section2Subsection5 : {vars(self)}'
    __str__ = __repr__


class NavSystemSubsection1Entry:
    def __init__(self, f):
        self.section2relativeOffset = struct.unpack('<I', f.read(4))[0]
        self.entryCount = struct.unpack('<H', f.read(2))[0]
        self.u2 = struct.unpack('<B', f.read(1))[0]
        self.u3 = struct.unpack('<B', f.read(1))[0]

    def __repr__(self):
        return f'NavSystemSubsection1Entry : {vars(self)}'
    __str__ = __repr__


class NavSystemSubsection2Entry:
    def __init__(self, f):
        self.groupId = struct.unpack('<b', f.read(1))[0]
        self.u1 = struct.unpack('<b', f.read(1))[0]
        self.u2 = struct.unpack('<H', f.read(2))[0]
        self.count = struct.unpack('<I', f.read(4))[0]
        self.vals = [struct.unpack('<H', f.read(2))[0] for i in range(self.count)]

    def __repr__(self):
        return f'NavSystemSubsection2Entry : {vars(self)}'
    __str__ = __repr__


class NavSystem:
    def __init__(self, f):
        self.SelfStartPosition = f.tell()
        self.u1 = Vector4(f)
        self.n1 = struct.unpack('<I', f.read(4))[0]
        self.n2 = struct.unpack('<I', f.read(4))[0]
        self.u3 = struct.unpack('<I', f.read(4))[0]
        self.chunkSize = struct.unpack('<I', f.read(4))[0]
        self.n5 = struct.unpack('<I', f.read(4))[0]
        self.subsection1Offset = struct.unpack('<I', f.read(4))[0]
        assert (self.subsection1Offset == 48)

        self.subsection2Offset = struct.unpack('<I', f.read(4))[0]
        self.subsection3Offset = struct.unpack('<I', f.read(4))[0]

        f.seek(self.SelfStartPosition + self.subsection1Offset)

        self.subsection1 = [NavSystemSubsection1Entry(f) for i in range(self.n1*self.u3)]

        for i in range(self.n1*self.u3):

            f.seek(self.SelfStartPosition + self.subsection1Offset +
                   (i * 8) + self.subsection1[i].section2relativeOffset)
            self.entries = [NavSystemSubsection2Entry(f) for j in range(self.subsection1[i].entryCount)]


class Nav2:
    def __init__(self):
        pass

    def Read(self, f):
        nav2_name = os.path.basename(f).split('.')[0]
        f = open(f, 'rb')
        header = Header(f)
        manifest = Manifest(f)
        f.seek(header.endOfHeaderOffset)
        entry = [Entry(f, header, i) for i in range(header.entryCount)]
        print(navWorlds)
        print(segmentGraphs)
        print(segmentChunks)
        print(navmeshChunks)

        if (header.section2Offset):
            f.seek(header.section2Offset)

            remainingEntries = header.section2EntryCount
            while(remainingEntries != 0):
                startOffset = f.tell()
                section2Entry = Section2Entry(f)
                section2Entries.append(section2Entry)
                f.seek(startOffset + section2Entry.nextEntryRelativeOffset)
                remainingEntries -= 1

        if (header.navSystemOffset != 0):
            f.seek(header.navSystemOffset)
            navSystem = NavSystem(f)

        for gr, group in enumerate(segmentChunks.keys()):
            navmesh = navmeshChunks[group]
            vertices = [[-(verts[0] / header.xDivisor + header.origin[0]), verts[2] / header.zDivisor +
                         header.origin[2], verts[1] / header.yDivisor + header.origin[1]]for verts in navmesh.vertices]
            create_empty(nav2_name, f'{nav2_name}_NavMeshChunk[{gr}]')

            for ch, chunk in enumerate(segmentChunks[group].subsection2):
                faces = []
                for i in range(chunk.faces):

                    navmeshChunk = navmesh.faces[chunk.navmeshChunkSubsection2EntryIndex + i]
                    f1 = navmeshChunk[0] + chunk.vertexIndexOffset
                    f2 = navmeshChunk[1] + chunk.vertexIndexOffset
                    f3 = navmeshChunk[2] + chunk.vertexIndexOffset
                    faces.append([f1, f2, f3])
                create_mesh(
                    nav2_name, f'{nav2_name}_NavMeshChunk[{gr}]', f'{nav2_name}_NavMeshChunk[{gr}]_chunk[{ch}]', vertices=vertices, faces=faces)

        for gr, group in enumerate(segmentChunks.keys()):
            create_empty(nav2_name, f'{nav2_name}_SegmentGraph[{gr}]')

            vertices = []
            v = 0
            for ch, node in enumerate(segmentGraphs[group].subsection1):
                x = node.position[0] / header.xDivisor + header.origin[0]
                y = node.position[2] / header.zDivisor + header.origin[2]
                z = node.position[1] / header.yDivisor + header.origin[1]
                vertices.append([-(x - 0.5), y + 0.5, z - 0.5])
                vertices.append([-(x - 0.5), y + 0.5, z + 0.5])
                vertices.append([-(x + 0.5), y + 0.5, z - 0.5])
                vertices.append([-(x + 0.5), y + 0.5, z + 0.5])
                faces = [[v, v+1, v+2, v+3]]
                create_mesh(
                    nav2_name, f'{nav2_name}_SegmentGraph[{gr}]', f'{nav2_name}_SegmentGraph[{gr}]_chunk[{ch}]', vertices=vertices, faces=faces)

                v += 4

        if (header.section2EntryCount > 0):
            create_empty(nav2_name, f'{nav2_name}_Section2[{gr}]')
            vertices = []
            for nb, section2_entry in enumerate(section2Entries[0].subsection1Entries):
                x = section2_entry.position[0] / header.xDivisor + header.origin[0]
                y = section2_entry.position[2] / header.zDivisor + header.origin[2]
                z = section2_entry.position[1] / header.yDivisor + header.origin[1]
                vertices.append([-(x - 0.5), y + 0.5, z - 0.5])
                vertices.append([-(x - 0.5), y + 0.5, z + 0.5])
                vertices.append([-(x + 0.5), y + 0.5, z - 0.5])
                vertices.append([-(x + 0.5), y + 0.5, z + 0.5])
            edges = []
            for i in range(len(section2Entries[0].subsection1Entries)):
                try:
                    for j in range(len(section2Entries[0].aEntries[i].adjacentNodeIndex)):
                        adjacentEdge = section2Entries[0].aEntries[i].adjacentNodeIndex[j]
                        edges.append([i, adjacentEdge + i])
                except:
                    edges = []

            create_mesh(nav2_name, f'{nav2_name}_Section2[{gr}]',
                        f'{nav2_name}_Section2[{gr}]_chunk[{ch}]', vertices=vertices, edges=edges)
