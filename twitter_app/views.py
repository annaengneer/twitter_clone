from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import SignUpForm, ProfileForm
from django.shortcuts import render, redirect, get_object_or_404
from .forms import PostForm, CommentForm
from .models import Post,Profile
from twitter_app.models import Post

@login_required
def top(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('twitter_app:top')
    else:
        form = PostForm()

    posts = Post.objects.all().order_by('-id')
    return render(request, 'top_authenticated.html',{
        "form":form,
        "object_list":posts,
    })

class SignupView(CreateView):
    form_class = SignUpForm
    template_name = "signup.html"
    success_url = reverse_lazy("account_login")

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")
        user = authenticate(username=username, password=password)
        login(self.request, user)
        return response

@login_required  
def ProfileView(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)

    posts = Post.objects.filter(user=request.user).order_by('-created_at')

    context = {
        'profile': profile,
        'form': form,
        'posts': posts,
    }
    return render(request, 'profile.html', context)

def profile_view(request, username):
    profile = get_object_or_404(Profile, user__username=username)
    posts = Post.objects.filter(user=profile.user).order_by('-created_at')
    
    context = {
        "profile": profile,
        "object_list": posts,
    }

    return render(request, 'profile.html', context)

@login_required
def profile_edit(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile, user= request.user)
        if form.is_valid():

            request.user.username = form.cleaned_data['username']
            if hasattr(request.user,'display_name'):
                request.user.display_name = form.cleaned_data['display_name']
            request.user.save()

            form.save()
            return redirect('twitter_app:profile_detail', username=request.user.username)
    else:
        form = ProfileForm(instance=profile, user=request.user)
        
    return render(request, 'profile_edit.html', {'form': form, 'profile': profile})

@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post,id=post_id)

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.post = post
            new_comment.user = request.user
            new_comment.save()
            return redirect('twitter_app:post_detail', post_id=post.id)
    else:
        form = CommentForm()
    comments = post.comments.order_by('-created_at')

    return render(request, 'post_detail.html',{
        "post": post,
        "form": form,
        "comments": comments,
    })
