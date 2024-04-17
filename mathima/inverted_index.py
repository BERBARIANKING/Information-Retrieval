#DEN DOULEUEI

#Mas exei pei oti mporoume na baloume mia exwterikh for gia na anoigoume ta eggrafa (opws enas pinakas me eggrafa example[1,2,4,5] ktl)
#opote anoigei ena eggrafo kai to scannarei me basei to frequency diaforwn terms 

#Epishs mporoume na baloume eggrafa typou texts keimeno.summarizer.txt etc.
#'H enas allos tropos afora mia bash dedomenwn. Opote uparxoun arketoi tropoi na paixoume me auto

def create_inverted_index(file_path):
    inverted_index = {}
    with open(file_path, "r", encoding="utf-8") as file:
         text = file.read()
            #Diakommatismos tou keimenou se lekseis
         words = text.split()
         for word in words:
                 #Auxhsh tou arithmou lexhs sto ekastote eggrafo - setdefault() orismos lexikou kleidiou
                 inverted_index.setdefault(word, 0) #douleuei opws to hashmap , kleidi value
                 #edw mas exei pei pws prepei na ftiaxoume mia synarthsh h opoia afairei ta commata kai ta sumbola.
                 #Giati? Dioti tha mporei na mhn taggarei to text kala logw autwn twn symbolwn. Ara , thelei kai perimenei kati diaforetiko
                 inverted_index[word] +=1
    return inverted_index

def search_inverted_index(inverted_index, word):
   if word in inverted_index:
    return inverted_index[word]
   else:
       return "Word not found in the inverted index"
   
if __name__ == "__main__":
#Orismos tou onomatos tou arxeiou
    file_path = "Python_(programming_language.txt)"
#Dhmioyrgia tou inverted index
    inverted_index = create_inverted_index(file_path)
#Ektypwsh tou inverted index
    print("Inverted Index:")
    for word , count in inverted_index.items():
        print(f"{word}: {count}")
#Anazhthsh lexhs sto inverted index
    search_word = "Python"
    search_result = search_inverted_index(inverted_index, search_word)
    print(f"Occurences of the word '{search_word}': {search_result}")
