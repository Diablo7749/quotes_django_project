from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import AuthorForm, QuoteForm
from .models import Author, Quote, Tag
from django.core.paginator import Paginator
from django.db.models import Count
import requests
from bs4 import BeautifulSoup


def register_view(request):
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('home')
    return render(request, 'quotes/register.html', {'form': form})

def login_view(request):
    form = AuthenticationForm(data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect('home')
    return render(request, 'quotes/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def add_author(request):
    form = AuthorForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('home')
    return render(request, 'quotes/add_author.html', {'form': form})

@login_required
def add_quote(request):
    form = QuoteForm(request.POST or None)
    if form.is_valid():
        quote = form.save(commit=False)
        quote.created_by = request.user
        quote.save()
        for tag in form.cleaned_data['tags'].split(','):
            tag = tag.strip()
            if tag:
                t, _ = Tag.objects.get_or_create(name=tag)
                quote.tags.add(t)
        return redirect('home')
    return render(request, 'quotes/add_quote.html', {'form': form})

def home(request):
    quotes = Quote.objects.all().order_by('-id')
    paginator = Paginator(quotes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'quotes/home.html', {'quotes': page_obj})

def author_detail(request, author_id):
    author = Author.objects.get(pk=author_id)
    return render(request, 'quotes/author_detail.html', {'author': author})

def quotes_by_tag(request, tag_name):
    tag = Tag.objects.get(name=tag_name)
    quotes = Quote.objects.filter(tags=tag)
    return render(request, 'quotes/tag_quotes.html', {'quotes': quotes, 'tag': tag})

def top_tags(request):
    tags = Tag.objects.annotate(num=Count('quote')).order_by('-num')[:10]
    return render(request, 'quotes/top_tags.html', {'tags': tags})

@login_required
def scrape_site(request):
    if request.method == 'POST':
        url = 'http://quotes.toscrape.com/page/1/'
        while url:
            res = requests.get(url)
            soup = BeautifulSoup(res.text, 'html.parser')
            for q in soup.select('.quote'):
                text = q.select_one('.text').text.strip()
                author_name = q.select_one('.author').text.strip()
                tags = [t.text for t in q.select('.tag')]
                author, _ = Author.objects.get_or_create(fullname=author_name)
                quote = Quote.objects.create(text=text, author=author, created_by=request.user)
                for tag in tags:
                    t, _ = Tag.objects.get_or_create(name=tag)
                    quote.tags.add(t)
            next_btn = soup.select_one('.next > a')
            url = 'http://quotes.toscrape.com' + next_btn['href'] if next_btn else None
        return redirect('home')
