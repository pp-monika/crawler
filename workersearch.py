'''
Report the list of all subdomains with high textual contents
'''

import re


subdomains_dict = {}

if __name__ == "__main__":
    with open("worker.txt") as f:
        
        for line in f:
            tokens = line.split()

            for token in tokens:
                if "uci.edu" in token and "styx" not in token:
                    if "http:" in token:
                        token = token.replace("http:", '')
                    if "https:" in token:
                        token = token.replace("https:", '')
                    token = token.split("/")[2]
                    if "www" in token:
                        token = token[4:]
                        index = token.find(".edu")
                    if index != len(token)-4:
                        token = token.replace(token[index+4:], '')

                    
                    # Count the frequency of subdomains for popularity ranking
                    if token not in subdomains_dict:
                        subdomains_dict.update({token : 1})
                    else:
                        count = subdomains_dict.get(token) + 1
                        subdomains_dict.update({token : count})
                    
    f.close()
    
    
    # Rank the subdomains under UCI ICS department by frequency
    dict_items = subdomains_dict.items()
    sorted_dict = sorted(dict_items)
    for k,v in sorted_dict:
        print(k, v)
    