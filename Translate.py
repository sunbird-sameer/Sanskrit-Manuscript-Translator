import googletrans
from googletrans import Translator

#print(googletrans.LANGUAGES)

translator = Translator(service_urls=['translate.googleapis.co.in'])
translated = translator.translate(open("OCR.txt", encoding='utf-8').read(),src='auto', dest='en')

file = open("Translated.txt", "w", encoding='utf-8')
file.write(str(translated.text))
file.close

#print(translated.text)