from django.db import models

class Author(models.Model):     
    name = models.CharField(max_length=200)
    def __unicode__(self):
        return self.name
        
class Book(models.Model):
    name = models.CharField(max_length=200)
    author = models.ForeignKey(Author)
    year = models.CharField(max_length=200)
    def __unicode__(self):
        return self.name
        
