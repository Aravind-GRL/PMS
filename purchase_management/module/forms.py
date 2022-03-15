from django import forms  
from module.models import project,purchase,purchase_request 
 
class ProjectForm(forms.ModelForm):  
    class Meta:  
        model = project  
        fields = "__all__"  

class PurchaseForm(forms.ModelForm):  
    class Meta:  
        model = purchase  
        fields = "__all__"  

class RequestForm(forms.ModelForm):  
    class Meta:  
        model = purchase_request  
        fields = "__all__"  