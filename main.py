import easyocr
import os
import googletrans
from googletrans import Translator

#print(googletrans.LANGUAGES)

reader = easyocr.Reader(['hi', 'en'])#Devanagari Lipi & English
translator = Translator(service_urls=['translate.googleapis.co.in'])

file = open("OCR.txt", "w", encoding='utf-8')
file = open("Translated.txt", "w", encoding='utf-8')

ocr_output = ""
for image in os.listdir("Images"):
    print("Reading from File: " + image)


    ocr_output = reader.readtext(str("Images\\" + str(image)), detail=0)
    file = open("OCR.txt", "a", encoding='utf-8')
    file.write(str(ocr_output))
    file.close

    print(ocr_output)

    for item in ocr_output:
        translated = translator.translate(item,src='auto', dest='en')
        file = open("Translated.txt", "a", encoding='utf-8')
        file.write(str(" \n " + translated.text))
        file.close

        print(translated.text)
