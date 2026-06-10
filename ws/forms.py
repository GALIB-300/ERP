from django import forms
from .models import Ws

class WsForm(forms.ModelForm):
    class Meta:
        model = Ws
        fields = [
            'project_name_ws',
            'task_name_ws',
            'planned_start',
            'planned_finish',
            'start_date',
            'finish_date',
            'actual_progress',
        ]
        labels = {
            'project_name_ws': 'Project Name',
            'task_name_ws': 'Task Name',
            'planned_start': 'Planned Start',
            'planned_finish': 'Planned Finish',
            'start_date': 'Start Date',
            'finish_date': 'Finish Date',
            'actual_progress': 'Actual Progress',
        }
        widgets = {
            'project_name_ws': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter project name'
            }),
            'task_name_ws': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter task name'
            }),
            'planned_start': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'planned_finish': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'finish_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'actual_progress': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter actual progress (%)'
            }),
        }

