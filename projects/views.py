from django.shortcuts import redirect, render
from django.contrib import messages
from django.http import HttpResponse
from .models import Project, Tag
from .forms import ProjectForm, ReviewForm
from django.contrib.auth.decorators import login_required
from .utils import search_projects, paginate_projects


# Create your views here.

def projects(request):
    projects_list, search_query = search_projects(request)
    custom_range, projects_list = paginate_projects(request, projects_list, 3)

    context = {'page': 'Projects', 'number': 10,  'projects': projects_list, 'custom_range': custom_range, 'search_query': search_query}
    return render(request, 'projects/projects.html', context)

def project(request, pk):
    project_obj = Project.objects.get(id = pk)
    form = ReviewForm()
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.owner = request.user.profile
            review.project = project_obj
            review.save()
            messages.success(request, 'Review was submitted!')
            project_obj.calculate_vote_ratio
            return redirect('project', project_obj.id)
    context = {"project": project_obj, 'form': form}
    return render(request, 'projects/single_project.html', context)

@login_required(login_url='login')
def create_project(request):
    profile = request.user.profile
    form = ProjectForm()
    if request.method == 'POST':
        project = ProjectForm(request.POST, request.FILES)
        project = project.save(commit=False)
        project.owner = profile
        project.save()
        return redirect('projects')
    context = {'form': form}
    return render(request, "projects/project_form.html", context)

@login_required(login_url='login')
def update_project(request, pk):
    profile = request.user.profile
    project = profile.project_set.get(id=pk)
    form = ProjectForm(instance=project)
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project)
        form.save()
        return redirect('projects')
    context = {'form': form}
    return render(request, 'projects/project_form.html', context)

@login_required(login_url='login')
def delete_project(request, pk):
    profile = request.user.profile
    project = profile.project_set.get(id=pk)
    if request.method == 'POST':
        project.delete()
        return redirect('projects')
    context = {'object': project}
    return render(request, 'delete_template.html', context)