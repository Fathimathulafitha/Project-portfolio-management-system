from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db.models import Sum
from django.contrib.auth import login
from .models import CustomUser, Project, Task, Resource
from .forms import UserRegistrationForm, ProjectForm, TaskForm
from .decorators import role_required
from .forms import FeedbackForm  # Import FeedbackForm at the top


# Home Page
def index(request):
    return render(request, "index.html")

# Registration
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Hash password
            user.save()
            login(request, user)
            return redirect('login')  # Redirect to home/dashboard
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

# Home Page for Logged-in Users
@login_required
def home(request):
    return render(request, "home.html")

# Dashboards
from django.shortcuts import render
from .models import CustomUser, Project

@role_required(['admin'])
def admin_dashboard(request):
    total_users = CustomUser.objects.count()
    total_projects = Project.objects.count()

    completed_projects = Project.objects.filter(status='completed').count()
    in_progress_projects = Project.objects.filter(status='in_progress').count()
    pending_projects = Project.objects.filter(status='on_hold').count()

    context = {
        'total_users': total_users,
        'total_projects': total_projects,
        'completed_projects': completed_projects,
        'in_progress_projects': in_progress_projects,
        'pending_projects': pending_projects,
    }

    return render(request, 'admin_dashboard.html', context)

# @role_required(['manager'])
# def manager_dashboard(request):
#     # Get all projects
#     total_projects = Project.objects.count()
    
#     # Get projects by status (update status values to match those in the model)
#     completed_projects = Project.objects.filter(status='completed').count()  # 'completed' from model
#     ongoing_projects = Project.objects.filter(status='in_progress').count()  # 'in_progress' from model
#     pending_projects = Project.objects.filter(status='on_hold').count()  # 'on_hold' from model

#     context = {
#         'total_projects': total_projects,
#         'completed_projects': completed_projects,
#         'ongoing_projects': ongoing_projects,
#         'pending_projects': pending_projects,
#         'projects': Project.objects.all(),  # All projects for listing
#     }
    
#     return render(request, 'manager_dashboard.html', context)

############################################################################################
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone
from .models import Project, Task, User

# Custom decorator to check user role
def role_required(roles):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.role in roles:
                return view_func(request, *args, **kwargs)
            return render(request, 'access_denied.html')  # Adjust as needed
        return wrapper
    return decorator

@role_required(['manager'])
def manager_dashboard(request):
    # Get all projects
    total_projects = Project.objects.count()
    
    # Get projects by status
    completed_projects = Project.objects.filter(status='completed').count()
    ongoing_projects = Project.objects.filter(status='in_progress').count()
    pending_projects = Project.objects.filter(status='on_hold').count()

    # Get all tasks
    tasks = Task.objects.all()

    # Get all users for task assignment
    users = User.objects.all()

    # Additional context for charts
    total_tasks = tasks.count()
    overdue_tasks = tasks.filter(deadline__lt=timezone.now(), status__in=['to_do', 'in_progress']).count()
    alice_tasks = tasks.filter(assigned_to__username='Alice').count()
    bob_tasks = tasks.filter(assigned_to__username='Bob').count()
    charlie_tasks = tasks.filter(assigned_to__username='Charlie').count()

    context = {
        'total_projects': total_projects,
        'completed_projects': completed_projects,
        'ongoing_projects': ongoing_projects,
        'pending_projects': pending_projects,
        'projects': Project.objects.all(),
        'tasks': tasks,
        'users': users,
        'total_tasks': total_tasks,
        'overdue_tasks': overdue_tasks,
        'alice_tasks': alice_tasks,
        'bob_tasks': bob_tasks,
        'charlie_tasks': charlie_tasks,
    }
    
    return render(request, 'manager_dashboard.html', context)
###########################################################################################################################

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Project, Task, ResourceAllocation, Feedback, Notes

@login_required
def team_member_dashboard(request):
    tasks = Task.objects.filter(assigned_to=request.user)
    context = {
        'user': request.user,
        'projects': Project.objects.filter(assigned_members=request.user),
        'tasks': tasks,
        'resources': ResourceAllocation.objects.filter(assigned_to=request.user),
        'notes': Notes.objects.filter(project__assigned_members=request.user).order_by('-created_at')[:5],
        'total_tasks': tasks.count(),
        'pending_tasks': tasks.filter(status='to_do').count(),
        'ongoing_tasks': tasks.filter(status='in_progress').count(),
        'completed_tasks': tasks.filter(status='completed').count(),
    }
    return render(request, 'team_member_dashboard.html', context)

#########################################################################################
@login_required
def profile(request):
    if request.method == 'POST':
        # Handle profile updates (e.g., email, avatar)
        request.user.email = request.POST.get('email', request.user.email)
        request.user.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('app:profile')
    return render(request, 'profile.html', {'user': request.user})



