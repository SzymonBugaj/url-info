from django import forms

"""
class LinkForm(forms.Form):
    link = forms.CharField(max_length=300)

"""
class LinkForm(forms.Form):
    link = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    def __init__(self, *args, **kwargs):
        super(LinkForm, self).__init__(*args, **kwargs) 
        self.fields['link'].widget.attrs['style']  = 'width:550px; height:24px;'