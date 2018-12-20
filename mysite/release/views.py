# Create your views here.
import datetime

from django.http import HttpResponse
from django.shortcuts import render
from polls.models import *
import sys
import time
from faker import Faker
from django.http import HttpResponse
from django.shortcuts import render
from faker import Faker
from polls.models import *
import sys
import time
import datetime
from math import ceil




def bs_css(request):
    values = {}
    try:
        return render(request,'release/bs_form.html',values)
    except:
        return HttpResponse('Wrong ......')