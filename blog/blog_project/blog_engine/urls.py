from django.conf.urls import patterns, url
from django.views.generic import ListView
from blog_engine.models import Post

urlpatterns = patterns('',
	url('^$', ListView.as_view(
		model=Post,
		)),
	)
