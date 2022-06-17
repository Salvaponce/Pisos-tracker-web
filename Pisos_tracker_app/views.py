from operator import add
from django.shortcuts import render

import ast
from datetime import datetime
import re
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from Pisos_tracker_app.pisos_traker import PisosAPI
from Pisos_tracker_app.form import login_form, FeedbackForm
from Pisos_tracker_app.models import House, Report

def home(request):
    if request.session.get('ls'):
        del request.session['ls']
    if request.session.get('count'):
        del request.session['count']
    if request.session.get('data_list'):
        del request.session['data_list']
    if request.session.get('place'):
        del request.session['place']
    if request.session.get('filter'):
        del request.session['filter']
    return render(request, 'home.html')

def results(request):
    # 'https://www.idealista.com/'
    ls = request.session.get('ls', ['https://www.pisos.com/', 'https://www.habitaclia.com/','https://www.yaencontre.com/'])
    count = request.session.get('count', 0)
    data_list = request.session.get('data_list', [])
    place = request.session.get('place', False)
    filter = request.session.get('filter', False)
    if request.method == 'POST':
        if not place:
            place = request.POST.get('place', False)
            request.session['place'] = place
        if not filter:
            filter = request.POST.get('filter',  False)
            request.session['filter'] = filter
        piso = PisosAPI(place.lower(), ls[count], filter) 
        data = piso.run()    
        for i in data:
            data_list.append(i)   
        request.session['data_list'] = data_list
        count += 1
        request.session['count'] = count
        if str(request.user) != 'AnonymousUser' and count == len(ls):
            save_data(place, data_list, request.user)
        return render(request, 'results.html', {'data': data_list, 'place':place, 'web':ls, 'count':count})
    return render(request, 'home.html')

# Keep the information when we finish the search
def save_data(name, data, user):
    title = name + " " + str(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    report = Report.objects.create(title = title, user = user)
    report.save()
    for h in data:
        house = House.objects.create(data = str(h), report = report)
        house.save()


def login_view(request):    
    if request.method == 'POST':
        form = login_form(request.POST)
        if form.is_valid():
            user = authenticate(username=request.POST['username'], password = request.POST['password'])            
            if user is not None:
                login(request, user)
                return home(request)
    else:
        form = login_form()
    return render(request, 'login.html', {'form': form})


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username = user.username, password = raw_password)
            if user is not None:
                login(request, user)
                return render(request, 'home.html')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


def logout_view(request):
    logout(request)
    return home(request)

# Get the report and display it
def history(request):
    report_list = Report.objects.filter(user = request.user)
    if request.method == 'POST' and request.POST.get('report_name'):
        house_list = House.objects.filter(report = request.POST.get('report_name', False))
        print(house_list)
        data = []
        for p in house_list:
            data.append(ast.literal_eval(p.data))
        print(data)
        return render(request, "results.html", {"data": data})
    elif request.method == 'POST':
        print("deleting")
        house_list = Report.objects.filter(id = request.POST.get('delete', False)).delete()
    return render(request, 'history.html', {'report_list': report_list})


def feedback(request):
    if request.method == 'POST':
        f = FeedbackForm(request.POST)
        if f.is_valid():
            f.save()
            messages.add_message(request, messages.INFO, 'Feedback Submitted.')
            return render(request, 'feedback.html', {'form': f})
    else:
        f = FeedbackForm()
    return render(request, 'feedback.html', {'form': f})
