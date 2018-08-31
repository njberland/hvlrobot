import logging
import time
import threading
import socket
import numpy
import random
import struct
from statistics import mean

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                    filename='robot.log',
                    level=logging.DEBUG)
logging.debug('Loading module robot')

HOST = '158.37.74.84'  # raspi IP.   VIKTIG! HVIS DENNE ENDRER SEG PÅ RASPI MÅ DENNE ENDRES TIL RIKTIG IP
LIDARPORT = 12346  # port til å motta Lidardata
VEHICLEPORT = 12345

LASER_ANGLES = [-15, 1, -13, 3, -11, 5, -9, 7, -7, 9, -5, 11, -3, 13, -1, 15]
NUM_LASERS = 16

EXPECTED_PACKET_TIME = 0.001327  # valid only in "the strongest return mode"
EXPECTED_SCAN_DURATION = 0.1


class Directions(object):
    
    def __init__(self):
        
        self.direction = 0

        self.minsteFrem = 100
        self.gjenomsnittFrem = 0

        self.lengdePaLister = 5  # length of lists
        
        self.alisteH = []  # distances to the right
        self.alisteV = []
        self.alisteF = []
        self.alisteB = []

        self.vlisteH = []  # angle to the right
        self.vlisteV = []
        self.vlisteF = []
        self.vlisteB = []

        self.ah = 0  # count in list (redundant)
        self.av = 0  # 
        self.af = 0  # 
        self.ab = 0  # 

        self.h = 0  # max value to the right
        self.vv = 0  #
        self.f = 0  # 
        self.b = 0  # 

        self.rettfrem = 0
        self.lll = 0
        

    def update(self,packet):
        """
        v = bytearray(packet)  # alt fra pakken legges i denne bytearrayen

        i = 0  # brukes i for-loopen for å holde styr på bytearrayen
        vinkel2 = 0  # brukes til å sjekke vinkler, slik at vi kan sortere vekk vinkler som er for nerme hverandre

        # loop over hele pakken - men vi VET hva som kommer og burde heller ha hoppet 100 bytes ...
        for value in v:
            if (v[i] == 255 and v[                    i + 1] == 238):  # leter etter start bytes som er "ff ee" som tilsvarer tallene 255 og 238
                vinkel = int.from_bytes(struct.pack("B", v[i + 2]) + struct.pack("B", v[i + 3]),
                                        byteorder='little')  # reverserer bytsene, setter de sammen og finner vinkelen. PS en må dele vinkelen på 100 for å få den i grader

                lengde = int.from_bytes(struct.pack("B", v[i + 7]) + struct.pack("B", v[i + 8]),
                                        byteorder='little')  # reverserer bytsene, setter de sammen og finner lengden til avstanden som er 1 grad oppver, dette er for å fjerne pungter som ikke er nødvendige må gange med 0.002 for å få meter

                vinkel = vinkel / 100  # HER ER VINKELEN TIL PUNTET SOM BLE LEST
                lengde = lengde * 0.002  # HER ER LENGDEN TIL PUNGTET SOM BLE LEST

                if vinkel2 == 0:  # bare en sjekk
                    vinkel2 = vinkel

                if (vinkel2 + 1 < vinkel or vinkel2 - 10 > vinkel):  # her sjekker vi om vinkelen er mer en 1 grad større enn den forje, slik at vi ikke får 10 forsjkellige målinger fra samme vinkel, dette er for å filtrer vekk pungter vi ikke trenger. den sjekker og om vinkelen har gått fra 360 grader til 0

                    if vinkel > 70 and vinkel < 110:  # sjekker til høyre for bilen (mellom vinkel 70 og 110 på lidaren)
                        if self.ah < self.lengdePaLister:  # listen har antal elementer som en vil ha. jo mindre elementer i listen jo mer resonsive blir den
                            self.ah += 1  # hvis listen har mindre enn 10 elementer så få denne sjekken +1
                            self.alisteH.append(lengde)  # også legges verdiene til i listene, dette er avstands listen
                            self.vlisteH.append(vinkel)  # dette er vinkel listen(derfor den begynner med "v")
                        else:  # hvis ah er større en 10 så er listen full
                            self.alisteH.pop(0)  # da fjerner jeg den første verdien i begge lister
                            self.vlisteH.pop(0)
                            self.alisteH.append(lengde)  # og adder den nye verdien i begge listene
                            self.vlisteH.append(vinkel)

                        self.h = max(self.alisteH)  # sørste målte lengde til høyre for bilen
                        #storsteposH = self.alisteH.index(h)  # posisjonen til sørste målte lengde til høyre for bilen

                    elif (vinkel > 0 and vinkel < 10) or (vinkel < 360 and vinkel > 350):  # vinkler foran bilen
                        if self.af < self.lengdePaLister:  # listen har antal elementer som en vil ha. jo mindre elementer i listen jo mer resonsive blir den
                            self.af += 1  # hvis listen har mindre enn 10 elementer så få denne sjekken +1
                            self.alisteF.append(lengde)  # også legges verdiene til i listene, dette er avstands listen
                            self.vlisteF.append(vinkel)  # dette er vinkel listen(derfor den begynner med "v")

                        else:  # hvis ah er større en 10 så er listen full, vi må derfor fjerne de eldste verdiene
                            self.alisteF.pop(0)  # fjerner verdien i posisjon 0, siden den er elst
                            self.vlisteF.pop(0)  # fjerner verdien i posisjon 0, siden den er elst
                            self.alisteF.append(lengde)  # legger til nye verdien
                            self.vlisteF.append(vinkel)  # legger til nye verdien

                        self.f = max(self.alisteF)  # største verdi i listen
                        self.minsteFrem = min(self.alisteF)  # minste verdi i listen
                        self.gjenomsnittFrem = mean(self.alisteF)  # gjenomsnittsverdi i listen

                    elif vinkel > 240 and vinkel < 300:  # til venstre for bilen
                        if self.av < self.lengdePaLister:
                            self.av += 1
                            self.alisteV.append(lengde)
                            self.vlisteV.append(vinkel)
                        else:
                            self.alisteV.pop(0)
                            self.vlisteV.pop(0)
                            self.alisteV.append(lengde)
                            self.vlisteV.append(vinkel)

                        self.vv = max(self.alisteV)  # alisteV[alisteV.index(max(alisteV))]

                    elif vinkel > 150 and vinkel < 210:
                        if self.ab < self.lengdePaLister:
                            self.ab += 1
                            self.alisteB.append(lengde)
                            self.vlisteB.append(vinkel)
                        else:
                            self.alisteB.pop(0)
                            self.vlisteB.pop(0)
                            self.alisteB.append(lengde)
                            self.vlisteB.append(vinkel)

                        # bstorsteVinkel = vlisteB[alisteB.index(max(alisteB))] #denne gir vinkelen til største vinkel i bakover retning
                        self.b = max(self.alisteB)  # største lengde målt i bakover retning

        """

        self.direction = random.randint(0,3)
        print("New direction ", self.direction)
        i = 0
        return

