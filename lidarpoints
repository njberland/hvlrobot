import logging
import random
from statistics import mean


"""
Module for storing points received and handling operations


"""

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                    filename='robot.log',
                    level=logging.DEBUG)
logging.debug('Loading module robot')

class Point(object):
""" Class for one lidar point - next version should have pitch too
"""
    def __init__(self,dist,angle):
        self.dist = dist
        self.angle = angle


class LidarPoints(object):
    """ class for the storage and operations """

    def __init__(self,size):
        """ Storing arrays """
        self.maxsize = size

        self.leftdist = []
        self.leftangle = []

        self.rightdist = []
        self.rightangle = []

        self.frontdist = []
        self.frontangle = []

        self.backdist = []
        self.backangle = []

    def addtoleft(self,point):

        if len(self.leftangle) == self.maxsize:
            self.leftangle.pop(0)
            self.leftdist.pop(0)
        self.leftangle.append(point.angle)
        self.leftdist.append(point.dist)

    def addtoright(self,point):

        if len(self.rightangle) == self.maxsize:
            self.rightangle.pop(0)
            self.rightdist.pop(0)
        self.rightangle.append(point.angle)
        self.rightdist.append(point.dist)

    def addtofront(self,point):

        if len(self.frontangle) == self.maxsize:
            self.frontangle.pop(0)
            self.frontdist.pop(0)
        self.frontangle.append(point.angle)
        self.frontdist.append(point.dist)

    def addtoback(self,point):

        if len(self.backangle) == self.maxsize:
            self.backangle.pop(0)
            self.backdist.pop(0)
        self.backangle.append(point.angle)
        self.backdist.append(point.dist)

    def storenew(self,point):
        """ stores a new point in one of three directions - front, left, back and right

            methods to get status of the directions
        """

        # check out right
        if point.angle >= 70 and point.angle < 110:
            self.addtoright(point)

        # front
        elif (point.angle >= 0 and point.angle < 10) or (point.angle < 360 and point.angle >= 350):
            self.addtofront(point)

        # left
        elif point.angle >= 240 and point.angle < 300:
            self.addtoleft(point)

        # back
        elif point.angle >= 150 and point.angle < 210:
            self.addtoback(point)

        else:
            logging.debug("Angle out of range")

    def findmeandist(self):

        return (mean(self.leftdist), mean(self.rightdist), mean(self.frontdist), mean(self.backdist))

    def findcounts(self):
        return (len(self.leftdist), len(self.rightdist), len(self.frontdist), len(self.backdist))


if __name__ == "__main__":

    pointstore = LidarPoints(10)

    for i in range(100000):
        point = Point(random.randint(2,6), random.randint(0,359))
        pointstore.storenew(point)

    print(pointstore.findcounts())
    print(pointstore.findmeandist())
