from concurrent.futures import process
from datetime import datetime
import mailbox
from multiprocessing import context
from posixpath import split
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

def addfile(request):
    file = request.FILES['file']
    datecreate = datetime.now()
    f = Document.objects.create(file=file,datecreate=datecreate,dictionary="",name_document="")
    f.save()
    get_file_new= Document.objects.latest('datecreate')
    context = {"newfile":get_file_new}
    return render(request,"home/openfile.html",context)

def readfile(request):
    link = request.POST["link"]
    dictionary = request.POST["dictionary"]
    document_new= Document.objects.latest('datecreate')
    link_split = link.split("/")
    id_document_new=document_new.doc_id
    Document.objects.filter(doc_id=id_document_new).update(dictionary=dictionary,name_document=link_split[len(link_split)-1])
    link_document = "D:/HeThong_CSDLDPT/HeThong_CSDLDPT/File/files/" + link_split[len(link_split)-1]
    text = docx2txt.process(link_document)
    text_processing = preProcessing(text)
    #print(text_processing)
    arr = countTerm(text_processing)
    get_file_new= Document.objects.latest('datecreate')
    arr.sort()
    #ghi vao file tu dien tung van ban
    with open(get_file_new.dictionary, mode='w+') as f:
        for i in range(len(arr)):
            f.write("{},{};".format(arr[i][0],arr[i][1]))
    createidf()
    #createFileWeight()
    return render(request,"home/addDocument.html")

def Search(request):
    strSearch = request.POST["strSearch"]
    strSearch_pro = preProcessing(strSearch)
    rank = DoTuongDong(strSearch_pro)
    list_tyle=[]
    id=0
    x=0
    if len(rank) >= 10:
        x = 10
    else:
        x = len(rank)
    for i in range (x):
        if rank[i][0] > 0:
            id = int(rank[i][1])+1
            doc = Document.objects.get(doc_id=id)
            list_tyle.append(Tyle(str(round(rank[i][0],4)),doc.name_document))
    print(list_tyle)
    check = ""
    if list_tyle :
        check=""
        context={"list_tyle":list_tyle,"check":check}
    else:
        check="Không tìm thấy tài liệu nào phù hợp"
        context={"check":check}
    return render(request,"home/search.html",context)

# Tao tu dien van ban
def createidf():
    doc = Document.objects.latest('datecreate')
    dic_idf=[]
    url ="D:/HeThong_CSDLDPT/HeThong_CSDLDPT/File/dictionary/dictionary" + str(doc.doc_id)  +".txt"
    f = open(url,'r')
    s = f.read()
    url_idf ="D:/HeThong_CSDLDPT/HeThong_CSDLDPT/File/dictionary/idf_Dictionary.txt"
    f_idf = open(url_idf,'r')
    s_idf = f_idf.read()
    strsplit = s.split(";")
    strsplit_idf = s_idf.split(";")
    if strsplit_idf != None:
        for i in range(len(strsplit_idf)-1):
            s_split_idf = strsplit_idf[i].split(",")
            dic_idf.append([s_split_idf[0],s_split_idf[1]])

        for i in range(len(strsplit)-1):
            s_split= strsplit[i].split(",")
            cnt=0 
            for j in range(len(dic_idf)):
                if(s_split[0]==dic_idf[j][0]):
                    dic_idf[j][1] = int(dic_idf[j][1]) + 1
                    cnt+=1
                    break
            if cnt == 0:
                dic_idf.append([s_split[0],1])
    else:
        for i in range(len(strsplit)-1):
            s_split= strsplit[i].split(",")
            dic_idf.append([s_split[0],1])
    #print(all_Term)
    dic_idf.sort()
    with open("D:/HeThong_CSDLDPT/HeThong_CSDLDPT/File/dictionary/idf_Dictionary.txt", mode='w+') as f:
        for i in range(len(dic_idf)):
                f.write("{},{};".format(dic_idf[i][0],dic_idf[i][1]))
    return 1

def DoTuongDong(str_search):
    dic_str_search = countTerm(str_search)
    rank = []
    doc = Document.objects.latest('datecreate')
    for i in range(doc.doc_id):
        url ="D:/HeThong_CSDLDPT/HeThong_CSDLDPT/File/trongso/trongso" + str(i+1)  +".txt"
        f = open(url,'r',encoding = 'utf-8')
        s = f.read()
        s_split = s.split(";")
        S=0
        TQ=0
        T=0
        Q=0
        for j in range(len(s_split)-1):
            s_split2=s_split[j].split(",")   
            Q=Q+float(s_split2[1])*float(s_split2[1])
            for k in range(len(dic_str_search)):
                if dic_str_search[k][0] == s_split2[0]:
                    TQ+= float(s_split2[1])
                    T+=1
            mau = math.sqrt(T*Q)
        if mau==0:
            S=0
        else:
            S=TQ/mau
        rank.append([S,i])
    rank  = sorted(rank, reverse=True)
    print(rank)
    return rank

