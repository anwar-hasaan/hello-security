from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.core.mail import send_mail
from django.conf import settings
import random
from cryptography.fernet import Fernet
from mechanize import Browser
import favicon
from .models import Password

Browser = Browser()
Browser.set_handle_robots(False)
Fernet = Fernet(settings.KEY)

# Create your views here.
def home(request):   
    if request.method == 'POST':
        ######## Signup section #########
        if 'signup-form' in request.POST:
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            password2 = request.POST.get('password2')
            if password != password2:
                msg = "Make sure you're using same password."
                messages.error(request, msg)
                return HttpResponseRedirect(request.path)
            elif len(password) < 8:
                msg = "Use atleast 8 (digit, symbal, special character) character password"
                messages.error(request, msg)
                return HttpResponseRedirect(request.path)
            elif User.objects.filter(username=username).exists():
                msg = f"\"{username}\" already exists, try another."
                messages.error(request, msg)
                return HttpResponseRedirect(request.path)
            elif User.objects.filter(email=email).exists():
                msg = f"{email} already exists, try another."
                messages.error(request, msg)
                return HttpResponseRedirect(request.path)
            else:
                user_obj = User.objects.create_user(username=username, email=email)
                user_obj.set_password(password)
                user_obj.save()
                new_user = authenticate(request, username=username, password=password)
                if new_user is not None:
                    code  = str(random.randint(100000, 999999))
                    send_mail(
                        'Password Manager Verificatin',
                        f'Your verification code is {code}',
                        settings.EMAIL_HOST_USER,
                        [new_user.email],
                        fail_silently=False
                    )
                return render(request, 'index.html', {'code': int(code)+555555, 'email': new_user.email, })
        ######## Login section #########
        elif 'login-form' in request.POST:
            username = request.POST.get('username')
            password = request.POST.get('password')
            user_data = authenticate(request, username=username, password=password)
            if user_data is not None:
                code  = str(random.randint(100000, 999999))
                send_mail(
                    'Password Manager Verificatin',
                    f'Your verification code is {code}',
                    settings.EMAIL_HOST_USER,
                    [user_data.email],
                    fail_silently=False
                )
                return render(request, 'index.html', {'code': int(code)+555555, 'email': user_data.email, })
            else:
                msg = "Invalid username or password"
                messages.error(request, msg)
                return HttpResponseRedirect(request.path)
            
        ######## verification section #########
        elif 'code-confirm' in request.POST:
            initial_code = request.POST.get('initial_code')
            initial_code = int(initial_code)-555555
            initial_code = str(initial_code)
            
            inp_code = request.POST.get('inp_code')
            email = request.POST.get('email')
            
            if initial_code  != inp_code:
                msg = "Wrong verification code, use the code you've got in your mail or try to login again"
                messages.error(request, msg)    
                return HttpResponseRedirect(request.path)
            
            elif initial_code == inp_code:
                user = User.objects.filter(email=email).first()
                login(request, user)
                msg = f"{user.username} -welcome  again."
                messages.success(request, msg)
                return HttpResponseRedirect(request.path)
            
        ######## Logout section #########
        elif 'logout' in request.POST:
            user = request.user
            if user.is_authenticated:
                msg = f"{user.username} -logged out."
                messages.success(request, msg)
                logout(request)
                return HttpResponseRedirect(request.path)
        
        ######## add accounts section #########
        elif 'add-account' in request.POST:
            url = request.POST.get('url')
            username = request.POST.get('username')
            password = request.POST.get('password')
            # Encrypted 
            encrypted_username = Fernet.encrypt(username.encode())
            encrypted_password = Fernet.encrypt(password.encode())
            # get  the title of the site
            try:
                Browser.open(url)
                title = Browser.title()
            except:
                title = url
            try:
                icon = favicon.get(url)[0].url
            except:
                icon = "https://cdn-icons-png.flaticon.com/128/1006/1006771.png"
            
            new_account = Password.objects.create(
                user=request.user, title=title, 
                username=encrypted_username.decode(), 
                password=encrypted_password.decode(), 
                icon=icon
            )
            msg = f"{title} -added successfully."
            messages.success(request, msg)
            return HttpResponseRedirect(request.path)
        elif 'update-btn' in request.POST:
            update_id = request.POST.get('update-id')
            update_obj = Password.objects.get(id=update_id)
            update_obj.username = Fernet.decrypt(update_obj.username.encode()).decode()
            update_obj.password = Fernet.decrypt(update_obj.password.encode()).decode()
            return render(request, 'index.html', {'update_obj': update_obj, })
        
        elif 'update-password' in request.POST:
            id = request.POST.get('id')
            url = request.POST.get('url')
            username = request.POST.get('username')
            password = request.POST.get('password')
            
            encrypted_username = Fernet.encrypt(username.encode())
            encrypted_password = Fernet.encrypt(password.encode())
            
            update_obj = Password.objects.get(id=id)
            update_obj.title = url
            update_obj.username = encrypted_username.decode()
            update_obj.password = encrypted_password.decode()
            update_obj.save()
            
            msg = f"{update_obj.title} -updated."
            messages.success(request, msg)
            return HttpResponseRedirect(request.path)
            
        elif 'delete-btn' in request.POST:
            delete_id = request.POST.get('delete-id')
            delete_obj = Password.objects.get(id=delete_id)
            return render(request, 'index.html', {'delete_confirm': delete_id, 'title': delete_obj.title, })
        
        elif 'delete-confirm' in request.POST:
            delete_id = request.POST.get('delete_id')
            delete_obj = Password.objects.get(id=delete_id)
            msg = f"{delete_obj.title} -deleted."
            messages.success(request, msg)
            delete_obj.delete()
            return HttpResponseRedirect(request.path)
            
            
    if request.user.is_authenticated:
        passwords = Password.objects.filter(user=request.user)
        for password in passwords:
            password.username = Fernet.decrypt(password.username.encode()).decode()
            password.password = Fernet.decrypt(password.password.encode()).decode()
        return render(request, 'index.html', {'passwords': passwords, })        
    return render(request, 'index.html')