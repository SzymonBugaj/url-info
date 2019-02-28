from django.db import models

# Create your models here.
class Report(models.Model):
    title = ""
    meta_tags = []
    page_size = ""
    word_count = 0
    unique_words_count = 0
    common_words = []
    keywords_not_in_content = []
    keywords = []
    links = []
    main_link = ""