from django.db import models
from django.utils import timezone
# Create your models here.

class AboutPage(models.Model):
    """Model for the about page content"""
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

class Feature(models.Model): 
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=1000,blank=True, null=True)
    image = models.ImageField(upload_to='features/',blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['title']
        verbose_name = "Feature"
        verbose_name_plural = "Features"



class News(models.Model):
    content = models.TextField()
    image = models.ImageField(upload_to='news/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    from_date = models.DateTimeField(null=True, blank=True)
    to_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"News {self.id} - {self.content[:50]}..."

    class Meta:
        verbose_name_plural = "News"







