from django.http import HttpResponse,FileResponse, HttpResponseNotFound,JsonResponse,HttpResponseRedirect
from django.shortcuts import render,redirect,get_object_or_404
from api.models import *
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404
from django.conf import settings
from datetime import datetime, timedelta
import os
import requests
import random
import jwt
from youtube_search import YoutubeSearch
from ckeditor_uploader.views import upload
from dotenv import load_dotenv
load_dotenv()
BASE_FOLDER_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def install(request):
    if Admin.objects.count() == 0:
        dummy_admin = Admin.objects.create(email="admin@mail.com", password="1234")
        dummy_admin.save()
    if Settings.objects.count() == 0:
        dummy_setting = Settings.objects.create(iframe_url="http://freeytapi.cam/?url=",cobalt_api_url="https://api.mp3c.info/",current_use="iframe",direct_ad="",social_link="")
        dummy_setting.save()    
    if Theme.objects.count() == 0:
        dummy_theme = Theme.objects.create()
        dummy_theme.save()    
    return HttpResponse("<h1>Installed Successfully</h1>")

@csrf_exempt
def ckeditor_upload(request):
    return upload(request)


def search_video(request):
    if request.method == "POST":
        try:
            query = request.POST.get('query')
            if not query:
                return JsonResponse({'error': 'Search field is required'}, status=400)
            results = YoutubeSearch(query, max_results=10).to_dict()
            return JsonResponse(results,safe=False,status=200)
        except Exception as e:
          return JsonResponse({"error":e},safe=False,status=500)
    else:
        return JsonResponse({"error":f"{request.method} method not allowed!"},safe=False,status=405)
    
api_settings = Settings.objects.first()
# api_settings = []
log_api_url = os.getenv("LOG_API_URL")

import base64

def encode_string(string):
    return base64.b64encode(string.encode()).decode()


def audio(request):
    if request.method == "POST":
        try:
            url = request.POST.get('url')
            if not url:
                return JsonResponse({'error': 'URL field is required'}, status=400)
            payload = {
                "url": url,
                "audioFormat": "mp3",
                "downloadMode": "audio",
                "filenameStyle": "basic",
                "youtubeHLS": True
            }
            print("API URL:", api_settings.cobalt_api_url)
            print("LOG URL:", log_api_url)
            cobalt_response = requests.post(
                api_settings.cobalt_api_url,
                json=payload,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                }
            )
            response_data = cobalt_response.json()
            if cobalt_response.status_code == 200:
                requests.get(f"{log_api_url}/convert",json={"url":url,"format":"mp3"})
                return JsonResponse({"url":encode_string(response_data["url"]),"filename":response_data["filename"]}, safe=False)
            else:
                return JsonResponse({'error': response_data}, status=cobalt_response.status_code)
        except Exception as e:
            return JsonResponse({"error": str(e)}, safe=False, status=500)
    else:
        return JsonResponse({"error": f"{request.method} method not allowed!"}, safe=False, status=405)
    

def video(request):
    if request.method == "POST":
        try:
            url = request.POST.get('url')
            if not url:
                return JsonResponse({'error': 'URL field is required'}, status=400)
            payload = {
                "url": url,
                'videoQuality': "720",
                'filenameStyle': 'basic',
                "youtubeHLS": True
                
            }
            print("API URL:", api_settings.cobalt_api_url)
            print("LOG URL:", log_api_url)

            cobalt_response = requests.post(
                api_settings.cobalt_api_url,
                json=payload,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                }
            )
            response_data = cobalt_response.json()
            if cobalt_response.status_code == 200:
                requests.get(f"{log_api_url}/convert",json={"url":url,"format":"mp4"})
                return JsonResponse({"url":encode_string(response_data["url"]),"filename":response_data["filename"]}, safe=False)
            else:
                return JsonResponse({'error': response_data}, status=cobalt_response.status_code)
        except Exception as e:
            return JsonResponse({"error": str(e)}, safe=False, status=500)
    else:
        return JsonResponse({"error": f"{request.method} method not allowed!"}, safe=False, status=405)


def home_page(request):
    if 'admin' not in request.session:
        return redirect('login_page')
    return render(request,"admin/index.html")



def login_page(request):
    if 'admin' in request.session:
        return redirect('home_page')
    return render(request,"admin/login.html")

def logout(request):
    if 'admin' in request.session:
        del request.session['admin']
    return redirect('login_page')



def account_page(request):
    if 'admin' not in request.session:
        return redirect('login_page')
    return render(request,"admin/account.html",{"data":Admin.objects.first()})

def languages_page(request):
    if 'admin' not in request.session:
        return redirect('login_page')
    return render(request,"admin/languages.html",{"data":Languages.objects.all()})


def add_new_language_page(request):
    if 'admin' not in request.session:
        return redirect('login_page')
    return render(request, 'admin/add-new-language.html')


def language_pages_page(request, id):
    if 'admin' not in request.session:
        return redirect('login_page')
    language_data = get_object_or_404(Languages, id=id)
    return render(request, "admin/languages-pages.html", {'data': language_data,"pages":Page.objects.filter(language=language_data)})

def language_edit_page(request, id):
    if 'admin' not in request.session:
        return redirect('login_page')
    language_data = get_object_or_404(Languages, id=id)
    redirects = DirectRedirect.objects.filter(language=language_data)
    return render(request, "admin/edit-language.html", {'data': language_data,"redirects":redirects})


def add_new_cutom_page(request, id):
    if 'admin' not in request.session:
        return redirect('login_page')
    language_data = get_object_or_404(Languages, id=id)
    return render(request, "admin/add-new-cutom-page.html", {'data': language_data})


def edit_cutom_page(request, id):
    if 'admin' not in request.session:
        return redirect('login_page')
    page_data = get_object_or_404(Page, id=id)
    return render(request, "admin/edit-cutom-page.html", {'data': page_data})


def api(request):
    if 'admin' not in request.session:
        return redirect('login_page')
    return render(request,"admin/api.html",{"data":Settings.objects.first()})

def theme(request):
    if 'admin' not in request.session:
        return redirect('login_page')
    return render(request,"admin/theme.html",{"data":Theme.objects.first()})

def logo_and_favicon(request):
    if 'admin' not in request.session:
        return redirect('login_page')
    return render(request,"admin/logo-and-favicon.html")

def global_header_page(request):
    if 'admin' not in request.session:
        return redirect('login_page')
    if GlobalHeader.objects.count() < 1:
        header = GlobalHeader.objects.create()
        header.header = ""
        header.save()
    global_header = GlobalHeader.objects.first()
    return render(request,"admin/global-header.html",{"content":global_header.header})

def global_footer_page(request):
    if 'admin' not in request.session:
        return redirect('login_page')
    if GlobalFooter.objects.count() < 1:
        footer = GlobalFooter.objects.create()
        footer.footer = ""
        footer.save()
    global_footer = GlobalFooter.objects.first()
    return render(request,"admin/global-footer.html",{"content":global_footer.footer})

def redirects_page(request):
    if 'admin' not in request.session:
        return redirect('login_page')
    return render(request,"admin/redirects.html",{"data":Redirect.objects.all()})


def robots_dot_txt_page(request):
    if 'admin' not in request.session:
        return redirect('login_page')
    sitemap_path = os.path.join(BASE_FOLDER_DIR,'robots.txt')
    with open(sitemap_path, 'r') as file:
        content = file.read()
        return render(request,"admin/robots.txt.html", {'content': content})