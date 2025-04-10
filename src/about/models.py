from django.db import models

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
