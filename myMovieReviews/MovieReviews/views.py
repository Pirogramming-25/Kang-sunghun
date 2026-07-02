from django.shortcuts import render, redirect
from .models import Review

# Create your views here.
def index(request):
    sort = request.GET.get('sort', '-id')
    reviews = Review.objects.order_by(sort)
    for review in reviews:
        review.hour = review.runningtime // 60
        review.minute = review.runningtime % 60
    context = {'reviews': reviews}
    return render(request, 'review_list.html', context)

def detail(request, id):
    review = Review.objects.get(id=id)
    hour = review.runningtime // 60
    minute = review.runningtime % 60
    context = {'review': review, 'hour': hour, 'minute' : minute}
    return render(request, 'review_detail.html', context)

def new(request):
    return render(request, 'review_write.html')

def create(request):
    review = Review(
        title = request.POST['title'],
        openyear = request.POST['openyear'],
        genre = request.POST['genre'],
        starpoint = request.POST['starpoint'],
        runningtime = request.POST['runningtime'],
        reviewcontent = request.POST['reviewcontent'],
        director = request.POST['director'],
        actor = request.POST['actor'],
    )
    review.save()
    return redirect('index')

def edit(request, id):
    review = Review.objects.get(id=id)
    context = {'review': review}
    return render(request, 'review_edit.html', context)

def update(request, id):
    review = Review.objects.get(id=id)
    review.title = request.POST['title']
    review.openyear = request.POST['openyear']
    review.genre = request.POST['genre']
    review.starpoint = request.POST['starpoint']
    review.runningtime = request.POST['runningtime']
    review.reviewcontent = request.POST['reviewcontent']
    review.director = request.POST['director']
    review.actor = request.POST['actor']
    review.save()
    return redirect('detail', id)

def delete(request, id):
    review = Review.objects.get(id=id)
    review.delete()
    return redirect('index')