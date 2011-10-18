from django.forms import ModelForm
from eurreca.models import Study
from django.forms.models import modelformset_factory

class StudyForm(ModelForm):
 
    class Meta:
        model = Study
        
StudyFormSet = modelformset_factory(Study, form=StudyForm, max_num=1)
#StudyFormSet = modelformset_factory(Study, max_num=5, extra=3)