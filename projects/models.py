from django.db import models
import uuid
from users.models import Profile

# Create your models here.
class Project(models.Model):
    owner = models.ForeignKey(Profile, blank=True, null=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    featured_image = models.ImageField(null=True, blank=True, default='default.jpg')
    demo_link = models.CharField(max_length=2000, null=True, blank=True)
    source_link = models.CharField(max_length=2000, null=True, blank=True)
    tags = models.ManyToManyField('Tag', blank=True)
    vote_total = models.IntegerField(default=0, null=True, blank=True)
    vote_ratio = models.IntegerField(default=0, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True, editable=False)

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ('-vote_ratio', '-vote_total', 'title', )

    @property
    def project_votes(self):
        queryset = self.review_set.all().values_list('owner__id', flat=True)
        return queryset
    
    @property
    def calculate_vote_ratio(self):
        reviews = self.review_set.all()
        total_votes = reviews.count()
        up_votes = reviews.filter(value__exact='up').count()

        ratio = (up_votes / total_votes) * 100
        self.vote_ratio = ratio
        self.vote_total = total_votes
        self.save()

    
class Review(models.Model):
    vote_type = (('up', 'Up Vote'), ('down', 'Down Vote'))
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, null= True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    body = models.TextField(null=True, blank=True)
    value = models.CharField(max_length=200, choices=vote_type)
    created_at = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True, editable=False)

    def __str__(self):
        return self.value
    
    class Meta:
        unique_together = [['owner', 'project']]

class Tag(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True, editable=False)

    def __str__(self):
        return self.name