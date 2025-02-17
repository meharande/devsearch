from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .serializers import ProjectSerializer
from projects.models import Project, Review


@api_view(['GET', 'POST'])
def get_routes(request):
    routes = [
        {'GET': '/api/projects'},
        {'GET': '/api/projects/id'},
        {'POST': '/api/projects/id/vote'},

        {'POST': '/api/users/token'},
        {'POST': '/api/users/token/refresh'}
    ]
    return Response(routes)

@api_view(['GET'])
def get_projects(request):
    projects = Project.objects.all()
    serializer = ProjectSerializer(projects, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_project(request, pk):
    project = Project.objects.get(id=pk)
    serializer = ProjectSerializer(project)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def vote_project(request, pk):
    project = Project.objects.get(id=pk)
    user = request.user
    data = request.data
    
    review, created = Review.objects.get_or_create(
        owner = user.profile,
        project=project,
    )

    review.value = data['vote']
    review.save()

    project.calculate_vote_ratio

    serializer = ProjectSerializer(project, many=False)
    return Response(serializer.data)