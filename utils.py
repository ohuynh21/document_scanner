import os
import settings
import cv2


import numpy as np
import matplotlib.pyplot as plt
import cv2
import imutils
from imutils.perspective import four_point_transform




class DocumentScan():
    def __init__(self):
        pass

    def save_image(self, file):
        self.img = cv2.imread(file.filename)
        filename = file.filename
        name, ext = filename.split(".") 
        filename = f"upload.{ext}"
        path = settings.join_path(settings.SAVE_DIR, filename)
        file.save(path)
        return path

    def resize(self, width=500):
        h,w,c = self.img.shape
        height = h/w * width
        size = (width, height)
        return cv2.resize(self.img, (width, int(height))), size

    def find_doc(self, img_path):
        self.img = cv2.imread(img_path)
        resized, self.dim = self.resize()
        # save resized image
        filename = 'resized_img.jpg'
        path = settings.join_path(settings.SAVE_DIR, filename)
        cv2.imwrite(path, resized)
        # preprocess
        try:
            detail = cv2.detailEnhance(resized, sigma_s=20, sigma_r=0.15)
            gray = cv2.cvtColor(detail, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5,5), 0)
            edge = cv2.Canny(blur, 75, 200)
            kernel = np.ones((5,5), np.uint8)
            dilate = cv2.dilate(edge, kernel, iterations=1)
            closing = cv2.morphologyEx(dilate, cv2.MORPH_CLOSE, kernel)
            
            # get 4 points
            contours, _ = cv2.findContours(closing, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

            # find the largest rectangular contour
            contours = sorted(contours, key=cv2.contourArea, reverse=True)
            for contour in contours:
                perimeter = cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, 0.02*perimeter, True)
                if len(approx) == 4:
                    four_points = np.squeeze(approx)
                    break
            # boxed = cv2.drawContours(resized, [four_points], -1, (0,255,0), 3)
            return four_points, self.dim
        except:
            return None, self.dim
        
    

    def calibrate(self, pts):
        # crop orig image based on 4 points
        multiplier = self.img.shape[1] / self.dim[0]
        
        four_points = pts * multiplier
        
        four_points = four_points.astype(int)
        
        return four_point_transform(self.img, four_points)