import re
import requests
from html import unescape

def parse_From_HTML(string):
    return (unescape(string))

def fix_Search(search, output):
    search = search.lower()
    word = search.split(' ')[-1]

    try:
        indx = search.index(word)
        ret = output[indx:]
        return ret
    except:
        return output

def getAutoComplete(search_input):
    '''
    This function gets a search string, and asks google what suggestions
    this search could autocomplete to. Uses regex to parse xml result to list.

    :param search_input: String of search

    :return: List of suggestions
    '''

    url = "http://suggestqueries.google.com/complete/search?output=toolbar&use_similar=0&q="
    #url += parse.quote(search_input)
    url+= search_input

    data = requests.get(url).text
    pattern = r'suggestion data="(.*?)"/>'
    result = re.findall(pattern, data)

    #Remove if search_string is the same
    for i in range(len(result)):
        if result[i] == search_input:
            del result[i]
            return result

    if len(result)< 1:
        return [None]

    result = [parse_From_HTML(x) for x in result]
    result = [re.sub(search_input.lower(), '', x) for x in result]

    result = [re.sub(r'^ ', '', x) for x in result]

    return result



if __name__ == "__main__":
    print(getAutoComplete("Why can't my cat sit"))
