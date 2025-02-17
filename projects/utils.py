from .models import Tag, Project
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

def paginate_projects(request, projects_list, results):
    page = request.GET.get('page')
    paginator = Paginator(projects_list, results)
    try:
        projects_list = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        projects_list = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages
        projects_list = paginator.page(page)
    
    left_index = (int(page) - 1)

    if left_index < 1:
        left_index = 1
    
    right_index = (int(page) + 2)

    if right_index> paginator.num_pages:
        right_index = paginator.num_pages + 1

    custom_range = range(left_index, right_index)

    return custom_range, projects_list

def search_projects(request):
    search_query = ''
    if request.GET.get('search_query'):
        search_query = request.GET.get('search_query')

    tags = Tag.objects.filter(name__icontains=search_query)

    projects_list = Project.objects.distinct().filter(
        Q(title__icontains=search_query) |
        Q(description__icontains=search_query) |
        Q(owner__name__icontains=search_query) |
        Q(tags__in=tags)
    )
    return projects_list, search_query