from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.users.models import CustomUser
from .models import Document

@login_required
def document_list_view(request):
    user = request.user
    
    # Access level filtering based on role
    if user.is_superuser or user.role == CustomUser.Role.CHAIRMAN:
        documents = Document.objects.all()
    elif user.role in [CustomUser.Role.FINANCIAL_SECRETARY, CustomUser.Role.OTHER_EXCO]:
        documents = Document.objects.filter(access_level__in=[Document.AccessLevel.ALL_MEMBERS, Document.AccessLevel.EXCO_ONLY])
    else:
        documents = Document.objects.filter(access_level=Document.AccessLevel.ALL_MEMBERS)

    return render(request, 'documents/document_list.html', {'documents': documents})

@login_required
def upload_document_view(request):
    if not (request.user.is_superuser or request.user.role in [CustomUser.Role.CHAIRMAN, CustomUser.Role.FINANCIAL_SECRETARY, CustomUser.Role.OTHER_EXCO]):
        messages.error(request, "Unauthorized to upload official documents.")
        return redirect('document_list')

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        access_level = request.POST.get('access_level', Document.AccessLevel.ALL_MEMBERS)
        doc_file = request.FILES.get('document_file')

        if title and doc_file:
            Document.objects.create(
                title=title,
                description=description,
                access_level=access_level,
                file=doc_file,
                uploaded_by=request.user
            )
            messages.success(request, f"Document '{title}' uploaded successfully.")
            return redirect('document_list')

    return render(request, 'documents/upload_document.html')
