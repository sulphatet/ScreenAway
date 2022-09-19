import cv2

import streamlit as st

import time

import numpy as np
import simpleaudio as sa

st.title('Screen Away')
st.text('Its unhealthy to have the screen too close to your eyes.')
st.text(' This webapp will remind you if you get too close')

#I had to make my own music
# calculate note frequencies
A_freq = 440
Csh_freq = A_freq * 2 ** (4 / 12)
E_freq = A_freq * 2 ** (7 / 12)

# get timesteps for each sample, T is note duration in seconds
sample_rate = 44100
T = 0.5
t = np.linspace(0, T, int(T * sample_rate), False)

# generate sine wave notes
A_note = np.sin(A_freq * t * 2 * np.pi)
Csh_note = np.sin(Csh_freq * t * 2 * np.pi)
E_note = np.sin(E_freq * t * 2 * np.pi)

# mix audio together
audio = np.zeros((44100, 2))
n = len(t)
offset = 0
audio[0 + offset: n + offset, 0] += A_note
audio[0 + offset: n + offset, 1] += 0.125 * A_note
offset = 5500
audio[0 + offset: n + offset, 0] += 0.5 * Csh_note
audio[0 + offset: n + offset, 1] += 0.5 * Csh_note
offset = 11000
audio[0 + offset: n + offset, 0] += 0.125 * E_note
audio[0 + offset: n + offset, 1] += E_note

# normalize to 16-bit range
audio *= 32767 / np.max(np.abs(audio))
# convert to 16-bit data
audio = audio.astype(np.int16)

#######

min_dist = st.slider(label = 'Select distance',min_value = 10, max_value = 100, value = 22,key = 0)
st.text('Naturally, the measurements shown are approximate.')
st.text(' So feel free to find a distance that feels comfortable to you')


Known_distance = 30  

Known_width = 5.7  

GREEN = (0, 255, 0)
RED = (0, 0, 255)
BLACK = (0, 0, 0)
YELLOW = (0, 255, 255)
WHITE = (255, 255, 255)
CYAN = (255, 255, 0)
MAGENTA = (255, 0, 242)
GOLDEN = (32, 218, 165)
LIGHT_BLUE = (255, 9, 2)
PURPLE = (128, 0, 128)
CHOCOLATE = (30, 105, 210)
PINK = (147, 20, 255)
ORANGE = (0, 69, 255)

fonts = cv2.FONT_HERSHEY_COMPLEX
fonts2 = cv2.FONT_HERSHEY_SCRIPT_SIMPLEX
fonts3 = cv2.FONT_HERSHEY_COMPLEX_SMALL
fonts4 = cv2.FONT_HERSHEY_TRIPLEX
cap = cv2.VideoCapture(0)  
Distance_level = 0


face_detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")



def FocalLength(measured_distance, real_width, width_in_rf_image):
    
    focal_length = (width_in_rf_image * measured_distance) / real_width
    return focal_length



def Distance_finder(Focal_Length, real_face_width, face_width_in_frame):
    
    distance = (real_face_width * Focal_Length) / face_width_in_frame
    return distance


def face_data(image, CallOut, Distance_level):
    

    face_width = 0
    
    face_center_x = 0
    face_center_y = 0
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_detector.detectMultiScale(gray_image, 1.3, 5)
    for (x, y, w, h) in faces:        
        face_width = w
        face_center_x = int(w / 2) + x
        face_center_y = int(h / 2) + y
        if Distance_level < 10:
            Distance_level = 10
    return face_width, faces, face_center_x, face_center_y


ref_image_face_width = 182
Focal_length_found = 957.8947368421052


flag = False
with st.empty():
    while True:
        
        _, frame = cap.read()
        
        face_width_in_frame, Faces, FC_X, FC_Y = face_data(frame, True, Distance_level)
        
        for (face_x, face_y, face_w, face_h) in Faces:
            flag = False
            
            if face_width_in_frame != 0:
                flag = False
                
                Distance = Distance_finder(
                    Focal_length_found, Known_width, face_width_in_frame
                )
                Distance = round(Distance, 2)
                
                Distance_level = int(Distance)
    
           
                if Distance < min_dist:
                   play_obj = sa.play_buffer(audio, 2, 2, sample_rate)
                   st.write("### Whoa! Move a little bit away there.")
                   
                   flag = True
                   play_obj.wait_done()
                else:
                    st.write(f"### You're {Distance} inches away from the screen!")
             
        if (len(Faces))  == 0:
            st.write("### Camera can't see you there")
            if flag:
                 play_obj = sa.play_buffer(audio, 2, 2, sample_rate)
                 play_obj.wait_done()
            

        if cv2.waitKey(1) == ord("q"):
            break

cap.release()

cv2.destroyAllWindows()
