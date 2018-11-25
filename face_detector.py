from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import csv
import matplotlib.pyplot as plt

imageWidth = 320
imageHeight = 240

n = 5100
distractedArray = [0]*n
distractions = []

fontTitle = {'family': 'sans-serif', 'color':'darkblue', 'weight':'bold', 'size':24}
fontParagraph = {'family': 'sans-serif', 'color':'slateblue', 'weight':'normal', 'size':16}

def continuous_capture():
    original_time = time.time()
    camera = PiCamera()
    camera.resolution = (320, 240)
    camera.framerate = 32
    rawCapture = PiRGBArray(camera, size=(320, 240))
    
    print('initialized the instance of the camera object')
    
    #Load a cascade file for detecting faces
    face_cascade = cv2.CascadeClassifier('/home/pi/Documents/Facial Detection/RPi-OpenCV-Face-Rec-Python/faces.xml')
    profile_face_cascade = cv2.CascadeClassifier('/home/pi/Documents/Facial Detection/RPi-OpenCV-Face-Rec-Python/profile_faces.xml')

    print('imported the cascade classifier')
##        # allow the camera to warm up
    time.sleep(0.1)
    print('done sleeping')
    
##        # capture frames from the camera
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
##           print("at the start of the for loop")
        image = frame.array
##
##            #Convert to grayscale
        gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        gray_flipped = cv2.flip(gray, 1)
##
##            #Look for faces in the image using the loaded cascade file
        faces = face_cascade.detectMultiScale(gray, 1.1, 5)
        if (len(faces) > 0):                
            for (x,y,w,h) in faces:
                cv2.rectangle(image,(x,y),(x+w,y+h),(0,255,0),2)
        else:
            profile_faces_left = profile_face_cascade.detectMultiScale(gray, 1.1, 5)                   
            for (x,y,w,h) in profile_faces_left:       
                cv2.rectangle(image,(x,y),(x+w,y+h),(0,0,255),2)
            profile_faces_right = profile_face_cascade.detectMultiScale(gray_flipped, 1.1, 5)                   
            for (x,y,w,h) in profile_faces_right:       
                cv2.rectangle(image,(imageWidth-(x+w),y),(imageWidth-x,y+h),(0,0,255),2)
                    
        cv2.imshow("Frame", image)
##            print("after the imshow")
        key = cv2.waitKey(1) & 0xFF
        rawCapture.truncate(0)
        if key == ord("q"):
            break

        #analyze the image to see if they're being distracted
        time.sleep(0.0001)
    

        #if distracted, log it
        if len(faces) == 0:
            distractedArray.append(1)
        else:

            distractedArray.append(0)


        #analyze the past 5 seconds of the array to see how long they've been distracted for
        if (distractedArray[-1] == 1) & (distractedArray[-2] == 0):
            start = time.time()
        if (distractedArray[-1] == 0) & (distractedArray[-2] == 1):
            end = time.time()
            if (end-start) > 1.5:
                distractions.append(end - start)
    
    final_time = time.time()
    print(sum(distractions))
    attentive_percentage = ((1 - (sum(distractions))/(final_time - original_time)))*100
    print("Congratulations! You were attentive for %s%% of the time you were driving!" % attentive_percentage)
    print(distractions)
    print(final_time - original_time)
    #print(sum(distractions)/len(distractions))

    nhood = 'Woburn'

    with open('Neighbs_stats_v3.csv', 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in spamreader:
            if row[0] == nhood:
                print(', '.join(row))

    fig = plt.figure()
    #fig.suptitle('FocusTrack', fontdict=fontTitle)
    frame1 = plt.gca()
    #frame1.axes.get_xaxis().set_visible(False)
    #frame1.axes.get_yaxis().set_visible(False)
    plt.axis('off')
    plt.text(0.3,1,'FocusTrack', fontdict=fontTitle)
    plt.text(0,0.9,'You were attentive %d%% percent of the time'%attentive_percentage, fontdict=fontParagraph)
    plt.text(0,0.8,'Attentive multipliers', fontdict=fontParagraph)
    plt.text(0.1,0.7,'- School zones: ', fontdict=fontParagraph)
    plt.text(0.1,0.6,'- Busy intersections: ', fontdict=fontParagraph)
    plt.text(0,0.3,'Overall score: ' , fontdict=fontParagraph)
    plt.show()

if __name__ == '__main__':
    continuous_capture()


