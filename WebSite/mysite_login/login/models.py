from django.db import models
class User(models.Model):
    '''用户表'''
    gender = (
        ('male','男'),
        ('female','女'),
    )
    name = models.CharField(max_length=128,unique=True)
    password = models.CharField(max_length=256)
    email = models.EmailField(unique=True)
    sex = models.CharField(max_length=32,choices=gender,default='男')
    c_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=256,default='正常')
    def __str__(self):
        return self.name
    class Meta:
        ordering = ['c_time']
        verbose_name = '用户'
        verbose_name_plural = '用户'
# Create your models here.

class Admin(models.Model):
    name = models.CharField(max_length=128, unique=True)
    password = models.CharField(max_length=256)

class Content(models.Model):
    name = models.CharField(max_length=128, unique=True)
    habit = models.CharField(max_length=256)
    address = models.CharField(max_length=256)

class Picture(models.Model):
    name = models.CharField(max_length=32)
    date1 = models.DateTimeField(auto_now=True,null=True)
    date2 = models.DateTimeField(auto_now_add=True,null=True)
    img = models.ImageField(upload_to='img',null=True)