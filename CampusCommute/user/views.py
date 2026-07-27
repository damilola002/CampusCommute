from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.contrib import messages
from .models import CustomerUser, VerificationCode
import random


def login_user(request):
    if request.method == "POST":
        email_entered    = request.POST['email']
        password_entered = request.POST['password']
        user = authenticate(request, username=email_entered, password=password_entered)
        if user is not None:
            # Generate 2FA code
            code = f"{random.randint(1000, 9999)}"
            
            # Deactivate previous 2FA codes for this user
            VerificationCode.objects.filter(email=user.email, purpose='two_factor').update(is_used=True)
            
            # Save the code
            VerificationCode.objects.create(
                email=user.email,
                code=code,
                purpose='two_factor'
            )
            
            # Send email code (prints to console in local settings)
            send_mail(
                'CampusCommute Login Verification Code',
                f'Your 2-Factor Authentication code is: {code}\nThis code will expire in 10 minutes.',
                'noreply@campuscommute.com',
                [user.email],
                fail_silently=False,
            )
            
            # Put the user's ID in the session to track pre-2FA login state
            request.session['pre_2fa_user_id'] = user.id
            return redirect('user:verify_2fa')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')


def verify_2fa(request):
    user_id = request.session.get('pre_2fa_user_id')
    if not user_id:
        return redirect('user:login')

    try:
        user = CustomerUser.objects.get(id=user_id)
    except CustomerUser.DoesNotExist:
        return redirect('user:login')

    if request.method == 'POST':
        code_entered = request.POST.get('code')
        
        # Get the latest unused code for this email and purpose
        code_obj = VerificationCode.objects.filter(
            email=user.email,
            purpose='two_factor',
            is_used=False
        ).order_by('-created_at').first()

        if code_obj and not code_obj.is_expired() and code_obj.code == code_entered:
            # Mark code as used and log the user in
            code_obj.is_used = True
            code_obj.save()
            
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            # Clean up pre-2FA session state
            del request.session['pre_2fa_user_id']
            return redirect('community_board')
        else:
            return render(request, 'verify_2fa.html', {'error': 'Invalid or expired verification code.'})

    return render(request, 'verify_2fa.html')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = CustomerUser.objects.get(email=email)
            # Generate code
            code = f"{random.randint(1000, 9999)}"
            
            # Deactivate previous reset codes for this email
            VerificationCode.objects.filter(email=email, purpose='password_reset').update(is_used=True)
            
            # Save the code
            VerificationCode.objects.create(
                email=email,
                code=code,
                purpose='password_reset'
            )
            
            # Send email code (prints to console in local settings)
            send_mail(
                'CampusCommute Password Reset Code',
                f'Your password reset verification code is: {code}\nThis code will expire in 10 minutes.',
                'noreply@campuscommute.com',
                [email],
                fail_silently=False,
            )
            return render(request, 'reset_password.html', {'email': email})
        except CustomerUser.DoesNotExist:
            return render(request, 'forgot_password.html', {'error': 'No account associated with this email.'})

    return render(request, 'forgot_password.html')


def reset_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        code_entered = request.POST.get('code')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            return render(request, 'reset_password.html', {'email': email, 'error': 'Passwords do not match.'})

        # Check code
        code_obj = VerificationCode.objects.filter(
            email=email,
            purpose='password_reset',
            is_used=False
        ).order_by('-created_at').first()

        if code_obj and not code_obj.is_expired() and code_obj.code == code_entered:
            try:
                user = CustomerUser.objects.get(email=email)
                user.set_password(new_password)
                user.save()
                
                # Mark code as used
                code_obj.is_used = True
                code_obj.save()
                
                # Log them in automatically
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                return redirect('community_board')
            except CustomerUser.DoesNotExist:
                return render(request, 'reset_password.html', {'email': email, 'error': 'User not found.'})
        else:
            return render(request, 'reset_password.html', {'email': email, 'error': 'Invalid or expired verification code.'})

    return redirect('user:forgot_password')


def register_user(request):
    if request.method == "POST":
        email_entered    = request.POST['email']
        password_entered = request.POST['password']
        username_entered = request.POST['username']
        full_name_entered = request.POST.get('full_name', '')
        role_entered     = request.POST.get('role', 'rider')

        if role_entered not in ('rider', 'driver'):
            role_entered = 'rider'

        user = CustomerUser.objects.create_user(
            username=username_entered,
            email=email_entered,
            password=password_entered,
            full_name=full_name_entered,
            role=role_entered,
        )
        if user is not None:
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('community_board')
        else:
            return render(request, 'signup.html', {'error': 'Something went wrong. Please try again.'})

    return render(request, 'signup.html')

from django.contrib.auth.decorators import login_required
@login_required
def profile_view(request):
    if request.method == 'POST':
        user = request.user
        user.bio = request.POST.get('bio', user.bio)
        user.vehicle_model = request.POST.get('vehicle_model', user.vehicle_model)
        user.vehicle_type = request.POST.get('vehicle_type', user.vehicle_type)
        if request.POST.get('vehicle_year'):
            user.vehicle_year = request.POST.get('vehicle_year')
        user.license_plate = request.POST.get('license_plate', user.license_plate)
        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']
        user.save()
        return redirect('user:profile')
    return render(request, 'profile.html')

def home_redirect(request):
    if request.user.is_authenticated:
        return redirect('community_board')
    return redirect('user:login')
