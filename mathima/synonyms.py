#This program helps with synonyms 
#For example it can find synonyms for the word action etc.
#So this can help woith the genres


#if problem with library , imprort nltk
from nltk.corpus import wordnet 

def find_synonyms(word):
    synonyms = []
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.append(lemma.name())
    return set(synonyms)

if __name__ == '__main__':
    word = input("Input is the word: ")
    sysnonyms = find_synonyms(word)
    if sysnonyms:
        print(f"The synonyms of \"{word}\" are: {', '.join(sysnonyms)}")
    else:
        print(f"No synonyms found for the \"{word}\".")
