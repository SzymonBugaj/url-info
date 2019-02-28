from django.shortcuts import render
from .forms import LinkForm
from .models import Report
from django.shortcuts import redirect
from bs4 import BeautifulSoup
from urllib.request import urlopen
import urllib.request
import collections
import re

# Create your views here.

def index(request):
    form = LinkForm()
    return render(request, 'urlinfo/index.html', {'form': form})

def result(request):
    url = request.POST.get('link')

    content = urlopen(url).read()
    soup = BeautifulSoup(content)
    report = Report()

    words = words_in_text(soup)
    page_size = len(content)/1000 + "K"
  
    report.title = soup.title.text
    report.page_size = page_size
    report.word_count = len(words)
    report.meta_tags = set(meta_tags(soup))
    report.unique_words_count = len(set(words))
    report.common_words = most_common(words, report)
    report.keywords = set(keywords_in_text(soup))
    report.keywords_not_in_content = keywords_not_in_content(words, report)
    report.main_link = url
    linki = links(soup)
    report.links = links(soup)

    return render(request, 'urlinfo/result.html', {'Report': report, 'linki' : linki})

def words_in_text(soup):
    words = []
    tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'li', 'ul',] #['div']
    for tag in tags:
        for words_in_tag in soup.find_all(tag):
            paragraph = delete_punctuation(words_in_tag.text)
            words += paragraph.split()
    return words

def meta_tags(soup):
    meta_tags = []
    for tag in soup.find_all('meta'):
        if tag.get('name') != None and tag.get('name') not in meta_tags:
            meta_tags.append(tag.get('name'))
    return meta_tags

def most_common(paragraph, report):
    common_words = collections.Counter(paragraph).most_common(5)
    report.common_words.clear()
    for word in common_words:
        if word[0] not in report.common_words:
            report.common_words.append(word[0])
    return report.common_words

def keywords_in_text(soup):
    keywords = ""
    for tag in soup.find_all('meta'):
        if tag.get('name') == "keywords" or tag.get('name') == "Keywords":
            keywords += tag.get('content')
    keywords_list = set(keywords.split(','))
    return keywords_list

def keywords_not_in_content(words, report):
    report.keywords_not_in_content.clear()
    for keyword in report.keywords:
        if keyword not in words:
            report.keywords_not_in_content.append(keyword)
    return report.keywords_not_in_content

def links(soup):
    links = {}
    for link in soup.find_all('a', attrs={'href': re.compile("")}):
        #links.append(link.get_text())
        links.update({link.get_text() : link.get('href')})
    return links

def delete_punctuation(paragraph):
    paragraph = re.sub(r'[^\w\s]','',paragraph)
    paragraph = paragraph.lower()
    return paragraph