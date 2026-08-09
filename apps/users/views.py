from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .forms import MemberRegistrationForm, LoginForm
from .models import CustomUser
from apps.membership.models import MemberProfile
from apps.membership.views import chairman_dashboard_view

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        form = MemberRegistrationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    email = form.cleaned_data['email']
                    password = form.cleaned_data['password']
                    
                    user = CustomUser.objects.create_user(
                        email=email,
                        password=password,
                        role=CustomUser.Role.GENERAL_MEMBER
                    )

                    MemberProfile.objects.create(
                        user=user,
                        first_name=form.cleaned_data['first_name'],
                        last_name=form.cleaned_data['last_name'],
                        phone_number=form.cleaned_data['phone_number'],
                        residential_address=form.cleaned_data['residential_address'],
                        status=MemberProfile.Status.PENDING
                    )

                    messages.success(request, 'Registration successful! Your account is pending Chairman approval.')
                    return redirect('login')
            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
    else:
        form = MemberRegistrationForm()

    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.email}!')
            return redirect('dashboard_redirect')
        else:
            messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()

    return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')

@login_required
def dashboard_redirect_view(request):
    user = request.user
    if user.is_superuser or user.role == CustomUser.Role.CHAIRMAN:
        return redirect('chairman_dashboard')
    elif user.role == CustomUser.Role.FINANCIAL_SECRETARY:
        return redirect('financial_dashboard')
    elif user.role == CustomUser.Role.OTHER_EXCO:
        return redirect('exco_dashboard')
    else:
        return redirect('member_dashboard')
