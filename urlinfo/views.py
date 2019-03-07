from django.shortcuts import render, redirect
from .forms import LinkForm
from bs4 import BeautifulSoup
from urllib.request import urlopen
import urllib.request
import collections
import re
from django.http import HttpResponseRedirect
from django.views.generic import FormView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.messages import get_messages

# Create your views here.
class UrlView(FormView):
   form_class = LinkForm
   template_name = "urlinfo/index.html"
   success_url = 'result'
   url = None

   def get_success_url(self):
        messages.info(self.request, self.url)
        return reverse_lazy(self.success_url)

   def form_valid(self, form, **kwargs):
        self.url = form.cleaned_data['link']
        return HttpResponseRedirect(self.get_success_url())

class ResultView(TemplateView):
   template_name = "urlinfo/results.html"
   url = None

   def get(self, request, *args, **kwargs):
        storage = get_messages(self.request)
        try:
            self.url = [message for message in storage][0]
        except IndexError:
            return redirect('base')
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

   def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        result_dict = Report(str(self.url))
        #context['report'] = result_dict
        context['report'] = result_dict.__dict__
        return context


class Report:
    def __init__(self, url):
        self.url = url
        self.soup = self.boil_soup()
        self.title = self.soup.title.text
        self.meta_tags = self.find_meta_tags()
        self.words = self.words_in_text()
        self.page_size = f"{len(urlopen(self.url).read())/1000} K"
        self.word_count = len(self.words)
        self.unique_words_count = len(set(self.words))
        self.common_words = self.most_common_words()
        self.keywords_list = self.find_keywords()
        self.keywords_not_in_text = self.find_keywords_not_in_text()
        self.links = self.find_links()

    def boil_soup(self):
        content = urlopen(self.url).read()
        self.soup = BeautifulSoup(content)
        return self.soup

    def words_in_text(self):
        self.words = self.soup.body.get_text().split()
        self.words = self.delete_punctuation_and_nums()
        return self.words

    def find_meta_tags(self):
        meta_tags = []
        for tag in self.soup.find_all('meta'):
            if tag.get('name') != None and tag.get('name') not in meta_tags:
                meta_tags.append(tag.get('name'))
        self.meta_tags = set(meta_tags)
        return self.meta_tags

    def most_common_words(self):
        common_words = collections.Counter(self.words).most_common(6)
        self.common_words = []
        for word in common_words:
            if word not in self.common_words and len(word[0]) > 0 and len(self.common_words) < 5:
                self.common_words.append(word[0])
        return self.common_words

    def find_keywords(self):
        self.keywords_list = []
        for tag in self.soup.find_all('meta'):
            if tag.get('name') == "keywords" or tag.get('name') == "Keywords":
                self.keywords_list = tag.get('content').split(',')
        return self.keywords_list

    def find_keywords_not_in_text(self):
        self.keywords_not_in_text = []
        for keyword in self.keywords_list:
            if keyword not in self.soup.body.text and keyword not in self.keywords_not_in_text:
                self.keywords_not_in_text.append(keyword)
        return self.keywords_not_in_text
    
    def find_links(self):
        self.links = {}
        for link in self.soup.findAll('a'):
            url2 = link.get('href')
            url_name = link.string
            self.links.update({url_name : urllib.parse.urljoin(self.url, url2)})
        return self.links

    def delete_punctuation_and_nums(self):
        words_without_punct_and_nums = []
        for word in range(len(self.words)):
            self.words[word] = re.sub(r'[^\w\s]','',self.words[word])
            self.words[word] = self.words[word].lower()
            try:
                float(self.words[word])
            except:
                words_without_punct_and_nums.append(self.words[word])
        return words_without_punct_and_nums
