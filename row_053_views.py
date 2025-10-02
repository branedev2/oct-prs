from django.shortcuts import render, redirect
from django.contrib import messages
from . models import *
# Create your views here.
def index(request):
    return render(request, 'index.html')


def about(request):
    return render(request, 'about.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email =  request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:

            if UserModel.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists')
                return redirect('register')
            else:
                UserModel.objects.create(
                    username=username,
                    email=email,
                    password=password
                    
                ).save()
                messages.success(request, 'Registration successful')
                return redirect('login')
        else:
            messages.error(request, 'Passwords do not match')
            return redirect('register')


    return render(request, 'register.html')

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        if email == 'cloud@gmail.com' and password == 'cloud':
            request.session['email']=email
            return redirect('cloudhome')
        elif UserModel.objects.filter(email=email, password=password).exists():
            request.session['email']=email
            return redirect('userhome')
        else:
            messages.error(request, 'Invalid Email or Password')
            return redirect('login')
    return render(request, 'login.html')



def userhome(request):
    return render(request, 'userhome.html')

def logout(request):
    del request.session['email']
    return redirect('index')




from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import UploadFile, RequestFile  # Assuming RequestFile model is defined
import os

# AES Encryption Function
def aes_encrypt(plain_text, aes_key):
    if isinstance(plain_text, str):
        plain_text = plain_text.encode()  # Convert string to bytes
    cipher = AES.new(aes_key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(plain_text, AES.block_size))  # Apply padding
    return cipher.iv + ct_bytes  # Return IV concatenated with ciphertext

# AES Decryption Function
def aes_decrypt(encrypted_text, aes_key):
    iv = encrypted_text[:AES.block_size]  # Extract the IV from the encrypted text
    ct = encrypted_text[AES.block_size:]  # Extract the ciphertext
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    decrypted_text = unpad(cipher.decrypt(ct), AES.block_size)  # Remove padding
    return decrypted_text.decode()  # Convert bytes back to string

# RSA Encryption Function for AES key
def rsa_encrypt(plain_text, public_key):
    rsa_cipher = PKCS1_OAEP.new(public_key)
    return rsa_cipher.encrypt(plain_text)

# RSA Decryption Function for AES key
def rsa_decrypt(encrypted_text, private_key):
    rsa_cipher = PKCS1_OAEP.new(private_key)
    return rsa_cipher.decrypt(encrypted_text)

# Django View to handle file upload
def uploadfile(request):
    email = request.session.get('email')
    
    if request.method == 'POST' and 'file' in request.FILES:
        file = request.FILES['file']
        file_name = file.name
# {fact rule=unrestricted-file-upload@v1.0 defects=1}
        
        # Save file temporarily in the server
        temp_file_path = os.path.join('static', 'assets', 'Files', file_name)
        os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)
        
