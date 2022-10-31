import sys
import re
import urllib.parse
import os
from functools import reduce
from datetime import date

# dir includes wiki raw data
PUKIWIKI_DATA_DIR = "/home/www/inside-cgi/wiki/wiki"

PUKIWIKI_URL_MATCHER = re.compile(
    "https?://inside\.kmc\.gr\.jp/wiki/\?([^>\s]*)")


# return wiki data iter
def get_wiki_datas(text):
    datas = []
    # regex
    for match in PUKIWIKI_URL_MATCHER.finditer(text):
        url = match.group(0)
        decoded_title = urllib.parse.unquote(match.group(1))
        body = _get_wiki_data_or_None(decoded_title)
        if body:
            datas.append({
                "title_link": url,
                "text": "".join(body.splitlines(True)[:100])[:1000],
                "title": decoded_title
            })
    return datas


def _get_wiki_data_or_None(title_str):
    f = _get_wiki_file_or_None(title_str)
    if f:
        read = f.read()
        f.close()
        return read
    else :
        return None

def _get_wiki_file_or_None(title_str,mode = "r"):
    # utf-8 encode -> to-hex
    #
    # e.g. "練習会" -> utf-8: \xE7\xB7\xB4\xE7\xBF\x92\xE4\xBC\x9A
    #               -> pukiwiki: E7B7B4E7BF92E4BC9A.txt
    text_filename = reduce(
        lambda x, y: x + "{0:X}".format(y), title_str.encode("utf-8"), "") + ".txt"
    text_file_path = os.path.join(PUKIWIKI_DATA_DIR, text_filename)
    try:
        f = open(text_file_path,mode, encoding="utf-8")
        return f
    except Exception as e:
        return None

def append_reikai_log(text):
    text = text.replace("～","〜")
    ignorelist =  [
        "例会","例会開始","例会ログ","予定確認",
        "日程確認","例会おわり","例会終わり",
        "例会終了","例会講座", "終わり"
    ]
    if text in ignorelist:
        return
    f = _get_wiki_file_or_None("例会ログ","r+")
    read = f.read()
    now = date.today()
    nowstr = "* {0}/{1}/{2}".format(now.year,now.month,now.day)
    if nowstr not in read :
        refstr = " [#log{0}-{1}-{2}]".format(now.year,now.month,now.day)
        f.write("\n" + nowstr + refstr + "\n")
    text = format_url_for_log(text)
    f.write("- " + text.replace("\n","\n- ") + "\n")
    f.close()

def format_url_for_log(text):
    # https://inside.kmc.gr.jp/wiki/?%E9%83%A8%E5%AE%A4%2F%E8%B3%BC%E5%85%A5%E6%8F%90%E6%A1%88
    "<(https?://.*)> を$1 にして、PUKIWIKI_URL_MATCHERを掛ける"
    def replacer(matchobj):
        matched = matchobj.group(0)
        matched = matched[1:-1]
        for match in PUKIWIKI_URL_MATCHER.finditer(matched):
            parsed = urllib.parse.unquote(match.group(1))
            matched = "[[" + parsed + "]]"
        return matched
    text = text.replace("cmd=read&amp;page=","")
    text = text.replace("cmd=read&page=","")
    text = re.sub(r'<https?://.*?>',replacer,text)
    text = re.sub(r'\&word\=\S*?',"",text)
    return text

if __name__ == "__main__":
    # print("TEST WIKI")
    with open(sys.argv[1]) as f :
        s = f.read()
    s = format_url_for_log(s)
    print(s)
    # print(get_wiki_datas(
    #    r'https://inside.kmc.gr.jp/wiki/?%E4%BE%8B%E4%BC%9A%E3%81%AE%E9%83%A8%E5%B1%8B%E3%81%A8%E8%AC%9B%E5%BA%A7'))
    # append_reikai_log("-～ ゆゆ式は神\n")