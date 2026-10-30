                                                                
                                                                 

import json

with open("B1/side/library.json", encoding="utf-8") as file:
    library = json.load(file)

books = library["books"]

                                                               
total_pages = 0
for book in books:
    print(f"- {book['title']} ({book['pages']} pages)")
    total_pages += book["pages"]
print(f"Total: {total_pages} pages")

                                                      
print("Available:")
for book in books:
    if book["borrowed_by"] == "":
        print(f"- {book['title']}")

                                                         
genres = {}
for book in books:
    genre = book["genre"]
    if genre in genres:
        genres[genre] += 1
    else:
        genres[genre] = 1
print(genres)

                                                                 
thickest = books[0]
for book in books:
    if book["pages"] > thickest["pages"]:
        thickest = book
print(f"Thickest: {thickest['title']}")
