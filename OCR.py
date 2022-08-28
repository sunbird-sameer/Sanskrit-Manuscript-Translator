# pip install easyocr
import easyocr
import os

reader = easyocr.Reader(['hi', 'en'])#Devanagari Lipi & English

file = open("OCR.txt", "w", encoding='utf-8')
output = ""
for image in os.listdir("Images"):
    print("Reading from File: " + image)
    output = reader.readtext(str("Images\\" + str(image)), detail=0)

    #print(output)

    file = open("OCR.txt", "a", encoding='utf-8')
    file.writelines(list(output))
    file.close