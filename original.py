import socket
import time
from datetime import datetime, timedelta
import struct
from statistics import mean

HOST = '158.37.74.84'  # raspi IP.   VIKTIG! HVIS DENNE ENDRER SEG PÅ RASPI MÅ DENNE ENDRES TIL RIKTIG IP
PORT = 12346  # port til å motta Lidardata

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
print("koblet til lidar")

PORT1 = 12345  # port til å sende meldinger
ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ss.connect((HOST, PORT1))
print("koblet til styring")

i = 0

ah = 0  # dette er verdier for å telle hvor mange verdier det er i hver liste, ah står for avstandHøyre
av = 0  # av er avstand venstre
af = 0  # avstand foran
ab = 0  # avstand bak

h = 0  # disse brukes til å lagre største verdi i. h = største avstand til høyre for robotten
vv = 0  # største verdi til venstre
f = 0  # største verdi frem
b = 0  # største verdi bak

minsteFrem = 100
gjenomsnittFrem = 0

lengdePaLister = 5  # setter lenge på listene, hvis det oppdaterer seg for sakte må den lavere hvis den ikke er nøyktig nok må den høyere

# savefile = open('test.txt','w')   #dene brukes til feiltesting. skriver ned alle pungter
alisteH = []  # liste med alle avstander til høyre for robotten
alisteV = []
alisteF = []
alisteB = []

vlisteH = []  # liste med vinkler for høyre side
vlisteV = []
vlisteF = []
vlisteB = []

rettfrem = 0

lll = 0