# Project Management
@login_required
@role_required(['admin', 'manager'])
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            # Save the form with commit=False to get the project instance
            project = form.save(commit=False)
            project.save()
            
            # Now save the many-to-many data
            form.save_m2m()
            
            return redirect('admin_dashboard')
    else:
        form = ProjectForm()
    
    # Get all users who can be assigned to projects (team members and managers)
    users = CustomUser.objects.filter(role__in=['team_member', 'manager'])
    
    return render(request, 'create_project.html', {'form': form, 'users': users})
@login_required
def project_details(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    # Check if user has access to this project
    if request.user.role != 'admin' and request.user not in project.assigned_members.all():
        messages.error(request, "You don't have permission to access this project.")
        return redirect('team_member_dashboard')
    
    context = {
        'project': project,
        'tasks': Task.objects.filter(project=project),
        'notes': Notes.objects.filter(project=project)
    }
    return render(request, 'project_details.html', context)
# Task Management
# views.py
@login_required
@role_required(['admin', 'manager'])
def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()  # Save to database
            messages.success(request, 'Task created successfully!')
            return redirect('manager_dashboard')
        else:
            messages.error(request, 'Error creating task. Check the form.')  # Show errors
    else:
        form = TaskForm()
    
    return render(request, 'create_task.html', {'form': form})


@login_required
@role_required(['team_member'])
def update_task_status(request, task_id):
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user)
    if request.method == 'POST':
        task.status = request.POST.get('status')
        task.save()
        return redirect('team_member_dashboard')
    return HttpResponseForbidden("You are not authorized to update this task.")

@login_required
def task_details(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    # Check if user has access to this task
    if request.user.role != 'admin' and request.user != task.assigned_to and request.user not in task.project.assigned_members.all():
        messages.error(request, "You don't have permission to access this task.")
        return redirect('team_member_dashboard')
    
    context = {
        'task': task
    }
    return render(request, 'task_details.html', context)
# Resource Allocation Dashboard
@login_required
@role_required(['manager'])
def resource_dashboard(request):
    # Get the manager's assigned projects
    manager_projects = Project.objects.filter(assigned_members=request.user)

    # Get all team members working under this manager
    team_members = CustomUser.objects.filter(projects__in=manager_projects).distinct()

    # Fetch only resources allocated to team members under this manager
    allocations = ResourceAllocation.objects.filter(assigned_to__in=team_members)

    context = {
        'allocations': allocations,
    }
    return render(request, 'resource_dashboard.html', context)

# User Management
def users_list(request):
    users = CustomUser.objects.all()
    return render(request, 'users.html', {'users': users})

#adminhome
def adminhome(request):
   return render(request, "adminhome.html")

#projectmanagers
from django.shortcuts import render
from app.models import CustomUser  # Import your CustomUser model

def projectmanagers(request):
    managers = CustomUser.objects.filter(role='manager')  # Fetch only managers
    return render(request, "projectmanagers.html", {"managers": managers})


#projects

@login_required
def projects(request):
    if request.user.role == 'admin':
        # Admin sees all projects
        projects = Project.objects.all()
    elif request.user.role == 'manager':
        # Manager sees projects they're associated with
        projects = Project.objects.filter(assigned_members=request.user)
    else:
        # Team members only see projects they're assigned to
        projects = Project.objects.filter(assigned_members=request.user)
    
    context = {
        'projects': projects
    }
    return render(request, 'projects.html', context)


#tasks

@login_required
def tasks(request):
    if request.user.role == 'admin':
        # Admin sees all tasks
        tasks = Task.objects.all()
    elif request.user.role == 'manager':
        # Manager sees tasks in their projects
        tasks = Task.objects.filter(project__assigned_members=request.user)
    else:
        # Team members only see tasks assigned to them
        tasks = Task.objects.filter(assigned_to=request.user)
    
    context = {
        'tasks': tasks
    }
    return render(request, 'tasks.html', context)

#resources
from django.shortcuts import render
from .models import ResourceAllocation, Resource, CustomUser

def manage_resources(request):
    resources = Resource.objects.all()
    users = CustomUser.objects.all()
    allocations = ResourceAllocation.objects.all()
    
    context = {
        'resources': resources,
        'users': users,
        'allocations': allocations
    }
    return render(request, 'manage_resources.html', context)

#assign resource
from django.shortcuts import render, redirect
from .models import Resource, CustomUser, ResourceAllocation
from django.utils.timezone import now

def assign_resource(request):
    if request.method == "POST":
        resource_id = request.POST.get("resource")
        user_id = request.POST.get("assigned_to")
        resource = Resource.objects.get(id=resource_id)
        user = CustomUser.objects.get(id=user_id)

        # Create the allocation
        ResourceAllocation.objects.create(resource=resource, assigned_to=user, assigned_date=now())

        return redirect("manage_resources")  # Redirect back to resource management page

    resources = Resource.objects.all()
    users = CustomUser.objects.all()
    
    return render(request, "assign_resource.html", {"resources": resources, "users": users})
###################################################################################################################

#pdf report view

from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import ResourceAllocation  # Ensure this model exists

def generate_pdf_report(request):
    template_path = "report_pdf_template.html"  # Ensure this template exists
    allocations = ResourceAllocation.objects.all()

    context = {"allocations": allocations}
    template = get_template(template_path)
    html = template.render(context)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="resource_allocations.pdf"'

    # Convert HTML to PDF
    pisa_status = pisa.CreatePDF(BytesIO(html.encode("UTF-8")), dest=response)

    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)

    return response

