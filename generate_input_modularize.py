"""
This module is related to the NLP.
It generates the input for morph generator.
Pass the input through morph genetor to collect output.
Collect the Hindi text from the output text
Write the output data into a file.
"""


import sys
import re
import subprocess


from wxconv import WXC


def read_file(file_path):
    """Read data from text file"""

    with open(file_path, 'r') as file:
        data = file.read().splitlines()
    return data


def pre_process(data):
    """Process and Filterize the file data"""

    root_words = data[1]
    index_data = data[2]
    gnp_values = data[4]
    case_data = data[5]
    respect_info = data[7]
    semantic_data = data[3]
    indeclinable_words = (
        '"waWA,Ora,paranwu,kinwu,evaM,waWApi,Bale hI,'
        'wo,agara,magara,awaH,cUMki,cUzki,jisa waraha,'
        'jisa prakAra,lekina,waba,waBI,yA,varanA,anyaWA,'
        'wAki,baSarweM,jabaki,yaxi,varana,paraMwu,kiMwu,'
        'hAlAzki,hAlAMki,va"'
    )
    return (root_words, index_data,
            semantic_data, gnp_values,
            case_data, respect_info,
            indeclinable_words
            )


def process_root_words(words):
    """Put all the root words into a single list"""

    root_words = words.split(",")
    return root_words


def process_index_data(info):
    """Process the index infos"""

    index_data = info.split(",")
    return index_data


def process_semantic_data(words):
    """Put all the semantic data into a single list"""

    semantic_data = words.split(",")
    return semantic_data


def process_gnp_values(words):
    """Put all the gnp values into a single list"""

    gnp_values = words.split(",")
    return gnp_values


def process_case_info(words):
    """Put all the case infos into a single list"""

    case_data = words.split(",")
    return case_data


def process_respect_info(words):
    """Put all the respect infos into a single list"""

    respect_info = words.split(",")
    return respect_info


def process_indeclinable_words(words):
    """Put all the indeclinable words into a single list"""

    indeclinable_words = words.split(",")
    return indeclinable_words


def process_verb_words(words):
    """
    Take the verb word from the root words &
    Filterize it into a proper format"""

    verb_word = []
    if '0' in words:
        words = words.split("_")
        for char in words:
            if char.isalpha():
                verb_word.append(char)
    else:
        res1 = re.sub(r'[^a-zA-Z]', ' ', words).split(" ")
        for char in res1:
            if len(char) >= 1:
                verb_word.append(char)
        verb_word = [verb_word[0]+verb_word[1]] + verb_word[2:]
    return " ".join(verb_word)


def handle_noun(root_words, gnp_value, case_info, seman_data, index_data):
    """Look the data from the root words and gnp values to get noun info"""

    noun_info = []
    adj_info = []
    for word in range(len(root_words[:(len(gnp_value) - 1)])):
        data = gnp_value[word].strip('][').split(' ')
        root_word = (root_words[word].split("_")[0]).strip()
        if len(data) > 1:
            gender = 'm' if data[0].lower(
            ) == 'm' else 'f' if data[0].lower() == 'f' else 'm'
            number = 's' if data[1].lower(
            ) == 'sg' else 'p' if data[1].lower() == 'pl' else 's'
            category = 'n'
            if "k1" in case_info[word]:
                case = "d"
            elif "k2" in case_info[word] and 'anim' in seman_data[word]:
                case = 'o'
            elif "k2" in case_info[word] and 'anim' not in seman_data[word]:
                case = 'd'
            else:
                case = 'o'
            if root_word in ('addressee', 'speaker'):
                pass
            else:
                noun_info.append(
                    (int(index_data[word]),
                     root_word, category,
                     case, gender, number))
        else:
            adj_info.append(
                (int(index_data[word]), root_word, case_info[word]))
    return noun_info, adj_info


def handle_adjective(adj_list, noun_info):
    """ Look the data from the noun infos
        and collect the adjective information"""

    adj_data = []
    if len(adj_list) >= 1 and len(noun_info) >= 1:
        for data in adj_list:
            if len(data[-1]) >= 1:
                index_data = int(data[-1].split(":")[0])
                for noun_data in noun_info:
                    if index_data in noun_data:
                        case, gender, number,  = noun_data[3:]
                        adj_data.append(
                            (data[0], data[1], 'adj', case, gender, number))
            else:
                adj_data.append((data[0], data[1], 'adj', 'o', 'm', 's'))
    return adj_data