try:

    while True:

        reply = s.recv(2000)  # motar pakkene fra lidar

        vinkel2 = 0  # brukes til å sjekke vinkler, slik at vi kan sortere vekk vinkler som er for nerme hverandre
        v = bytearray(reply)  # alt fra pakken legges i denne bytearrayen

        i = 0  # brukes i forloopen for å holde styr på bytearrayen

        for value in v:

            try:
                if (v[i] == 255 and v[
                    i + 1] == 238):  # leter etter start bytes som er "ff ee" som tilsvarer tallene 255 og 238
                    vinkel = int.from_bytes(struct.pack("B", v[i + 2]) + struct.pack("B", v[i + 3]),
                                            byteorder='little')  # reverserer bytsene, setter de sammen og finner vinkelen. PS en må dele vinkelen på 100 for å få den i grader

                    lengde = int.from_bytes(struct.pack("B", v[i + 7]) + struct.pack("B", v[i + 8]),
                                            byteorder='little')  # reverserer bytsene, setter de sammen og finner lengden til avstanden som er 1 grad oppver, dette er for å fjerne pungter som ikke er nødvendige må gange med 0.002 for å få meter

                    vinkel = vinkel / 100  # HER ER VINKELEN TIL PUNTET SOM BLE LEST
                    lengde = lengde * 0.002  # HER ER LENGDEN TIL PUNGTET SOM BLE LEST

                    if vinkel2 == 0:  # bare en sjekk
                        vinkel2 = vinkel

                    if (
                            vinkel2 + 1 < vinkel or vinkel2 - 10 > vinkel):  # her sjekker vi om vinkelen er mer en 1 grad større enn den forje, slik at vi ikke får 10 forsjkellige målinger fra samme vinkel, dette er for å filtrer vekk pungter vi ikke trenger. den sjekker og om vinkelen har gått fra 360 grader til 0

                        if vinkel > 70 and vinkel < 110:  # sjekker til høyre for bilen (mellom vinkel 70 og 110 på lidaren)
                            if ah < lengdePaLister:  # listen har antal elementer som en vil ha. jo mindre elementer i listen jo mer resonsive blir den
                                ah += 1  # hvis listen har mindre enn 10 elementer så få denne sjekken +1
                                alisteH.append(lengde)  # også legges verdiene til i listene, dette er avstands listen
                                vlisteH.append(vinkel)  # dette er vinkel listen(derfor den begynner med "v")
                            else:  # hvis ah er større en 10 så er listen full
                                alisteH.pop(0)  # da fjerner jeg den første verdien i begge lister
                                vlisteH.pop(0)
                                alisteH.append(lengde)  # og adder den nye verdien i begge listene
                                vlisteH.append(vinkel)

                            h = max(alisteH)  # sørste målte lengde til høyre for bilen

                            storsteposH = alisteH.index(h)  # posisjonen til sørste målte lengde til høyre for bilen

                        if (vinkel > 0 and vinkel < 10) or (vinkel < 360 and vinkel > 350):  # vinkler foran bilen

                            if af < lengdePaLister:  # listen har antal elementer som en vil ha. jo mindre elementer i listen jo mer resonsive blir den
                                af += 1  # hvis listen har mindre enn 10 elementer så få denne sjekken +1
                                alisteF.append(lengde)  # også legges verdiene til i listene, dette er avstands listen
                                vlisteF.append(vinkel)  # dette er vinkel listen(derfor den begynner med "v")

                            else:  # hvis ah er større en 10 så er listen full, vi må derfor fjerne de eldste verdiene
                                alisteF.pop(0)  # fjerner verdien i posisjon 0, siden den er elst
                                vlisteF.pop(0)  # fjerner verdien i posisjon 0, siden den er elst
                                alisteF.append(lengde)  # legger til nye verdien
                                vlisteF.append(vinkel)  # legger til nye verdien

                            f = max(alisteF)  # største verdi i listen
                            minsteFrem = min(alisteF)  # minste verdi i listen
                            gjenomsnittFrem = mean(alisteF)  # gjenomsnittsverdi i listen

                        if vinkel > 240 and vinkel < 300:  # til venstre for bilen
                            if av < lengdePaLister:
                                av += 1
                                alisteV.append(lengde)
                                vlisteV.append(vinkel)
                            else:
                                alisteV.pop(0)
                                vlisteV.pop(0)
                                alisteV.append(lengde)
                                vlisteV.append(vinkel)

                            vv = max(alisteV)  # alisteV[alisteV.index(max(alisteV))]

                        if vinkel > 150 and vinkel < 210:
                            if ab < lengdePaLister:
                                ab += 1
                                alisteB.append(lengde)
                                vlisteB.append(vinkel)
                            else:
                                alisteB.pop(0)
                                vlisteB.pop(0)
                                alisteB.append(lengde)
                                vlisteB.append(vinkel)

                            # bstorsteVinkel = vlisteB[alisteB.index(max(alisteB))] #denne gir vinkelen til største vinkel i bakover retning
                            b = max(alisteB)  # største lengde målt i bakover retning

                        # print('v :{}'.format(vinkel/100))
                        # print('\n L: {} \n'.format(lengde*0.002))
                        # print()

                        if vinkel2 - 10 > vinkel:  # sjekker om vinkelen er 10 grader midre en forje registrerte vinkel. hvis den er det så er den gått over 360 grader og må begynne fra bunnen av
                            vinkel2 = vinkel

                            """
                            HER BØR DERE LEGGE INN STYREKODE.
                            PROGRAMMET GÅN INN I DENNE "IF" HVER GANG LIDAREN HAR PROSESERT EN RUNDE MED DATA
                            GJØR DU DET UTTENFOR HER KAN PROGRAMMET BLI FOR TREGT 

                            """

                            """
                            # TEST PROGRAM 1
                            if ab>=lengdePaLister:
                                if(minsteFrem>1.5):             #hvis det er mer enn 1.5 m fremfor så kjører den frem
                                    print("Frem")
                                    ss.send(str.encode("w"))    #Sender signal om å kjøre fremmover

                                elif(vv>h and vv>f and vv>1): #hvis venstre er den siden med best plass på svinger den mott venste
                                    print("V")


                                    ss.send(str.encode("a"))    #sender signal om å svinge mot venstre
                                    print(vv)
                                    print(vlisteV[alisteV.index(max(alisteV))])
                                elif(vv<h and f<h and h>1 ):
                                    print("H")
                                    ss.send(str.encode("d"))
                                elif(f>h and f>vv and f>1 ):
                                    print("F")
                                    ss.send(str.encode("w"))
                                elif(f<1 and h<1 and vv<1 and b>1):
                                    print("B")
                                    ss.send(str.encode("s"))

                                else:
                                    print("ingen sted å gå")
                                    ss.send(str.encode("q"))


                            """

                            # TEST PROGRAM 2
                            if (
                                    minsteFrem > 1.5):  # Hvis den minste verdien fremfor bilen er støre enn 1.5 så skal billen kjøre fremmover
                                print("Frem")
                                ss.send(str.encode("w"))  # kjører frem
                                print(minsteFrem)

                            elif (
                                    vv > h and vv > 1.5):  # sjekker om venstre side er lengre enn 1.5m og om den er lengre enn høyre side
                                print("Venstre")
                                ss.send(str.encode(
                                    "a"))  # Svinger mot venstre frem til fremoverlisten sitt minste tall er større enn 1.5m
                                print(minsteFrem)

                            elif (
                                    vv < h and h > 1.5):  # sjekker om høyre siden er lengre enn 1.5m og at det er lengre enn venstresiden
                                print("H")
                                ss.send(str.encode(
                                    "d"))  # Svinger mot høyre frem til fremoverlisten sitt minste tall er større enn 1.5m
                                print(minsteFrem)

                            elif (
                                    f < 1 and h < 1 and vv < 1 and b > 1):  # hvis det ikke er noe sted å gå mortset fra bak så rygger bilen
                                print("B")
                                ss.send(str.encode("s"))
                                print(minsteFrem)
                            else:  ##hvis det ikke er noe sted å gå så stopper bilen
                                print("ingen sted å gå")
                                ss.send(str.encode("q"))
                                print(minsteFrem)

                        vinkel2 = vinkel

                i += 1




            except:
                print('',
                      end='')  # når array går out of bounds så vil den gi denne feilmeldingen, og denne feilmeldingen er usynlig.

        # print(i)

except:
    ss.send(str.encode("q"))  # hvis alt går gale stopper den bilen
