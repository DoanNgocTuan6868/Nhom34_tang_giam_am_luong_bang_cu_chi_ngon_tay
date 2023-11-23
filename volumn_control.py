import math
import  cv2
import  time
import  numpy as np
import  hand as htm
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

cap = cv2.VideoCapture(0)
pTime =0 ;
# bắt các điểm trên bàn tay
detector =htm.handDetector(detectionCon=1)
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

volRange=volume.GetVolumeRange()  # phạm vi âm lương máy của mình là -65 đến  0

minVol = volRange[0] # -65
maxVol = volRange[1] # 0

while True:
    ret,frame = cap.read()
    frame = detector.findHands(frame)
    lmList = detector.findPosition(frame,draw=False) # đẩy ra các điểm trên bàn tay

    #print(lmList)
    if len(lmList)!=0:
        #print(lmList[4],lmList[8])
        x1,y1 = lmList[4][1],lmList[4][2]
        x2,y2 = lmList[8][1],lmList[8][2]
        # vẽ 2 đường tròn trên 2 đầu ngón cái và trỏ
        cv2.circle(frame,(x1,y1),15,(255,0,255),-1)
        cv2.circle(frame, (x2, y2), 15, (255, 0, 255), -1)
        cv2.line(frame,(x1,y1),(x2,y2),(255,0,255),3)
        # vẽ đường tròn ở giữa
        cx,cy = (x1+x2)//2,(y1+y2)//2
        cv2.circle(frame, (cx, cy), 15, (255, 0, 255), -1)

        # xác định độ dài đoạn thẳng nối từ ngón trái đến ngón trỏ
        length = math.hypot(x2-x1,y2-y1)

        # độ dài tay khoảng 25 đến 230
        vol = np.interp(length,[25,230],[minVol,maxVol] )#hàm này sẽ chuyển đổi chiều dài của 25 ,230 đến min vol đến max
        volBar = np.interp(length, [25, 230], [400,150])
        vol_tyle =np.interp(length, [25, 230], [0,100])
        volume.SetMasterVolumeLevel(vol, None)
        print(length)

        if length<25:
            cv2.circle(frame, (cx, cy), 15, (0, 255, 0), -1)

        #vẽ hình chự nhật
        cv2.rectangle(frame,(50,150),(100,400),(0,255,0),3)
        cv2.rectangle(frame,(50,int(volBar)),(100,400),(0,255,0),-1)
        #show % volum
        cv2.putText(frame, f"{int(vol_tyle)} %", (50, 120), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

    # viết ra fps
    cTime = time.time() # thời điểm bắt đầu của thời gian
    fps = 1/(cTime-pTime)
    pTime = cTime
    cv2.putText(frame,f"FPS: {int(fps)}",(350,70),cv2.FONT_HERSHEY_PLAIN,3,(255,0,0),3)
    cv2.imshow("testcam",frame)
    if cv2.waitKey(1) ==ord("q"):
        break
cap.release()
cv2.destroyAllWindows()