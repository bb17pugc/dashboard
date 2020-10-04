from django.shortcuts import render
from django.shortcuts import render
from django.db.models import Count
import django.db;
from django.http import HttpResponse
from django.shortcuts import render , redirect
from .models import  User , Songs , FingerPrints,Report
import hashlib, os
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
import json 
from django.http import JsonResponse
from django.db.models import Q
from django.core.files.storage import FileSystemStorage
import datetime
from datetime import timedelta
from django.db.models import Sum
import os
import sys
from musicapp.libs import fingerprint
from django.db import transaction

# from termcolor import colored
from musicapp.libs.reader_file import FileReader
# from musicapp.libs.db_sqlite import SqliteDatabase
from musicapp.libs.config import get_config
from django.core import serializers
import math 


# Create your views here.
def admin(request):
    
    try:        
        password = "1234567"
        if not  User.objects.filter(Username="admin@gmail.com").exists():
            user=User(
                First_Name="Admin",
                Last_Name="Admin",
                Username="admin@gmail.com"  , 
                Password=make_password(password.encode('utf-8')), 
                Role = "admin",
                Is_Email_Verified=1
                )
            user.save()    
    except Exception:    
        return redirect('/signin')

def StartUp(request):
    admin(request)

def check_password(hash, password):
    """Generates the hash for a password and compares it."""
    generated_hash = make_password(password)
    return hash == generated_hash

def make_password(password):
    assert password
    hash = hashlib.md5(password).hexdigest()
    return hash

def check_password(hash, password):
    """Generates the hash for a password and compares it."""
    generated_hash = make_password(password)
    return hash == generated_hash


def IsAuthentcated(request):
    
    # try:
    StartUp(request)
    if  request.session.get('email', False) == False:
        return False
    else:
        return True        
    # except Exception:
    #     return True


def streams(request):
    user_id = ""    
    if IsAuthentcated(request) == False:
       return redirect('signin')
    if request.method == 'POST':
       response_data = {}     
       streams=request.POST['streams']
       user=request.POST['user']
       user = User.objects.get(Username = user)
       user.Streams =streams
       user.save() 
       response = {
                        'streams':streams # response message
        }
       return JsonResponse(response) # return response as JSON
    return redirect('signin')


def user_panel(request):
    if IsAuthentcated(request) == False:
       return redirect('signin')
    songs  = Songs.objects.filter(User_id = int(request.session.get('id', False))).all()
    param = {'songs':songs}
    return render(request, 'musicapp/user_panel.html' , param)

def remove(request):
    id = request.GET['id']
    User.objects.filter(id = int(id)).delete()
    return redirect('users')
def users(request):

    if IsAuthentcated(request) == False or request.session.get('role', False) != "admin":
       return redirect('signin')

    total = User.objects.all().count()   
    pages = math.ceil(total/10)
    page=1
    if request.method == 'GET' and 'page' in request.GET:
        page = int(request.GET['page'])
    if page < 1:
       page=1
    if page > pages:
       page=pages 
    
    users = User.objects.all()[(page-1)*10:total][:10]
    

    songs = Songs.objects.count()
    total_price = User.objects.all().aggregate(Sum('Streams'))

    param={'songs':songs,'users':users , 'total':total_price , 'pages' : pages , 'url':"users?page=" , 'current':page  ,'list':True }   

    return render(request, 'musicapp/users.html' , param)

def newuser(request):

    if IsAuthentcated(request) == False or request.session.get('role', False) != "admin":
       return redirect('signin')

    if request.method == 'POST':
        try:
            username = request.POST['username']
            password = request.POST['password']
            gender = request.POST['gender']
            role = request.POST['role']
            firstname = request.POST['firstname']
            lastname = request.POST['lastname']

            if len(password) < 7 :
               messages.error(request ,'password must be 7 character long or higher') 
               return render(request ,'musicapp/newuser.html')  
        except Exception:
                messages.error(request ,'Must select all the fields')
                return render(request ,'musicapp/newuser.html')    
        # try:
        
        if User.objects.filter(Username = username).exists() == False:
            
            try:

                user = User(
                    First_Name = firstname,
                    Last_Name = lastname,
                    Username = username,
                    Password = make_password(password.encode('utf-8')),
                    Gender = gender,
                    Role = role,
                    
                )
                user.full_clean()
                user.save()
                messages.success(request, "User saved successfully")  
            except ValidationError as e:
                for i in e.messages:
                    messages.error(request , i)
                return render(request ,'musicapp/newuser.html')      
                                        
        else:
            messages.error(request, "user already exists")    
            return render(request ,'musicapp/newuser.html')      
        # except Exception:
        #     messages.error(request, "user not found")    
        #     return render(request ,'musicapp/newuser.html')  
             
    return render(request, 'musicapp/newuser.html')


