import requests
from bs4 import BeautifulSoup
import re
from fake_useragent import UserAgent

class Detail:
    thing = ""
    informal = ""
    phrase = ""
    chinese = ""
    english = ""

    def __init__(self, a, b, c, d, e):
        self.thing = a
        self.informal = b
        self.phrase = c
        self.chinese = d
        self.english = e
    
    def print_plain(self):
        res = self.thing + " " + self.informal + " " + self.phrase + " " + self.chinese + " " + self.english
        # print(res)
        return res

    def print_markdown(self):
        markdown = ""
        if self.thing != "":
            markdown += "<font color=#cc0000>" + self.thing + "</font>" + " "
        if self.informal != "":
            markdown += "<font color=#cc0000>" + self.informal + "</font>" + " "
        if self.phrase != "":
            markdown += "**" + self.phrase + "**" + "\n"
        # if self.chinese != "":
        #     markdown += self.chinese + " "
        if self.english != "":
            markdown += self.english
        
        return markdown


if __name__ == '__main__':
    output = './output.md'
    with open('./source.txt', 'r') as f:
        words = f.read().splitlines()
    with open(output, 'w') as f:
        pass

    words = [x for x in words if x != '']

    with open(output, 'a') as f:
         print("##", words[0] + "\n", file=f)

    words = words[1:]
    for word in words:
        with open(output, 'a') as f:
            print("[**" + word + "**](#" + word + ")<br>", file=f)

    for word in words:
        url = "https://www.bing.com/dict/search?q={0}&mkt=zh-cn".format(word)
        title = "[{0}]({1})".format(word, url)
        with open(output, 'a') as f:
            print("\n###", title, file=f)

        ua = UserAgent()
        headers = {
            'User-Agent': ua.random
        }
        
        response = requests.get(url, headers=headers)
        soup =  BeautifulSoup(response.text, features="lxml")

        # 没有中英解释的情况，直接使用meta的释义
        if soup.find("div", {"class": "li_pos"}) is None:
            content = soup.find(attrs={"name":"description"})['content']
            description = content.split("]，")
            description = description[-1]
            count = 1
            for desc in description.split('； '):
                if desc == "":
                    continue
                with open(output, 'a') as f:
                    print(str(count) + ".", desc, file=f)
                count += 1
        else:
            # 单词按照词性的划分
            for part in soup.find_all("div", {"class": "li_pos"}):
                part_of_speech = part.find("div", {"class": "pos"})
                with open(output, 'a') as f:
                    print("\n**" + part_of_speech.string + "**\n", file=f)
                # 每种词性下，有不同的解释
                count = 1
                for segment in part.find_all("div", {"class": "de_co"}):
                    # 每一条解释的detail
                    b = segment.find_all("span", {"class": "gra b_regtxt"})
                    sum_b = ""
                    for item in b:
                        sum_b += item.string
                    c = segment.find("span", {"class": "infor b_regtxt"})
                    c = "" if c is None else c.string
                    d = segment.find("span", {"class": "comple b_regtxt"})
                    d = "" if d is None else d.string

                    e = segment.find_all("span", {"class": "bil b_primtxt"})
                    sum_e = ""
                    for item in e:
                        sum_e += item.string

                    # f = segment.find_all("span", {"class": "val b_regtxt"})
                    f = segment.find("div", {"class": "def_pa"}).find_all("span")
                    sum_f = ""
                    for item in f:
                        if 'val' in item['class'] and sum_f[-1] != " ":
                            sum_f += " "
                        sum_f += str(item.get_text())
                        
                    det = Detail(sum_b, c, d, sum_e, sum_f)
                    with open(output, 'a') as f:
                        print(str(count) + ".", det.print_markdown(), file=f)
                    count += 1
    print("done")