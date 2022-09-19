#!/usr/bin/env python3.6

import sys
from serial import Serial
from time import sleep

import cv2


hello = b'''\r\nGrbl 1.1f ['$' for help]\r\n'''
ok = b'''ok\r\nok\r\n'''


class Sentry(object):
    def __init__(self, tty, baudrate):
        self._serial = Serial(tty, baudrate)

        b = b''
        while b != hello:
            b += self._serial.read_all()

        self.code = ok
        self.x_rate = 5000
        self.y_rate = 4000
        self.x_acc  = 1000
        self.y_acc  = 1000

        self._feed_rate = 9000


    def __del__(self):
        self._serial.close()


    def jog(self, x, y):
        self.send(f'$J=G91 G21 X{x} Y{y} F{self._feed_rate}')


    def send(self, cmd):
        self._serial.write(f'{cmd}\r\n'.encode('ascii'))

        self.code = b''
        while self.code != ok:
            self.code += self._serial.read_all()


    def recv(self):
        return self._serial.read_all()


    @property
    def x_rate(self):
        return self._x_rate

    @x_rate.setter
    def x_rate(self, rate):
        self._x_rate = rate
        self.send(f'$110={rate}')


    @property
    def y_rate(self):
        return self._y_rate

    @y_rate.setter
    def y_rate(self, rate):
        self._y_rate = rate
        self.send(f'$111={rate}')


    @property
    def x_acc(self):
        return self._x_acc

    @x_acc.setter
    def x_acc(self, acc):
        self._x_acc = acc
        self.send(f'$120={acc}')


    @property
    def y_acc(self):
        return self._y_acc

    @y_acc.setter
    def y_acc(self, acc):
        self._y_acc = acc
        self.send(f'$121={acc}')




if __name__ == '__main__':
    if sys.version_info < (3, 6):
        sys.exit('Python 3.6 or later is required.\n')

    sentry = Sentry('/dev/ttyACM0', 115200)

    casc_path = sys.argv[1]

    face_cascade = cv2.CascadeClassifier(casc_path)
    video_capture = cv2.VideoCapture(1)

    cw, ch = video_capture.get(cv2.CAP_PROP_FRAME_WIDTH), video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
    print(f'Resolution: {cw}x{ch}')

    while True:
        ret, frame = video_capture.read()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(40, 40),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        cv2.imshow('Video', frame)


        if len(faces) > 0:
            # face = min(faces, key=lambda f: (w/2 - f[0])**2 + (h/2 - f[1])**2) # closest to center
            face = max(faces, key=lambda f: f[2]*f[3]) # biggest

            x, y, w, h = face
            x += w/2
            y += h/2

            shift_x = cw/2 - x
            shift_y = ch/2 - y

            k = 1

            jx = 0
            jy = 0

            if abs(shift_x) > 40:
                jx = 1 if shift_x > 0 else -1
            if abs(shift_y) > 40:
                jy = 1 if shift_y > 0 else -1


            if jx != 0 or jy != 0:
                sentry.jog(*map(int, (jx*k, 0)))


        key = cv2.waitKey(1) & 0xFF

        if key == 27:
            quit()
