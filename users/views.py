from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm, ProfileForm, SkillForm, MessageForm
from .models import Profile, Skill
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .utils import search_profiles, paginate_profiles

# Create your views here.

def login_user(request):
    page = 'login'
    context = {'page': page}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist!')

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(request.GET.get('next') if request.GET.get('next') else 'account')
        else:
            messages.error(request, 'Username or Password is incorrect!')

    return render(request, 'users/login_register.html', context)

def logout_user(request):
    logout(request)
    messages.info(request, 'Logged out successfully!')
    return redirect('profiles')

def register_user(request):
    page = 'register'
    form =  CustomUserCreationForm()


    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            messages.success(request, 'User was created!')

            login(request, user)
            return redirect('edit-account')
        else:
            messages.error(request, 'An error occurred during registration!')

    context = {'page': page, 'form': form}
    return render(request, 'users/login_register.html', context)

def profiles(request):
    profiles_list, search_query = search_profiles(request)
    custom_range, profiles_list = paginate_profiles(request, profiles_list, 1)
    context = {'profiles': profiles_list, 'search_query': search_query, 'custom_range': custom_range}
    return render(request, 'users/profiles.html', context)

def user_profile(request, pk):
    profile_obj = Profile.objects.get(id=pk)
    top_skills = profile_obj.skill_set.exclude(description__exact="")
    other_skills = profile_obj.skill_set.filter(description__exact= "")
    context = {'profile': profile_obj, 'top_skills': top_skills, 'other_skills': other_skills}
    return render(request, 'users/user_profile.html', context)

@login_required(login_url='login')
def user_account(request):
    profile = request.user.profile
    skills = profile.skill_set.all()
    projects = profile.project_set.all()
    context = {'profile': profile, 'skills': skills, 'projects': projects}
    return render(request, 'users/account.html', context)

@login_required(login_url='login')
def edit_account(request):
    profile = request.user.profile
    form = ProfileForm(instance=profile)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('account')
        
    context = {'form': form}
    return render(request, 'users/profile_form.html', context)

@login_required(login_url='login')
def create_skill(request):
    profile = request.user.profile
    form = SkillForm()
    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.owner = profile
            skill.save()
            messages.success(request, 'Skill was added successfully!')
            return redirect('account')
    context = {'form': form}
    return render(request, 'users/skill_form.html', context)

@login_required(login_url='login')
def update_skill(request, pk):
    profile = request.user.profile
    skill = profile.skill_set.get(id=pk)
    form = SkillForm(instance=skill)
    if request.method == 'POST':
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            messages.success(request, 'Skill was updated successfully!')
            return redirect('account')
    context = {'form': form}
    return render(request, 'users/skill_form.html', context)

@login_required(login_url='login')
def delete_skill(request, pk):
    profile = request.user.profile
    skill = profile.skill_set.get(id=pk)
    if request.method == 'POST':
        skill.delete()
        messages.success(request, 'Skill was deleted successfully')
        return redirect('account')
    context = {'object':skill}
    return render(request, 'delete_template.html', context)

@login_required(login_url='login')
def inbox(request):
    profile = request.user.profile
    messages_list = profile.messages.all()
    unread_messages_count = profile.messages.filter(is_read=False).count()
    context = {'messages_list': messages_list, 'unread_messages_count': unread_messages_count}
    return render(request, 'users/inbox.html', context)

@login_required(login_url='login')
def view_message(request, pk):
    profile = request.user.profile
    message = profile.messages.get(id=pk)
    if message.is_read == False:
        message.is_read = True
        message.save()
    context = {'message': message}
    return render(request, 'users/message.html', context)

def create_message(request, pk):
    recipient = Profile.objects.get(id=pk)
    try:
        sender = request.user.profile
    except:
        sender = None

    form = MessageForm()
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.recipient = recipient

            if sender:
                message.sender = sender
            message.save()
            messages.success(request, 'Message was sent')
            return redirect('user-profile', recipient.id)
    context = {'recipient': recipient, 'form': form}
    return render(request, 'users/message_form.html', context)