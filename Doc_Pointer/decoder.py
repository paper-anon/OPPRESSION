import os
import sys
import networkx as nx
from networkx.classes.filters import *
from bitstring import BitArray



global oppression_type
global savefile
global sources


def save_words(count,doc,pos):
    for source in sources:
        curr = source.split(';')
        list= []
        if int(curr[1][:-1])== int(doc,2):
            with open(curr[0],'r') as file:
                list = file.read().split(" ")

            int_pos=int(pos,2)
            int_count=int(count,2)
#            print(int(doc,2))
#            print(int_pos)
#            print(int_count)
            words = list[int_pos:int_pos+int_count]
            #print(words)
            #print(list)
            for word in words:
                open(savefile,'a').write(word + " ")
            break
    return



def decode_word(bstring):
    #print(bstring)
    n = int(bstring, 2)
    hexstring = '%x' % n
    #print(hexstring)
    word=bytes.fromhex(hexstring).decode("UTF-8",errors='ignore')

    open(savefile, 'a').write(word + " ")
    
    return



def decode(bstring):
    ## length of the word counter
    len_count= 4
    if oppression_type == 'book':
        len_doc=4
    elif oppression_type == 'twitter':
        len_doc=15
    elif oppression_type == 'general':
        #len_doc=12
        len_doc=18
    elif oppression_type == 'standard':
        len_doc=5
    else:
        print("Coding Type must be either book, twitter, general or standard")
        exit(99)


    count = bstring[0:len_count]
    doc = bstring[0+len_count:len_count+len_doc]
    pos = bstring[0+len_count+len_doc:bstring.__len__()]


    save_words(count, doc, pos)
    return


def to_bytes(string):
    bstring= BitArray('0b' + string[:-1]).tobytes()
    return bstring

def create_bitstring(doc_idx,word_idx,word_count):
    if oppression_type == 'book':
        count_bin='{0:04b}'.format(word_count)
        doc_bin='{0:03b}'.format(doc_idx)
        word_bin='{0:017b}'.format(word_idx)

    elif oppression_type == 'twitter':
        count_bin='{0:04b}'.format(word_count)
        doc_bin='{0:015b}'.format(doc_idx)
        word_bin='{0:05b}'.format(word_idx)

    elif oppression_type == 'general':
        count_bin='{0:04b}'.format(word_count)
        #doc_bin='{0:012b}'.format(doc_idx)
        doc_bin='{0:018b}'.format(doc_idx)
        #word_bin='{0:16b}'.format(word_idx)
        word_bin='{0:18b}'.format(word_idx)

    elif oppression_type == 'standard':
        count_bin='{0:04b}'.format(word_count)
        doc_bin='{0:05b}'.format(doc_idx)
        word_bin='{0:015b}'.format(word_idx)


    oppressed_string= count_bin+ doc_bin + word_bin +'\n'
    return oppressed_string

def not_found(word):
    ## up to 8 words possible
    ## if no word is found set counter to 15, to signal following word-string
    word_len= '{0:04b}'.format(len(word))
    preamble="1111" + word_len
    bin_string= ''
    for char in word:
        bin_string = bin_string + '{0:08b}'.format(ord(char))
    wordcode = preamble + bin_string + '\n'
    return wordcode

file_to_decode = sys.argv[1]
source_list =sys.argv[2]
oppression_type =sys.argv[3]


##default length of one encoded pointer is three, in general coding-type is four bytes
coding_len=3
if oppression_type == 'general':
    coding_len= 5
##length of one byte
bitlen = 8

sources = open(source_list,'r').readlines()

savefile= file_to_decode + ".decoded"


text_to_decode = open(file_to_decode, 'rb').read()

doc_idx = 0
word_idx = 0
word_count = 0

bytestring = ''

for single_byte in text_to_decode:
    bytestring= bytestring + '{0:08b}'.format(single_byte)

curr_pointer = 0
prev_pointer = 0

maxlen = len(bytestring)# / bitlen
#print(len(bytestring))
#print(maxlen)



while curr_pointer < maxlen:
#while True:
    #print(curr_pointer)
    firstbyte = bytestring[curr_pointer:curr_pointer+bitlen]
    #print(firstbyte)
    if firstbyte.startswith('1111'):
        #print(firstbyte[4:])
        length=int(firstbyte[4:],2)+1
        #print(length)
        prev_pointer=curr_pointer
        curr_pointer= curr_pointer+(bitlen*length)
        byte=bytestring[prev_pointer+bitlen:curr_pointer]
    #    print(byte)
        decode_word(byte)

    else:
        prev_pointer = curr_pointer
        curr_pointer = curr_pointer + (bitlen * coding_len)
        byte = bytestring[prev_pointer:curr_pointer]
    #    print(byte)
        decode(byte)






