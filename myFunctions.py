import cv2 #to load image
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage
from skimage.color import rgb2gray
from skimage.morphology import skeletonize
import statistics as st
from PIL import Image


def diferenciadorSobel(gray): #calcula a primeira derivada (sobel) na horizontal e vertica
    sobel_horizontal = np.array([
        [1, 2, 1],
        [0, 0, 0],
        [-1,-2,-1]])

    sobel_vertical = np.array([
        [1, 0, -1],
        [2, 0, -2],
        [1, 0, -1]])

    #convolução dos filtros com a imagem em preto e branco
    imgH = ndimage.convolve(gray, sobel_horizontal)
    imgV = ndimage.convolve(gray, sobel_vertical)
    '''
    plt.subplot(121)
    plt.imshow(imgH)
    plt.subplot(122)
    plt.imshow(imgV)
    plt.show()
    '''
    return imgH, imgV



def gaussianFilter(img):
    kernel = np.array([
        [0,0,0.8,0,0],
        [0,1,1,1,0],
        [0.8,1,1.1,1,0.8],
        [0,1,1,1,0],
        [0,0,0.8,0,0]])
    gaussian = ndimage.convolve(img, kernel)
    return gaussian



def calcAngle(gray, tipoFiltro, valorFiltro, *amostrasHist):
    
    #calculo do sobel H e V
    imgH, imgV = diferenciadorSobel(gaussianFilter(gray))
    #inicia a matriz angulo com tamanho da imagem
    imgA = np.zeros(imgH.shape)

    #filtro gaussiano para suavisar os ANGULOS nas regiões turbulentas que podem formar uma reta
    #HtoMean = gaussianFilter(imgH)
    #VtoMean = gaussianFilter(imgV)

    HtoMean = imgH
    VtoMean = imgV

    for i in range(imgH.shape[0]):
        for j in range(imgH.shape[1]):
            try: #try evita problemas quando posições inexistentes são acessadas
                #pega os 8 pexel ao redor para melhor distribuição diferencias. calculo da media entre eles
                if VtoMean[i,j] != 0: # para que não haja divisão por zero
                    imgA[i,j] = ((np.arctan(HtoMean[i,j]/VtoMean[i,j]))*2)/np.pi
                else: #caso haja algum V zerado, pode ser que estejamos fora do escopo da digital (sem alterações verticais)
                    if HtoMean[i,j] < 0:
                        imgA[i,j] = -1
                    elif HtoMean[i,j] > 0:
                        imgA[i,j] = 1
                    elif HtoMean[i,j] == 0:
                        imgA[i,j] = 3
            except IndexError as e:
                pass # resposta para posições inexistentes, pois, não quero que ele pare quando chegar á borda da matriz

    imgAbs = absoluteQuantoH(imgA)
    imgAbsPi = ((imgAbs + 1)/2)*np.pi #ajuste de (-1 á 1) para (pi á 2pi) para calcular angulo

    print("maior valor da matriz ANGULAÇÃO final:", imgAbsPi.max())
    print("Menor valor da matriz ANGULAÇÃO final:", imgAbsPi.min())

    if tipoFiltro == "hist" or tipoFiltro == "meanHarmonic":
        print('CALC MAP GRADIENT usando: ', tipoFiltro, valorFiltro, amostrasHist)
        imgAbsPi = predominaAng(imgAbsPi, tipoFiltro, valorFiltro, amostrasHist)
    if tipoFiltro == "blur":
        print('CALC MAP GRADIENT usando tamanho de nucleo:', valorFiltro,'x',valorFiltro)
        imgAbsPi = cv2.blur(imgAbsPi,(int(valorFiltro), int(valorFiltro)))
    #plt.subplot(133)

    print("maior valor da matriz ANGULAÇÃO final:", imgAbsPi.max())
    print("Menor valor da matriz ANGULAÇÃO final:", imgAbsPi.min())


    #imgA = predominaAng(imgA)

    np.save("./arquivos-de-processos/imgAngulo-gradient.npy",imgA)
    np.save("./arquivos-de-processos/imgAngulo-gradient-abs-pi.npy",imgAbsPi)
    return imgA, imgH, imgV, imgAbsPi, imgAbs

def absoluteQuantoH(imgA):
    imgA = np.abs(imgA)
    return imgA


def plotGradient(gray, imgA):
    #ax = plt.axes()
    plt.imshow(gray, cmap='gray')
    for i in range(0, imgA.shape[0], 10):
        for j in range(0, imgA.shape[1], 10):
            if imgA[i,j] >= np.pi and imgA[i,j] <= 2*np.pi:
                anguloY = np.sin(imgA[i,j])
                anguloX = np.cos(imgA[i,j])
                plt.quiver(j, i, anguloX, anguloY, headaxislength=1, headwidth=3, headlength=10, scale=20, pivot='mid',color='b', alpha=0.7)
                #plt.scatter(i, j, s=1, c="blue", alpha=0.8)
    plt.show()



