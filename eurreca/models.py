from django.db import models
        
class Study(models.Model):
    GENDER_CHOICES = (
        ('F', 'Female'),
        ('M', 'Male'),
        ('X', 'Mixed'),
        ('U', 'Unknown'),
    )
    study_id = models.CharField(max_length=50)
    pubmed_id = models.IntegerField(max_length=9)
    year_of_publication = models.CharField(max_length=4)
    authors = models.CharField(max_length=200)
    micronutrient = models.CharField(max_length=200, blank=True)
    population = models.CharField(max_length=200, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    endpoint = models.CharField(max_length=200, blank=True)
    paper_title = models.CharField(max_length=200)
    journal_title = models.CharField(max_length=200)
    study_type = models.CharField(max_length=200, blank=True)
    
    def __unicode__(self):
        return self.study_id
                
class Phenotype(models.Model):
    study_id = models.ForeignKey(Study)
    phenotype_name = models.CharField(max_length=200)
    environmental_factor = models.CharField(max_length=200)
    type = models.CharField(max_length=200)
    intake_data = models.CharField(max_length=200, blank=True)
    
    def __unicode__(self):
        return self.phenotype_name
        
class Genotype(models.Model):
    TYPE_CHOICES = (
        ('E', 'Heterozygote'),
        ('O', 'Homozygote'),
        ('W', 'Wildtype'),
        ('U', 'Unknown'),
    )
    study_id = models.ForeignKey(Study)
    gene = models.CharField(max_length=200)
    snp_ref = models.CharField(max_length=200)
    snp_variant = models.CharField(max_length=200, blank=True)
    snp_name = models.CharField(max_length=200, blank=True)
    allele = models.CharField(max_length=200, blank=True)
    mutation = models.CharField(max_length=200, blank=True)
    type = models.CharField(max_length=1, choices=TYPE_CHOICES)
    
    def __unicode__(self):
        # Order of preference:
        # snp_ref
        # snp_name
        if self.snp_ref != '' and self.snp_ref != None:
            return self.snp_ref
        else:
            return self.snp_name