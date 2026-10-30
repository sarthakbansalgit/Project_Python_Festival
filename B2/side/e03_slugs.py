                                                                  
                                                               

import unicodedata

word = "Crème brûlée"

                                                    
decomposed = unicodedata.normalize("NFKD", word)
print(len(word), len(decomposed))                                          

                                                                            
plain = decomposed.encode("ascii", "ignore").decode("ascii")
print(plain)                

                                                                   
result = ""
for char in plain.lower():
    if char.isalnum():
        result += char
    elif not result.endswith("-"):
        result += "-"
print(result)                
