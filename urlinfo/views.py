from django.shortcuts import render
from .forms import LinkForm
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

    report.title = soup.title.text
    report.words = report.words_in_text(soup)
    report.word_count = len(report.words)
    report.meta_tags = report.find_meta_tags(soup)
    report.unique_words_count = len(set(report.words))
    report.page_size = f"{len(content)/1000} K"
    report.common_words = report.most_common_words()
    report.keywords = report.keywords_in_text(soup)
    report.keywords_not_in_content = report.find_keywords_not_in_text(soup)
    report.main_link = url
    report.links = report.find_links(soup, url)

    return render(request, 'urlinfo/result.html', {'Report': report})

class Report():
    main_link = ""
    title = ""
    meta_tags = []
    words = []
    page_size = ""
    word_count = 0
    unique_words_count = 0
    common_words = []
    keywords_not_in_text = []
    keywords_list = []
    links = []
    page_size = ""
    
    def words_in_text(self, soup):
        self.words = soup.body.text.split()
        self.words = self.delete_punctuation_and_nums(self.words)
        return self.words

    def find_meta_tags(self, soup):
        for tag in soup.find_all('meta'):
            if tag.get('name') != None and tag.get('name') not in self.meta_tags:
                self.meta_tags.append(tag.get('name'))
        self.meta_tags = set(self.meta_tags)
        return self.meta_tags

    def most_common_words(self):
        common_words = collections.Counter(self.words).most_common(6)
        self.common_words.clear()
        for word in common_words:
            if word not in self.common_words and len(word[0]) > 0 and len(self.common_words) < 5:
                self.common_words.append(word[0])
        self.common_words = self.common_words
        return self.common_words

    def keywords_in_text(self, soup):
        keyword = ""
        for tag in soup.find_all('meta'):
            if tag.get('name') == "keywords" or tag.get('name') == "Keywords":
                self.keywords_list = tag.get('content').replace(' ', '').split(',')
        #self.keywords_list = set(self.keywords_list.split(','))
        return self.keywords_list

    def find_keywords_not_in_text(self, soup):
        self.keywords_not_in_text.clear()
        for keyword in self.keywords_list:
            if keyword not in soup.body.text and keyword not in self.keywords_not_in_text:
                self.keywords_not_in_text.append(keyword)
        return self.keywords_not_in_text

    def find_links(self, soup, url):
        self.links.clear()
        for link in soup.findAll('a'):
            url2 = link.get('href')
            #if urllib.parse.urljoin(self.main_link, url2) not in self.links:
            self.links.append(urllib.parse.urljoin(self.main_link, url2))
        return self.links

    def delete_punctuation_and_nums(self, soup):
        words_without_punct_and_nums = []
        for word in range(len(self.words)):
            self.words[word] = re.sub(r'[^\w\s]','',self.words[word])
            self.words[word] = self.words[word].lower()
            try:
                float(self.words[word])
            except:
                words_without_punct_and_nums.append(self.words[word])
        return words_without_punct_and_nums