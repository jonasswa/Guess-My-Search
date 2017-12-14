import re
import requests

def getAutoComplete(search_input):
    '''
    This function gets a search string, and asks google what suggestions
    this search could autocomplete to. Uses regex to parse xml result to list.

    :param search_input: String of search

    :return: List of suggestions
    '''

    url = "http://suggestqueries.google.com/complete/search?output=toolbar&q="
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
    
    return result

if __name__ == "__main__":
    print(getAutoComplete('kan man bruke '))
