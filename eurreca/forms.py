from django.forms import ModelForm
from eurreca.models import Study, Genotype, Phenotype, Panel, Interaction
from django.forms.models import modelformset_factory

class StudyForm(ModelForm):
    class Meta:
        model = Study
        
StudyFormSet = modelformset_factory(Study, form=StudyForm, max_num=1)

class GenotypeForm(ModelForm):
    class Meta:
        model = Genotype
        
GenotypeFormSet = modelformset_factory(Genotype, form=GenotypeForm, max_num=1)

class PhenotypeForm(ModelForm):
    class Meta:
        model = Phenotype
        
PhenotypeFormSet = modelformset_factory(Phenotype, form=PhenotypeForm, max_num=1)

class PanelForm(ModelForm):
    class Meta:
        model = Panel
        
PanelFormSet = modelformset_factory(Panel, form=PanelForm, max_num=1)

class InteractionForm(ModelForm):
    class Meta:
        model = Interaction
        
InteractionFormSet = modelformset_factory(Interaction, form=InteractionForm, max_num=1)