from django.shortcuts import render
from django.shortcuts import render
from app.models import ResourceAllocation  # Import your model

def report_pdf_template(request):
    allocations = ResourceAllocation.objects.all()  # Fetch allocations from DB
    context = {"allocations": allocations}  # Pass data to template
    return render(request, "report_pdf_template.html", context)

###########################################################################################################
from django.shortcuts import render, redirect
from .models import TeamMember, ProjectManager
from .forms import AssignTeamMemberForm

def assign_team_members(request):
    if request.method == "POST":
        form = AssignTeamMemberForm(request.POST)
        if form.is_valid():
            manager = form.cleaned_data['manager']
            team_members = form.cleaned_data['team_members']

            for member in team_members:
                member.manager = manager
                member.save()

            return redirect('view_assigned_team')

    else:
        form = AssignTeamMemberForm()

    return render(request, 'assign_team.html', {'form': form})

def view_assigned_team(request):
    managers = ProjectManager.objects.prefetch_related('team_members')
    return render(request, 'view_assigned_team.html', {'managers': managers})

###############################################################################
#manager dashboasd milestone

from django.shortcuts import render, redirect, get_object_or_404
from .models import Milestone, Project
from .forms import MilestoneForm
from django.contrib.auth.decorators import login_required
from .decorators import role_required

@login_required
@role_required(['admin', 'manager'])
def create_milestone(request):
    if request.method == 'POST':
        form = MilestoneForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('project_details', project_id=form.cleaned_data['project'].id)
    else:
        form = MilestoneForm()
    return render(request, 'create_milestone.html', {'form': form})

@login_required
def milestone_progress(request, milestone_id):
    milestone = get_object_or_404(Milestone, id=milestone_id)
    progress = milestone.progress_percentage()
    return render(request, 'milestone_progress.html', {'milestone': milestone, 'progress': progress})

##############################################
#TEAM MEMBER DASHBOARD
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Project, Task, ResourceAllocation, Notes
from .decorators import role_required
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Project, Task, ResourceAllocation, Notes
from .decorators import role_required

# @login_required
# @role_required(['team_member'])
# def team_member_dashboard(request):
#     user = request.user  # Get the logged-in user

#     projects = Project.objects.filter(assigned_members=user)  # Projects assigned to this user
#     tasks = Task.objects.filter(assigned_to=user)  # Tasks assigned to this user
#     resources = ResourceAllocation.objects.filter(assigned_to=user)  # Resources allocated
#     notes = Notes.objects.filter(project__in=projects) if projects.exists() else Notes.objects.none()

#     context = {
#         'projects': projects,
#         'tasks': tasks,
#         'resources': resources,
#         'notes': notes
#     }
#     return render(request, 'team_member_dashboard.html', context)

#######################################################################################################
from django.shortcuts import render, redirect, get_object_or_404
from .models import Feedback, FeedbackResponse
from .forms import FeedbackResponseForm
from django.contrib.auth.decorators import login_required

@login_required
def submit_feedback(request): 
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user  # Associate feedback with logged-in user
            feedback.save()
            return redirect('feedback_list')  # Redirect to feedback list after submission
    else:
        form = FeedbackForm()
    return render(request, 'feedback_form.html', {'form': form})

@login_required
def feedback_list(request):
    feedbacks = Feedback.objects.all().order_by('-created_at')  # Show latest feedback first
    return render(request, 'feedback_list.html', {'feedbacks': feedbacks})

@login_required
def respond_to_feedback(request, feedback_id):
    feedback = get_object_or_404(Feedback, id=feedback_id)
    
    # Ensure that only managers or admins can respond
    if not request.user.is_staff and not request.user.is_superuser:
        return redirect('feedback_list')  # Redirect if user is not authorized
    
    if request.method == "POST":
        form = FeedbackResponseForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.feedback = feedback
            response.responder = request.user
            response.save()
            return redirect('feedback_list')
    else:
        form = FeedbackResponseForm()
    
    return render(request, 'respond_feedback.html', {'form': form, 'feedback': feedback})

