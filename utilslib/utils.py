import os

def get_google_API_key():
    path_to_txt_key = r'./misc/googleAPI.txt'
    key = ''

    with open(path_to_txt_key) as APIfile:
        for line in APIfile:
            key = line

    return key

def list_to_HTML_table(table, html_class = ""):

    ret = '<table class = "'+html_class+'">\n'

    for row in table:
        ret+='\t<tr>\n'
        for el in row:
            ret+='\t\t<td>'
            ret+=str(el)
            ret+='</td>\n'
        ret+='\t</tr>\n'


    ret += '</table>'

    return ret


if __name__ == "__main__":
    a = [[1,2],[1,2], [1,2], [1,2,3]]
    print(list_to_HTML_table(a))