class Lidar(object):
    def __init__(self, setup, directions):
        
        self.setup = setup
        self.directions = directions

        #self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.sock.connect((setup['IPADDRESS'],setup['LIDARPORT'] ))
        logging.info('Lidar started')

        self.thread = threading.Thread(target=self.lidarreader, args=())
        self.thread.daemon = True  # Daemonize thread
        self.thread.start()
        
        return

    def lidarreader(self):
        """This method runs the lidar as a thread"""
        while True:

            logging.debug('Hello from lidar reader')

            # receive a packet and process it 
            #self.sock.recv()

            # process the data from lidar 
            self.directions.update("Dummy packet")

            time.sleep(1)

class Vehicle(object):
    def __init__(self, setup, directions):
        logging.info('Vehicle operational')

        self.directions = directions
        self.thread = threading.Thread(target=self.vehicleguide, args=())
        self.thread.daemon = True  # Daemonize thread
        self.thread.start()
        return

    def vehicleguide(self):
        while True:
            
            newdirection = self.directions.direction

            logging.debug('Navigation here - new direction '+str(self.directions.direction))
            time.sleep(1)

class Robot(object):

    def __init__(self, setup):
        self.ipaddress = setup['IPADDRESS']
        self.lidarport = setup['LIDARPORT']
        self.vehicleport = setup['VEHICLEPORT']
        self.directions = Directions()
        self.lidar = Lidar(setup,self.directions)
        self.vehicle = Vehicle(setup, self.directions)

        if True:
            logging.warning("Something funny")

    def run(self):
        while True:
            logging.info('Robot running')
            time.sleep(5)
        
if __name__ == "__main__":

    setup = {'IPADDRESS': HOST,
             'LIDARPORT': LIDARPORT,
             'VEHICLEPORT': VEHICLEPORT}

    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                        filename='robot.log',
                        level=logging.DEBUG)

    robot = Robot(setup)
    robot.run()


    
