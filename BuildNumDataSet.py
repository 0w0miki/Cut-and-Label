# -*- coding: utf-8 -*-

import cv2
import numpy as np
import matplotlib.pyplot as plt

# 需要先在Output_Path下建好0-9 a-z的文件夹
# 运行后按空格
# 鼠标框选区域后按下其对应数字或字母按键
# ESC:退出 c:清除图上的框 空格回车:下一张图
# z:撤销 需要输入过数字字母后再按
# 圈出的图片会保存到Output_Path下的文件夹内
# 格式为xx_i.jpg xx为来源图片 i是该图中第i个圈出的数字或字母
# 包含图片是啥和在原图中位置信息的 test.txt

drag = False # 鼠标左键是不是按下
inputComplete = True
ix,iy = -1,-1
px,py = -1,-1
nums = []

imagedir = "../images/ag/ag"
suffix = ".jpg"
Output_Path = "../images/ag/ag"

class number(object):
    """store num pic and position value"""
    # pic: picture
    # position: (xmin,ymin,xmax,ymax)
    # value: char''
    def __init__(self, pic, position):
        self.pic = pic
        self.position = position
        self.value = None
    def setNumValue(self,val):
        self.value = val

# 鼠标回调函数
def MouseCallBack(event,x,y,flags,param):
    global ix,iy,drag,px,py,img,inputComplete
    if event == cv2.EVENT_LBUTTONDOWN:
        if inputComplete:
            # print("down",x,y)
            drag = True
            ix,iy = x,y
            inputComplete = False
    elif event == cv2.EVENT_MOUSEMOVE:
        if drag == True:
            temp = img.copy()
            cv2.rectangle(temp,(ix,iy),(x,y),(255,255,255),2)
            cv2.imshow("image",temp)
    elif event == cv2.EVENT_LBUTTONUP:
        if drag:
            # print("up",x,y)
            drag = False
            cv2.rectangle(img,(ix,iy),(x,y),(255,255,255),2)
            undoimgs.append(img.copy())
            cv2.imshow("image",img)
            xmin,ymin,xmax,ymax = min(ix,x),min(iy,y),max(ix,x),max(iy,y)
            nums.append(number(origin[ymin:ymax,xmin:xmax],(xmin,ymin,xmax,ymax)))
            cv2.imshow("num",nums[-1].pic)
        else:
            print("please input number or character")

def save(num,Outdir,imagedir,imagei):
    saveFile = open(imagedir + str(imagei) + '.txt', 'w')
    for n in range(len(num)):
        outname = Outdir + num[n].value + "/" + str(imagei) + "_" + str(n) + ".jpg"
        cv2.imwrite(outname,num[n].pic)
        saveFile.write(num[n].value + " "
                + str(num[n].position[0]) + " " + str(num[n].position[1]) + " "
                + str(num[n].position[2]) + " " + str(num[n].position[3]) + "\n"
        )



imagei = 0
cv2.namedWindow("image",0)
cv2.setMouseCallback('image',MouseCallBack)
f = open(Output_Path+'test.txt', 'a')
while imagei < 124:
    k = cv2.waitKey() & 0xFF
    if k == 27:
        #ESC
        f.close()
        break
    if not inputComplete:
        if 48 <= k <= 57 or 65 <= k <= 90 or 97 <= k <= 122:
            # 数字字母
            nums[-1].setNumValue(chr(k))
            print(imagei,"set number picture as",nums[-1].value)
            inputComplete = True
    elif k == 13:
        # Enter
        if nums:save(nums,Output_Path,imagedir,imagei)
        imagei += 1
        image_name = imagedir + str(imagei) + suffix
        origin = cv2.imread(image_name,0)
        img = origin.copy()
        nums, undoimgs = [], []
        undoimgs.append(origin)
        cv2.imshow("image",origin)
    elif k == 32:
        # Space
        if nums:save(nums,Output_Path,imagedir,imagei)
        imagei += 1
        image_name = imagedir + str(imagei) + suffix
        origin = cv2.imread(image_name,0)
        img = origin.copy()
        nums, undoimgs = [], []
        undoimgs.append(origin)
        cv2.imshow("image",origin)
    elif k == ord('c'):
        # clear
        img = origin.copy()
        cv2.imshow("image",img)
    elif k == ord("z"):
        # undo
        if len(undoimgs) > 1:
            undoimgs.pop()
            nums.pop()
            img = undoimgs[-1].copy()
            cv2.imshow("image",img)
            if nums != []:
                cv2.imshow("num",nums[-1].pic)

f.close()
