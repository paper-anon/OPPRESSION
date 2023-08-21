import os
import sys
import networkx as nx
import gzip
from networkx.classes.filters import *
from progress.bar import Bar
from bitstring import BitArray

global oppression_type
global node_mode


def to_bytes(string):
    #print(string)
    bytes= BitArray('0b' + string[:-1]).tobytes()
    return bytes

def create_bitstring(doc_idx,word_idx,word_count):
    count_bin = ""
    doc_bin = ""
    word_bin = ""
    if oppression_type == 'book':
        count_bin='{0:04b}'.format(word_count)
        doc_bin='{0:03b}'.format(doc_idx)
        word_bin='{0:017b}'.format(word_idx)

    elif oppression_type == 'twitter':
        count_bin='{0:04b}'.format(word_count)
        doc_bin='{0:015b}'.format(doc_idx)
        word_bin='{0:05b}'.format(word_idx)

#    elif oppression_type == 'general':
#        count_bin='{0:04b}'.format(word_count)
#        doc_bin='{0:013b}'.format(doc_idx)
#        word_bin='{0:017b}'.format(word_idx)

    elif oppression_type == 'general':
        count_bin='{0:04b}'.format(word_count)
        doc_bin='{0:018b}'.format(doc_idx)
        word_bin='{0:018b}'.format(word_idx)

    elif oppression_type == 'standard':
        count_bin='{0:04b}'.format(word_count)
        doc_bin='{0:05b}'.format(doc_idx)
        word_bin='{0:015b}'.format(word_idx)


    oppressed_string= count_bin+ doc_bin + word_bin +'\n'
    return oppressed_string

def get_nullpointer():
    doc = 0 
    word= 0 
    count = 0
    if oppression_type == 'general':
        count_bin='{0:04b}'.format(count)
        doc_bin='{0:018b}'.format(doc)
        word_bin='{0:18b}'.format(word)
    else:
        count_bin='{0:04b}'.format(count)
        doc_bin='{0:03b}'.format(doc)
        word_bin='{0:017b}'.format(word)

    nullpointer= count_bin+ doc_bin + word_bin +'\n'
    return nullpointer


def not_found(word):
    ## if no word is found set counter to 15 (=depth 16), to signal following word-string
    word_len= '{0:04b}'.format(len(word))
    preamble="1111" + word_len
    bin_string= ''
    for char in word:
        bin_string = bin_string + '{0:08b}'.format(ord(char))
    wordcode = preamble + bin_string
    return wordcode

maxdepth = int(sys.argv[1])
dir_of_files_to_oppress = sys.argv[2]
word_db_rootdir = sys.argv[3]
config = open(sys.argv[4],'r').readlines()
out_dir = sys.argv[5]
steps = [100,200,300,400,500,1000]
#tree_rootdir =sys.argv[3]
#oppression_type =sys.argv[4]
list_of_files_to_oppress=[]
for curr in os.listdir(dir_of_files_to_oppress):
    list_of_files_to_oppress.append(dir_of_files_to_oppress + curr)

if maxdepth > 15:
    print("madepth has to be 15 or lower")
    print("encoding not ensured, exiting")
    exit()

#binary = open(list_of_files_to_oppress[1], 'r').read()
#with gzip.GzipFile(fileobj="testfile.zip", mode="w") as gzip_save:
#    gzip_save.write(binary)
#exit()

if not word_db_rootdir.endswith('/'):
    word_db_rootdir = word_db_rootdir + '/'


for file_to_oppress in list_of_files_to_oppress:
    file = file_to_oppress.split('/')[-1]
    for set_dictionary in config:
        last = False
        set = set_dictionary.split(';')
        set_name = set[0]
        tree_rootdir = word_db_rootdir + set[1]
        oppression_type = set[2]

        if oppression_type.endswith('\n'):
            oppression_type = oppression_type[:-1]

        savefile = out_dir + file + "_" + set_name + '.opp'
        savefile_bin = out_dir + file + "_" + set_name + '.opp.bin'
        savefile_bin_null = out_dir + file + "_" + set_name + '_null.opp.bin'

        savefile_gzip = savefile_bin + ".zip"
        text_to_oppress = open(file_to_oppress, 'r').read().split(" ")

        doc_idx = 0
        word_idx = 0
        word_count = 0
        exists_child = False


        for curr_step in steps:
            curr_text = text_to_oppress[:curr_step]
            curr_savefile = savefile + '_' + str(curr_step)
            curr_savefile_bin = savefile_bin +'_' + str(curr_step)
            curr_savefile_bin_null = savefile_bin_null +'_' + str(curr_step)

            bar_name= file + '_' + set_name + '_' + str(curr_step)

            with Bar(bar_name, max=len(curr_text), suffix='%(percent)d%%') as bar:

                for index, curr_word in enumerate(curr_text):
                    bar.next()
                    word_does_not_exist = False

                    word= curr_word
