# Create your views here.
from django.shortcuts import render, get_object_or_404
from .models import NewsArticle

def news_detail(request, article_id):
    article = get_object_or_404(NewsArticle, id=article_id)
    return render(request, 'news/news_detail.html', {'article': article})

def news_feed(request):
    country = request.GET.get('country')
    sector = request.GET.get('sector')
    impact = request.GET.get('impact')

    articles = NewsArticle.objects.all().order_by('-created_at')

    if country:
        articles = articles.filter(country=country)
    if sector:
        articles = articles.filter(sector=sector)
    if impact:
        articles = articles.filter(impact=impact)

    countries = NewsArticle.COUNTRY_CHOICES
    sectors = NewsArticle.SECTOR_CHOICES
    impacts = NewsArticle.IMPACT_CHOICES

    return render(request, 'news/news_feed.html', {
        'articles': articles,
        'countries': countries,
        'sectors': sectors,
        'impacts': impacts,
        'selected_country': country,
        'selected_sector': sector,
        'selected_impact': impact,
    })
