import os
import PyPDF2
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.summarizers.lex_rank import LexRankSummarizer

def extract_text_from_pdf(pdf_file):
    with open(pdf_file, "rb") as f:
        pdf_reader = PyPDF2.PdfReader(f)
        text = ''
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
        return text
    
def summarize_text(text, language='english',sentences_count=5 , output_file='summary.txt'):
    temp_file = 'temp.txt'
    with open(temp_file, 'w' , encoding='utf-8') as f:
      f.write(text)
    parser = PlaintextParser.from_file(temp_file, Tokenizer(language))
    summarizer = LexRankSummarizer()
    summary = summarizer(parser.document, sentences_count)
   
    print('Summary:')
    for sentence in summary:
        print(sentence)
    with open(output_file, 'w' , encoding="utf-8") as f:
        f.write("Summary:\n")
        for sentence in summary:
            f.write(str(sentence) + '\n')
    os.remove(temp_file)

if __name__ == '__main__':
    pdf_file = input('Enter the PDF file name: ')
    output_file = input('Enter the output file name: ')
    text = extract_text_from_pdf(pdf_file)
    summarize_text(text , output_file=output_file)
