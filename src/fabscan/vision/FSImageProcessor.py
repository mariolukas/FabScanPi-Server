__author__ = "Mario Lukas"
__copyright__ = "Copyright 2015"
__license__ = "AGPL"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import math
import logging, os
import numpy as np
import cv2

class FSPoint():
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z

class FSLine():
    def __init__(self, a=0.0, b=0.0):
        self.a = a
        self.b = b


class ImageProcessor():
    def __init__(self, config, settings):

        self._logger =  logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)
        self.settings = settings
        self.config = config


    def get_texture_preview_image(self,cam_image):
        return cam_image


    def get_preview_image(self, cam_image, type='CAMERA'):

        x_center = cam_image.shape[1] * self.settings.center
        x_center_delta = cam_image.shape[1] * 0.5 - x_center

        sub_pixel, cam_image = self.line_coords(cam_image,filter=True, fast=False ,x_center_delta=x_center_delta) #np.argmax(line[ 0: width])

        cv2.line(cam_image, (0,int(self.config.scanner.origin.y*cam_image.shape[0])), (cam_image.shape[1],int(0.75*cam_image.shape[0])), (0,255,0), thickness=1, lineType=8, shift=0)
        cv2.line(cam_image, (int(0.5*cam_image.shape[1]),0), (int(0.5*cam_image.shape[1]), cam_image.shape[0]), (0,255,0), thickness=1, lineType=8, shift=0)

        r = 320.0 / cam_image.shape[1]
        dim = (320, int(cam_image.shape[0] * r))
        cam_image = cv2.resize(cam_image, dim, interpolation = cv2.INTER_AREA)
        return cam_image




    def process_image(self, angle, laser_image, color_image=None):
        ''' Takes picture and angle (in degrees).  Adds to point cloud '''

        x_center = laser_image.shape[1] * self.settings.center
        x_center_delta = laser_image.shape[1] * 0.5 - x_center

        pixels, image = self.line_coords(laser_image,filter=True, fast=False, x_center_delta=x_center_delta)  # Get line coords from image

        points = self.process_line(pixels, angle , color_image)
        return points


    def calculate_laser_angle(self, calibration_image):


        point = self.detect_laser(calibration_image)

        if point != None:
            self._logger.debug("Found a point for laser angle calculation")
            self.settings.backwall.laser.x = point.x
            self.settings.backwall.laser.y = point.y
            self.settings.backwall.laser.z = point.z

            b = self.config.laser.position.x - point.x
            a = self.config.laser.position.z - point.z
            angle = math.atan(b/a) * 180.0 / math.pi
            self.config.laser.angle = angle
            return  angle
        else:
            self._logger.debug("No laser angle calculated")
            return None



    def detect_laser(self, image):

        x_center = image.shape[1] * self.settings.center
        x_center_delta = image.shape[1] * 0.5 - x_center

        basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        dir_name =  basedir+"/static/"
        cv2.imwrite(dir_name+"debug.jpg", image)

        x, image = self.line_coords(image, filter=False, fast=True, x_center_delta=x_center_delta)

        if x != []:
            x = x[:,0]
            new_x = []

            for i in xrange(1,20):
                new_x.append(x[i])


            x = np.sort(new_x)
            point = FSPoint( x[len(x)/2] , 0.0, 0.0)

            # save pixel position of laser line x direction
            self.settings.backwall.laser_pixel_position = point.x

            # make a camera system point of laser line on backwall
            laser_backwall = FSPoint()
            laser_backwall.x = point.x
            laser_backwall = self.convertCvPointToPoint(laser_backwall)


            self.settings.backwall.laser.x = laser_backwall.x
            self.settings.backwall.laser.y = laser_backwall.y
            self.settings.backwall.laser.z = laser_backwall.z

            self._logger.debug("Laser Backwall x: %d" % (point.x, ))

            fs_point = self.convertCvPointToPoint(point)

            return fs_point

        else:
            self._logger.debug("Can not detect laser line on backwall.")
            return None

    def get_grey(self, image):
        hsv_img = cv2.cvtColor(image, cv2.cv.CV_BGR2HSV)
        h, s, v = cv2.split(hsv_img)
        height, width, channels = image.shape

        blur = cv2.GaussianBlur(v,(11,11),0)
        return blur


    def line_coords(self, image,  filter=True, fast=False, x_center_delta=None):
        '''
        Return [a list of (x,y)] tuples representing middle white pixel per line
        If x_center given, transforms coordinates so that
            the axis of rotation is x=0.
        '''
        grey = self.get_grey(image)

        pixels = []
        if filter:
            start = self.settings.backwall.laser_pixel_position+20
        else:
            start = 0

        if fast:

            for y, line in enumerate(grey):
                    sub_pixel =  np.argmax(line[ start: image.shape[1]]) + start
                    if line[sub_pixel] > self.settings.threshold:
                        cv2.line(image, (int(sub_pixel)-5,int(y)), (int(sub_pixel)+5,int(y)), (255,0,0), thickness=1, lineType=8, shift=0)
                        pixels.append(( sub_pixel, y))

        else:


            start = self.settings.backwall.laser_pixel_position+20
            id = np.indices((image.shape[0],image.shape[1]))[1]

            grey[grey < self.settings.threshold] = 0

            id_mul = id[:,start:]*grey[:,start:]

            sum_t = id_mul.astype(float).sum(axis=1)
            sum_a = grey[:,start:].astype(float).sum(axis=1)

            weight =  np.squeeze(sum_t/sum_a)



            it = np.nditer(weight, flags=['f_index'])
            while not it.finished:

                   if it[0] > 0:
                       pixels.append((float(it[0]),it.index))
                       cv2.line(image, (int(it[0])-5,int(it.index)), (int(it[0])+5,int(it.index)), (255,0,0), thickness=1, lineType=8, shift=0)

                   it.iternext()



        if x_center_delta:
               pixels = [(x -x_center_delta, y) for (x, y) in pixels]


        return np.array(pixels), image


    def process_line(self, line_coords, angle, color_image=None):


        point_line = []

        for x, y in line_coords:

            # create new cv point
            #x_center = self.config.camera.resolution.width * self.settings.center
            # laser_point = FSPoint(x+x_center ,y)

            point = FSPoint(x ,y)

            ## world coordinates without deepth
            point = self.convertCvPointToPoint(point)

            camera_position = FSPoint(self.config.camera.position.x, self.config.camera.position.y, self.config.camera.position.z)
            laser_position = FSPoint(self.config.laser.position.x,self.config.laser.position.y,self.config.laser.position.z)
            laser_backwall = FSPoint(self.settings.backwall.laser.x,self.settings.backwall.laser.y, self.settings.backwall.laser.z)


            line1 = self.computeLineFromPoints(camera_position, point)
            line2 = self.computeLineFromPoints(laser_backwall, laser_position)

            intersection = self.computeLineIntersections(line1, line2)

            point.x = intersection.x
            point.z = intersection.z

            point.y -= self.config.camera.position.y
            point.y *= (self.config.camera.position.z - point.z)/self.config.camera.position.z
            point.y += self.config.camera.position.y

            point.z -= self.config.turntable.position.z
            alphaDetla = angle
            alphaOld = float(math.atan(point.z/point.x))
            alphaNew = alphaOld+alphaDetla*(math.pi/180.0)
            hypotenuse = float(math.sqrt(point.x*point.x + point.z*point.z))

            if point.z < 0 and point.x < 0:
                alphaNew += math.pi
            elif (point.z > 0) and (point.x < 0):
                alphaNew -= math.pi

            point.z = math.sin(alphaNew)*hypotenuse
            point.x = math.cos(alphaNew)*hypotenuse

            lowerLimit = 1.09

            if (point.y>lowerLimit and hypotenuse < 7 ):
                new_point = dict()

                new_point['x'] = str(point.x)
                new_point['y'] = str(point.y)
                new_point['z'] = str(-point.z)

                if not color_image is None:
                    b,g,r = color_image[y,x]
                    new_point['r'] = str(r)
                    new_point['g'] = str(g)
                    new_point['b'] = str(b)


                point_line.append(new_point)

        return point_line


    def computeLineFromPoints(self, p1, p2):
        line = FSLine()
        line.a = (p2.z-p1.z)/(p2.x-p1.x)
        line.b = p1.z-line.a*p1.x
        return line

    def computeLineIntersections(self,  line1, line2):
        intersection = FSPoint()
        intersection.x = (line2.b - line1.b)/(line1.a-line2.a)
        intersection.z = line2.a*intersection.x+line2.b
        return intersection


    def convertPointToCvPoint(self, point):
        fsImgWidth = self.config.camera.frame.dimension
        fsImgHeight = self.config.camer.frame.dimension*(self.config.camera.resolution.height/self.config.camera.resolution.width)

        origin = FSPoint(self.config.camera.resolution.width/2.0, self.config.camera.resolution.height*self.config.scanner.origin.y)
        point_x = (point.x*self.config.camera.resolution.width/fsImgWidth) + origin.x
        point_y = (-point.y*self.config.camera.resolution.height/fsImgHeight) +origin.y

        cvPoint = FSPoint(point_x, point_y)
        return cvPoint


    def convertCvPointToPoint(self, cvPoint):

        fsImgWidth = self.config.camera.frame.dimension
        fsImgHeight = fsImgWidth*(float(self.config.camera.resolution.height)/ float(self.config.camera.resolution.width))
        origin = FSPoint(self.config.camera.resolution.width/2.0, float(self.config.camera.resolution.height)*self.config.scanner.origin.y)
        point = FSPoint()
        point.x = (cvPoint.x -origin.x)*fsImgWidth/float(self.config.camera.resolution.width)
        point.y = -(cvPoint.y - origin.y)*fsImgHeight/float(self.config.camera.resolution.height)
        point.z = 0.0

        return point




