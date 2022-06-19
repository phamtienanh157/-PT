from concurrent.futures import process
from datetime import datetime
import mailbox
from multiprocessing import context
from django import dispatch
from django.shortcuts import render,HttpResponse,HttpResponseRedirect
from scipy.fftpack import idstn
from .models import Document
import docx2txt
import os,math,re
# Create your views here.
def index(request):
    return render(request,"home/search.html")
def viewdocument(request):
    return render(request,"home/addDocument.html")

def readfile(request):
    link = request.POST["link"]
    dictionary = request.POST["dictionary"]
    document_new= Document.objects.latest('datecreate')
    link_split = link.split("/")
    id_document_new=document_new.doc_id
    Document.objects.filter(doc_id=id_document_new).update(dictionary=dictionary,name_document=link_split[len(link_split)-1])
    with open(dictionary, 'w') as f:
        pass
    text = docx2txt.process(link)

    text_processing = preProcessing(text)
    print(text_processing)
    arr = countTerm(text_processing)
    get_file_new= Document.objects.latest('datecreate')
    arr.sort()
    with open(get_file_new.dictionary, mode='w') as f:
        for i in range(len(arr)):
            f.write("{},{};".format(arr[i][0],arr[i][1]))
    createidf()
    return render(request,"home/addDocument.html")

def addfile(request):
    file = request.FILES['file']
    datecreate = datetime.now()
    f = Document.objects.create(file=file,datecreate=datecreate,dictionary="",name_document="")
    f.save()
    get_file_new= Document.objects.latest('datecreate')
    context = {"newfile":get_file_new}
    return render(request,"home/openfile.html",context)

def solve(request):
    strSearch = request.POST["strSearch"]
    rank = soSanh(strSearch)
    list_doc=[]
    id=0
    for i in range (len(rank)):
        id = int(rank[i][1])+1
        doc = Document.objects.get(doc_id=id)
        list_doc.append(doc)
    context={"list_doc":list_doc}
    return render(request,"home/search.html",context)

# tao tu dien cho tung van ban
def dictionary(request):
    doc = request.POST["vanban"]
    arr = countTerm(doc)
    get_file_new= Document.objects.latest('datecreate')
    arr.sort()
    with open(get_file_new.dictionary, mode='w') as f:
        for i in range(len(arr)):
            f.write("{},{};".format(arr[i][0],arr[i][1]))
    createidf()

    return HttpResponseRedirect("/readfile/")

# Tao tu dien van ban
def createidf():
    doc = Document.objects.latest('datecreate')
    all_Term=[]
    for i in range(doc.doc_id):
        print(i)
        print("233423423")
        url ="D:/HeThong_CSDLDPT/HeThong_CSDLDPT/File/dictionary/" + str(i+1)  +".txt"
        f = open(url,'r',encoding = 'utf-8')
        s = f.read()
        strsplit = s.split(";")
        for j in range(len(strsplit)-1):
            s1 = strsplit[j]
            s1_split= s1.split(",")
            if all_Term != None:
                d=0
                for k in range(len(all_Term)):
                    if all_Term[k][0] == s1_split[0]:
                        all_Term[k][1] = str(int(all_Term[k][1]) + int(s1_split[1]))
                        d=d+1
                if d==0:
                    all_Term.append([s1_split[0],s1_split[1]])
            else:
                    all_Term.append([s1_split[0],s1_split[1]])
        all_Term.sort()
        print(all_Term)
        with open("D:/HeThong_CSDLDPT/HeThong_CSDLDPT/File/dictionary/idf_Dictionary.txt", mode='w+') as f:
            for i in range(len(all_Term)):
                f.write("{},{};".format(all_Term[i][0],all_Term[i][1]))
    return 1

def soSanh(str_search):
    doc = Document.objects.latest('datecreate')
    #tinh trong so cho tung van ban
    trongso_vb_all=[]
    for i in range(doc.doc_id):
        url ="D:/HeThong_CSDLDPT/HeThong_CSDLDPT/File/dictionary/" + str(i+1)  +".txt"
        f = open(url,'r',encoding = 'utf-8')
        s = f.read()
        s_split = s.split(";")
        arr=[]
        trongso = []
        for j in range(len(s_split)-1):
            s_split2=s_split[j].split(",")
            arr.append([s_split2[0],s_split2[1]])
        trongso = tinhTrongSo(arr)
        trongso_vb_all.append(trongso)
    #so sanh do tuong dong
    dic_str_search = countTerm(str_search)
    rank = []
    for i in range(len(trongso_vb_all)):
        S=0
        tu=0
        d=0
        for j in range(len(trongso_vb_all[i])):
            for k in range(len(dic_str_search)):
                if dic_str_search[k][0] == trongso_vb_all[i][j][0]:
                    tu+= trongso_vb_all[i][j][1]
                    d+=1
        mau = math.sqrt(tu*tu*d*d)
        if mau==0:
            S=0
        else:
            S=tu/mau
        rank.append([S,i])
    rank  = sorted(rank, reverse=True)
    print(rank)
    return rank

def tinhTrongSo(arr):
    trongso=[]
    f = open("D:/HeThong_CSDLDPT/HeThong_CSDLDPT/File/dictionary/idf_Dictionary.txt",'r',encoding = 'utf-8')
    s = f.read()
    s_split = s.split(";")
    for i in range(len(arr)):
        for j in range(len(s_split)-1):
            s_split2 = s_split[j].split(",")
            if(arr[i][0]==s_split2[0]):
                ts = float(arr[i][1])*math.log(100/int(s_split2[1]))
                trongso.append([arr[i][0],ts])
                break
    return trongso

def preProcessing(str):
    str=str.lower()
    str_process1 = str.lstrip()
    str_process2 = str_process1.rstrip()
    str_process2 = str_process2.replace(",","")
    f = open("D:/HeThong_CSDLDPT/HeThong_CSDLDPT/File/stopword/stopword.txt",'r')
    stopword = f.read()
    stopword_split = stopword.split(",")
    print(stopword_split)
    del_stopword=""
    for i in range(len(stopword_split)):
        del_stopword = str_process2.replace(stopword_split[i]," ")
        str_process2 = del_stopword
    str_result = re.sub(r'\s+',' ', del_stopword.strip())
    print(str_result)
    return str_result

def countTerm(str):
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