from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

# Create your views here.
def user_login(request):
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)

		if user is not None and user.is_active:
			login(request, user)
			return render(request, 'session/login_complete.html')
		else:
			error = "Invalid login"
		return render(request, 'session/login.html', {'error': error})
	return render(request, 'session/login.html')

def user_logout(request):
	if request.user.is_authenticated():
		logout(request)
	return redirect('/session/login')

def user_register(request):
	if request.method == "POST":
		username = request.POST['username']
		password = request.POST['password']
		if password != request.POST['password_confirmation']:
			error = "Password doesn't match the confirmation"
			return render(request, "session/register.html", {'error': error})
		email = request.POST['email']
		first_name = request.POST['first_name']
		last_name = request.POST['last_name']
		new_user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name) 
		new_user.save()
		return render(request, 'session/register_complete.html')
	return render(request, 'session/register.html')




