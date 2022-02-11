from django import forms
from django.forms.widgets import Widget


class NewSearchForm(forms.Form):
    search = forms.CharField(required= False,
    widget= forms.TextInput(attrs={'placeholder':'Search Encyclopedia'}))


class NewPageForm(forms.Form):
    pagename = forms.CharField(label="Title", required = True, widget= forms.TextInput(attrs={'placeholder':'Enter Title'}))

    body = forms.CharField(label="Markdown content", required= True, widget= forms.Textarea(attrs={'placeholder':'Enter markdown content'}))


class EditPageForm(forms.Form):
    title = forms.CharField(label="Title", widget= forms.HiddenInput())
    body = forms.CharField(label="Markdown content", widget= forms.Textarea(attrs={"rows": 20, "cols": 40}))