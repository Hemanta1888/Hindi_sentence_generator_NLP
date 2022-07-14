import doctest
import subprocess
from wxconv import WXC
import sys
import re

def read_file(path):
    """
    Read data from text file
    >>> read_file(path)
    """

    with open(path, 'r') as file:
        data = file.read().splitlines( )
    return data
    
def pre_process(data):
    """Process the file data"""

    new_data = data[1:8]
    gram_data = (new_data[-4]).split(",")
    root_words = new_data[0].split(",")
    case_info =  (new_data[-3]).split(",")
    semantic_info = new_data[2].split(",")
    respect_info = new_data[-1]
    unchanged_word = "waWA,Ora,paranwu,kinwu,evaM,waWApi,Bale hI,wo,agara,magara,awaH,cUMki,cUzki,jisa waraha,jisa prakAra,lekina,waba,waBI,yA,varanA,anyaWA,wAki,baSarweM,jabaki,yaxi,varana,paraMwu,kiMwu,hAlAzki,hAlAMki,va".split(",")
    return root_words,gram_data,case_info,semantic_info,respect_info

def analyze_data(results):
    """
        Analyze the pre_process data to get the result
    """
    root_words = results[0]
    gram_data = results[1]
    case_info = results[2]
    seman_data = results[3]
    res_data = results[4].split(",")
    input_data = []
    verb_data = root_words[-1]
    verb_word = []
    rel_index_num = ''
    index_num = 0
    adj_words = ''
    if '0'  in verb_data:
        verb_data = verb_data.split("_")
        for char in verb_data:
            if char.isalpha():
                verb_word.append(char)
    else:         
        res1 = re.sub(r'[^a-zA-Z]', ' ', verb_data).split(" ")
        for char in res1:
            if len(char) >= 1:
                verb_word.append(char)
        verb_word = [verb_word[0]+verb_word[1]] +verb_word[2:]
    
    for word in range(len(root_words[:(len(gram_data) - 1)])):
        if  'm' in gram_data[word] or '-' in gram_data[word]:
            gen = 'm'
            gra = 'n'
        elif 'f' in gram_data[word]:
            gen = 'f'
            gra = 'n'
            print(case_info[word])
        elif len(gram_data[word]) == 0 and 'mod' in case_info[word]:
            gra = 'adj'
            adj_words += root_words[word]
            rel_index_num += case_info[word][0]
        elif len(gram_data[word]) == 0 and 'ord' in case_info[word]:
            gra = 'adj'
            adj_words += root_words[word]
            rel_index_num += case_info[word][0]
        elif len(gram_data[word]) == 0 and 'card' in case_info[word]:
            gra = 'adj'
            adj_words += root_words[word]
            rel_index_num += case_info[word][0]
        elif len(gram_data[word]) == 0 and 'intf' in case_info[word]:
            gra = 'adj'
            adj_words += root_words[word]
            rel_index_num += case_info[word][0]
        elif len(gram_data[word]) == 0 and 'dem' in case_info[word]:
            gra = 'adj'
            adj_words += root_words[word]
            rel_index_num += case_info[word][0]
        num = "p" if 'pl' in gram_data[word][3:5] else 's'
        if "k1" in case_info[word]:
            case = "d"
        elif "k2" in case_info[word] and 'anim' in seman_data[word]:
            case = 'o'
        elif "k2" in case_info[word] and 'anim' not in seman_data[word]:
            case = 'd'
        else:
            case ='o'
        
        if root_words[word] == 'addressee' and "respect" in res_data[0]:
            analyse_data = f'^Apa<cat:p><case:o><parsarg:0><gen:m><num:{num}><per:{gram_data[word][-2]}>$'
        elif root_words[word] == 'addressee' and len(res_data[0]) == 0:
            analyse_data = f'^wuma<cat:p><case:o><parsarg:0><gen:m><num:{num}><per:{gram_data[word][-2]}>$'
        elif root_words[word] == 'addressee' and "informal" in res_data[0]:
            analyse_data = f'^wU<cat:p><case:o><parsarg:0><gen:m><num:{num}><per:{gram_data[word][-2]}>$'
        elif root_words[word] == 'speaker':
            analyse_data = f'^mEM<cat:p><case:o><parsarg:0><gen:{gen}><num:{num}>$'
        # elif root_words[word] == "koI" or "kuCa" or "kyA" or "kOna" or "kazhA" or "kaba" :
        #     analyse_data = f'^{root_words[word].split("_")[0]}<cat:p><case:o><parsarg:0><gen:{gen}><num:{num}><per:{gram_data[word][-2]}><tam:0>$'
        else:
            analyse_data = f'^{root_words[word].split("_")[0]}<cat:{gra}><case:{case}><gen:{gen}><num:{num}>$'
        input_data.append(analyse_data)
    for data in input_data:
        if 'adj' in data:
            index_num += input_data.index(data)
            adj_data = input_data[int(rel_index_num) - 1]
            input_data[index_num] = f'^{adj_words.split("_")[0]}<cat:adj>'+adj_data[adj_data.index('<case'):]
            return input_data, verb_word
    return input_data, verb_word

def write_file(input_results):
    """
        Write the output data in a file
    """

    input_data = input_results[0]
    verb_words = input_results[1]
    results = " ".join(input_data)
    verb_word = " ".join(verb_words)
    with open("output_data.txt", 'w',encoding="utf8") as file:
            file.write(results+ " " + verb_word +"\n")
    return "Output data write successfully"

if __name__ == "__main__":
    path = sys.argv[1]
    # print(path)
    data_info = read_file(path)
    result = pre_process(data_info)
    data_info = analyze_data(result)
    write_data = write_file(data_info)
    print(write_data)

# calling bash file to collect the output
subprocess.call("./run_morph-generator.sh output_data.txt", shell=True)

# Reading the result from the file
f = open('output_data.txt-out.txt', 'r')
new_input = []
for data in f.read().split(" "):
    if '#' in data:
        with open("output_data.txt", 'r') as file:
            mor_input = file.read().split(" ")
            for input in mor_input:
                if data[1:] in input:
                    new_input.append(input.replace('<gen:m>', '<gen:f>'))
                elif 'nayA' in input:
                    new_input.append(input.replace('<gen:m>', '<gen:f>'))
                else:
                    new_input.append(input)
            with open("output_data.txt", 'w') as file:
                file.write(" ".join(new_input))
            break
                
f.close()
subprocess.call("./run_morph-generator.sh output_data.txt", shell=True)

f = open('output_data.txt-out.txt', 'r')
data = f.read()


# Converting the result into hindi format
con = WXC(order='wx2utf', lang='hin')
hindi_text = con.convert(data)

# # Writing hindi data to the file
f = open('output_data.txt-out.txt', 'a')
f.write(hindi_text)
f.close()