def plotGradientInCanny(gray, imgAbsPi, imgA, intervalo, aproximaLocal, tamanhoNucleo):
    if aproximaLocal != "nenhum":
        print('PLOT GRADIENT Usando tipo de media:', aproximaLocal,'para calcular setas no gradiente')
        print('PLOT GRADIENT usando intervalo de', intervalo, 'pixels. São colocadas setas a cada intervalo')
        print('PLOT GRADIENT usando tipo de nucleo:', tamanhoNucleo)
    plt.imshow(gray, cmap='gray', alpha=0.5)
    for i in range(0, imgAbsPi.shape[0], intervalo):
        for j in range(0, imgAbsPi.shape[1], intervalo):
            #if edges[i,j] == 1:
            if aproximaLocal != "nenhum":
                imgAbsPi_u = pontosAoRedor(imgAbsPi, i, j, aproximaLocal, tamanhoNucleo)

            if imgA[i,j] >= 0: #verifica no mapa de 180 a direção, < 0 é pra esquerda, > 0 é para a direita
                anguloY = np.sin(imgAbsPi_u)
                anguloX = np.cos(imgAbsPi_u)*(-1)
            else:
                anguloY = np.sin(imgAbsPi_u)
                anguloX = np.cos(imgAbsPi_u)

            plt.quiver(j, i, anguloX, anguloY, headaxislength=1, headwidth=3, headlength=10, scale=30, pivot='mid',color='r', alpha=0.7)
            #plt.scatter(j, i, s=1, c="blue", alpha=0.2)
    plt.savefig('setas.png', bbox_inches='tight', pad_inches=0, dpi=200)




def plotHist(imgA, amostra, gray):
    imgAd = (imgA.ravel()) - np.pi #transforma a matriz em um vetor linear

    fig = plt.figure()
    ax = fig.add_subplot(121, polar=True)

    ax.set_thetamin(0)
    ax.set_thetamax(180)
    a,_,_ = plt.hist(imgAd, amostra,range=(0, np.pi)) #histograma do vetor de angulos, com 50 amostras no intervalo de 0 á pi
    plt.title("Approximate angle: [ " + str(round((np.argmax(a)/amostra)*180,1)) + " º ] \nappearances: "+str(a.max()))
    # (np.argmax(a)/amostra)*180 obtém a posição (entre as amostras) do angulo com maior frequencia e converte para angulos de 0 á 180 º
    ax = fig.add_subplot(122, polar=False)
    plt.imshow(gray)

    plt.show()



def predominaAng(img, tipoFiltro, valorFiltro, *amostrasHist):
    imgAfinal = np.zeros(img.shape)*.0
    for i in range(0, img.shape[0]):
        for j in range(0, img.shape[1]):
            imgAfinal[i,j] = pontosAoRedor(img, i, j, tipoFiltro, valorFiltro, amostrasHist)
    #imgAfinal = np.where(np.isnan(imgAfinal), .0, imgAfinal)
    #imgAfinal = imgAfinal[~np.isnan(imgAfinal)]
    '''
    for i in range(0, img.shape[0]):
        for j in range(0, img.shape[1]):
            if imgAfinal[i,j] == np.nan:
                imgAfinal = .0
    '''
    return imgAfinal




def pontosAoRedor(imgA, i, j, type, tamanhoNucleo, amostrasHist=30):
    #amostraHist não esta sendo usado no momento
    '''
    freq = (
            imgA[i-1,j+1], imgA[i,j+1], imgA[i+1,j+1],
            imgA[i-1,j  ], imgA[i,j  ], imgA[i+1,j  ],
            imgA[i-1,j-1], imgA[i,j-1], imgA[i+1,j-1],)
    if tamanhoNucleo == "5x5":
        freq = (imgA[i-2,j+2], imgA[i-1,j+2], imgA[i,j+2], imgA[i+1,j+2], imgA[i+2,j+2],
                imgA[i-2,j+1], imgA[i-1,j+1], imgA[i,j+1], imgA[i+1,j+1], imgA[i+2,j+1],
                imgA[i-2,j  ], imgA[i-1,j  ], imgA[i,j  ], imgA[i+1,j  ], imgA[i+2,j  ],
                imgA[i-2,j-1], imgA[i-1,j-1], imgA[i,j-1], imgA[i+1,j-1], imgA[i+2,j-1],
                imgA[i-2,j-2], imgA[i-1,j-2], imgA[i,j-2], imgA[i+1,j-2], imgA[i+2,j-2])
    '''
    freq = criaFreq(imgA, i, j, tamanhoNucleo)
    if type == "hist":
        a,b = np.histogram(freq, density=False, range=(np.pi/2, np.pi), bins=40)
        #print(a)
        #print(b)
        return b[np.argmax(a)] #posição do elemento "a" (q aparece mais vezes) aplicado ao vetor de valores aparecidos "b"
        
    elif type == "meanHarmonic":
        return st.harmonic_mean(freq)

def criaFreq(imgA, i, j, tamanhoNucleo):
    freqFin = []
    if tamanhoNucleo == "3x3":
        freq = [
            (i-1,j+1), (i,j+1), (i+1,j+1),
            (i-1,j  ), (i,j  ), (i+1,j  ),
            (i-1,j-1), (i,j-1), (i+1,j-1)]
        for k in freq:
            try:
                freqFin.append(imgA[k])
            except IndexError as e:
                pass
    elif tamanhoNucleo == "5x5":
        freq = [
            (i-2,j+2), (i-1,j+2), (i,j+2), (i+1,j+2), (i+2,j+2),
            (i-2,j+1), (i-1,j+1), (i,j+1), (i+1,j+1), (i+2,j+1),
            (i-2,j  ), (i-1,j  ), (i,j  ), (i+1,j  ), (i+2,j  ),
            (i-2,j-1), (i-1,j-1), (i,j-1), (i+1,j-1), (i+2,j-1),
            (i-2,j-2), (i-1,j-2), (i,j-2), (i+1,j-2), (i+2,j-2)]
        for k in freq:
            try:
                freqFin.append(imgA[k])
            except IndexError as e:
                pass
    return freqFin




############################################ ESQUELETIZAÇÃO extração das linhas com métodos melhorados
