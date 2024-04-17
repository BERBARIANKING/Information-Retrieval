import os
import pyPDF2
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

def extract_text_from_pdf(pdf_file):
    with open(pdf_file, 'rb') as file:
        pdf_reader = pyPDF2.PdfFileReader(file)
        text = ''
        for page_num in range(pdf_reader.numPages):
            text += pdf_reader.getPage(page_num).extract_text()
        return text
    
def summarize_text(text, language='english',sentences_count=5 , output_file='summary.txt'):
   temp_file = 'temp.txt'
   with open(temp_file, 'w') as file:
         file.write(text)
parser = PlaintextParser.from_file(temp_file, Tokenizer(language))
summarizer = LsaSummarizer()
summary = summarizer(parser.document, sentences_count)
   
print('Summary:')
for sentence in summary:
    print(sentence)
    with open(output_file, 'w' , encoding="utf-8") as f:
     f.write(str(sentence))
    os.remove(temp_file)

if __name__ == '__main__':
    pdf_file = input('Enter the PDF file name: ')
    output_file = input('Enter the output file name: ')
    text = extract_text_from_pdf(pdf_file)
    summarize_text(text , text=output_file)
