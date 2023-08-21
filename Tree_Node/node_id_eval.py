import itertools

from node_id_tree import (compress, write_text, make_rand_pointer, read_sources, window, read_or_create_tree)
from tqdm.auto import tqdm
import os
import sys
import multiprocessing as mp
import multiprocessing.pool as mpp
import glob
import pickle
import pandas as pd
import argparse
from pathlib import Path
import networkx as nx


def worker(eval_tree, eval_target, depth, string_target, string_tree, lengths, spell, temp_folder):
    maxnode = list(eval_tree.nodes())[-1]
    

    for length in lengths:
        res = compress(eval_tree,eval_target[:length],spell)
        write_text(res,f"{temp_folder}/target{length}_{depth}_{string_target}_{string_tree}.bin",maxnode)
        make_rand_pointer(f"{temp_folder}/target{length}_{depth}_{string_target}_{string_tree}.bin",f"{temp_folder}/target{length}_{depth}_{string_target}_{string_tree}.bin.rand",maxnode)

        with open(f"{temp_folder}/target{length}_{depth}_{string_target}_{string_tree}.txt","w") as f:
            for w in eval_target[:length]:
                f.write(f"{w} ")
    
    # GZIP
    os.system(f"gzip -fk -9 -n {temp_folder}/*_{depth}_{string_target}_{string_tree}.txt")
    os.system(f"gzip -fk -9 -n {temp_folder}/*_{depth}_{string_target}_{string_tree}.bin")
    os.system(f"gzip -fk -9 -n {temp_folder}/*_{depth}_{string_target}_{string_tree}.bin.rand")

    res = {}
    for length in lengths:
        res[f"{length}"]={"Txt": Path(f"{temp_folder}/target{length}_{depth}_{string_target}_{string_tree}.txt").stat().st_size}

    for length in lengths:
        res[f"{length}"]["Opp"]=Path(f"{temp_folder}/target{length}_{depth}_{string_target}_{string_tree}.bin").stat().st_size

    for length in lengths:
        res[f"{length}"]["TxTGZ"]=Path(f"{temp_folder}/target{length}_{depth}_{string_target}_{string_tree}.txt.gz").stat().st_size

    for length in lengths:
        res[f"{length}"]["OppGZ"]=Path(f"{temp_folder}/target{length}_{depth}_{string_target}_{string_tree}.bin.gz").stat().st_size
    
    for length in lengths:
        res[f"{length}"]["OppRandGZ"]=Path(f"{temp_folder}/target{length}_{depth}_{string_target}_{string_tree}.bin.rand.gz").stat().st_size

    df = pd.DataFrame(res).T
    df["OppRatio"] = df["Opp"]/df["Txt"]
    df["GzRatio"] = df["TxTGZ"]/df["Txt"]
    df["OppGzRatio"] = df["OppGZ"]/df["Txt"]
    df["OppRandGzRatio"] = df["OppRandGZ"]/df["Txt"]

    return {"tree":string_tree,"target":string_target,"OppRatio":dict(df["OppRatio"]),"GzRatio":dict(df["GzRatio"]),"OppGzRatio":dict(df["OppGzRatio"]),"OppRandGzRatio":dict(df["OppRandGzRatio"])}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        prog = 'Node Tree Eval Script',
                        description = 'What the program does T.B.D',
                        epilog = 'Text at the bottom of help T.B.D.')
    parser.add_argument('depth', type=int, default=2)           # positional argument
    parser.add_argument('--spell', action="store_true")      # option that takes a value
    parser.add_argument('--force', action="store_true")      # option that takes a value
    parser.add_argument('--long', action="store_true")      # option that takes a value
    parser.add_argument('--keep', action="store_true")
    parser.add_argument("-j", default=1,type=int)
    parser.add_argument("--temp", default="temp", type=str)
    parser.add_argument("--res", default="results", type=str)
    parser.add_argument("--pickle", default="pickle", type=str)
    parser.add_argument("--texts", default="../texts", type=str)
    parser.add_argument("--test", action="store_true")


    args = parser.parse_args()

    depth = args.depth
    spell = args.spell
    force_calc = args.force
    keep = args.keep
    temp_folder = args.temp
    res_folder = args.res
    pickle_folder = args.pickle
    texts_folder = args.texts

    Path(temp_folder).mkdir(parents=True, exist_ok=True)
    Path(res_folder).mkdir(parents=True, exist_ok=True)
    Path(pickle_folder).mkdir(parents=True, exist_ok=True)

    if args.long and args.test:
        print("--long and --test incompatible")
        sys.exit(1)

    if args.j < 1:
        processes = mp.cpu_count()
    else:
        processes = args.j

    if args.long:
        lengths = [100000]
    else:
        lengths = [100,200,300,400,500,1000]
    
    if args.test:
        lengths = [100, 200]
        
        processes = mp.cpu_count()

    source_dict = {
        "PandP": (f"{texts_folder}/sanitized/books/san_pride_and_prejudice.txt", 0), 
        "grimm": (f"{texts_folder}/sanitized/books/san_grimms_fairy_tales.txt", 0), 
        "holmes": (f"{texts_folder}/sanitized/books/san_the_adventures_of_sherlock_holmes.txt", 0), 
        "bbc": (f"{texts_folder}/sanitized/newspapers/bbc/*", 0),
        "reuters": (f"{texts_folder}/sanitized/newspapers/reuters/*", 0),
        "wiki_cities": (f"{texts_folder}/sanitized/wikipedia/cities/*", 0),
        "wiki_history": (f"{texts_folder}/sanitized/wikipedia/history/*", 0),
        "wiki_science": (f"{texts_folder}/sanitized/wikipedia/science/*", 0),
        "wiki_sports": (f"{texts_folder}/sanitized/wikipedia/sports/*", 0),
        "twitter_defcon": (f"{texts_folder}/sanitized/twitter/defcon/*", 0),
        "twitter_gates": (f"{texts_folder}/sanitized/twitter/gates/*", 0),
        "twitter_huckabee": (f"{texts_folder}/sanitized/twitter/huckabee/*", 0),
        "twitter_musk": (f"{texts_folder}/sanitized/twitter/musk/*", 0),
        "twitter_rice": (f"{texts_folder}/sanitized/twitter/rice/*", 0),
        "twitter_twitter": (f"{texts_folder}/sanitized/twitter/twitter/*", 0),
    }

    target_dict = {
        "book_target": (f"{texts_folder}/to_submit/sanitized/book-dracula", 0), 
        "bbc_target": (f"{texts_folder}/to_submit/sanitized/newspapers-reuters", 0),
        "reuters_target": (f"{texts_folder}/to_submit/sanitized/newspapers-reuters", 0),
        "wiki_cities_target": (f"{texts_folder}/to_submit/sanitized/wikipedia-cities", 0),
        "wiki_history_target": (f"{texts_folder}/to_submit/sanitized/wikipedia-history", 0),
        "wiki_science_target": (f"{texts_folder}/to_submit/sanitized/wikipedia-science", 0),
        "wiki_sports_target": (f"{texts_folder}/to_submit/sanitized/wikipedia-sports", 0),
        "twitter_target": (f"{texts_folder}/to_submit/sanitized/twitter-ellenshow", 0)
    }

    combi_dict = {
        "book_combi": ["PandP", "grimm", "holmes"],
        "news_combi": ["bbc", "reuters"],
        "wiki_combi": ["wiki_cities", "wiki_history", "wiki_science", "wiki_sports"],
        "twitter_combi": ["twitter_defcon", "twitter_gates", "twitter_huckabee", "twitter_musk", "twitter_rice",
                          "twitter_twitter"],
        "complete_combi": source_dict.keys()
    }


    source_data_dict = {}
    for name, (path, offset) in source_dict.items():
        source_data_dict[name] = read_sources(path)[offset:]

    for name, keys in combi_dict.items():
        templist = [source_data_dict[key] for key in keys]
        source_data_dict[name] = list(itertools.chain(*templist))

    target_data_dict = {}
    for name, (path, offset) in target_dict.items():
        target_data_dict[name] = read_sources(path)[offset:]

    for name, words in source_data_dict.items():
        source_data_dict[name] = read_or_create_tree(pickle_folder, name, words, depth, force_calc)


    worker_args = []
    for string_tree, eval_tree in source_data_dict.items():
        for string_target, eval_target in target_data_dict.items():
            worker_args.append((eval_tree,eval_target,depth,string_target,string_tree,lengths,spell,temp_folder))

    print("Opening Pool")
    with mp.get_context('spawn').Pool(processes) as pool:
        print("Starting Workers.")
        results = pool.starmap(worker, worker_args)
        print("Stopping Workers.")

    df_results = pd.DataFrame(results)
    if spell:
        if args.long:
            df_results.to_pickle(f"{res_folder}/Crossref_spelling_{depth}_long.p")
        else:
            df_results.to_pickle(f"{res_folder}/Crossref_spelling_{depth}.p")

    else:
        if args.long:
            df_results.to_pickle(f"{res_folder}/Crossref_{depth}_long.p")
        else:
            df_results.to_pickle(f"{res_folder}/Crossref_{depth}.p")

    if not keep:
        os.system(f"rm {temp_folder}/*_{depth}_*.txt")
        os.system(f"rm {temp_folder}/*_{depth}_*.txt.gz")
        os.system(f"rm {temp_folder}/*_{depth}_*.bin")
        os.system(f"rm {temp_folder}/*_{depth}_*.bin.gz")
        os.system(f"rm {temp_folder}/*_{depth}_*.bin.rand")
        os.system(f"rm {temp_folder}/*_{depth}_*.bin.rand.gz")