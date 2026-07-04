from django.shortcuts import render, redirect
from .models import DevTool, Idea, IdeaStar
from django.db.models import Count
from django.core.paginator import Paginator

# Create your views here.
def develop_list(request):
    devtools = DevTool.objects.all()
    context = {'devtools': devtools}
    return render(request, 'IdeaSite/develop_list.html', context)

def develop_detail(request, id):
    devtool = DevTool.objects.get(id=id)
    context = {'devtool': devtool}
    return render(request, 'IdeaSite/develop_detail.html', context)

def develop_register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        kind = request.POST.get('kind')
        content = request.POST.get('content')
        devtool = DevTool.objects.create(name=name, kind=kind, content=content)
        return redirect('develop_detail', id=devtool.id)
    return render(request, 'IdeaSite/develop_register.html')

def develop_modify(request, id):
    devtool = DevTool.objects.get(id=id)
    if request.method == 'POST':
        devtool.name = request.POST.get('name')
        devtool.kind = request.POST.get('kind')
        devtool.content = request.POST.get('content')
        devtool.save()
        return redirect('develop_detail', id=devtool.id)
    context = {'devtool': devtool}
    return render(request, 'IdeaSite/develop_modify.html', context)

def develop_delete(request, id):
    devtool = DevTool.objects.get(id=id)
    devtool.delete()
    return redirect('develop_list')

def idea_list(request):
    sort = request.GET.get('sort', 'latest')

    if sort == 'name':
        ideas = Idea.objects.all().order_by('title')
    elif sort == 'oldest':
        ideas = Idea.objects.all().order_by('created_at')
    elif sort == 'star':
        ideas = Idea.objects.annotate(star_count=Count('ideastar')).order_by('-star_count')
    else:
        ideas = Idea.objects.all().order_by('-created_at')

    paginator = Paginator(ideas, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'ideas': page_obj, 'sort': sort}
    return render(request, 'IdeaSite/idea_list.html', context)

def idea_detail(request, id):
    idea = Idea.objects.get(id=id)
    is_starred = IdeaStar.objects.filter(idea=idea).exists()
    context = {'idea': idea, 'is_starred': is_starred}
    return render(request, 'IdeaSite/idea_detail.html', context)

def idea_register(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        image = request.FILES.get('image')
        content = request.POST.get('content')
        interest = request.POST.get('interest')
        devtool_id = request.POST.get('devtool')
        idea = Idea.objects.create(
            title=title,
            image=image,
            content=content,
            interest=interest,
            devtool_id=devtool_id,
        )
        return redirect('idea_detail', id=idea.id)
    devtools = DevTool.objects.all()
    context = {'devtools': devtools}
    return render(request, 'IdeaSite/idea_register.html', context)

def idea_modify(request, id):
    idea = Idea.objects.get(id=id)
    if request.method == 'POST':
        idea.title = request.POST.get('title')
        if request.FILES.get('image'):
            idea.image = request.FILES.get('image')
        idea.content = request.POST.get('content')
        idea.interest = request.POST.get('interest')
        idea.devtool_id = request.POST.get('devtool')
        idea.save()
        return redirect('idea_detail', id=idea.id)
    devtools = DevTool.objects.all()
    context = {'idea': idea, 'devtools': devtools}
    return render(request, 'IdeaSite/idea_modify.html', context)

def idea_delete(request, id):
    idea = Idea.objects.get(id=id)
    idea.delete()
    return redirect('idea_list')

def idea_interest_up(request, id):
    idea = Idea.objects.get(id=id)
    idea.interest += 1
    idea.save()
    return redirect('idea_detail', id=idea.id)

def idea_interest_down(request, id):
    idea = Idea.objects.get(id=id)
    idea.interest -= 1
    idea.save()
    return redirect('idea_detail', id=idea.id)

def idea_star(request, id):
    idea = Idea.objects.get(id=id)
    star = IdeaStar.objects.filter(idea=idea)
    if star.exists():
        star.delete()
    else:
        IdeaStar.objects.create(idea=idea)
    return redirect('idea_detail', id=idea.id)