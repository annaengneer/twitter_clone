from django.contrib.auth import login, authenticate
from django.views.generic import CreateView

from django.urls import reverse_lazy
from .forms import SignUpForm
from django.shortcuts import render, redirect
from .forms import PostForm
from .models import Post

def top(request):
    if request.user.is_authenticated:
        form = PostForm()
        posts = Post.objects.all().order_by('-id')
        return render(request, "top_after.html",{
            "form": form,
            "object_list": posts,
        })
    else:
        return render(request, "top_before.html") 

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

