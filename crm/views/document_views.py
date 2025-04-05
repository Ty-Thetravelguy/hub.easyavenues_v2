from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import os

from crm.models import Company, Document, Activity
from crm.forms import DocumentUploadForm

@login_required
def document_upload(request, company_id):
    """
    Handle document uploads for a company
    """
    company = get_object_or_404(Company, id=company_id)
    
    # Check if user has permission (superuser, admin, or marketing)
    if request.user.role not in ['superuser', 'admin', 'marketing']:
        messages.error(request, "You don't have permission to upload documents.")
        return redirect('crm:company_detail', pk=company_id)
    
    if request.method == 'POST':
        # Validate file size (limit to 10MB)
        if 'file' in request.FILES:
            file = request.FILES['file']
            
            # Size validation
            if file.size > 10 * 1024 * 1024:  # 10MB in bytes
                messages.error(request, "File size exceeds the 10MB limit. Please upload a smaller file.")
                return redirect('crm:document_upload', company_id=company_id)
            
            # File type validation
            ext = os.path.splitext(file.name)[1].lower()
            allowed_extensions = [
                '.pdf', '.doc', '.docx', '.xls', '.xlsx', 
                '.ppt', '.pptx', '.txt', '.csv', '.rtf', '.odt', '.ods'
            ]
            
            if ext not in allowed_extensions:
                messages.error(request, f"Unsupported file type. Allowed file types: {', '.join(allowed_extensions)}")
                return redirect('crm:document_upload', company_id=company_id)
                
        # Create a new document
        document = Document(
            company=company,
            title=request.POST['title'],
            document_type=request.POST['document_type'],
            file=request.FILES['file'],
            uploaded_by=request.user,
            description=request.POST.get('description', ''),
            version=request.POST.get('version', '')
        )
        
        # Handle expiry date if provided
        expiry_date = request.POST.get('expiry_date')
        if expiry_date:
            document.expiry_date = expiry_date
            
        document.save()
        
        # Create activity record for document upload
        Activity.objects.create(
            company=company,
            activity_type='document',
            description=f"Uploaded document: {document.title}",
            performed_by=request.user,
            is_system_activity=True
        )
        
        messages.success(request, f"Document '{document.title}' uploaded successfully.")
        return redirect('crm:company_detail', pk=company_id)
    
    # Handle GET request - render a form
    context = {
        'company': company,
        'document_types': Document.DOCUMENT_TYPES
    }
    return render(request, 'crm/document_upload.html', context)

@login_required
def document_delete(request, document_id):
    """
    Delete a document
    """
    document = get_object_or_404(Document, id=document_id)
    company_id = document.company.id
    
    # Check if user has permission (superuser, admin, or marketing)
    if request.user.role not in ['superuser', 'admin', 'marketing']:
        messages.error(request, "You don't have permission to delete documents.")
        return redirect('crm:company_detail', pk=company_id)
    
    # Only allow POST requests for deletion
    if request.method != 'POST':
        messages.error(request, "Invalid request method for document deletion.")
        return redirect('crm:company_detail', pk=company_id)
    
    document_title = document.title
    
    # Delete the document
    document.delete()
    
    # Create activity record for document deletion
    Activity.objects.create(
        company=document.company,
        activity_type='document',
        description=f"Deleted document: {document_title}",
        performed_by=request.user,
        is_system_activity=True
    )
    
    messages.success(request, f"Document '{document_title}' deleted successfully.")
    return redirect('crm:company_detail', pk=company_id)

@login_required
def document_detail(request, document_id):
    """
    View detailed information about a document
    """
    document = get_object_or_404(Document, id=document_id)
    company = document.company
    
    # Check if user has permission
    if request.user.role not in ['superuser', 'admin', 'marketing', 'operations']:
        messages.error(request, "You don't have permission to view document details.")
        return redirect('crm:company_detail', pk=company.id)
    
    context = {
        'document': document,
        'company': company,
    }
    return render(request, 'crm/document_detail.html', context)

@login_required
def document_update(request, document_id):
    """
    Update document details
    """
    document = get_object_or_404(Document, id=document_id)
    company = document.company
    
    # Check if user has permission
    if request.user.role not in ['superuser', 'admin', 'marketing']:
        messages.error(request, "You don't have permission to update documents.")
        return redirect('crm:company_detail', pk=company.id)
    
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            updated_document = form.save(commit=False)
            
            # If a new file is uploaded, handle it
            if 'file' in request.FILES:
                file = request.FILES['file']
                
                # Size validation
                if file.size > 10 * 1024 * 1024:  # 10MB in bytes
                    messages.error(request, "File size exceeds the 10MB limit. Please upload a smaller file.")
                    return redirect('crm:document_update', document_id=document_id)
                
                # File type validation
                ext = os.path.splitext(file.name)[1].lower()
                allowed_extensions = [
                    '.pdf', '.doc', '.docx', '.xls', '.xlsx', 
                    '.ppt', '.pptx', '.txt', '.csv', '.rtf', '.odt', '.ods'
                ]
                
                if ext not in allowed_extensions:
                    messages.error(request, f"Unsupported file type. Allowed file types: {', '.join(allowed_extensions)}")
                    return redirect('crm:document_update', document_id=document_id)
            
            updated_document.save()
            
            # Create activity record for document update
            Activity.objects.create(
                company=company,
                activity_type='document',
                description=f"Updated document: {document.title}",
                performed_by=request.user,
                is_system_activity=True
            )
            
            messages.success(request, f"Document '{document.title}' updated successfully.")
            return redirect('crm:document_detail', document_id=document.id)
    else:
        form = DocumentUploadForm(instance=document)
    
    context = {
        'form': form,
        'document': document,
        'company': company,
    }
    return render(request, 'crm/document_update.html', context) 