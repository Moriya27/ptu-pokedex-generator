import datagen
from PyPDF2 import PdfFileMerger
from subprocess import call
import os.path

data = datagen.data
numbers = data.keys()
merger = PdfFileMerger()
command_string = 'xelatex -job-name={0} -output-directory="'+datagen.BASE_PATH+'/pdfs" "'+datagen.BASE_PATH+'/tex/Template_.tex"'
CREATE_NO_WINDOW = 0x08000000
total = 0

def create_pdfs(number_group):
    for number in number_group:
        try:
            datagen.prep_for_tex(number)
            call(command_string.format(number), creationflags=CREATE_NO_WINDOW)
            global total
            total += 1
            if(total % 20 == 0):
                print(str(total) + "/" + str(len(numbers)))
        except Exception:
            print("Failed on creating " + number)
        
    
    

#create_pdfs(numbers)
print("pdf gen done")
for number in numbers:
    try:
        merger.append(datagen.BASE_PATH + "/pdfs/" + number+".pdf")
    except Exception:
        print("Failed on appending " + number)        

if os.path.isfile(datagen.BASE_PATH + "/../dex.pdf"):
    os.remove(datagen.BASE_PATH + "/../dex.pdf")
merger.write(datagen.BASE_PATH + "../dex.pdf")

print("done")
