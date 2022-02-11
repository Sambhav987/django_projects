from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from . import util, forms

from random import choice
import markdown2

form = forms.NewSearchForm()

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form": form
    })

def entry(request, title):
    entry = util.get_entry(title)

    if entry == None:
        return render(request, "encyclopedia/error.html")

    else:
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "entry": markdown2.markdown(entry),
            "form": form,
    })


def search(request):
    if request.method == "GET":
        form = forms.NewSearchForm(request.GET)
      
        if form.is_valid():
            searchquery = form.cleaned_data["search"].lower()
            all_entries = util.list_entries()
            
       
            files=[filename for filename in all_entries if searchquery in filename.lower()]
    

            if len(files) == 0:
                return render(request,"encyclopedia/search.html",{
                    "error" : "No results found",
                    "form":form,
                    "query": searchquery
                })
            
            elif len(files) == 1 and files[0].lower() == searchquery:
                title = files[0]
                return entry(request, title)

            
            else: 
                title = [filename for filename in files if searchquery == filename.lower()]

                if len(title)>0:
                    return entry(request, title[0])
                else:
                    return render(request, "encyclopedia/search.html",{
                        "results" : files,
                        "form" : form,
                        "query": searchquery

                    })

        else:
            return index(request)

    return index(request)


def new(request):

    if request.method == "GET":
        new_form= forms.NewPageForm()
        return render(request, "encyclopedia/new.html",{
            "form":form,
            "new_form":new_form

        })

    else:
        new_form = forms.NewPageForm(request.POST)
        if new_form.is_valid():

            title = new_form.cleaned_data["pagename"]
            body = new_form.cleaned_data["body"]


            all_entries = util.list_entries()

            for filename in all_entries:

                if title.lower()== filename.lower():

                    new_form = forms.NewPageForm()
                    error_message=f"Entry exists with the title {title}. Please try again with different title."

                    return render(request, "encyclopedia/new.html",{
                        "form": form,
                        "new_form": new_form,
                        "error": error_message
                        

                    })

            util.save_entry(title,body)
            return entry(request, title)

        else:
            
            return render(request, "encyclopedia/new.html",{
            "form": form,
            "new_form": new_form

        })


def edit(request):
    title = request.POST.get("edit")
    content = util.get_entry(title)
    edit_form = forms.EditPageForm(initial={'title': title, 'body': content})

    if edit_form.is_valid():

        return render (request, "encyclopedia/edit.html",{
                "title": title,
                "form": form,
                "edit_form": edit_form
            
                

            })
    else:
        return render (request, "encyclopedia/edit.html",{
                "title": title,
                "form": form,
                "edit_form": edit_form        

        })


def save(request):
    edit_form = forms.EditPageForm(request.POST)

    if edit_form.is_valid():

        title = edit_form.cleaned_data["title"]
        content = edit_form.cleaned_data["body"]
        
        util.save_entry(title, content)

        return entry(request, title)

    else:
        return render (request, "encyclopedia/edit.html",{
                "form": form,
                "edit_form": edit_form
            
        })


def random(request):
    return entry(request, (choice(util.list_entries())))