# defect
        with open(temp_file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        with open(temp_file_path, 'rb') as f:
            file_data = f.read()
# {/fact}

        # AES Encryption
        aes_key = get_random_bytes(16)  # AES key (16 bytes for AES-128)
        aes_encrypted = aes_encrypt(file_data, aes_key)

        # RSA Key Generation for AES key
        rsa_key = RSA.generate(2048)
        public_key = rsa_key.publickey()
        private_key = rsa_key  # Save private key securely (e.g., for decryption later)

        # Encrypt AES key with RSA
        rsa_encrypted_key = rsa_encrypt(aes_key, public_key)

        # Save encrypted data and RSA-encrypted AES key to the database
        data = UploadFile.objects.create(
           
            filename=file_name,
            file=temp_file_path,  # Save original file path
            uploader=email,
            rsa_encrypted_key=rsa_encrypted_key,
            encrypted_data=aes_encrypted,
            private_key=private_key.export_key()  # Export private key (avoid storing it in DB)
        )
        data.save()

        # Remove the temporary file after upload
        os.remove(temp_file_path)

        # Show success message and redirect to file upload page
        messages.success(request, 'File Uploaded and Encrypted Successfully!')
        return redirect('uploadfile')

    return render(request, 'uploadfile.html')

from django.core.mail import send_mail
import random
# Django View to handle file decryption
def decryptmyfile(request, id):
    email = request.session['email']
    if RequestFile.objects.filter(fid=id,requester=email).exists():
        messages.error(request, 'File already decrypted, Check in Responses')
        return redirect('viewfiles')
    else:
        file = UploadFile.objects.get(id=id)
        
        # Decrypt AES key with RSA
        private_key = RSA.import_key(file.private_key)  # Import the private key from DB
        aes_key = rsa_decrypt(file.rsa_encrypted_key, private_key)
        
        # Decrypt AES-encrypted data
        aes_decrypted = aes_decrypt(file.encrypted_data, aes_key)

        # Define the new file path where you want to save the decrypted data
        decrypted_file_path = os.path.join('static', 'assets', 'RequestedFiles', file.filename)
        
        # Save decrypted data to a new file
        with open(decrypted_file_path, 'wb') as f:
            f.write(aes_decrypted.encode())  # Ensure data is written as bytes


      
        
        # Save the new data record in the database
        data = RequestFile.objects.create(
            fid = id,
            requester=email,
            uploader=email,
            filename=file.filename,
            file=decrypted_file_path,  # Save the new decrypted file path
            rsa_encrypted_key=file.rsa_encrypted_key,
            encrypted_data=aes_decrypted.encode(),
            private_key=file.private_key,
            status='Decrypted',
            otp=random.randint(1111,9999)
        )
        data.save()
        email_subject = 'Key Details'
        email_message = f'Hello {data.requester},\n\nWelcome To Our Website!\n\nHere are your Key details:\nEmail: {data.requester}\nKey: {data.otp}\n\nPlease keep this information safe.\n\nBest regards,\nYour Website Team'
        send_mail(email_subject, email_message, 'cse.takeoff@gmail.com', [data.requester])
        # messages.success(request, 'Key Sent Successfully!')
        messages.success(request, 'File Decrypted and Key Sent Successfully!')
        return redirect('viewfiles')




from django.core.paginator import Paginator
def viewfiles(request):
    email = request.session['email']
    
    files = UploadFile.objects.filter(uploader=email)
    paginator = Paginator(files, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'viewfiles.html',{'data':page_obj,'email':email})

def viewallfiles(request):
    # RequestFile.objects.all().delete()
    email = request.session['email']
    
    files = UploadFile.objects.all()
    paginator = Paginator(files, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'viewallfiles.html',{'data':page_obj,'email':email})


def sendrequest(request, id):
    email = request.session['email']
    if RequestFile.objects.filter(fid=id,requester=email).exists():
        messages.error(request, 'File already Requested, Check in Responses')
        return redirect('viewfiles')
    else:
        file = UploadFile.objects.get(id=id)
        data = RequestFile.objects.create(
            fid = id,
            requester=email,
            uploader=file.uploader,
            filename=file.filename,
            file=file.file,
            rsa_encrypted_key=file.rsa_encrypted_key,
            encrypted_data=file.encrypted_data,
            private_key=file.private_key,
            status='Pending',
        )
        data.save()
        messages.success(request, 'Request Sent Successfully!')
        return redirect('viewallfiles')
    
from django.db.models import Q
def viewrequests(request):
    email = request.session['email']
    requests = RequestFile.objects.filter(Q(uploader=email) 
                                          & ~Q(requester=email) 
                                          & Q(status='Pending'))
    paginator = Paginator(requests, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'viewrequests.html',{'data':page_obj})


def acceptanddecryptfile(request, id):
    email = request.session['email']
    file = RequestFile.objects.get(id=id)
     # Decrypt AES key with RSA
    private_key = RSA.import_key(file.private_key)  # Import the private key from DB
    aes_key = rsa_decrypt(file.rsa_encrypted_key, private_key)
    
    # Decrypt AES-encrypted data
    aes_decrypted = aes_decrypt(file.encrypted_data, aes_key)

    # Define the new file path where you want to save the decrypted data
    decrypted_file_path = os.path.join('static', 'assets', 'RequestedFiles', file.filename)
    
    # Save decrypted data to a new file
    with open(decrypted_file_path, 'wb') as f:
        f.write(aes_decrypted.encode())  # Ensure data is written as bytes

  
  
    file.file=decrypted_file_path  # Save the new decrypted file path
    
    file.encrypted_data=aes_decrypted.encode()
  
    file.status='Decrypted'
    file.save()
    messages.success(request, 'File Decrypted Successfully!')
    return redirect('viewrequests')
    


def viewresponses(request):
    email = request.session['email']
    data = RequestFile.objects.filter(Q(requester=email) & ~Q(otp=None))
    paginator = Paginator(data, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # return render(request, 'users.html',{'data':page_obj})
    return render(request, 'viewresponses.html',{'data':page_obj})

from django.http import FileResponse
def downloadfile(request, id):
    context = RequestFile.objects.get(id=id)
    filename=context.filename
    if request.method == 'POST':
        key = request.POST['otp']
        if int(key) == int(context.otp):
            file_path = context.file.path  # Get the file path
            file_name = context.filename.split('/')[-1]  # Extract the file name
            response = FileResponse(open(file_path, 'rb'), as_attachment=True, filename=file_name)
            return response
        else:
            messages.success(request, 'You Entered key is Wrong')
            return redirect('downloadfile', id)

    return render(request, 'downloadfile.html', {'filename': filename, 'id': id})