########################################################################################################3333333333333333333

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.http import JsonResponse
from .models import Project, Task, ResourceAllocation, Notes, FileUpload
from .decorators import role_required  # Assuming you have this decorator
import json

@login_required
@role_required(['team_member'])
def team_member_dashboard(request):
    user = request.user
    projects = Project.objects.filter(assigned_members=user)
    tasks = Task.objects.filter(assigned_to=user)
    resources = ResourceAllocation.objects.filter(assigned_to=user)
    notes = Notes.objects.filter(project__in=projects) if projects.exists() else Notes.objects.none()

    # Task statistics
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(status='Completed').count()
    pending_tasks = tasks.filter(status='Pending').count()
    ongoing_tasks = tasks.filter(status='Ongoing').count()

    context = {
        'user': user,
        'projects': projects,
        'tasks': tasks,
        'resources': resources,
        'notes': notes,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'ongoing_tasks': ongoing_tasks,
    }
    return render(request, 'team_member_dashboard.html', context)

@login_required
@role_required(['team_member'])
def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        file_type = request.POST.get('type', 'task')
        if file.size > 5 * 1024 * 1024:
            messages.error(request, f'File {file.name} exceeds 5MB limit.')
        else:
            FileUpload.objects.create(user=request.user, file=file, type=file_type)
            messages.success(request, f'File {file.name} uploaded successfully.')
        return redirect('team_member_dashboard')
    messages.error(request, 'Invalid file upload request.')
    return redirect('team_member_dashboard')
@login_required
def update_task_status(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    # Check if user has permission to update this task
    if request.user.role != 'admin' and request.user != task.assigned_to:
        messages.error(request, "You don't have permission to update this task.")
        return redirect('team_member_dashboard')
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        # Map UI status names to model status choices
        status_mapping = {
            'Pending': 'to_do',
            'Ongoing': 'in_progress',
            'Completed': 'completed'
        }
        
        task.status = status_mapping.get(new_status, 'to_do')
        task.save()
        messages.success(request, f"Task '{task.name}' status updated to {new_status}.")
        
        # Notify WebSocket clients
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'user_{request.user.id}',
                {
                    'type': 'data_update',
                    'message': {
                        'tasks': [{
                            'id': task.id,
                            'name': task.name,
                            'project': task.project.name,
                            'status': task.status,
                            'due_date': task.due_date.strftime('%b %d, %Y'),
                            'priority': task.priority,
                        }],
                        'task_stats': {
                            'total_tasks': Task.objects.filter(assigned_to=request.user).count(),
                            'completed_tasks': Task.objects.filter(assigned_to=request.user, status='Completed').count(),
                            'pending_tasks': Task.objects.filter(assigned_to=request.user, status='Pending').count(),
                            'ongoing_tasks': Task.objects.filter(assigned_to=request.user, status='Ongoing').count(),
                        }
                    }
                }
            )
        except Exception as e:
            # Log the error but don't interrupt the user flow
            print(f"WebSocket notification error: {e}")
    
    return redirect(request.META.get('HTTP_REFERER', 'team_member_dashboard'))
@login_required
@role_required(['team_member']) 
def get_dashboard_data(request):
    user = request.user
    projects = Project.objects.filter(assigned_members=user)
    tasks = Task.objects.filter(assigned_to=user)
    resources = ResourceAllocation.objects.filter(assigned_to=user)
    notes = Notes.objects.filter(project__in=projects) if projects.exists() else Notes.objects.none()

    data = {
        'projects': [{'id': p.id, 'name': p.name, 'status': p.status} for p in projects],
        'tasks': [{
            'id': t.id,
            'name': t.name,
            'project': t.project.name,
            'status': t.status,
            'due_date': t.due_date.strftime('%b %d, %Y'),
            'priority': t.priority or 'Normal'
        } for t in tasks],
        'resources': [{
            'id': r.id,
            'name': r.resource.name,
            'assigned_date': r.assigned_date.strftime('%b %d, %Y')
        } for r in resources],
        'notes': [{
            'id': n.id,
            'project': n.project.name,
            'content': n.content,
            'created_at': n.created_at.strftime('%b %d, %Y')
        } for n in notes],
        'task_stats': {
            'total_tasks': tasks.count(),
            'completed_tasks': tasks.filter(status='Completed').count(),
            'pending_tasks': tasks.filter(status='Pending').count(),
            'ongoing_tasks': tasks.filter(status='Ongoing').count(),
        }
    }
    return JsonResponse(data)

#####################################################################
