import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage
from skimage.color import rgb2gray

'''
g_kernel = cv2.getGaborKernel((21, 21), 3.0, np.pi/2, 9.5, 0.5, 0.1, ktype=cv2.CV_32F)
img90 = ndimage.convolve(gray, g_kernel)
g_kernel = cv2.getGaborKernel((21, 21), 3.0, np.pi, 9.5, 0.5, 0.1, ktype=cv2.CV_32F)
img180 = ndimage.convolve(gray, g_kernel)
g_kernel = cv2.getGaborKernel((21, 21), 3.0, np.pi/4, 9.5, 0.5, 0.1, ktype=cv2.CV_32F)
img45 = ndimage.convolve(gray, g_kernel)
g_kernel = cv2.getGaborKernel((21, 21), 3.0, 3*np.pi/4, 9.5, 0.5, 0.1, ktype=cv2.CV_32F)
img135 = ndimage.convolve(gray, g_kernel)

img90 = np.where(img90 < 5, 0, 1)
img180 = np.where(img180 < 5, 0, 1)
img45 = np.where(img45 < 5, 0, 1)
img135 = np.where(img135 < 5, 0, 1)

plt.subplot(141)
plt.imshow(img, cmap='gray')
plt.subplot(142)
plt.imshow(img45, cmap='gray')
plt.subplot(143)
imgg = img90*img180*img45*img135
plt.imshow(imgg, cmap='gray')
plt.subplot(144)

imgg = skeletonize(np.where(imgg == 1, 0,1))
plt.imshow(imgg, cmap='gray')
plt.show()
'''

img = cv2.imread("./finger.tif")
gray = rgb2gray(img)

#b,g,r = cv2.split(img)
#--------BLUR ####################################
blur_filter = np.array([
    [2, 4, 5, 4, 2],
    [4, 9, 12, 9, 4],
    [5, 12, 15, 12, 5],
    [4, 9, 12, 9, 4],
    [2, 4, 5, 4, 2]])
blur = ndimage.convolve(gray, blur_filter)
plt.subplot(141)
plt.imshow(blur, cmap='gray')
#--------BLUR #####################################

#--------sobel border (gratient intensidade ###############################
#calculo sobel vertical e horizontal com convolução
sobel_vertical = np.array([
    [1, 0, -1],
    [2, 0, -2],
    [1, 0, -1]])
sobel_horizontal = np.array([
    [1,2,1],
    [0,0,0],
    [-1,-2,-1]
])
grayH = ndimage.convolve(blur, sobel_horizontal)
grayV = ndimage.convolve(blur, sobel_vertical)

#aqui calculamos o gradient juntando os dois, G =  sqrt(G1² + G2²) ou G = |G1|+|G2|
gradient_sobel = np.abs(grayH) + np.abs(grayV)

plt.subplot(142)
plt.imshow(gradient_sobel, cmap='gray')
#plt.show()
#--------sobel e gradient calculados #####################################

#-------binarização #######################
def binarizar(image, limiar):
    for i in range(int(image.shape[0])):
        for j in range(int(image.shape[1])):
            if image[i,j] > limiar:
                image[i,j] = 1
            else :
                image[i,j] = 0
    return image

#gradient_sobel = binarizar(gradient_sobel, 34)
#plt.subplot(143)
#plt.imshow(gradient_sobel, cmap='gray')

#-------binarização #######################

#--------ESQUELETIZAÇÃO precisa de binarios scikit (supressao nao maxima) ########################
def non_max_suppression(img, D):
    M, N = img.shape
    Z = np.zeros((M,N), dtype=np.int32)
    angle = D * 180. / np.pi
    angle[angle < 0] += 180


    for i in range(1,M-1):
        for j in range(1,N-1):
            try:
                q = 255
                r = 255

               #angle 0
                if (0 <= angle[i,j] < 22.5) or (157.5 <= angle[i,j] <= 180):
                    q = img[i, j+1]
                    r = img[i, j-1]
                #angle 45
                elif (22.5 <= angle[i,j] < 67.5):
                    q = img[i+1, j-1]
                    r = img[i-1, j+1]
                #angle 90
                elif (67.5 <= angle[i,j] < 112.5):
                    q = img[i+1, j]
                    r = img[i-1, j]
                #angle 135
                elif (112.5 <= angle[i,j] < 157.5):
                    q = img[i-1, j-1]
                    r = img[i+1, j+1]

                if (img[i,j] >= q) and (img[i,j] >= r):
                    Z[i,j] = img[i,j]
                else:
                    Z[i,j] = 0

            except IndexError as e:
                pass

    return Z
##################
#################
###############

#--------ESQUELETIZAÇÃO scikit ########################

#----------double trashold ###################
def threshold(img, lowThresholdRatio=0.05, highThresholdRatio=0.09):

    highThreshold = img.max() * highThresholdRatio
    lowThreshold = highThreshold * lowThresholdRatio
    M, N = img.shape
    res = np.zeros((M,N), dtype=np.int32)

    weak = np.int32(25)
    strong = np.int32(255)

    strong_i, strong_j = np.where(img >= highThreshold)
    zeros_i, zeros_j = np.where(img < lowThreshold)

    weak_i, weak_j = np.where((img <= highThreshold) & (img >= lowThreshold))

    res[strong_i, strong_j] = strong
    res[weak_i, weak_j] = weak

    return res, weak, strong
#----------double trashold ###################

#----------rastreamento de borda por histerese #######################
def hysteresis(img, weak, strong=255):
    M, N = img.shape
    for i in range(1, M-1):
        for j in range(1, N-1):
            if (img[i,j] == weak):
                try:
                    if ((img[i+1, j-1] == strong) or (img[i+1, j] == strong) or (img[i+1, j+1] == strong)
                        or (img[i, j-1] == strong) or (img[i, j+1] == strong)
                        or (img[i-1, j-1] == strong) or (img[i-1, j] == strong) or (img[i-1, j+1] == strong)):
                        img[i, j] = strong
                    else:
                        img[i, j] = 0
                except IndexError as e:
                    pass
    return img
#----------rastreamento de borda por histerese #######################
''
from skimage.morphology import skeletonize
#esqueletizado = non_max_suppression(blur, gradient_sobel)
res, weak, strong = threshold(gradient_sobel, 0.05, 0.2)
plt.subplot(143)
plt.imshow(res, cmap='gray')
print(weak)

plt.subplot(144)
plt.imshow(hysteresis(res, weak, strong), cmap='gray')
plt.show()

#ravel achata  a matriz em uma 1D

hist,bins = np.histogram(blur.ravel(),256,[0,256])
plt.subplot(121)
plt.plot(hist)
plt.subplot(122)
plt.imshow(skeletonize(binarizar(blur, 120)), cmap='gray')
plt.show()
'''
'''
gscale = 2*g-r-b
print(gscale.shape[0],gscale.shape[1])
gscale = cv2.Canny(gscale, 250, 250)
#checking the results (good practice)
plt.figure()
plt.plot(), plt.imshow(gscale)
plt.title('Canny Edge-Detection Results')
plt.xticks([]), plt.yticks([])
plt.show()
