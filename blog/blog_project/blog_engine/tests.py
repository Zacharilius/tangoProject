import markdown2 as markdown
from django.test import TestCase, LiveServerTestCase, Client
from django.utils import timezone
from blog_engine.models import Post

class PostTest(TestCase):
	def test_create_post(self):
		post = Post()
		post.title = 'My first post'
		post.text = 'This is my first blog post'
		post.slug = 'my-first-post'
		post.pub_date = timezone.now()
		post.save()

		# Makes sure blog post was created correctly
		all_posts = Post.objects.all()
		self.assertEquals(len(all_posts), 1)
		only_post = all_posts[0]
		self.assertEquals(only_post, post)
		self.assertEquals(only_post.title, 'My first post')
		self.assertEquals(only_post.text, 'This is my first blog post')
		self.assertEquals(only_post.slug, 'my-first-post')
		self.assertEquals(only_post.pub_date.day, post.pub_date.day)
		self.assertEquals(only_post.pub_date.month, post.pub_date.month)
		self.assertEquals(only_post.pub_date.year, post.pub_date.year)

class AdminTest(LiveServerTestCase):
	fixtures = ['users.json']
	def setUp(self):
		self.client = Client()
	def test_login(self):
		# Get login page
		response = self.client.get('/admin/')
		# Check response code
		self.assertEquals(response.status_code, 200)
		# Check 'Log in' in response
		self.assertTrue('Log in' in response.content)
		# Log the user in
		self.client.login(username='bobsmith', password="password")
		# Check response code
		response = self.client.get('/admin/')
		self.assertEquals(response.status_code, 200)
		# Check 'Log out' in response
		self.assertTrue('Log out' in response.content)
	def test_logout(self):
		# Log in
		self.client.login(username='bobsmith', password="password")
		# Check response code
		response = self.client.get('/admin/')
		self.assertEquals(response.status_code, 200)
		# Check 'Log out' in response
		self.assertTrue('Log out' in response.content)
		# Log out
		self.client.logout()
		# Check response code
		response = self.client.get('/admin/')
		self.assertEquals(response.status_code, 200)
		# Check 'Log in' in response
		self.assertTrue('Log in' in response.content)
	def test_create_post(self):
		self.client.login(username='bobsmith', password="password")

		response = self.client.get('/admin/blog_engine/post/add/')
		self.assertEquals(response.status_code, 200)
		response = self.client.post('/admin/blog_engine/post/add/',{
			'title': 'My First post',
			'text': 'This is what I\'m all about bro',
			'pub_date_0': '2013-12-28',
			'pub_date_1': '22:00:04',
			'slug': 'my-first-post'
		},
		follow=True
		)
		self.assertEquals(response.status_code, 200)

		self.assertTrue('added successfully' in response.content)
		all_posts = Post.objects.all()
		self.assertEquals(len(all_posts), 1)

	def test_edit_post(self):
		# Create the post
		post = Post()
		post.title = 'My first post'
		post.text = 'This is my first blog post'
		post.slug = 'my-first-post'
		post.pub_date = timezone.now()
		post.save()

		# Log in
		self.client.login(username='bobsmith', password="password")

		# Edit the post
		response = self.client.post('/admin/blog_engine/post/1/', {
			'title': 'My second post',
			'text': 'This is my second blog post',
			'pub_date_0': '2013-12-28',
			'pub_date_1': '22:00:04',
			'slug': 'my-second-post'
		},
		follow=True
		)
		self.assertEquals(response.status_code, 200)

		# Check changed successfully
		self.assertTrue('changed successfully' in response.content)

		# Check post amended
		all_posts = Post.objects.all()
		self.assertEquals(len(all_posts), 1)
		only_post = all_posts[0]
		self.assertEquals(only_post.title, 'My second post')
		self.assertEquals(only_post.text, 'This is my second blog post')

	def test_delete_post(self):
		post = Post()
		post.title = 'My first post'
		post.text = 'This is my first blog post'
		post.slug = 'my-first-post'
		post.pub_date = timezone.now()
		post.save()

		all_posts = Post.objects.all()
		self.assertEquals(len(all_posts), 1)

		self.client.login(username='bobsmith', password="password")

		response = self.client.post('/admin/blog_engine/post/1/delete/', {
			'post': 'yes'
		}, follow=True)
		self.assertEquals(response.status_code, 200)

		self.assertTrue('deleted successfully' in response.content)

		all_posts = Post.objects.all()
		self.assertEquals(len(all_posts), 0)

class PostViewTest(LiveServerTestCase):
	def setUp(self):
		self.client = Client()
	
	def test_index(self):
		post = Post()
		post.title = 'My first post'
		post.text = 'This is [my first blog post](http://127.0.0.1:8000/)'
		post.slug = 'my-first-post'
		post.pub_date = timezone.now()
		post.save()

		all_posts = Post.objects.all()
		self.assertEquals(len(all_posts), 1)

		response = self.client.get('/')
		self.assertEquals(response.status_code, 200)

		self.assertTrue(post.title in response.content)

		self.assertTrue(post.text in response.content)

		self.assertTrue(str(post.pub_date.year) in response.content)
		self.assertTrue(post.pub_date.strftime('%b') in response.content)
		self.assertTrue(str(post.pub_date.day) in response.content)


		self.assertTrue('<a href="http://127.0.0.1:8000/">my first blog post</a>' in response.content)
	
	def test_post_page(self):
		# Create the post
		post = Post()
		post.title = 'My first post'
		post.text = 'This is [my first blog post](http://127.0.0.1:8000/)'
		post.slug = 'my-first-post'
		post.pub_date = timezone.now()
		post.save()

		# Check new post saved
		all_posts = Post.objects.all()
		self.assertEquals(len(all_posts), 1)
		only_post = all_posts[0]
		self.assertEquals(only_post, post)

		# Get the post URL
		post_url = only_post.get_absolute_url()

		# Fetch the post
		response = self.client.get(post_url)
		self.assertEquals(response.status_code, 200)

		# Check the post title is in the response
		self.assertTrue(post.title in response.content)

		# Check the post text is in the response
		self.assertTrue(markdown.markdown(post.text) in response.content)

		# Check the post date is in the response
		self.assertTrue(str(post.pub_date.year) in response.content)
		self.assertTrue(post.pub_date.strftime('%b') in response.content)
		self.assertTrue(str(post.pub_date.day) in response.content)

		# Check the link is marked up properly
		self.assertTrue('<a href="http://127.0.0.1:8000/">my first blog post</a>' in response.content)
