__author__ = "Mario Lukas"
__copyright__ = "Copyright 2015"
__license__ = "AGPL"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import os
from fabscan.FSConfig import Config


class FSPointCloud():

    def __init__(self, color=True):
        self.points = []
        self.file_name = None
        self._dir_name = None
        self.color = color
        self.config = Config.instance()

    def append_point(self, points):
        self.points.append(points)

    def get_size(self):
        return len(self.points)

    def writeHeader(self):
        pass

    def writePointsToFile(self):
        pass

    def calculateNormals(self):
        pass

    def saveAsFile(self, file_name):

        basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self._dir_name = self.config.folders.scans+file_name

        if not os.path.exists(self._dir_name):
            os.makedirs(self._dir_name)

        with open(self._dir_name +'/scan_' +file_name + '.ply', 'w') as f:
            f.write("ply\nformat ascii 1.0\n")
            f.write("element vertex {0}\n".format(len(self.points)))
            f.write("property float x\nproperty float y\nproperty float z\nproperty uchar red\nproperty uchar green\nproperty uchar blue\n")
            f.write("element face 0\n")
            f.write("element edge 0\n")
            f.write("element face 0\n")
            f.write("property list uchar int vertex_indices\n")
            f.write("end_header\n")
            scaler_in_mm = 10
            for point in self.points:
                x = float(point['x'])*scaler_in_mm
                y = float(point['y'])*scaler_in_mm
                z = float(point['z'])*scaler_in_mm
                if self.color:
                    f.write("{0} {1} {2} {3} {4} {5}\n".format( str(x),str(z),str(y) , point['r'], point['g'], point['b']))
                else:
                    f.write("{0} {1} {2} {3} {4} {5}\n".format( str(x),str(z),str(y) , 255, 255, 255))