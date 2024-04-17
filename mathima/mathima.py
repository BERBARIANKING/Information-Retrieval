import sumy
from PyPDF2 import PdfReader


from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

#Input text to the summarizer
input_text = ""
#Parse the input text
parser = PlaintextParser.from_string(input_text, Tokenizer("english"))
#create an LSA summarizer
summarizer = LsaSummarizer()
#Generate the summary
summary = summarizer(parser.document, sentences_count=3) #you can adjust the number qf sentences in the summary

#output of the summary 
print('Originl text:')
print(input_text)
print('Summary:')
for sentence in summary:
    print(sentence)
