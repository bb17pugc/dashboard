from django.db import models
from django.db import models
from django.core.validators import validate_email
from django.core.validators import RegexValidator
import django.dispatch
from time import gmtime, strftime 
from datetime import datetime
from datetime import date  

class Report(models.Model):
    id = models.AutoField
    Name = models.TextField(default='null')
    Date = models.DateField(blank=True, null=True,default=date.today())
    Time = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    User = models.ForeignKey('User', on_delete=models.CASCADE , related_name='song_report1_user')


class Songs(models.Model):
    id = models.AutoField
    Name = models.TextField(default='null')
    FileHash = models.TextField(default='null')
    User = models.ForeignKey('User' , on_delete=models.CASCADE , related_name='song_user')

class FingerPrints(models.Model):
    id = models.AutoField
    songs = models.ForeignKey('Songs' , on_delete=models.CASCADE , related_name='subsciber_user')
    Offset = models.IntegerField(default=0)
    Hash = models.TextField(default='null')


# Create your models here.
class User(models.Model):

   
    def validate_email(value):

        try:
            validate_email(value)
            return value
        except validate_email.ValidationError:
            raise ValidationError("Username is not valid")

        if not ".edu" in value:
            raise ValidationError("First name is invalid only use alphbets")
        else:
            return value        

   

    id = models.AutoField
    First_Name = models.CharField(max_length=30,validators=[RegexValidator(regex='^[a-z A-Z]*$',message='First name must be Alphanumeric',code='invalid_firstname'),] , default='noname' )
    Last_Name = models.CharField(max_length=30,validators=[RegexValidator(regex='^[a-z A-Z]*$',message='Last name must be Alphanumeric',code='invalid_lastname'),] , default='noname' )
    
    Username = models.CharField(max_length=200,validators=[RegexValidator(regex='^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$',message='Username must be valid',code='invalid_email'),] , default='noname' )

    Password = models.CharField(max_length=256)
    Role = models.CharField(max_length=256 , default='user' )
    Status = models.BooleanField(default=False)
    
    Is_Email_Verified = models.BooleanField(default=False)
    Gender = models.CharField(max_length=256 , default='male' )
    Streams = models.IntegerField(default=0 )
    UsedStreams = models.IntegerField(default=0 )
    
    image = models.ImageField(upload_to='images/%y/%m/%d/%H/%m/%S/',default='/static/images/dummy.png')
    

# @django.dispatch.receiver(models.signals.post_init, sender=User)
# def set_default_loremipsum_initials(sender, instance, *args, **kwargs):
#     instance.Username = instance.Username.split("@")[0]   
