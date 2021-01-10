from myFunctions import *
# resolução da tela ------------------
from screeninfo import get_monitors
resolution = get_monitors()
# resolução da tela ------------------
print(resolution[0])
# interface pusimplegui --------------------------------------------------------------------------------------------
import PySimpleGUI as sg
layout = [
    [
        sg.Text('Caminho da imagem. Ex:', size =(40, 1)), sg.InputText("./data-finger/finger.tif", key="-pathImage-"),
    sg.Submit(),
    sg.Cancel()
    ],
    [sg.Text('\nCALCULO DOS MAPAS PRIMÁRIOS\n')],
    [sg.Text("O Diferencial Sobel retorna o resultado da convolução dos filtros sobel H e V e É NECESSÁRIO PARA OS PASSOS SEGUINTES")],
    [sg.Text("A função calcAngle calcula uma matriz do tamanho da imagem com um mapa com os anglos edentificados entre pi e 2pi")],
    [
        sg.InputCombo(('nenhum','hist', 'meanHarmonic', 'blur'), default_value="hist",  size=(20, 1), key="-calcAproxima-"),
        sg.Text('Caso seja Hist ou Mean:'),
        sg.InputCombo(('3x3', '5x5'), default_value="3x3", size=(5, 1), key="-calcAproximaNucleo-"),
        #sg.Text('Amostras Hist:'),
        #sg.InputText(50, key="-amostrasHist-", size =(4, 1)),
        sg.Text('Caso seja Blur:'),
        sg.InputText(5, key="-aplicarBlurValue-", size =(4, 1)),
        sg.Text('Tamanho do núcle do filtro blur, não exagerar'),
    ],
    [sg.Checkbox('Mostrar resultados destes processamentos', default=False, key="-ShowSobel-")],
    [sg.Text('Estes dados estão sendo salvos em ./arquivos-de-processos como arquivos npy')],
    
    
    [sg.Text('\nUSANDO MAPA PARA GERAR SETAS DIRECIONAIS\n')],
    [sg.Checkbox('Gerar e salvar mapa (imagem) com setas indicando direção do gradiente', default=True, key="-generateMapAngle-")],
    [
        sg.InputText(10, key="-intervalo-", size =(4, 1)),
        sg.Text('Intervalo em píxels das setas. Recomendado: 10'),
    ],
    [sg.Checkbox('Mostrar o gradiente (é necessário selecionar Gerar para mostrar)', default=True, key="-ShowMapAngle-")],
    [sg.Text('Estamos usando aproximação local no gradiente para melhorar a precisão caso o ponto seja defeituoso')],
    [sg.InputCombo(('nenhum','hist', 'meanHarmonic'), default_value="hist",  size=(20, 1), key="-tipoDeMedia-"), sg.Text(' Tipo de aproximação a ser usada')],
    [sg.InputCombo(('3x3', '5x5'), default_value="3x3", size=(5, 1), key="-tipoDeNucleo-"), sg.Text(' tamanho do núcleo usado para calcular a aproximação ao redor do ponto')],
    [sg.Text('\nProximos passos: Melhorar precisão, usarm filtros de gabor para ressaltar linhas, esqueletizar linhas e encontrar minúcias\n usando os mapas acima para determinar a sentido vetorial')]
]
window = sg.Window('Finger print', layout, no_titlebar=False, resizable=True).Finalize()
#caminhogui.Maximize() #tela cheia sem borao fechar
eventgui, valgui = window.read()
pathgui = [valgui["-pathImage-"]]
#sg.Window(title="Hello World", layout=[[]], margins=(500, 300)).read()
#window = sg.Window('My new window', layout, no_titlebar=False, resizable=False).Finalize()
#window.Maximize()
# interface pusimplegui -------------------------------------------------------------------------------------------


#variaveis
amostra = 100; #quantidade de amostra no histograma, (melhor resultado quando proximo de 50)
#a imagem a ser analisada
img = cv2.imread(pathgui[0]) #load image
gray = rgb2gray(img)
#filtros sobel







imgA, imgH, imgV, imgAbsPi, imgAbs = calcAngle(gray,
 tipoFiltro=valgui["-calcAproxima-"], valorFiltro= valgui["-calcAproximaNucleo-"])

setaFinal = cv2.imread('setas.png')
'''
if valgui["-ShowSobel-"]: # duas colunas
    plt.subplot(221).set_title('sobel horizontal')
    plt.imshow(imgH, cmap='gray')
    plt.subplot(222).set_title('sobel vertical')
    plt.imshow(imgV, cmap='gray')
    plt.subplot(223).set_title('Angulação')
    plt.imshow(imgA, cmap='gray')
    plt.subplot(224).set_title('original gray')
    plt.imshow(gray, cmap='gray')
    plt.show()
'''
# ou
if valgui["-ShowSobel-"]: #uma coluna
    plt.subplot(141).set_title('original')
    plt.imshow(gray, cmap='gray')
    plt.subplot(142).set_title('sobels arctg')
    plt.imshow(imgA, cmap='gray')
    plt.subplot(143).set_title('abs do sobel')
    plt.imshow(imgAbs, cmap='gray')
    plt.subplot(144).set_title('abs em pi aproximado')
    plt.imshow(imgAbsPi, cmap='gray')
    plt.show()
print(valgui["-tipoDeMedia-"])
if valgui["-generateMapAngle-"]:
    plotGradientInCanny(gray, imgAbsPi, imgA, intervalo = int(valgui["-intervalo-"]),
     aproximaLocal= str(valgui["-tipoDeMedia-"]), tamanhoNucleo=valgui["-tipoDeNucleo-"])
    if valgui["-ShowMapAngle-"]:
        plt.show()
'''
plt.subplot(121)
plt.imshow(aaa, cmap='gray')
plt.subplot(122)
plt.imshow(gray, cmap='gray')


plotGradient(gray, aaa)
plotGradientInCanny(gray, aaa)
plotHist(aaa, amostra, gray)

plt.subplot(121)
plt.imshow(aaa, cmap='gray')
plt.subplot(122)
escala = np.zeros((180, 10))
for i in range(0,180):
    escala[i, :] = ((np.pi/180)*i) + np.pi
plt.title("escala angulo")
plt.imshow(escala, cmap='gray')
plt.show()
'''