from django.http import HttpResponseRedirect, HttpResponse
from django.http import HttpResponseServerError
from api.models import *
from django.db.models import Q
from django.forms.models import model_to_dict
from django.utils import timezone
from django.shortcuts import render,redirect
import random
from django.utils.timezone import now
import requests
import os
import json
from dotenv import load_dotenv
from urllib.parse import urlparse
load_dotenv()

def extract_domain(url):
    # Parse the URL
    parsed_url = urlparse(url)
    
    # Extract the domain name from the netloc attribute
    domain = parsed_url.netloc
    
    # If the domain includes 'www.', remove it
    if domain.startswith('www.'):
        domain = domain[4:]
    
    return domain

class RedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'GET':
            current_path = request.path
            try:
                redirect_path = DirectRedirect.objects.get(old_slug=current_path)
                print(redirect_path.language.slug)
                return HttpResponseRedirect(
                    redirect_path.language.slug, 
                    status=301
                )
            except DirectRedirect.DoesNotExist:
                pass  # Continue with the normal request flow
            try:
                redirect_path = Redirect.objects.get(path=current_path)
                return HttpResponseRedirect(
                    redirect_path.redirect_url, 
                    status=int(redirect_path.http_status_code)
                )
            except Redirect.DoesNotExist:
                pass  # Continue with the normal request flow

        response = self.get_response(request)
        return response
    
api_settings = Settings.objects.first()
# api_settings = []
DEFAULT_LANGUAGE_NAME = os.getenv("DEFAULT_LANGUAGE_NAME")

import base64

def encode_string(string):
    return base64.b64encode(string.encode()).decode()

class DynamicURLMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_path = request.path
        try:
            def getDynamicGlobalData():
                return {
                    "global_header": GlobalHeader.objects.first(),
                    "global_footer": GlobalFooter.objects.first(),
                    "languages": Languages.objects.all(),
                    "domain": os.getenv("WEBSITE_URL"),
                    "domain_name": extract_domain(os.getenv("WEBSITE_URL")),
                }
            global_data = getDynamicGlobalData()
            request.global_data = global_data
           
            
            is_language = Languages.objects.filter(slug=current_path).first()
            if is_language:
                other_pages = Page.objects.filter(language=is_language)
                formatted_time = now().strftime("%d %b %Y %H:%M:%S")
                default_langauge = Languages.objects.filter(name=DEFAULT_LANGUAGE_NAME).first()
                if api_settings.current_use == "iframe":
                    return render(request, "web/index.html", {
                        "page_info": is_language,
                        "current_language": is_language,
                        "other_pages": other_pages,
                        "iframe_url": api_settings.iframe_url,
                        'current_time': formatted_time,
                        "default_langauge": default_langauge
                    })
                else:
                    return render(request, "web/index_with_cobalt.html", {
                        "page_info": is_language,
                        "current_language": is_language,
                        "other_pages": other_pages,
                        'current_time': formatted_time,
                        "log_url": encode_string(os.getenv("LOG_API_URL")),
                        "default_langauge": default_langauge,
                        "direct_ad": encode_string(api_settings.direct_ad),
                        "social_link": encode_string(api_settings.social_link)
                    })

            
            manual_page = Page.objects.filter(slug=current_path).first()
            if manual_page:
                page_info = manual_page
                current_language = page_info.language
                other_pages = Page.objects.filter(language=current_language)
                return render(request, "web/page.html", {
                    "page_info": page_info,
                    "current_language": current_language,
                    "other_pages": other_pages,
                })
                
            response = self.get_response(request)
            return response
        except Exception as e:
            print("Error:", e)
            response = self.get_response(request)
            return response