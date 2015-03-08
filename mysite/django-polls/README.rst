===
Polls
===

Polls is a simple django application that uses web-based polls

Quick Start
-----------
1. Add "polls" to your INSTALLED_APPS setting liek this:
	INSTALLED_APPs = (
		...
		'polls',
	)
2. Include polls URLconf in your project urls.py like this
	url(r'^polls/', include('polls.urls')),

3) Run python manage.py syncdb to create polls models

4) Go to admin site

5) Go to polls to see polls