def logout(request):

    for key in list(request.session.keys()):
      del request.session[key]
    return redirect('signin') 

    return render(request, 'musicapp/dashboard.html')

def songs_streams(request):

    if IsAuthentcated(request) == False or request.session.get('role', False) != "admin":
       return redirect('signin') 
    
    total = User.objects.all().count()   
    pages = math.ceil(total/10)
    page = int(request.GET['page'])
    if page < 1:
       page=1
    if page > pages:
       page=pages 
    users = User.objects.all()[(page-1)*10:total][:10]    
    param={'users':users , 'pages' : pages , 'url':"songs_streams?page=" , 'current':page,'list':True }   
    return render(request, 'musicapp/songs_streams.html' , param)
def reports(request):

    if IsAuthentcated(request) == False:
       return redirect('signin') 

    return redirect('users?page=1')

def admin_reports(request):

    if IsAuthentcated(request) == False or request.session.get('role', False) != "admin":
       return redirect('signin')
    users = User.objects.all()
    param = {'users' : users}   
    if request.method == 'POST':    
        data1 = request.POST['date1'] 
        data2 = request.POST['date2'] 
        user = request.POST['user'] 
        
        data1=changer(data1 , "%Y-%m-%d")
        data2=changer(data2 , "%Y-%m-%d")
        
        # data1 =  datetime.datetime.strptime(data1, "YYYY-MM-DD")
        # data2 =  datetime.datetime.strptime(data2, "YYYY-MM-DD")
        selected = users.get(id = int(user))
        songs = Report.objects.filter(User_id = int(user)).filter(Date__range=[data1, data2]).all().values('Name','User_id').annotate(total=Count('Name')).order_by('Name')
        param = {'songs':songs , 'date1':data1 , 'date2':data2 , 'users' : users , 'selected':selected}
        return render(request, 'musicapp/admin_reports.html' , param)    

    return render(request, 'musicapp/admin_reports.html' , param)
def change_password(request):
    if IsAuthentcated(request) == False or request.session.get('role', False) != "admin":
       return redirect('signin') 
    id =request.GET['id'] 
    if request.method == 'POST':
       user = User.objects.get(id = int(request.GET['id']))
       oldpassword = request.POST['old']
       newpassword = request.POST['new']
       id = request.POST['id']
       confirmnewpassword = request.POST['confirmnew']
       if check_password(user.Password , oldpassword.encode('utf-8')):
          if newpassword == confirmnewpassword:
             user.Password=make_password(newpassword.encode('utf-8'))  
             user.save()
             messages.success(request, "Pssword changed successfully")
          else:
             messages.error(request, "New password not matched with confirm password")
       else:
           messages.error(request, "Pssword not matched with old password ")
    return render(request ,'musicapp/change_password.html' , {'id':request.GET['id']})                    
def edit_profile(request):
    if IsAuthentcated(request) == False or request.session.get('role', False) != "admin":
       return redirect('signin') 
    user = User.objects.get(id = int(request.GET['id']))
    param = {'user':user}
    if request.method == 'POST':
        # try:
        username = request.POST['username']
        User_id = request.POST['id']            
        gender = request.POST['gender']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        
        # except Exception:
        # try:
        
        if User.objects.filter(Username = username).exists() == False:
            
            try:

                user = User.objects.get(id=int(User_id))
                user.First_Name = firstname
                user.Last_Name = lastname
                user.Username = username
                user.Gender = gender
                user.full_clean()
                user.save()
                messages.success(request, "Profile updated  successfully")  
            except ValidationError as e:
                for i in e.messages:
                    messages.error(request , i)
                return render(request ,'musicapp/edit_profile.html' , param)      
                                        
        else:
            messages.error(request, "user already exists")    
            return render(request ,'musicapp/edit_profile.html' , param)  

    
    return render(request, 'musicapp/edit_profile.html' , param)

