import cv2
import mediapipe
import time
import numpy as np
import HandTrackingModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

wCam, hCam = 640, 480

cap = cv2.VideoCapture(0)
cap.set(3, wCam) #prop id at number 4 is width cam
cap.set(4, hCam)
pTime = 0
detector = htm.handDetector(detectionCon = 0.7)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None
)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = (volume.GetVolumeRange())
volume.SetMasterVolumeLevel(0.0,None)
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volPer =0
while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw = False)
    if len(lmList) != 0:            #determine landmark number
        print(lmList[4], lmList[8])  # for volume control we need 4th and 8 th landmark i.e. thumb tip and first finger tip
        x1, y1 = lmList[4][1:]
        x2, y2 = lmList[8][1:]
        cx, cy = (x1+x2)// 2,(y1+y2)// 2
        cv2.circle(img, (x1,y1), 10, (250,56,255),cv2.FILLED)
        cv2.circle(img, (x2, y2), 10, (250, 98, 255), cv2.FILLED)
        cv2.line(img,(x1,y1),(x2,y2),(255,0,255),3)
        cv2.circle(img, (cx,cy), 10, (250, 98, 255), cv2.FILLED)

        length = math.hypot(x2 - x1, y2 - y1)
        print( length )

        # Hand Range 10 to 170
        # Volume Range -65 to 0

        vol = np.interp(length,[10,170],[minVol,maxVol])
        volBar = np.interp(length,[10,170],[400,150])
        volPer = np.interp(length, [10, 170], [0, 100])
        print(int(length),vol)
        volume.SetMasterVolumeLevel(vol,None)

        if length < 20:
            cv2.circle(img,(cx,cy),15,(123,232,21),cv2.FILLED)

    cv2.rectangle(img, (50,150),(75,400),(67, 25, 9),3)
    cv2.rectangle(img, (50, int(volBar)), (75, 400), (25, 25, 85), cv2.FILLED)
    cv2.putText(img, f'{int(volPer)}%',(45,450),cv2.FONT_HERSHEY_COMPLEX,1,(25,25,25),2)

    # frame rate
    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}',(40,40), cv2.FONT_HERSHEY_COMPLEX, 1, (255,45,0),2)

    cv2.imshow("img", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

