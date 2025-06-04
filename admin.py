from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import *

admin.site.register(CustomUser)
admin.site.register(Project)
admin.site.register(Task)

admin.site.register(Resource)
admin.site.register(ResourceAllocation)

from django.contrib import admin
from .models import ProjectManager, TeamMember

@admin.register(ProjectManager)
class ProjectManagerAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name')  # Customize fields displayed in the admin panel
    search_fields = ('user__username', 'name')

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'manager')  
    search_fields = ('user__username', 'name', 'manager__name')
    list_filter = ('manager',)  # Add filtering for managers



# Registering Feedback and FeedbackResponse models
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'feedback_type', 'project', 'task', 'rating', 'created_at')  # Customize the fields displayed in the list view
    search_fields = ('user__username', 'project__name', 'task__name', 'feedback_type')
    list_filter = ('feedback_type', 'rating', 'created_at')  # Filter by type and rating

@admin.register(FeedbackResponse)
class FeedbackResponseAdmin(admin.ModelAdmin):
    list_display = ('feedback', 'responder', 'response_text', 'responded_at')
    search_fields = ('feedback__user__username', 'responder__username')
    list_filter = ('responded_at',)


