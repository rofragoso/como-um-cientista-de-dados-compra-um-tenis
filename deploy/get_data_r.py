import requests as rq
import bs4 as bs4
import re
import time


def download_search_page(page):
    url ="https://runrepeat.com/catalog/running-shoes?page={page}"
    urll = url.format(page=page)
#     print(urll)
    response = rq.get(urll)
    
    return response.text
   
    return response.text

def parse_search_page(page_html):
    parsed = bs4.BeautifulSoup(page_html, 'html.parser')

    tags = parsed.findAll("a")
    
    video_list = []
    
    for e in tags:
        if e.has_attr("data-v-45baff66") and e.find("span", itemprop="name") != None:
            link = e['href']
            tenis= e.find("span", itemprop="name").get_text()
            data = {"link": link, "name": tenis}
            video_list.append(data)
    
    seen = set()
    video_list_no_dup = []
    for d in video_list:
        t = tuple(d.items())
        if t not in seen:
            seen.add(t)
            video_list_no_dup.append(d)
    
    return video_list_no_dup

def download_shoes_page(link):
    url = "https://runrepeat.com{link}"
    urll = url.format(link=link)
    response = rq.get(urll)
    
    return response.text

def download_shoes_page_api(link):
    url = "https://runrepeat.com{link}"
    urll = url.format(link=link)
    response = rq.get(urll)
    
    return response.text


def parse_shoes_page(page_html):
    
    parsed = bs4.BeautifulSoup(page_html, 'html.parser')

    class_image= parsed.find_all('img')
    class_value = parsed.find_all(attrs={"class":re.compile(r"-value")})
    class_fact = parsed.find_all(attrs={"class":re.compile(r"-fact")})
    class_ranktext= parsed.find_all(attrs={"class":re.compile(r"rank-text")})
    class_expertreview = parsed.find_all(attrs={"class":re.compile(r"rr-reviews-score-average")})
    class_reasons=parsed.find_all(attrs={"class":re.compile(r"gb-w-title")})
    class_good=parsed.find_all(attrs={"id":"the_good"})
    class_bad=parsed.find_all(attrs={"id":"the_bad"})

    data = dict()

    for e in class_image:
        if e.has_attr('src'):
            colname = 'image'
            data[colname] = e['src']
        break

    for e in class_value:
        colname = "_".join(e['class'])
        data[colname] = e.text.strip()

    for e in class_fact:
        if e.text.strip() != None:
            colname =  e.text.strip()
            if e.find("span",{"class":re.compile(r"rating-fact-bar-value-(\d+)")}) != None:
                data[colname] = e.find("span",{"class":re.compile("rating-fact-bar-value-*")})['class'][1]


    for e in class_fact:
        if e.find("span",{"class":"label-rating-fact"}) != None:
            colname =  e.find("span",{"class":"label-rating-fact"}).text.strip()
            if e.find("span",{"class":"rating-value"}) != None:
                data[colname] = e.find("span",{"class":"rating-value"}).text.strip()

    for e in class_ranktext:
        colname = e.text.replace('\n','').replace('           ',' ').strip()
        data[colname] = 1

    for e in class_expertreview:
        colname = "_".join(e['class'])
        data[colname] = e.text.strip()

    for e in class_reasons:
        if re.compile(r'(\d+)').match(e.text.replace('\n','')) != None:
            colname = "_".join(re.compile('[a-z]+').findall(e.text.replace('\n','')))
            data[colname] = re.compile(r'(\d+)').match(e.text.replace('\n','')).group()

    write=""
    for e in class_good:
        if e.find_all("li") != None:
            texts=e.find_all("li")
            for textss in texts:
                write= write + " " + textss.text.strip()         
            colname = "good_reasons_to_buy"
            data[colname] = write

    write=""
    for e in class_bad:
        if e.find_all("li") != None:
            texts=e.find_all("li")
            for textss in texts:
                write= write + " " + textss.text.strip()         
            colname = "bad_reasons_to_buy"
            data[colname] = write  


    return data