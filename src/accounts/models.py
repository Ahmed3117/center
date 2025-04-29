import random
from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Year(models.Model):
    name = models.CharField(max_length=50)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return  f'{self.name}  - id: {self.id}'

class TypeEducation(models.Model):
    name = models.CharField(max_length=50)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return  f'{self.name}  - id: {self.id}'

class Student(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=50,blank=True, null=True)
    parent_phone = models.CharField(max_length=11,blank=True, null=True)
    type_education = models.ForeignKey(TypeEducation, null=True, blank=True, on_delete=models.SET_NULL)
    year = models.ForeignKey(Year,null=True, on_delete=models.SET_NULL)
    points = models.IntegerField(default=1)
    division = models.CharField(max_length=50,blank=True, null=True)
    government = models.CharField(max_length=100,blank=True, null=True)
    jwt_token = models.CharField(max_length=1000, blank=True, null=True)
    active = models.BooleanField(default=False)
    block = models.BooleanField(default=False)
    code = models.CharField(max_length=50,blank=True, null=True)
    by_code = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} | {self.id}'

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    promo_video = models.FileField(upload_to='teacher_videos/', blank=True, null=True)
    promo_video_link = models.CharField(max_length=300, blank=True, null=True)
    image = models.ImageField(upload_to='teachers/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.name} | {self.id}'





