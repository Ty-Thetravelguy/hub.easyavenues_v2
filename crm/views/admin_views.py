from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from ..models import NoteSubject
from ..forms import NoteSubjectForm
from django.contrib.messages.views import SuccessMessageMixin

class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to ensure user is logged in and is staff/superuser."""
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def handle_no_permission(self):
        # Optional: Redirect or show an error message
        from django.shortcuts import redirect
        from django.contrib import messages
        messages.error(self.request, "You do not have permission to access this page.")
        # Redirect to admin dashboard or another appropriate page
        # Assuming you have a dashboard URL named 'admin_dashboard' in 'accounts' app
        return redirect(reverse_lazy('accounts:admin_dashboard')) # Adjust if your dashboard URL is different

# --- Note Subject Management Views ---

class NoteSubjectListView(StaffRequiredMixin, ListView):
    model = NoteSubject
    template_name = 'crm/manage_subjects/note_subject_list.html' # Define template path
    context_object_name = 'subjects'
    paginate_by = 25 # Optional: Add pagination

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'note_subjects'
        return context

class NoteSubjectCreateView(StaffRequiredMixin, SuccessMessageMixin, CreateView):
    model = NoteSubject
    form_class = NoteSubjectForm
    template_name = 'crm/manage_subjects/note_subject_form.html'
    success_url = reverse_lazy('crm:manage_note_subject_list')
    success_message = "Note subject \"%(name)s\" was created successfully."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Create Note Subject'
        context['active_tab'] = 'note_subjects'
        return context

class NoteSubjectUpdateView(StaffRequiredMixin, SuccessMessageMixin, UpdateView):
    model = NoteSubject
    form_class = NoteSubjectForm
    template_name = 'crm/manage_subjects/note_subject_form.html'
    success_url = reverse_lazy('crm:manage_note_subject_list')
    success_message = "Note subject \"%(name)s\" was updated successfully."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Update Note Subject'
        context['active_tab'] = 'note_subjects'
        return context

class NoteSubjectDeleteView(StaffRequiredMixin, SuccessMessageMixin, DeleteView):
    model = NoteSubject
    template_name = 'crm/manage_subjects/note_subject_confirm_delete.html'
    success_url = reverse_lazy('crm:manage_note_subject_list')
    success_message = "Note subject deleted successfully." # Note: %(name)s doesn't work easily on delete

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Delete Note Subject'
        context['active_tab'] = 'note_subjects'
        return context
