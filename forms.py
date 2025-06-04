from django import forms
from .models import CustomUser
from django import forms
from .models import CustomUser
from .models import Milestone

# class UserRegistrationForm(forms.ModelForm):
#     password = forms.CharField(
#         widget=forms.PasswordInput(attrs={
#             'placeholder': 'Password',
#             'class': 'form-control with-icon',  # Add a CSS class
#             'data-icon': 'fa-lock',  # Example: Add a data attribute for icons
#         })
#     )
#     confirm_password = forms.CharField(
#         widget=forms.PasswordInput(attrs={
#             'placeholder': 'Confirm Password',
#             'class': 'form-control with-icon',
#             'data-icon': 'fa-lock',
#         })
#     )

#     class Meta:
#         model = CustomUser
#         fields = ['username', 'email', 'password', 'role']

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Set placeholders for all fields dynamically
#         for field_name, field in self.fields.items():
#             if field_name != 'role':  # Skip role field for now
#                 field.widget.attrs['placeholder'] = field.label
#             field.widget.attrs['class'] = 'form-control'  # Optional: Add a CSS class for styling

#         # Custom placeholder for the role field
#         self.fields['role'].widget.attrs['placeholder'] = 'Select Role'

#     def clean(self):
#         cleaned_data = super().clean()
#         password = cleaned_data.get("password")
#         confirm_password = cleaned_data.get("confirm_password")
#         if password != confirm_password:
#             raise forms.ValidationError("Passwords do not match!")
#Form for Project Creation (forms.py):
from django import forms
from .models import CustomUser

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password',
            'class': 'form-control with-icon',
            'data-icon': 'fa-lock',
        }),
        max_length=150,  # Limiting password length
        error_messages={
            'required': 'Password is required.',
            'max_length': 'Password must be 150 characters or fewer.',
        }
    )
    
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm Password',
            'class': 'form-control with-icon',
            'data-icon': 'fa-lock',
        }),
        max_length=150,  # Limiting confirm password length
        error_messages={
            'required': 'Please confirm your password.',
            'max_length': 'Confirmation password must be 150 characters or fewer.',
        }
    )

    username = forms.CharField(
        max_length=150,  # Setting the max length to 150
        error_messages={
            'required': 'Username is required.',
            'max_length': 'Username must be 150 characters or fewer.',
            'invalid': 'Username must consist of only letters, digits, and @/./+/-/_ characters.',
        }
    )

    email = forms.EmailField(
        error_messages={
            'required': 'Email is required.',
            'invalid': 'Enter a valid email address.',
        }
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'role']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set placeholders for all fields dynamically
        for field_name, field in self.fields.items():
            if field_name != 'role':  # Skip role field for now
                field.widget.attrs['placeholder'] = field.label
            field.widget.attrs['class'] = 'form-control'  # Optional: Add a CSS class for styling

        # Custom placeholder for the role field
        self.fields['role'].widget.attrs['placeholder'] = 'Select Role'

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        
        # Ensure the passwords match
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match!")
        
        return cleaned_data



from django import forms
from .models import Project, Task, CustomUser

class ProjectForm(forms.ModelForm):
    # Define the assigned_members field specifically for the form
    assigned_members = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.filter(role__in=['team_member', 'manager']),
        required=True
    )
    
    class Meta:
        model = Project
        fields = ['name', 'description', 'start_date', 'end_date', 'status', 'assigned_members']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

#Create a Task Form : by creating a form for admins/managers to add tasks.
from django import forms
from .models import Task

# forms.py
class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'description', 'deadline', 'project', 'assigned_to', 'status']  # Include all fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Restrict "assigned_to" to team members only
        self.fields['assigned_to'].queryset = CustomUser.objects.filter(role='team_member')
######################################################################################################
from django import forms
from .models import TeamMember, ProjectManager

class AssignTeamMemberForm(forms.Form):
    manager = forms.ModelChoiceField(queryset=ProjectManager.objects.all(), label="Select Manager")
    team_members = forms.ModelMultipleChoiceField(queryset=TeamMember.objects.filter(manager__isnull=True), widget=forms.CheckboxSelectMultiple, label="Select Team Members")


#################################################################################################################
#milestone
class MilestoneForm(forms.ModelForm):
    class Meta:
        model = Milestone
        fields = ['project', 'name', 'description', 'start_date', 'end_date', 'status']


############################################################################################3
from django import forms
from .models import Feedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['feedback_type', 'project', 'task', 'comments', 'rating']
        widgets = {
            'feedback_type': forms.Select(attrs={'class': 'form-control'}),
            'project': forms.Select(attrs={'class': 'form-control'}),
            'task': forms.Select(attrs={'class': 'form-control'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter your feedback'}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
        }


from django import forms
from .models import FeedbackResponse

class FeedbackResponseForm(forms.ModelForm):
    class Meta:
        model = FeedbackResponse
        fields = ['response_text']
        widgets = {
            'response_text': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter your response'}),
        }

###################################################################################################################################
# from django import forms
# from .models import Manager, TeamMember

# class AssignMembersForm(forms.Form):
#     manager = forms.ModelChoiceField(
#         queryset=Manager.objects.all(), 
#         label="Select Manager"
#     )
#     members = forms.ModelMultipleChoiceField(
#         queryset=TeamMember.objects.all(),
#         widget=forms.CheckboxSelectMultiple,  # Allows multiple selection
#         label="Select Team Members"
#     )