#                    print(word)
                    try:
                        tree = nx.read_gexf(tree_rootdir + word)
                    except:
                        word_does_not_exist = True


                    if word_does_not_exist:
                        for c in word:
                            print(c)
                        if len(word) < 16:
                            bits = not_found(word)
                            nullbits = get_nullpointer()
                            with open(curr_savefile, 'a') as save:
                                save.write(bits +'\n')
                                save.close()
                            with open(curr_savefile_bin, 'ab') as save:
                                save.write(to_bytes(bits))
                                save.close()
                            with open(curr_savefile_bin_null, 'ab') as save:
                                save.write(to_bytes(nullbits))
                                save.close()
                        else:
                            n = 15
                            chunks = [word[i:i + n] for i in range(0, len(word), n)]
                            print(chunks)
                            for chunk in chunks:
                                bits = not_found(chunk)
                                with open(curr_savefile, 'a') as save:
                                    save.write(bits+ '\n')
                                    save.close()
                                with open(curr_savefile_bin, 'ab') as save:
                                    save.write(to_bytes(bits))
                                    save.close()
                            with open(curr_savefile_bin_null, 'ab') as save:
                                save.write(to_bytes(nullbits))
                                save.close()


                    else:
                        doc_idx = tree.nodes[word]['doc']
                        word_idx = tree.nodes[word]['pos']
                        for neighbor in tree.neighbors(word):

                            word_to_search =tree.nodes[neighbor]['word']
                            try:
                                testcall = text_to_oppress[index + 1]
                            except:
                                last = True
                            if last:
                                pass
                            elif word_to_search == text_to_oppress[index + 1]:
                                exists_child = True
                                doc_idx=tree.nodes[neighbor]['doc']
                                word_idx=tree.nodes[neighbor]['pos']
                                node_to_write=neighbor + '\n'
                                word_count += 1

                                continue
                            else:
                                pass

                    #print(create_bitstring(doc_idx,word_idx,word_count))

                        if not exists_child:

                            bits = create_bitstring(doc_idx,word_idx,word_count)
                            #print(bits)
                            with open(curr_savefile, 'a') as save:
                                save.write(bits)
                                save.close()
                            with open(curr_savefile_bin, 'ab') as save:
                                save.write(to_bytes(bits))
                                save.close()
                            with open(curr_savefile_bin_null, 'ab') as save:
                                save.write(to_bytes(bits))
                                save.close()
                            #print(bits)
#                            print('{0:04b}'.format(word_count)+ '\n')
#                            print('{0:018b}'.format(doc_idx) + '\n')
#                            print('{0:018b}'.format(word_idx) + '\n')
                            doc_idx = 0
                            word_idx = 0
                            word_count = 0

                        elif last:
                            bits = create_bitstring(doc_idx,word_idx,word_count)
                            #print(bits)
                            with open(curr_savefile, 'a') as save:
                                save.write(bits)
                                save.close()
                            with open(curr_savefile_bin, 'ab') as save:
                                save.write(to_bytes(bits))
                                save.close()
                            with open(curr_savefile_bin_null, 'ab') as save:
                                save.write(to_bytes(bits))
                                save.close()
#                            print('{0:04b}'.format(word_count)+ '\n')
#                            print('{0:018b}'.format(doc_idx) + '\n')
#                            print('{0:018b}'.format(word_idx) + '\n')

                            #print(bits)
                            doc_idx = 0
                            word_idx = 0
                            word_count = 0

                        elif exists_child and maxdepth== word_count +1 :

                            bits = create_bitstring(doc_idx,word_idx,word_count)
                            #print(bits)
                            with open(curr_savefile, 'a') as save:
                                save.write(bits)
                                save.close()
                            with open(curr_savefile_bin, 'ab') as save:
                                save.write(to_bytes(bits))
                                save.close()
                            with open(curr_savefile_bin_null, 'ab') as save:
                                save.write(to_bytes(bits))
                                save.close()

                            #print(bits)
#                            print('{0:04b}'.format(word_count)+ '\n')
#                            print('{0:018b}'.format(doc_idx) + '\n')
#                            print('{0:018b}'.format(word_idx) + '\n')

                            doc_idx = 0
                            word_idx = 0
                            word_count = 0
                            exists_child = False

                        else:
                            exists_child= False


            #    except:
            #        print("Ooops")
            #        exit()
#            binary = open(savefile_bin, 'rb').read()
#            with gzip.GzipFile(fileobj=savefile_gzip, mode="w") as gzip_save:
#                gzip_save.write(binary)
                bar.finish()
        set_name = ""
        tree_rootdir = ""
        oppression_type = ""




