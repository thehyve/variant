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
        
class Study(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('U', 'Unknown'),
    )
    study_id = models.CharField(max_length=50)
    pubmedId = models.IntegerField(max_length=9)
    year_of_publication = models.CharField(max_length=4)
    authors = models.CharField(max_length=200)
    micronutrient = models.CharField(max_length=200)
    population = models.CharField(max_length=200)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    endpoint = models.CharField(max_length=200)
    paper_title = models.CharField(max_length=200)
    journal_title = models.CharField(max_length=200)
    study_type = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.study_id