from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .forms import FileImpactForm
import xmlrpc.client
import json


# Create your views here.
def index(request):
    s = xmlrpc.client.ServerProxy('http://localhost:8008')
    if request.method == 'GET':
        form = FileImpactForm(s.get_file_lists())
        return render(request, 'file_impact.html', {"form": form})

    else:
        impact = s.get_impact(request.POST["files"])
        response = list()
        for target, conditions in impact.items():
            response.append({
                "target": target,
                "conditions": conditions
            })
        return HttpResponse(json.dumps(response))


@csrf_exempt
def filter_targets(request):
    if request.method == "POST":
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        for condition in body["conditions"]:
            if condition['_type'] == "BoolRef":
                condition['value'] = True if condition['value'] == "True" else False
        s = xmlrpc.client.ServerProxy('http://localhost:8008')
        impact = s.get_impact_by_file_condition(body["file"], body["conditions"])
        response = list()
        for target, conditions in impact.items():
            response.append({
                "target": target,
                "conditions": conditions
            })
        return HttpResponse(json.dumps(response))
