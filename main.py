import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

def bgrToHsv(b, g, r):
    r, g, b = r/255.0, g/255.0, b/255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    fark = mx-mn
    if mx == mn:
        h = 0
    elif mx == r:
        h = (60 * ((g-b)/fark) + 360) % 360
    elif mx == g:
        h = (60 * ((b-r)/fark) + 120) % 360
    elif mx == b:
        h = (60 * ((r-g)/fark) + 240) % 360
    if mx == 0:
        s = 0
    else:
        s = (fark/mx)*100
    v = mx*100
    return int(h), int(s), int(v)

# hue değerinin histogramı alınıyor
def hue_histogram(image,filename):
    hue = np.zeros(360, dtype=int)
    norm = np.zeros(360, dtype=float)
    hsv = image
    height, width = image.shape[:2]
    for i in range(height):
        for j in range(width):
            hsv[i][j] = bgrToHsv(image[i][j][0],image[i][j][1],image[i][j][2])
    for i in range(height):
        for j in range(width):
            hue[hsv[i][j][0]] = hue[hsv[i][j][0]] +1
    for i in range(360):
        norm[i] = (float(hue[i])/(width*height))
    np.savetxt("hue/" + filename +".txt",norm)

# lbp fonksiyonu için kullanılıyor
# pixelin değeri alınıyor eğer hata veriyorsa 0 olarak döndürüyorum bunun nedeni kenarlardaki pixellerin dışında pixel ve yok bu yüzden
# ortaya çıkacak herhangi bir hata düzeltiliyor
def pixel_degeri(image, i, j):
    try:
        return image[i,j]
    except IndexError:
        return 0

#her pixel için lbp değeri bulunuyor
def lbpValue(center, pixels):
    eightbits = []
    for i in pixels:
        if i >= center:
            eightbits.append(1)
        else:
            eightbits.append(0)
    return eightbits

# pixel değerinde kaç adet geçiş olduğuna bakılıyor
def gecis_bul(degerler):
    prev = degerler[-1]
    a = 0
    for i in range(0, len(degerler)):
        current = degerler[i]
        if current != prev:
            a += 1
        prev = current
    return a

# lbp kodlarının histogram değerinin elde edilmesi
def lbp(image,lbpimage,filename):
    lbp = np.zeros(59, dtype=int)
    norm = np.zeros(59, dtype=float)
    luminance = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.cvtColor(lbpimage, cv2.COLOR_BGR2GRAY)
    height, width = image.shape[:2]
    gecis_degerleri = set()
    for i in range(height):
        for j in range(width):
            center = luminance[i, j]
            top_left = pixel_degeri(luminance, i-1, j - 1)
            top_up = pixel_degeri(luminance, i, j - 1)
            top_right = pixel_degeri(luminance, i + 1, j - 1)
            right = pixel_degeri(luminance, i + 1, j)
            bottom_right = pixel_degeri(luminance, i + 1, j + 1)
            bottom_down = pixel_degeri(luminance, i, j + 1)
            bottom_left = pixel_degeri(luminance, i - 1, j + 1)
            left = pixel_degeri(luminance, i - 1, j)
            degerler = lbpValue(center, [top_left, top_up, top_right, right, bottom_right,bottom_down, bottom_left, left])
            agırlık = [1, 2, 4, 8, 16, 32, 64, 128]
            gecisler = gecis_bul(degerler)
            if gecisler <= 2:
                value = 0
                for a in range(0, len(degerler)):
                    value += agırlık[a] * degerler[a]
                gecis_degerleri.add(value)
            value = 0
            for a in range(0, len(degerler)):
                value += agırlık[a] * degerler[a]
            gray[i][j] = value
    gecis_degerleri = sorted(gecis_degerleri)
    for i in range(height):
        for j in range(width):
            value = gray[i][j]
            if(value in gecis_degerleri):
                index = gecis_degerleri.index(value)
                lbp[index] = lbp[index] + 1
            else:
                lbp[58] = lbp[58] + 1
    for i in range(59):
        norm[i] = (float(lbp[i])/(width*height))
    np.savetxt("lbp/" + filename + ".txt", norm)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
image_dir = os.path.join(BASE_DIR,"images")

for root, dirs, files in os.walk(image_dir):
    for file in files:
        if file.endswith("png") or file.endswith("jpg") or file.endswith("jpeg"):
            path = os.path.join(root,file)
            orimage = cv2.imread(path)
            image = cv2.resize(orimage, (500, 500))
            if file.endswith("jpg"):
                filename = file.replace(".jpg","")
            if file.endswith("png"):
                filename = file.replace(".png","")
            if file.endswith("jpeg"):
                filename = file.replace(".jpeg","")
            hue_histogram(image,filename)
            lbp(image,image,filename)
            print(file,"kayıt edildi.")



