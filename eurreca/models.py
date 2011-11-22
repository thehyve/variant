from django.db import models
        
class Study(models.Model):
    GENDER_CHOICES = (
        ('F', 'Female'),
        ('M', 'Male'),
        ('X', 'Mixed'),
        ('U', 'Unknown'),
    )
    study_id = models.CharField(max_length=50, blank=True)
    pubmed_id = models.IntegerField(max_length=9, blank=True, null=True)
    year_of_publication = models.CharField(max_length=4)
    authors = models.CharField(max_length=200, blank=True)
    micronutrient = models.CharField(max_length=200, blank=True)
    population = models.CharField(max_length=200, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    endpoint = models.CharField(max_length=200, blank=True)
    paper_title = models.CharField(max_length=200, blank=True)
    journal_title = models.CharField(max_length=200, blank=True)
    study_type = models.CharField(max_length=200, blank=True)
    number_of_participants = models.IntegerField(max_length=9, blank=True, null=True)
    
    def __unicode__(self):
        return self.study_id
                
class Phenotype(models.Model):
    study = models.ForeignKey(Study)
    phenotype_name = models.CharField(max_length=200, blank=True)
    environmental_factor = models.CharField(max_length=200, blank=True)
    type = models.CharField(max_length=200, blank=True)
    intake_data = models.CharField(max_length=200, blank=True)
    
    def __unicode__(self):
        return "{0}".format(self.phenotype_name)
        
class Genotype(models.Model):
    TYPE_CHOICES = (
        ('E', 'Heterozygote'),
        ('O', 'Homozygote'),
        ('W', 'Wildtype'),
        ('U', 'Unknown'),
    )
    study = models.ForeignKey(Study)
    gene = models.CharField(max_length=200, blank=True)
    snp_ref = models.CharField(max_length=200, blank=True)
    snp_variant = models.CharField(max_length=200, blank=True)
    snp_name = models.CharField(max_length=200, blank=True)
    allele = models.CharField(max_length=200, blank=True)
    mutation = models.CharField(max_length=200, blank=True)
    zygosity = models.CharField(max_length=1, choices=TYPE_CHOICES, blank=True)
    
    def __unicode__(self):
        # Order of preference:
        # snp_ref
        # snp_name
        if self.snp_ref != '' and self.snp_ref != None:
            return "{0}".format(self.snp_ref)
        else:
            return "{0}".format(self.snp_name)
            
class Panel(models.Model):
    GENDER_CHOICES = (
        ('F', 'Female'),
        ('M', 'Male'),
        ('X', 'Mixed'),
        ('U', 'Unknown'),
    )
    study = models.ForeignKey(Study)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    number_of_participants = models.IntegerField(max_length=9, blank=True, null=True)
    mean_age = models.FloatField(max_length=10, null=True, blank=True)
    additional_age_description = models.CharField(max_length=200, blank=True)
    panel_description = models.CharField(max_length=200, blank=True)
    
class Interaction(models.Model):
    RATIO_TYPE_CHOICES = (
        ('F', 'Female'),
        ('M', 'Male'),
        ('X', 'Mixed'),
        ('U', 'Unknown'),
    )
    study = models.ForeignKey(Study)
    genotypes = models.ManyToManyField(Genotype, null=True, blank=True)
    phenotypes = models.ManyToManyField(Phenotype, null=True, blank=True)
    panels = models.ManyToManyField(Panel, null=True, blank=True)
    statistical_model = models.CharField(max_length=200, blank=True)
    ratio_type = models.CharField(max_length=1, choices = RATIO_TYPE_CHOICES, blank=True)
    ratio = models.FloatField(max_length=10, null=True, blank=True)
    ci_lower = models.FloatField(max_length=10, null=True, blank=True)
    ci_upper = models.FloatField(max_length=10, null=True, blank=True)
    significant_associations = models.CharField(max_length=500, blank=True)