def analyze_data(noun_infos, adj_infos):
    """
    Analyze the data from inputs and filterize it.
    After filterization create the input for morph generator."""

    data = noun_infos + adj_infos
    data.sort()
    return data


def generate_input_for_morph_generator(input_data):
    """Process the input and generate the input for morph generator"""

    morph_input_data = []
    for data in input_data:
        morph_data = f'^{data[1]}<cat:{data[2]}><case:{data[3]}><gen:{data[4]}><num:{data[5]}>$'
        morph_input_data.append(morph_data)
    return morph_input_data


def write_data(noun_adj_data, verb_data):
    """Write the Morph Input Data into a file"""

    final_input = " ".join(noun_adj_data) + " " + verb_data
    with open("morph_input.txt", 'w', encoding="utf-8") as file:
        file.write(final_input + "\n")
    return "morph_input.txt"


def run_morph_generator(input_file):
    """ Pass the morph generator through the input file"""

    subprocess.call(f"./run_morph-generator.sh {input_file}", shell=True)
    return "morph_input.txt-out.txt"


def read_output_data(output_file):
    """Check the output file data for post processing"""

    with open(output_file, 'r') as file:
        data = file.read()
    return data


def analyze_output_data(output_data, morph_input, adj_infos):
    """Post process the output data if there is some error"""

    output_data = output_data.split(" ")
    combine_data = list(zip(output_data, morph_input))
    # print("Before Morph Input:",morph_input)
    adj_name_info = []
    if len(adj_infos) >= 1:
        for name in adj_infos:
            adj_name_info.append(name[1])
    for adj_name in adj_name_info:
        for data in combine_data:
            if "#" in data[0] or adj_name in data[0]:
                new_data = data[1][:4] + \
                    tuple(data[1][4].replace('m', 'f'))+data[1][5:]
                morph_input[morph_input.index(data[1])] = new_data
    # print("After Morph Input:", morph_input)
    return morph_input


def collect_hindi_output(output_text):
    """Take the output text and find the hindi text from it."""

    hindi_format = WXC(order="wx2utf", lang="hin")
    generate_hindi_text = hindi_format.convert(output_text)
    return generate_hindi_text


def write_hindi_text(hindi_text, output_file):
    """Append the hindi text into the file"""

    with open(output_file, 'a') as file:
        file.write(hindi_text)
    return "Output data write successfully"


if __name__ == "__main__":
    path = sys.argv[1]
    file_data = read_file(path)
    (root_words_info, index_data_info,
     semantic_data_info, gnp_values_info,
     case_data_info, respect_infos,
     indeclinable_words_info) = pre_process(file_data)
    root_info = process_root_words(root_words_info)
    index_info = process_index_data(index_data_info)
    semantic_info = process_semantic_data(semantic_data_info)
    gnp_info = process_gnp_values(gnp_values_info)
    case_infos = process_case_info(case_data_info)
    respect_data = process_respect_info(respect_infos)
    indeclinable_words_info = process_indeclinable_words(
        indeclinable_words_info
    )
    VERB_INFO = process_verb_words(root_info[-1])
    noun_info_list, adj_data_list = handle_noun(
        root_info[0:-1], gnp_info, case_infos, semantic_info, index_info)
    adj_info_data = handle_adjective(adj_data_list, noun_info_list)
    generate_input_data = analyze_data(noun_info_list, adj_info_data)
    morph_input_info = generate_input_for_morph_generator(generate_input_data)
    MORPH_INPUT_FILE = write_data(morph_input_info, VERB_INFO)
    OUTPUT_DATA = run_morph_generator(MORPH_INPUT_FILE)
    read_output = read_output_data(OUTPUT_DATA)
    analyze_output = analyze_output_data(
        read_output, generate_input_data, adj_data_list)
    generate_post_process_input = generate_input_for_morph_generator(
        analyze_output)
    WRITE_POST_OUTPUT = write_data(generate_post_process_input, VERB_INFO)
    POST_PROCESS_OUTPUT = run_morph_generator(WRITE_POST_OUTPUT)
    read_post_output = read_output_data(POST_PROCESS_OUTPUT)
    hindi_text_info = collect_hindi_output(read_post_output)
    WRITE_HINDI_OUTPUT = write_hindi_text(hindi_text_info, POST_PROCESS_OUTPUT)
    print(WRITE_HINDI_OUTPUT)
