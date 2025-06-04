

from django.db import models
from django.conf import settings
from django.utils.timezone import now
from django.contrib.auth.models import AbstractUser

# Custom User Model
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('team_member', 'Team Member'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='team_member')

    def __str__(self):
        return self.username

###################################################################################################
# Project Model
class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=[
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
    ], default='in_progress')

    assigned_members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='projects')

    def __str__(self):
        return self.name

###################################################################################################
# Milestone Model
class Milestone(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="milestones")
    name = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=50, choices=[
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ], default='not_started')

    def __str__(self):
        return f"{self.name} - {self.project.name}"

    def progress_percentage(self):
        tasks = self.tasks.all()
        if tasks.count() == 0:
            return 0
        completed_tasks = tasks.filter(status='completed').count()
        return (completed_tasks / tasks.count()) * 100

###################################################################################################
# Task Model
class Task(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    deadline = models.DateField()
    status = models.CharField(max_length=50, choices=[
        ('to_do', 'To Do'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ], default='to_do')

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tasks')
    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE, related_name='tasks', null=True, blank=True)  # Optional link to a milestone

    def __str__(self):
        return self.name

###################################################################################################
# Notes Model
class Notes(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="notes")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Note by {self.author.username} on {self.project.name}"

###################################################################################################
# Resource Model
class Resource(models.Model):
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=100, choices=[
        ('Developer', 'Developer'),
        ('Designer', 'Designer'),
        ('Tester', 'Tester'),
        
    ])

    def __str__(self):
        return self.name

class ResourceAllocation(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, default=None)
    assigned_date = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.resource.name} assigned to {self.assigned_to}"

###################################################################################################
# Project Manager Model
class ProjectManager(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# Team Member Model
class TeamMember(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    manager = models.ForeignKey(ProjectManager, on_delete=models.SET_NULL, null=True, blank=True, related_name="team_members")
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

############################################################################
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Feedback(models.Model):
    FEEDBACK_CHOICES = [
        ('Project', 'Project'),
        ('Task', 'Task'),
        ('Team Member', 'Team Member'),
        ('General', 'General'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Who gave the feedback
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_CHOICES)
    project = models.ForeignKey('Project', on_delete=models.SET_NULL, null=True, blank=True)
    task = models.ForeignKey('Task', on_delete=models.SET_NULL, null=True, blank=True)
    comments = models.TextField()
    rating = models.IntegerField(default=5)  # 1 to 5 rating
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.feedback_type} Feedback"


class FeedbackResponse(models.Model):
    feedback = models.OneToOneField(Feedback, on_delete=models.CASCADE)  # Link to feedback
    responder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="responses")  # Who responded
    response_text = models.TextField()
    responded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response to {self.feedback.user.username} by {self.responder.username}"
#############################################################################################################
class FileUpload(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/')
    type = models.CharField(max_length=50, choices=[('task', 'Task'), ('project', 'Project')])
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file.name} by {self.user.username}"