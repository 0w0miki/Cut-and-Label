# -*- coding: utf-8 -*-

import os
import os.path as ops
import argparse
import cv2
import numpy as np
import matplotlib.pyplot as plt

# 需要先在output_dir 下建好0-9 a-z的文件夹
# 运行后按空格
# 鼠标框选区域后按下其对应数字或字母按键
# ESC:退出 c:清除图上的框 空格回车:下一张图
# z:撤销 需要输入过数字字母后再按
# 圈出的图片会保存到output_dir 下的文件夹内
# 格式为xx_i.jpg xx为来源图片 i是该图中第i个圈出的数字或字母
# 包含图片是啥和在原图中位置信息的 test.txt


class Number(object):
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

class Cut(object):
    def __init__(self, image_dir, output_dir):
        self.ix=-1
        self.iy=-1
        self.drag=False
        self.px=-1
        self.py=-1
        self.undoimgs=[]
        self.files=[]
        self.nums=[]
        self.inputComplete=True
        self.suffix='.jpg'
        self.image_dir=image_dir
        self.output_dir=output_dir
        self.parse_image(image_dir,output_dir)

    # 鼠标回调函数
    def MouseCallBack(self,event,x,y,flags,param):
        # global ix,iy,drag,px,py,img,inputComplete
        if event == cv2.EVENT_LBUTTONDOWN:
            if self.inputComplete:
                # print("down",x,y)
                self.drag = True
                self.ix,self.iy = x,y
                self.inputComplete = False
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drag == True:
                temp = self.img.copy()
                cv2.rectangle(temp,(self.ix,self.iy),(x,y),(255,255,255),2)
                cv2.imshow("image",temp)
        elif event == cv2.EVENT_LBUTTONUP:
            if self.drag:
                # print("up",x,y)
                self.drag = False
                cv2.rectangle(self.img,(self.ix,self.iy),(x,y),(255,255,255),2)
                self.undoimgs.append(self.img.copy())
                cv2.imshow("image",self.img)
                xmin,ymin,xmax,ymax = min(self.ix,x),min(self.iy,y),max(self.ix,x),max(self.iy,y)
                self.nums.append(Number(self.origin[ymin:ymax,xmin:xmax],(xmin,ymin,xmax,ymax)))
                cv2.imshow("num",self.nums[-1].pic)
            else:
                print("please input Number or character")

    def save(self):
        saveFile = open(ops.join(self.image_dir , str(self.index) + '.txt'), 'w')
        for n in range(len(self.nums)):
            outname = ops.join(self.output_dir , self.nums[n].value + "/" + str(self.index) + "_" + str(n) + ".jpg")
            cv2.imwrite(outname,self.nums[n].pic)
            saveFile.write(self.nums[n].value + " "
                    + str(self.nums[n].position[0]) + " " + str(self.nums[n].position[1]) + " "
                    + str(self.nums[n].position[2]) + " " + str(self.nums[n].position[3]) + "\n"
            )

    def test_dir(self,path):
        for i in range(0,10):
            new_path = ops.join(path,str(i))
            if not ops.exists(new_path):
                os.makedirs(new_path)
        
        for i in range(0,26):
            new_path=ops.join(path,chr(ord('a')+i))
            if not ops.exists(new_path):
                os.makedirs(new_path)
    
    def init_file(self):
        files = os.listdir(self.image_dir)
        for file_name in files:
            full_name = ops.join(self.image_dir,file_name)
            if ops.isfile(full_name):
                if full_name.split('.')[-1] == 'jpg' or full_name.split('.')[-1] == 'JPG':
                    self.files.append(full_name)
        self.file_index= -1
        self.files.sort()
        
    def next_file(self):
        self.file_index=self.file_index+1
        return self.files[self.file_index]

    def this_file(self):
        return self.files[self.file_index]

    def parse_image(self,image_dir, output_dir):
        self.test_dir(output_dir)
        self.init_file()
        self.index = 0
        cv2.namedWindow("image",0)
        cv2.setMouseCallback('image',self.MouseCallBack)
        f = open(ops.join(output_dir ,'test.txt'), 'a')
        while self.index < 124:
            k = cv2.waitKey() & 0xFF
            if k == 27:
                #ESC
                print("用户中途退出,祝你训练成功~")
                break
            if not self.inputComplete:
                if 48 <= k <= 57 or 65 <= k <= 90 or 97 <= k <= 122:
                    # 数字字母
                    self.nums[-1].setNumValue(chr(k))
                    print(self.index,"set Number picture as",self.nums[-1].value)
                    self.inputComplete = True
            elif k == 13:
                # Enter
                # 标记下一张图片
                if self.nums:
                    self.save()
                self.index += 1
                try:
                    image_name = self.next_file()
                except:
                    print("所有图片标定完毕,祝你训练成功~")
                    break
                print('try to open {:s}'.format(image_name))
                self.origin = cv2.imread(image_name,0)
                self.img = self.origin.copy()
                self.nums, self.undoimgs = [], []
                self.undoimgs.append(self.origin)
                cv2.imshow("image",self.origin)
            elif k == 32:
                # Space
                # 标记下一个数字
                if self.nums:
                    self.save()
                # self.index += 1
                image_name = self.this_file()
                print('try to open {:s}'.format(image_name))
                self.origin = cv2.imread(image_name,0)
                self.img = self.origin.copy()
                # self.nums, self.undoimgs = [], []
                self.undoimgs.append(self.origin)
                cv2.imshow("image",self.origin)
            elif k == ord('c'):
                # clear
                self.img = self.origin.copy()
                cv2.imshow("image",self.img)
            elif k == ord("z"):
                # undo
                if len(self.undoimgs) > 1:
                    self.undoimgs.pop()
                    self.nums.pop()
                    self.img = self.undoimgs[-1].copy()
                    cv2.imshow("image",self.img)
                    if self.nums != []:
                        cv2.imshow("num",self.nums[-1].pic)
        f.close()

def init_args():
    '''
    :return:
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('--image_dir', type=str, help='where you store the image')
    parser.add_argument('--output_dir', type=str, help='where you save the output')

    return parser.parse_args()

if __name__ == '__main__':
    # init args
    args = init_args()
    if not ops.exists(args.image_dir):
        raise ValueError("image {:s} doesn't exist".format(args.image_dir))
    
    cut= Cut(image_dir=args.image_dir, output_dir=args.output_dir)
    # if not ops.exists(args.output_dir):
    #     raise ValueError("output directory {:s} doesn't exist".format(args.output_dir))