def setting(request):

    if IsAuthentcated(request) == False or request.session.get('role', False) != "admin":
       return redirect('signin') 
    id = request.GET['id']   
    user = User.objects.get(id = int(id))
    param = {'user':user}
    return render(request, 'musicapp/setting.html' , param)

def find_song(request):
    name = request.GET['name']
    folder='media/files/' 
    reader = FileReader(folder + name)
    audio = reader.parse_audio()
    report = Report()
    report.Name = name
    report.User = User.objects.get(id = int(request.session.get('id', False)))
    report.save()

    response = {
                   'file':audio['songname'] # response message
               }
    return JsonResponse(response)    


def upload_audio_file(request):
    django.db.close_old_connections()    
    if request.method == 'POST':
        vedio=request.FILES['audio']   
        
        folder='media/files/' 
        now = datetime.datetime.now()
        if request.method == 'POST' and request.FILES['audio']:
            myfile = request.FILES['audio']
            fs = FileSystemStorage(location=folder)
             #defaults to   MEDIA_ROOT  
            myfile.name=myfile.name[:len(myfile.name)-5] + str(request.session.get('id', False))+".mp3" 
            
            for filename in os.listdir(folder):
        
                if filename == myfile.name:
                    response = {
                                 'file':'400' # response message
                    }
                    return JsonResponse(response)    

            filename = fs.save(myfile.name, myfile)
            file_url = fs.url(filename)

            reader = FileReader(folder + filename)
            audio = reader.parse_audio()
            
            song_id = add_song(request,filename, audio['file_hash'])
            if song_id == False:
                response = {
                                 'file':'400' # response message
                    }
                
                return JsonResponse(response)
    
            hashes = set()
            channel_amount = len(audio['channels'])
            try:    
                for channeln, channel in enumerate(audio['channels']):
                    # print colored(msg, attrs=['dark']) % (channeln+1, channel_amount)
                    channel_hashes = fingerprint.fingerprint(channel, Fs=audio['Fs'], plots=False)
                    channel_hashes = set(channel_hashes)
                    msg = 'finished channel %d/%d, got %d hashes'
                    # print colored(msg, attrs=['dark']) % (
                    # channeln+1, channel_amount, len(channel_hashes)
                    # )
                    hashes |= channel_hashes
                # song_id=46
            except Exception:
                    print("hi")    
            # try:
            values=[]
            for hash,offset in hashes:
                values.append(FingerPrints(songs = Songs.objects.get(id = int(song_id)),Offset = offset,Hash = hash))
            FingerPrints.objects.bulk_create(values , batch_size=None)
            print(len(values))
            # except Exception:
            #         print("hi")

            return JsonResponse({'file':filename , 'id':song_id})
    return JsonResponse({'file':'200'})
def get_song_by_filehash(filehash):
    item = Songs.objects.filter(FileHash = filehash)
    return item

def add_song(request,filename, filehash):
    if Songs.objects.filter(FileHash = filehash).filter(id=int(request.session.get('id', False))).exists():
       return False 
    new_song = Songs()
    new_song.Name = filename
    new_song.FileHash = filehash
    new_song.User = User.objects.get(id = int(request.session.get('id', False)))
    
    new_song.save()
    return new_song.id

def get_song_hashes_count(song_id):
    return Songs.objects.filter(id = song_id).count()

