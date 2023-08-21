import os
import random
import sys
from os.path import exists
import networkx as nx
from networkx.classes.filters import *
from progress.bar import Bar


## set globals
global doc_idx
global text_to_analyze
global maxdepth
global id_seperator
id_seperator = '_'



def initiate_tree(index):
    begin_position = index
    tree = nx.DiGraph()

    tree.add_node(word, word=word, doc=doc_idx, pos=begin_position)

    prev_word = word
    curr_depth= 0
    while curr_depth < maxdepth:
        curr_depth += 1

        #print(len(text_to_analyze))
        #print(curr_depth)

        curr_word = text_to_analyze[index + curr_depth]
        word_id=curr_word
        if wordId_exists(tree,curr_word):
            word_id=get_next_word_id(tree,curr_word)
        tree.add_node(word_id, word=curr_word, doc=doc_idx, pos=begin_position)
        tree.add_edge(prev_word, word_id)
        prev_word = word_id
    return tree


def update_tree(tree, index):
    curr_depth = 1
    word_idx = index + curr_depth
    parent = text_to_analyze[index]

    while curr_depth < maxdepth:

        child = text_to_analyze[word_idx]
        existing_child= check_child_nodes(tree,parent,child)
        if existing_child:
            child_id= get_child_node(tree,parent,child)
            parent = child_id
            continue
        else:
            curr_word= child
            if wordId_exists(tree,child):
                child_id = get_next_word_id(tree, child)
            else:
                child_id = child
            tree.add_node(child_id, word=curr_word,doc= doc_idx, pos=index)
            #tree.add_node(child_id, word=child_id.split(id_seperator)[0],doc= doc_idx, pos=index)
            tree.add_edge(parent, child_id)
            parent=child_id
        curr_depth +=1
        word_idx = index + curr_depth
    return tree


def wordId_exists(tree, word_id):
    return tree.has_node(word_id)

def get_child_node(tree, parrent_node, word):
    for neighbor in tree.neighbors(parrent_node):
        neighbor_word= neighbor.split(id_seperator)[0]
        if neighbor_word == word:
            return neighbor
    print("Child not found exception")
    exit(1)

def get_next_word_id(tree, word):
    id_exists=True
    id_count=1
    curr_word_id=word + id_seperator + str(id_count)
    while id_exists:
        if tree.has_node(curr_word_id):
            id_count += 1
            curr_word_id = word + id_seperator + str(id_count)
        else:
            id_exists=False
    return curr_word_id


def check_child_nodes(tree, parrent_node, word):
    #print(parrent_node)
    #print(word)
    for neighbor in tree.neighbors(parrent_node):
        neighbor_word= neighbor.split(id_seperator)[0]
        if neighbor_word == word:
            return True
    return False


maxdepth=int(sys.argv[1])
save_maxdepth=maxdepth
if maxdepth < 1:
    print("Maxdepth has to be at least 1")
    exit(1)

file_to_analyze = sys.argv[2]
list_of_files=[]
if file_to_analyze.endswith('/'):
    for curr in os.listdir(file_to_analyze):
        list_of_files.append(file_to_analyze + curr)
else:
    list_of_files.append(file_to_analyze)
output_dir = sys.argv[3]

if not output_dir.endswith('/'):
    output_dir = output_dir + '/'


for file in list_of_files:
    ##If textindex does not exist, creat a new one
    # doc_idx is 1 for the first document
    if not exists(output_dir+"/textindex.db"):
        doc_idx = 1
        open(output_dir+"/textindex.db",'w').write(file + ";" + str(doc_idx) + '\n')

    ## If document was already analyzed, exit
    elif int(open(output_dir+"/textindex.db",'r').read().find(file)) != -1:
        print(file_to_analyze + " - Text already analyzed")
        print("--Skipping--")
        continue
    ## If doc is new and textindex exists, get last document id and increase by 1
    else:
        doc_idx= int(open(output_dir + "/textindex.db", 'r').readlines()[-1].split(';')[-1]) + 1
        open(output_dir + "/textindex.db", 'a').write(file + ";" + str(doc_idx)  + '\n')



    text_to_analyze = open(file, 'r').read().split(" ")
    with Bar(file,max=len(text_to_analyze),suffix='%(percent)d%%') as bar:
        dirty_maxdepth = False
        for index, word in enumerate(text_to_analyze):
            #print(maxdepth)
            #print(len(text_to_analyze))
            #print(index)
            #print(word)
            bar.next()
            if dirty_maxdepth:
                maxdepth=save_maxdepth
            if (maxdepth == 1) and (index + 1 == len(text_to_analyze)):
                break
            elif maxdepth >= (len(text_to_analyze) - index):
                maxdepth = maxdepth - 1
            elif maxdepth > len(text_to_analyze):
                maxdepth = len(text_to_analyze)
                dirty_maxdepth= True


            savefile=output_dir + word
            if exists(savefile):
                tree = nx.read_gexf(savefile)
                tree = update_tree(tree,index)
            else:
                tree = initiate_tree(index)
            nx.write_gexf(tree, savefile)

        bar.finish()