#Tao file trong so
def createFileWeight():
    doc = Document.objects.latest('datecreate')
    trongso_vb_all=[]
    for i in range(doc.doc_id):
        print(doc.doc_id)
        url ="D:/HeThong_CSDLDPT/HeThong_CSDLDPT/File/dictionary/dictionary" + str(i+1)  +".txt"
        f = open(url,'r',encoding = 'utf-8')
        s = f.read()
        s_split = s.split(";")
        arr=[]
        trongso = []
        for j in range(len(s_split)-1):
            s_split2=s_split[j].split(",")
            arr.append([s_split2[0],s_split2[1]])
        tentudien = "trongso"+str(i+1)
        trongso = CalculaWeight(arr,tentudien)
        trongso_vb_all.append(trongso)
    return 1

def CalculaWeight(arr,tentudien):
    trongso=[]
    f = open("D:/HeThong_CSDLDPT/HeThong_CSDLDPT/File/dictionary/idf_Dictionary.txt",'r')
    s = f.read()
    s_split = s.split(";")
    for i in range(len(arr)):
        for j in range(len(s_split)-1):
            s_split2 = s_split[j].split(",")
            if(arr[i][0]==s_split2[0]):
                ts = float(arr[i][1])*math.log(100/int(s_split2[1])) #Cong thuc tinh trong so
                trongso.append([arr[i][0],ts])
                break
    with open("D:/HeThong_CSDLDPT/HeThong_CSDLDPT/File/trongso/"+tentudien+".txt", mode='w+') as f:
        for i in range(len(trongso)):
            f.write("{},{};".format(trongso[i][0],trongso[i][1]))
    return trongso

#Tien xu ly
def preProcessing(str):
    str=str.lower()
    str_process1 = str.lstrip()
    str_process2 = str_process1.rstrip()
    str_process2 = str_process2.replace(",","")
    f = open("D:/HeThong_CSDLDPT/HeThong_CSDLDPT/File/stopword/stopword.txt",'r')
    stopword = f.read()
    stopword_split = stopword.split(",")
    #print(stopword_split)
    del_stopword=""
    for i in range(len(stopword_split)):
        del_stopword = str_process2.replace(stopword_split[i]," ")
        str_process2 = del_stopword
    str_result = re.sub(r'\s+',' ', del_stopword.strip())
    #print(str_result)
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


class Tyle:
     # thuộc tính đối tượng
     def __init__(self, tyle, name_document):
        self.tyle = tyle
        self.name_document=name_document


def auto_createidf(request):
    doc = Document.objects.latest('datecreate')
    all_Term=[]
    for i in range(doc.doc_id):
        print(i)
        print("233423423")
        url ="D:/HeThong_CSDLDPT/HeThong_CSDLDPT/File/dictionary/dictionary" + str(i+1)  +".txt"
        f = open(url,'r')
        s = f.read()
        strsplit = s.split(";")
        for j in range(len(strsplit)-1):
            s1 = strsplit[j]
            s1_split= s1.split(",")
            if all_Term != None:
                d=0
                for k in range(len(all_Term)):
                    if all_Term[k][0] == s1_split[0]:
                        all_Term[k][1] = int(all_Term[k][1]) + 1
                        d=d+1
                if d==0:
                    all_Term.append([s1_split[0],1])
            else:
                    all_Term.append([s1_split[0],1])
        all_Term.sort()
        #print(all_Term)
        with open("D:/HeThong_CSDLDPT/HeThong_CSDLDPT/File/dictionary/idf_Dictionary.txt", mode='w+') as f:
            for i in range(len(all_Term)):
                f.write("{},{};".format(all_Term[i][0],all_Term[i][1]))
    return render(request,"home/addDocument.html")

def auto_createFileWeight(request):
    doc = Document.objects.latest('datecreate')
    trongso_vb_all=[]
    for i in range(doc.doc_id):
        print(doc.doc_id)
        url ="D:/HeThong_CSDLDPT/HeThong_CSDLDPT/File/dictionary/dictionary" + str(i+1)  +".txt"
        f = open(url,'r',encoding = 'utf-8')
        s = f.read()
        s_split = s.split(";")
        arr=[]
        trongso = []
        for j in range(len(s_split)-1):
            s_split2=s_split[j].split(",")
            arr.append([s_split2[0],s_split2[1]])
        tentudien = "trongso"+str(i+1)
        trongso = CalculaWeight(arr,tentudien)
        trongso_vb_all.append(trongso)
        print(trongso)
    return render(request,"home/addDocument.html")