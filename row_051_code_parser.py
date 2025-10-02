'''Install dependencies'''
pip install django djangorestframework psycopg2 pyresparser python-magic spacy

'''You may also need to download language models for spacy if using pyresparser:'''
python -m spacy download en_core_web_sm

'''Create the project'''
django-admin startproject ResumeProcessor
cd ResumeProcessor

'''create the resume app'''
python manage.py startapp resume

'''Database Configuration
Edit ResumeProcessor/settings.py to configure PostgreSQL:'''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'resume_db',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

'''Models
In resume/models.py, define the Candidate model:'''
from django.db import models

class Candidate(models.Model):
    first_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=15)

    def __str__(self):
        return f'{self.first_name} - {self.email}'

'''Serializers
Create a new file resume/serializers.py and define the serializer for the Candidate model:'''
from rest_framework import serializers
from .models import Candidate

class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ['first_name', 'email', 'mobile_number']

'''Views and Business Logic
In resume/views.py, define the view that will handle the file upload, process the resume, and extract data:'''
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import CandidateSerializer
from pyresparser import ResumeParser
from .models import Candidate
import os
from django.conf import settings

@api_view(['POST'])
def extract_resume(request):
    if 'resume' not in request.FILES:
        return Response({'error': 'Please upload a resume file.'}, status=status.HTTP_400_BAD_REQUEST)
# {fact rule=unrestricted-file-upload@v1.0 defects=1}

    resume_file = request.FILES['resume']

    # Save the resume temporarily
    file_path = os.path.join(settings.MEDIA_ROOT, resume_file.name)
# defect
    with open(file_path, 'wb+') as temp_file:
        for chunk in resume_file.chunks():
            temp_file.write(chunk)

    # Parse the resume
    parsed_data = ResumeParser(file_path).get_extracted_data()
# {/fact}

    # Clean up the temporary file
    os.remove(file_path)

    if not parsed_data:
        return Response({'error': 'Unable to extract data from resume.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Extract candidate information
    first_name = parsed_data.get('name', '').split()[0]
    email = parsed_data.get('email')
    mobile_number = parsed_data.get('mobile_number')

    # Validate and save the candidate data
    candidate_data = {
        'first_name': first_name,
        'email': email,
        'mobile_number': mobile_number
    }
    
    serializer = CandidateSerializer(data=candidate_data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

'''URL Routing
In resume/urls.py, set up the routing for the API endpoint:'''
from django.urls import path
from .views import extract_resume

urlpatterns = [
    path('extract_resume/', extract_resume, name='extract_resume'),
]

'''Now, include this URL configuration in the main ResumeProcessor/urls.py:'''
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('resume.urls')),
]

''' Media Settings
Add media configuration in ResumeProcessor/settings.py:'''
import os

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

'''Migrations
Make migrations to set up the Candidate model in PostgreSQL:'''
python manage.py makemigrations
python manage.py migrate

'''python manage.py runserver'''
python manage.py runserver

'''Example API Request
Now, you can test the API with a POST request to /api/extract_resume/ by sending a PDF or Word file as the resume field.

Example JSON response:'''
{
    "first_name": "John",
    "email": "john.doe@example.com",
    "mobile_number": "123-456-7890"
}
