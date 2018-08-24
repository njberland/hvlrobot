import logging
import time
import threading
import struct
import socket
import time
from datetime import datetime, timedelta
import struct
from statistics import mean

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                    filename='robot.log',
                    level=logging.DEBUG)
logging.debug('Loading module robot')


class Directionlists(object):
    def __init__(self, length):

        self.lengdePaLister = length  # setter lenge på listene, hvis det oppdaterer seg for sakte må den lavere hvis den ikke er nøyktig nok må den høyere
        self.alisteH = []  # liste med alle avstander til høyre for robotten
        self.alisteV = []
        self.alisteF = []
        self.alisteB = []

        self.vlisteH = []  # liste med vinkler for høyre side
        self.vlisteV = []
        self.vlisteF = []
        self.vlisteB = []

        self.ah = 0  # dette er verdier for å telle hvor mange verdier det er i hver liste, ah står for avstandHøyre
        self.af = 0  # avstand foran
        self.av = 0  # av er avstand venstre
        self.af = 0  # avstand foran
        self.ab = 0  # avstand bak

        self.h = 0  # disse brukes til å lagre største verdi i. h = største avstand til høyre for robotten
        self.vv = 0  # største verdi til venstre
        self.f = 0  # største verdi frem
        self.b = 0  # største verdi bak

    def process(self,v):

        rettfrem = 0
        lll = 0
        vinkel2 = 0  # brukes til å sjekke vinkler, slik at vi kan sortere vekk vinkler som er for nerme hverandre
        i = 0  # brukes i forloopen for å holde styr på bytearrayen
        for value in v:
            try:
                if (v[i] == 255 and v[ i + 1] == 238):  # leter etter start bytes som er "ff ee" som tilsvarer tallene 255 og 238

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
                            else:  # hvis ah er større en 10 så er listen full
                                self.alisteH.pop(0)  # da fjerner jeg den første verdien i begge lister
                                self.vlisteH.pop(0)

                            self.alisteH.append(lengde)  # og adder den nye verdien i begge listene
                            self.vlisteH.append(vinkel)
                            self.h = max(self.alisteH)  # sørste målte lengde til høyre for bilen
                            self.storsteposH = self.alisteH.index(h)  # posisjonen til sørste målte lengde til høyre for bilen

                        if (vinkel > 0 and vinkel < 10) or (vinkel < 360 and vinkel > 350):  # vinkler foran bilen

                            if self.af < self.lengdePaLister:  # listen har antal elementer som en vil ha. jo mindre elementer i listen jo mer resonsive blir den
                                self.af += 1  # hvis listen har mindre enn 10 elementer så få denne sjekken +1

                            else:  # hvis ah er større en 10 så er listen full, vi må derfor fjerne de eldste verdiene
                                self.alisteF.pop(0)  # fjerner verdien i posisjon 0, siden den er elst
                                self.vlisteF.pop(0)  # fjerner verdien i posisjon 0, siden den er elst

                            self.alisteF.append(lengde)  # legger til nye verdien
                            self.vlisteF.append(vinkel)  # legger til nye verdien

                            self.f = max(self.alisteF)  # største verdi i listen
                            self.minsteFrem = min(self.alisteF)  # minste verdi i listen
                            self.gjenomsnittFrem = mean(self.alisteF)  # gjenomsnittsverdi i listen

                        if vinkel > 240 and vinkel < 300:  # til venstre for bilen
                            if self.av < self.lengdePaLister:
                                self.av += 1
                            else:
                                self.alisteV.pop(0)
                                self.vlisteV.pop(0)
                            self.alisteV.append(lengde)
                            self.vlisteV.append(vinkel)

                            self.vv = max(self.alisteV)  # alisteV[alisteV.index(max(alisteV))]

                        if vinkel > 150 and vinkel < 210:
                            if self.ab < self.lengdePaLister:
                                self.ab += 1
                            else:
                                self.alisteB.pop(0)
                                self.vlisteB.pop(0)
                            self.alisteB.append(lengde)
                            self.vlisteB.append(vinkel)

                            # bstorsteVinkel = vlisteB[alisteB.index(max(alisteB))] #denne gir vinkelen til største vinkel i bakover retning
                            self.b = max(self.alisteB)  # største lengde målt i bakover retning
                    i += 1
            except:
                logging.debug("Try failed")

class Lidar(object):
    def __init__(self, setup):

        logging.info('Lidar started')

        self.ipaddress = setup['IPADDRESS']
        self.lidarport = setup['LIDARPORT']
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.ipaddress, self.lidarport))
        print("koblet til lidar")

        self.directionlists = Directionlists(5)
        self.minsteFrem = 100
        self.gjenomsnittFrem = 0

        thread = threading.Thread(target=self.lidarreader, args=())
        thread.daemon = True  # Daemonize thread
        thread.start()

        return

    def lidarreader(self):
        """This method runs the lidar as a thread"""
        while True:
            logging.debug('Hello from lidar reader')
            reply = self.sock.recv(2000)  # motar pakkene fra lidar
            v = bytearray(reply)  # alt fra pakken legges i denne bytearrayen
            self.directionlists.process(v)

    def run(self):
        return


class Vehicle(object):
    def __init__(self, setup):

        self.ipaddress = setup['IPADDRESS']
        self.vehicleport = setup['VEHICLEPORT']
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.ipaddress, self.vehicleport))
        logging.info('Vehicle operational')

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.ipaddress, self.lidarport))

        return

    def run(self):
        return


class Robot(object):

    def __init__(self, setup):
        self.lidar = Lidar(setup)
        self.vehicle = Vehicle(setup)

        if True:
            logging.warning("Something funny")

    def run(self):
        logging.info('Robot running')

        while 1:
            logging.debug('One more turn')
            time.sleep(1)

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


"""    while True:
        logging.debug("Looping")
        time.sleep(5)
"""
