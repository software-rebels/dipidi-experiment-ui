from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from file_impact.pkls import FuncEntity

from .forms import FileImpactForm, FileUNDImpactForm
from pydriller import Git
import xmlrpc.client
import json
import os
from django.conf import settings


# Create your views here.
def index(request):
    s = xmlrpc.client.ServerProxy(settings.DIPIDI_ADDRESS)
    if request.method == 'GET':
        form = FileImpactForm(s.get_file_lists())
        return render(request, 'file_impact.html', {"form": form})

    else:
        selection_type = request.POST['selection_type']
        if selection_type == "1":
            impact = s.get_impact(request.POST["files"])
            response = list()
            for target, conditions in impact.items():
                response.append({
                    "target": target,
                    "conditions": conditions
                })
            return HttpResponse(json.dumps(response))
        else:
            s = xmlrpc.client.ServerProxy(settings.DIPIDI_ADDRESS)
            impact = s.get_impacted_by_commit_condition(request.POST["commit"], [])
            response = list()
            for target, conditions in impact.items():
                if target == "error":
                    return HttpResponse(json.dumps({
                        "error": True,
                        "message": "Invalid Commit!"
                    }))
                response.append({
                    "target": target,
                    "conditions": conditions
                })
            return HttpResponse(json.dumps(response))


@csrf_exempt
def understand_index(request):
    module_dir = os.path.dirname(__file__)  # get current directory
    file_path = os.path.join(module_dir, settings.PKL_NAME)
    FuncEntity.loadData(file_path)
    files = set()
    for key in FuncEntity.FuncEntity.lookup.keys():
        func, file = key.split(';')
        files.add(file)
    if request.method == 'GET':
        form = FileUNDImpactForm(files)
        return render(request, 'und_impact.html', {"form": form})
    if request.method == 'POST':
        form = FileUNDImpactForm(files, data=request.POST)
        if request.POST['selection_type'] == '1':
            file_name = request.POST['files']
            func_name = request.POST['func_name']
            try:
                local_impacted = FuncEntity.findImpactedFiles(FuncEntity.FuncEntity.get(func_name, file_name))
            except:
                return render(request, 'und_impact.html', {"form": form, "error": "Function not found!"})
            return render(request, 'und_impact.html', {"form": form, 'impacted': local_impacted})
        if request.POST['selection_type'] == '2':
            gr = Git(settings.GIT_PROJECT_PATH)
            try:
                commit = gr.get_commit(request.POST['commit'])
            except:
                return render(request, 'und_impact.html', {"form": form, "error": "Commit not found!"})
            changed_functions = []
            for file in commit.modified_files:
                for func in file.changed_methods:
                    changed_functions.append((func.name,file.old_path or file.new_path))
            impacted = set()
            for key in changed_functions:
                try:
                    local_impacted = FuncEntity.findImpactedFiles(FuncEntity.FuncEntity.get(key[0], key[1]))
                except:
                    continue
                for file in local_impacted:
                    impacted.add(file)
            return render(request, 'und_impact.html', {"form": form, 'impacted': impacted})
        return render(request, 'und_impact.html', {"form": form})


@csrf_exempt
def filter_targets(request):
    if request.method == "POST":
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        for condition in body["conditions"]:
            if condition['_type'] == "BoolRef":
                condition['value'] = True if condition['value'] == "True" else False
        s = xmlrpc.client.ServerProxy(settings.DIPIDI_ADDRESS)
        if body['selection_type'] == '1':
            impact = s.get_impact_by_file_condition(body["file"], body["conditions"])
        else:
            impact = s.get_impacted_by_commit_condition(body["commit"], body["conditions"])

        response = list()
        for target, conditions in impact.items():
            if target == "error":
                return HttpResponse(json.dumps({
                    "error": True,
                    "message": "Invalid Commit!"
                }))
            response.append({
                "target": target,
                "conditions": conditions
            })
        return HttpResponse(json.dumps(response))
