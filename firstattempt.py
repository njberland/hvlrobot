import logging
import time
import threading

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                    filename='robot.log',
                    level=logging.DEBUG)
logging.debug('Loading module robot')


class Lidar(object):
    def __init__(self, setup):
        logging.info('Lidar started')

        thread = threading.Thread(target=self.lidarreader, args=())
        thread.daemon = True  # Daemonize thread
        thread.start()
        return

    def lidarreader(self):
        """This method runs the lidar as a thread"""
        while True:
            logging.debug('Hello from lidar reader')
            time.sleep(1)

    def run(self):
        return

class Vehicle(object):
    def __init__(self, setup):
        logging.info('Vehicle operational')
        return

    def run(self):
        return


class Robot(object):

    def __init__(self, setup):
        self.ipaddress = setup['IPADDRESS']
        self.lidarport = setup['LIDARPORT']
        self.lidarport = setup['VEHICLEPORT']
        self.lidar = Lidar(setup)
        self.vehicle = Vehicle(setup)

        if True:
            logging.warning("Something funny")

    def run(self):
        logging.info('Robot running')
        return True


if __name__ == "__main__":
    setup = {'IPADDRESS': '123',
             'LIDARPORT': 123,
             'VEHICLEPORT': 124}

    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                        filename='robot.log',
                        level=logging.DEBUG)
    robot = Robot(setup)
    robot.run()

    while True:
        logging.debug("Looping")
        time.sleep(5)
