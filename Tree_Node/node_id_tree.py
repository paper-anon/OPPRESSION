import itertools
import pathlib
import pickle
from itertools import islice

import networkx as nx
import numpy as np

import glob


def byte_length(i):
    return (i.bit_length() + 7) // 8


def get_node_from_sentence(tree, start, target):
    """
        This Function searches the entire tree for a sentence and prints out the node ID of the last word.
        If only parts of the string are found it returns a negative value corresponding to the last found word.
        :param tree: Tree in wich to search
        :param start: Should be 0 when called, used for recursion
        :param target: Sentence to be found
    """
    if len(target) == 0:
        return start, 0
    children = {tree.nodes.get(i)["source"]: i for i in tree.neighbors(start)}
    currtar = target[0]

    if currtar in children:
        target.pop(0)
        return get_node_from_sentence(tree, children[currtar], target)
    else:
        return start, len(target)


def compress(tree, target, spelling=True):
    target = target.copy()
    res = []
    maxnode = list(tree.nodes())[-1]
    # pbar = tqdm(total=len(target),leave=False,desc="Compressing")
    last_len = len(target)
    while target:
        node = get_node_from_sentence(tree, 0, target)[0]
        if node == 0:
            if spelling:
                spelling = spell_word(target[0], maxnode)
                res.extend(spelling)
            else:
                res.append(0)
            target.pop(0)
        else:
            res.append(node)
        # pbar.update(last_len-len(target))
        last_len = len(target)
    # pbar.close()
    return res


def recover_sentence(graph, node):
    recovered = []
    prefix = ""
    v = node
    maxnode = list(graph.nodes())[-1]

    while v != 0:
        prefix = str(graph.nodes[v]["source"]) + ' ' + prefix
        v = next(graph.predecessors(v))  # only one predecessor
    return prefix


def recover_sentence_length(graph, node):
    recovered = []
    prefix = []
    v = node
    maxnode = list(graph.nodes())[-1]

    while v != 0:
        prefix += [str(graph.nodes[v]["source"])]
        v = next(graph.predecessors(v))  # only one predecessor
    return len(prefix)


def spell_word(word, maxlen):
    return [maxlen + 1, len(word)] + [ord(x) - 96 for x in word.lower()]


def get_sub_lists(x):
    return [x[i:] for i in range(len(x))]


def window(seq, n=10):
    """
    Returns a sliding window (of width n) over data from the iterable
    s -> (s0,s1,...s[n-1]), (s1,s2,...,sn), ...
    """
    assert len(seq) > n, f"{seq}"
    it = iter(seq)

    result = tuple(islice(it, n))
    if len(result) == n:
        yield result
    for elem in it:
        result = result[1:] + (elem,)
        yield result


def write_text(input_text, path, maxsize):
    byte_size = byte_length(maxsize)
    with open(path, "wb") as f:
        input_text_iterator = iter(input_text)
        for w in input_text_iterator:
            if w <= maxsize:
                f.write(w.to_bytes(byte_size, byteorder="little"))
            else:
                length = next(input_text_iterator)
                letters = itertools.islice(input_text_iterator, length)

                # lettersList = list(letters)
                f.write((maxsize + 1).to_bytes(byte_size, byteorder="little"))
                f.write(length.to_bytes(1, byteorder="little"))
                letter_count = 0
                for letter in letters:
                    letter_count += 1
                    if letter > 255:
                        letter = 42
                    f.write(letter.to_bytes(1, byteorder="little"))
                assert letter_count == length


def make_rand_pointer(path, output, maxsize):
    """

    :param path: Input File with null Pointers
    :param output: Output path
    :param maxsize: Max Node ID of the used graph
    :return:
    """
    byte_size = byte_length(maxsize)

    with open(path, "rb") as f:
        with open(output, "wb") as f_out:
            while (byte := f.read(byte_size)):
                node = int.from_bytes(byte, byteorder="little")
                if node == 0:
                    f_out.write(np.random.randint(maxsize).to_bytes(byte_size, byteorder="little"))
                else:
                    f_out.write(node.to_bytes(byte_size, byteorder="little"))


def read_bin(path, graph):
    """
    Decode binary file using a pre generated graph.
    :param path: Path of the binary file containing the encoded data
    :param graph: Graph used to decode
    """
    maxsize = list(graph.nodes())[-1]
    byte_size = byte_length(maxsize)
    result = ""
    with open(path, "rb") as f:
        while byte := f.read(byte_size):
            node = int.from_bytes(byte, byteorder="little")
            if node <= maxsize:
                result += recover_sentence(graph, node)
            else:
                size = int.from_bytes(f.read(1), byteorder="little")
                letters = ""
                for i in range(size):
                    letter = chr(int.from_bytes(f.read(1), byteorder="little") + 96)
                    letters += letter
                result += letters + ' '

    return result


def read_sources(path_glob):
    words = []
    for file in glob.glob(path_glob):
        words += open(file, "r").read().title().split(" ")
    return words


def read_or_create_tree(pickle_folder, name, words, depth, force=False):
    path = f"{pickle_folder}/{name}_{depth}.p"
    if pathlib.Path(path).exists() and not force:
        with open(path, "rb") as f:
            return pickle.load(f)
    else:
        if not words:
            print(name)
        tree = nx.prefix_tree(window(words, depth))
        with open(path, "wb") as f:
            pickle.dump(tree, f)
        return tree
