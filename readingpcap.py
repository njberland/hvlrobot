import socket
import struct
from statistics import mean
import numpy as np


LASER_ANGLES = [-15, 1, -13, 3, -11, 5, -9, 7, -7, 9, -5, 11, -3, 13, -1, 15]
NUM_LASERS = 16

EXPECTED_PACKET_TIME = 0.001327  # valid only in "the strongest return mode"
EXPECTED_SCAN_DURATION = 0.1
DISTANCE_RESOLUTION = 0.002
ROTATION_RESOLUTION = 0.01
ROTATION_MAX_UNITS = 36000

def calc(dis, azimuth, laser_id, timestamp):
    R = dis * DISTANCE_RESOLUTION
    omega = LASER_ANGLES[laser_id] * np.pi / 180.0
    alpha = azimuth / 100.0 * np.pi / 180.0
    X = R * np.cos(omega) * np.sin(alpha)
    Y = R * np.cos(omega) * np.cos(alpha)
    Z = R * np.sin(omega)
    return [X, Y, Z, timestamp]

def unpack(packet):
    points = []
    scan_index = 0
    prev_azimuth = None
    d = packet
    n = len(d)
    data = packet
    print(len(data))
    timestamp, factory = struct.unpack_from("<IH", data, offset=1200)
    #assert factory == 0x2237, hex(factory)  # 0x22=VLP-16, 0x37=Strongest Return
    timestamp = float(timestamp)
    seq_index = 0
    for offset in range(0, 1200, 100):
        flag, azimuth = struct.unpack_from("<HH", data, offset)
        assert flag == 0xEEFF, hex(flag)
        for step in range(2):
            seq_index += 1
            azimuth += step
            azimuth %= ROTATION_MAX_UNITS
            prev_azimuth = azimuth
            # H-distance (2mm step), B-reflectivity (0
            arr = struct.unpack_from('<' + "HB" * 16, data, offset + 4 + step * 48)
            for i in range(NUM_LASERS):
                time_offset = (55.296 * seq_index + 2.304 * i) / 1000000.0
                if arr[i * 2] != 0:
                    point = calc(arr[i * 2], azimuth, i, timestamp + time_offset)
                    print(point)
            

if __name__ == "__main__":
    import pyshark

    shark_cap = pyshark.FileCapture('sharktest.pcap')

    for packet in shark_cap:
    #    ba = bytearray.fromhex(str(packet.data.data))

        v = bytearray.fromhex(str(packet.data.data))  # alt fra pakken legges i denne bytearrayen
        print("packet length ",len(v))

            
        if len(v) == 1206:
            unpack(v)


