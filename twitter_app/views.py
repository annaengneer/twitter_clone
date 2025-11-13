from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import SignUpForm, ProfileForm
from django.shortcuts import render, redirect, get_object_or_404
from .forms import PostForm
from .models import Post,Profile
from twitter_app.models import Post

def top(request):
    if request.user.is_authenticated:
        form = PostForm()
        posts = Post.objects.all().order_by('-id')
        return render(request, "top_authenticated.html",{
            "form": form,
            "object_list": posts,
        })
    else:
        return render(request, "top_unauthenticated.html") 

def form_view(request):
    if request.method == 'POST':
        form = Post(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('twitter_app:top')
    else:
        form = Post()
    return render(request, 'form.html', {'form': form})


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
    return render(request, 'profile.html', {'profile': profile, 'posts': posts})

@login_required
def edit_profile(request):
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