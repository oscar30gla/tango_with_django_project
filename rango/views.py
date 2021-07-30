from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category, UserProfile
from rango.models import Page
from rango.forms import CategoryForm, PageForm
from django.shortcuts import redirect
from django.urls import reverse
from rango.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime

def index(request):
    # Query the database for a list of all categories currently stored
    # Order by descending number of likes
    # [:5] means top 5 only
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    # place the list after the boldmessage
    # will be passed to the template engine
    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = page_list

    visitor_cookie_handler(request)

    # Render the response and send it back
    response = render(request, 'rango/index.html', context=context_dict)
    return response

def about(request):
    context_dict = {}
    context_dict['boldmessage'] = 'This tutorial has been put together by Tsz Yui Tsang'
    
    visitor_cookie_handler(request)
    context_dict['visits'] = int(request.session['visits'])

    return render(request, 'rango/about.html', context=context_dict)

def show_category(request, category_name_slug):
    #Create a context dictionary
    context_dict = {}

    try:
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category)
        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['pages'] = None

    return render(request, 'rango/category.html', context=context_dict)

@login_required
def add_category(request):
    form = CategoryForm()

    # A HTTP POST?
    if request.method =='POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save(commit=True)
            return redirect('/rango/')
        else:
            print(form.errors)
    return render(request, 'rango/add_category.html', {'form': form})

@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None
   
    if category is None:
        return redirect('/rango/')

    form = PageForm()

    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()

                return redirect(reverse('rango:show_category', kwargs={'category_name_slug': category_name_slug}))
        else:
            print(form.errors)
            
    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context=context_dict)
        
def register(request):
    # boolean that tells if the registration is successful. Turn True if successfully register
    registered = False

    if request.method == 'POST':

        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            
            profile.save()
            registered = True
        
        else:
            # Invalid form(s) -> Print problems
            print(user_form.errors, profile_form.errors)
    
    else:
        # NOT a HTTP POST -> render the blank forms for user input
        user_form = UserForm()
        profile_form = UserProfileForm()
    
    # Render the template
    return render(request, 'rango/register.html', context ={'user_form': user_form, 
                                                            'profile_form': profile_form, 
                                                            'registered': registered})

def user_login(request):

    if request.method == 'POST':
        # request.POST.get() will return None if value doesn't exist
        # request.POST[] will raise a KeyError exception instead
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        # If user object exists, the username and password are correct and check if it is active
        if user:
            if user.is_active:
                login(request, user)
                return redirect(reverse('rango:index'))
            else:
                # Inactive account
                return HttpResponse("Your Rango account is disabled.")

        else:
            # Bad login details were provided
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")
    
    # NOT POST -> display login form
    else:
        return render(request, 'rango/login.html')

@login_required
def restricted(request):
    return render(request, 'rango/restricted.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('rango:index'))

# helper method
def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

# Updated
def visitor_cookie_handler(request):
    # number of visit
    # COOKIES.get() to get visits cookie
    # if cookie exists -> value returned casted into int
    # if not -> 1
    visits = int(get_server_side_cookie(request, 'visits', '1'))
    last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')

    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        request.session['last_visit'] = str(datetime.now())
    else:
        request.session['last_visit'] = last_visit_cookie
    
    # set or update visits cookie
    request.session['visits'] = visits