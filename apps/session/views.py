from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

# Create your views here.
def user_login(request):
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)

		if user is not None and user.is_active:
			login(request, user)
			return redirect('/')
		else:
			error = "Invalid login"
		return render(request, 'session/login.html', {'error': error})
	return render(request, 'session/login.html')

def user_logout(request):
	if request.user.is_authenticated():
		logout(request)
	return redirect('/')