def store_hashes(request):
    
    song_id=0

    
    path = 'media/files/'


    # fingerprint all files in a directory
    
    for filename in os.listdir(path):
        
        if filename.endswith(".mp3"):
            reader = FileReader(path + filename)
            audio = reader.parse_audio()
            
            song = get_song_by_filehash(audio['file_hash'])
            song_id = add_song(filename, audio['file_hash'])
            
            # msg = ' * %s %s: %s' % (
            #     colored('id=%s', 'white', attrs=['dark']),       # id
            #     colored('channels=%d', 'white', attrs=['dark']), # channels
            #     colored('%s', 'white', attrs=['bold'])           # filename
            # )
            # print msg % (song_id, len(audio['channels']), filename)

            # if song:
            #     hash_count = get_song_hashes_count(song_id)
                
            #     if hash_count > 0:
            #         msg = 'already exists (%d hashes), skip' % hash_count
            #         # print colored(msg, 'red')

            #         continue

            # print colored('   new song, going to analyze..', 'green')
            
            hashes = set()
            channel_amount = len(audio['channels'])

            for channeln, channel in enumerate(audio['channels']):
                msg = '   fingerprinting channel %d/%d'
                # print colored(msg, attrs=['dark']) % (channeln+1, channel_amount)

                channel_hashes = fingerprint.fingerprint(channel, Fs=audio['Fs'], plots=False)
                channel_hashes = set(channel_hashes)
                 
                msg = '   finished channel %d/%d, got %d hashes'
                # print colored(msg, attrs=['dark']) % (
                # channeln+1, channel_amount, len(channel_hashes)
                # )

                hashes |= channel_hashes

            msg = '   finished fingerprinting, got %d unique hashes'

            # song_id=46
            for hash, offset in hashes:
                
                store_fingerprints=FingerPrints()
                store_fingerprints.songs = Songs.objects.get(id = int(song_id))
                store_fingerprints.Offset = offset
                store_fingerprints.Hash = hash
                store_fingerprints.save()
            
            msg = '   storing %d hashes in db' % len(values)
            # print colored(msg, 'green')
            
            store_fingerprints(values)

    print('end')

    response = {
        'file':values # response message
                    }
    return JsonResponse(response)

# def store_fingerprints(values):
#     self.insertMany(self.TABLE_FINGERPRINTS,
#       ['song_fk', 'hash', 'offset'], values
#     )

def changer(datestr="", format="%Y-%m-%d"):
    from datetime import datetime
    if not datestr:
        return datetime.today().date()
    return datetime.strptime(datestr, format).date()

def delete_song(request):
    # try:
       folder='media/files/'
       id = request.GET['id']
       song=Songs.objects.get(User_id =  int(request.session.get('id', False)) , id = int(id) )
       name = song.Name
       song.delete()
       path = settings.MEDIA_ROOT
       os.remove(r''+folder+name)   
       return redirect('user_panel')  
    # except Exception :
    #    return redirect('user_panel')     

def user_report(request):

    if IsAuthentcated(request) == False:
       return redirect('signin')
    if request.method == 'POST':    
        data1 = request.POST['date1'] 
        data2 = request.POST['date2'] 
        
        data1=changer(data1 , "%Y-%m-%d")
        data2=changer(data2 , "%Y-%m-%d")
        
        # data1 =  datetime.datetime.strptime(data1, "YYYY-MM-DD")
        # data2 =  datetime.datetime.strptime(data2, "YYYY-MM-DD")

        songs = Report.objects.filter(Date__range=[data1, data2]).filter(User_id=int(request.session.get('id', False))).all().values('Name','User_id').annotate(total=Count('Name')).order_by('Name')
        param = {'songs':songs , 'date1':data1 , 'date2':data2}
        return render(request, 'musicapp/user_report.html' , param)
    return render(request, 'musicapp/user_report.html')


def dashboard(request):

    if IsAuthentcated(request) == False or request.session.get('role', False) != "admin":
       return redirect('signin') 
    return redirect('users')
def signin(request):

    if IsAuthentcated(request) == True:
       return redirect('dashboard') 

    if request.method == 'POST':
             
        loginusername = request.POST['username']
        loginpassword = request.POST['password']
        try:
            user = User.objects.get(Username = loginusername)
            if user is not None:
                if(check_password(user.Password , loginpassword.encode('utf-8'))):
                    request.session['firstname'] = user.First_Name
                    request.session['lastname'] = user.Last_Name
                    
                    request.session['email'] = user.Username
                    request.session['role'] = user.Role
                    request.session['id'] = user.id
                    request.session['IsVerified'] = user.Is_Email_Verified
                    request.session['image'] = user.image.url
                    request.session['streams'] = user.Streams
                    
                    if user.Role == "user":
                       return redirect('user_panel') 
                    else:
                       return redirect('dashboard')
                else:
                    messages.error(request, "email or password not correct")    
                    return redirect('signin')
                                        
            else:
                messages.error(request, "email or password not correct")    
                return redirect('signin')     
        except Exception:
            messages.error(request, "user not found")    
            return redirect('signin')
    else:
        return render(request, 'musicapp/signin.html')
    