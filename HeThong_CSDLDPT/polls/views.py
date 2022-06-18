from datetime import datetime
from multiprocessing import context
from django import dispatch
from django.shortcuts import render,HttpResponse,HttpResponseRedirect
from .models import Document
import docx2txt
import os
# Create your views here.
def index(request):
    return render(request,"home/home.html")

def readfile(request):
    link = request.POST["link"]
    dictionary = request.POST["dictionary"]
    document_new= Document.objects.latest('datecreate')
    id_document_new=document_new.doc_id
    Document.objects.filter(doc_id=id_document_new).update(dictionary=dictionary)
    with open(dictionary, 'w') as f:
        pass
    text = docx2txt.process(link)
    context={"text":text} 
    return render(request,"home/showtext.html",context)

def addfile(request):
    file = request.FILES['file']
    datecreate = datetime.now()
    f = Document.objects.create(file=file,datecreate=datecreate,dictionary="")
    f.save()
    get_file_new= Document.objects.latest('datecreate')
    context = {"newfile":get_file_new}
    return render(request,"home/openfile.html",context)

def dictionary(request):
    doc = request.POST["vanban"]
    arr = countterm(doc)
    get_file_new= Document.objects.latest('datecreate')
    print(arr)
    with open(get_file_new.dictionary, mode='w') as f:
        for i in range(len(arr)):
            f.write(arr[i][0])
            f.write(',')
            f.write(str(arr[i][1]))
            f.write(';')
    return HttpResponseRedirect("/readfile/")



def countterm(str):
    count = []
    strsplit = str.split(" ")
    for i in range(len(strsplit)):
        if checkterm(count,strsplit[i]) == 1:
            count.append([strsplit[i],strsplit.count(strsplit[i])])
    return count

def checkterm(arr,term):
    for i in range(len(arr)):
        if term == arr[i][0]:
            return 0
    return 1