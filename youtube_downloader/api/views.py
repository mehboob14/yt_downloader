from datetime import datetime, timedelta, timezone
from django.shortcuts import render,get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.db import transaction
from django.db.utils import IntegrityError
from django.utils import timezone
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.exceptions import ValidationError
from django.forms.models import model_to_dict
from django.core import serializers
from django.utils.timezone import localtime
from django.db.models import Count
from django.db.models import Avg, Count
from django.db.models.functions import Random
from django.utils.text import slugify
from .models import *
import re
import os
import requests
from requests.exceptions import RequestException
from django.core.files.storage import FileSystemStorage
from PIL import Image
from io import BytesIO
import uuid
import random
import string
import json
import time
import asyncio
import jwt
from dotenv import load_dotenv
load_dotenv()

BASE_FOLDER_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def handle_uploaded_image(file, save_dir):
    if isinstance(file, InMemoryUploadedFile) and file.content_type.startswith('image'):
        try:
            image = Image.open(file)
            output = BytesIO()
            image.save(output, format='WEBP')
            
            # Generate a unique filename
            filename = f'{uuid.uuid4()}.webp'
            
            # Construct the file path
            filepath = os.path.join(settings.MEDIA_ROOT, save_dir, filename)
            
            # Save the image
            with open(filepath, 'wb') as f:
                f.write(output.getvalue())
            
            # Create an InMemoryUploadedFile instance with the saved file
            return InMemoryUploadedFile(open(filepath, 'rb'), None, filename, 'image/webp', os.path.getsize(filepath), None)
        except Exception as e:
            print("Error converting image to WEBP:", e)
    return None




import threading
import xml.etree.ElementTree as ET


def xml_sitemap_generator():
    website_url = os.getenv("WEBSITE_URL")
    if not website_url:
        raise ValueError("The WEBSITE_URL environment variable is not set.")
    
    urlset = ET.Element('urlset', {
        'xmlns': 'http://www.sitemaps.org/schemas/sitemap/0.9',
        'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'xsi:schemaLocation': 'http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd'
    })
    lastmod = timezone.now().strftime('%Y-%m-%dT%H:%M:%S+00:00')

    languages = Languages.objects.all()
    
    for index, language in enumerate(languages):
        url_element = ET.SubElement(urlset, 'url')
        loc = ET.SubElement(url_element, 'loc')
        loc.text = f"{website_url}{language.slug}"
        lastmod_element = ET.SubElement(url_element, 'lastmod')
        lastmod_element.text = lastmod
        changefreq = ET.SubElement(url_element, 'changefreq')
        changefreq.text = 'weekly'
        priority = ET.SubElement(url_element, 'priority')
        priority.text = '1.00' if index == 0 else '0.80'


    pages = Page.objects.all()
    
    for page in pages:
        url_element = ET.SubElement(urlset, 'url')
        loc = ET.SubElement(url_element, 'loc')
        loc.text = f"{website_url}{page.slug}"
        lastmod_element = ET.SubElement(url_element, 'lastmod')
        lastmod_element.text = lastmod
        changefreq = ET.SubElement(url_element, 'changefreq')
        changefreq.text = 'weekly'
        priority = ET.SubElement(url_element, 'priority')
        priority.text = '0.80'
    

    
    # Write the sitemap to an XML file
    tree = ET.ElementTree(urlset)
    sitemap_path = "sitemap.xml"
    tree.write(sitemap_path, encoding='utf-8', xml_declaration=True)
    print(f"Sitemap generation completed: {sitemap_path}")

def run_async_xml_sitemap_generator():
    thread = threading.Thread(target=xml_sitemap_generator)
    thread.start()

run_async_xml_sitemap_generator()





# @csrf_exempt
def api_admin_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        if email and password:
            try:
                # Retrieve admin object using the provided email
                admin = Admin.objects.get(email=email)
            except Admin.DoesNotExist:
                # Admin with the provided email does not exist
                return JsonResponse({'error': 'Invalid email or password'}, status=400)

            # Check if the provided password matches the admin's password
            if admin.password == password:
                # Login successful
                request.session['admin'] = True  # Set session variable for admin
                print("Yes 123")
                print(request.session['admin'])
                return JsonResponse({'message': 'Login successful'})
            else:
                # Invalid credentials
                return JsonResponse({'error': 'Invalid email or password'}, status=400)
        else:
            # Missing email or password
            return JsonResponse({'error': 'Email and password are required'}, status=400)
    else:
        # Only allow POST requests
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
    
def api_admin_update(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if email and password:
            try:
                # Get the first Admin instance
                update_admin = Admin.objects.first()
                
                # Update the Admin instance with the new data
                update_admin.email = email
                update_admin.password = password
                update_admin.save()
                
                return JsonResponse({'message': 'Changes saved successfully'})
            except Exception as e:
                # Handle any exceptions during save operation
                return JsonResponse({'error': f'Failed to save changes: {str(e)}'}, status=500)
        else:
            # Missing email or password
            return JsonResponse({'error': 'Email and password are required'}, status=400)
    else:
        # Only allow POST requests
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
    





def create_new_language(request):
    if request.method == 'POST':
        # Check if the user is logged in
        if 'admin' not in request.session:
            return JsonResponse({'error': 'You are not logged in'}, status=401)

        try:
            # Retrieve form data
            lang = request.POST.get('lang')
            name = request.POST.get('name')
            dir = request.POST.get('dir')
            page_name = request.POST.get('page_name')
            slug = request.POST.get('slug')
            meta_title = request.POST.get('meta_title')
            meta_description = request.POST.get('meta_description')
            header = request.POST.get('header')
            heading = request.POST.get('heading')
            tag_line = request.POST.get('tag_line')
            message_one = request.POST.get('message_one')
            message_two = request.POST.get('message_two')
            banner_ad_one = request.POST.get('banner_ad_one')
            banner_ad_two = request.POST.get('banner_ad_two')
            placeholder = request.POST.get('placeholder')
            form_button_text = request.POST.get('form_button_text')
            content = request.POST.get('content')
            new_language = Languages(
                name=name,
                lang=lang,
                dir=dir,
                page_name=page_name,
                slug=slug,
                meta_title=meta_title,
                meta_description=meta_description,
                header=header,
                heading=heading,
                tag_line=tag_line,
                message_one=message_one,
                message_two=message_two,
                banner_ad_one=banner_ad_one,
                banner_ad_two=banner_ad_two,
                placeholder=placeholder,
                form_button_text=form_button_text,
                content=content,
            )
            new_language.save()
            run_async_xml_sitemap_generator()
            return JsonResponse({'message': 'Language created successfully'}, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
    


def edit_language(request):
    if request.method == 'POST':
        if 'admin' not in request.session:
            return JsonResponse({'error': 'You are not logged in'}, status=401)

        try:
            # Retrieve form data
            id = request.POST.get('id')
            if not id:
                return JsonResponse({'error': 'Language ID is required'}, status=400)

            # Fetch the language object
            language = Languages.objects.filter(id=id).first()
            if not language:
                return JsonResponse({'error': 'Language not found'}, status=404)

            # Check for slug change
            old_slug = language.slug
            new_slug = request.POST.get('slug', language.slug)

            # Ensure the new slug is unique across Languages and DirectRedirect
            if new_slug != old_slug:
                if Languages.objects.filter(slug=new_slug).exclude(id=language.id).exists() or \
                   DirectRedirect.objects.filter(old_slug=new_slug).exists():
                    return JsonResponse({'error': 'The new slug already exists in Languages or DirectRedirect'}, status=400)

                # Add old slug to DirectRedirect if it doesn't already exist
                if not DirectRedirect.objects.filter(language=language, old_slug=old_slug).exists():
                    DirectRedirect.objects.create(language=language, old_slug=old_slug)

            # Update fields
            language.lang = request.POST.get('lang', language.lang)
            language.name = request.POST.get('name', language.name)
            language.dir = request.POST.get('dir', language.dir)
            language.page_name = request.POST.get('page_name', language.page_name)
            language.slug = new_slug  # Set the new slug
            language.meta_title = request.POST.get('meta_title', language.meta_title)
            language.meta_description = request.POST.get('meta_description', language.meta_description)
            language.header = request.POST.get('header', language.header)
            language.heading = request.POST.get('heading', language.heading)
            language.tag_line = request.POST.get('tag_line', language.tag_line)
            language.message_one = request.POST.get('message_one', language.message_one)
            language.message_two = request.POST.get('message_two', language.message_one)
            language.banner_ad_one = request.POST.get('banner_ad_one', language.banner_ad_one)
            language.banner_ad_two = request.POST.get('banner_ad_two', language.banner_ad_two)
            language.placeholder = request.POST.get('placeholder', language.placeholder)
            language.form_button_text = request.POST.get('form_button_text', language.form_button_text)
            language.content = request.POST.get('content', language.content)

            # Save changes
            language.save()
            run_async_xml_sitemap_generator()

            return JsonResponse({'message': 'Language updated successfully'}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)


    


@csrf_exempt
def delete_language(request, language_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)

    if 'admin' not in request.session:
        return JsonResponse({"error": "Unauthorized access."}, status=401)

    try:
        # Fetch the language object
        language = Languages.objects.get(id=language_id)
        # Delete the language object
        language.delete()
        run_async_xml_sitemap_generator()
        return JsonResponse({"message": "Language deleted successfully."}, status=200)

    except Languages.DoesNotExist:
        return JsonResponse({"error": "Language not found."}, status=404)





def add_new_cutom_page(request):
    if request.method == 'POST':
        # Check if the user is authorized
        if 'admin' not in request.session:
            return JsonResponse({"error": "Unauthorized access."}, status=401)

        # Extract data from the request
        language_id = request.POST.get('language')
        page_name = request.POST.get('page_name')
        slug = request.POST.get('slug')
        meta_title = request.POST.get('meta_title')
        meta_description = request.POST.get('meta_description')
        header = request.POST.get('header')
        content = request.POST.get('content')

        # Validate inputs
        if not all([language_id, page_name, slug, meta_title, meta_description, content]):
            return JsonResponse({'error': 'All fields are required.'}, status=400)

        # Check if the language exists
        try:
            language = Languages.objects.get(id=language_id)
        except Languages.DoesNotExist:
            return JsonResponse({'error': 'Language not found.'}, status=404)

        # Check if a page with the same slug already exists for the given language
        if Page.objects.filter(slug=slugify(slug), language=language).exists():
            return JsonResponse({'error': 'A page with this slug already exists for the selected language.'}, status=400)

        # Create the page
        try:
            page = Page.objects.create(
                language=language,
                page_name=page_name,
                slug=slug,
                meta_title=meta_title,
                meta_description=meta_description,
                header=header,
                content=content
            )
            return JsonResponse({'message': 'Page created successfully.'}, status=201)
        except Exception as e:
            return JsonResponse({'error': f'An error occurred while creating the page: {str(e)}'}, status=500)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed.'}, status=405)
    




def edit_cutom_page(request):
    if request.method == 'POST':
        # Check if the user is authorized
        if 'admin' not in request.session:
            return JsonResponse({"error": "Unauthorized access."}, status=401)

        # Extract data from the request
        page_id = request.POST.get('id')
        page_name = request.POST.get('page_name')
        slug = request.POST.get('slug')
        meta_title = request.POST.get('meta_title')
        meta_description = request.POST.get('meta_description')
        header = request.POST.get('header')
        content = request.POST.get('content')

        # Validate inputs
        if not all([page_id, page_name, slug, meta_title, meta_description, content]):
            return JsonResponse({'error': 'All fields are required.'}, status=400)

        # Check if the page exists
        try:
            page = Page.objects.get(id=page_id)
        except Page.DoesNotExist:
            return JsonResponse({'error': 'Page not found.'}, status=404)
        
        old_slug = page.slug

        # Update the page fields
        page.page_name = page_name
        page.slug = slug
        page.meta_title = meta_title
        page.meta_description = meta_description
        page.header = header
        page.content = content

        # Save the updated page
        try:
            page.save()
            if old_slug != slug:
                redirect_entry, created = Redirect.objects.get_or_create(
                    path=old_slug,
                    redirect_url=slug,
                    defaults={"http_status_code": 301}
                )
                if created:
                    print("Redirect created successfully.")
                else:
                    print("Redirect already exists.")
            return JsonResponse({'message': 'Page updated successfully.'})
        except Exception as e:
            return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)

    else:
        return JsonResponse({'error': 'Only POST requests are allowed.'}, status=405)
    


@csrf_exempt
def delete_custom_page(request, page_id):
    if request.method == 'DELETE':
        if 'admin' not in request.session:
            return JsonResponse({"error": "Unauthorized access."}, status=401)
        try:
            page = Page.objects.get(id=page_id)
        except Page.DoesNotExist:
            return JsonResponse({"error": "Page not found."}, status=404)
        page.delete()
        return JsonResponse({"message": "Page deleted successfully."}, status=200)
    else:
        return JsonResponse({'error': 'Only DELETE requests are allowed'}, status=405)



def api_settings(request):
    try:
        if request.method == 'POST':
            iframe_url = request.POST.get("iframe_url")
            cobalt_api_url = request.POST.get("cobalt_api_url")
            current_use = request.POST.get("current_use")
            direct_ad = request.POST.get("direct_ad")
            social_link = request.POST.get("social_link")

            # Pehli record fetch karein
            settings = Settings.objects.first()
            
            if settings:  # Agar record exist karta hai to update karein
                settings.iframe_url = iframe_url
                settings.cobalt_api_url = cobalt_api_url
                settings.current_use = current_use
                settings.direct_ad = direct_ad
                settings.social_link = social_link
                settings.save()
            else:  # Agar record exist nahi karta to naya record create karein
                settings = Settings.objects.create(
                    iframe_url=iframe_url,
                    cobalt_api_url=cobalt_api_url,
                    current_use=current_use,
                    direct_ad=direct_ad,
                    social_link=social_link
                )

            return JsonResponse({'message': 'Changes saved successfully!'})

        else:
            return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)

    except Exception as e:
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)
    
def theme(request):
    try:
        if request.method == 'POST':
            # Get data from the POST request
            bg_light = request.POST.get('bg_light')
            bg_dark = request.POST.get('bg_dark')
            text_dark = request.POST.get('text_dark', 'black')
            text_light = request.POST.get('text_light', 'white')
            border_light = request.POST.get('border_light')
            border_dark = request.POST.get('border_dark')
            toggle_bg = request.POST.get('toggle_bg')
            moon_color = request.POST.get('moon_color')
            sun_color = request.POST.get('sun_color')
            dropdown_bg_light = request.POST.get('dropdown_bg_light')
            dropdown_bg_dark = request.POST.get('dropdown_bg_dark')
            dropdown_hover_light = request.POST.get('dropdown_hover_light')
            dropdown_hover_dark = request.POST.get('dropdown_hover_dark')
            message_bg_light = request.POST.get('message_bg_light')
            message_bg_dark = request.POST.get('message_bg_dark')
            message_icon = request.POST.get('message_icon')
            input_border = request.POST.get('input_border')
            search_bg_light = request.POST.get('search_bg_light')
            search_bg_dark = request.POST.get('search_bg_dark')
            search_button_bg = request.POST.get('search_button_bg')
            download_now_button_bg = request.POST.get('download_now_button_bg')
            convert_another_button_bg = request.POST.get('convert_another_button_bg')
            follow_us_button_bg = request.POST.get('follow_us_button_bg')
            mp3_button_bg = request.POST.get('mp3_button_bg')
            mp4_button_bg = request.POST.get('mp4_button_bg')

            # Get the first record in the Theme model (assuming only one theme is stored)
            theme_record = Theme.objects.first()

            if theme_record:
                # Update the fields with new values from the form
                theme_record.bg_light = bg_light
                theme_record.bg_dark = bg_dark
                theme_record.text_dark = text_dark
                theme_record.text_light = text_light
                theme_record.border_light = border_light
                theme_record.border_dark = border_dark
                theme_record.toggle_bg = toggle_bg
                theme_record.moon_color = moon_color
                theme_record.sun_color = sun_color
                theme_record.dropdown_bg_light = dropdown_bg_light
                theme_record.dropdown_bg_dark = dropdown_bg_dark
                theme_record.dropdown_hover_light = dropdown_hover_light
                theme_record.dropdown_hover_dark = dropdown_hover_dark
                theme_record.message_bg_light = message_bg_light
                theme_record.message_bg_dark = message_bg_dark
                theme_record.message_icon = message_icon
                theme_record.input_border = input_border
                theme_record.search_bg_light = search_bg_light
                theme_record.search_bg_dark = search_bg_dark
                theme_record.search_button_bg = search_button_bg
                theme_record.download_now_button_bg = download_now_button_bg
                theme_record.convert_another_button_bg = convert_another_button_bg
                theme_record.follow_us_button_bg = follow_us_button_bg
                theme_record.mp3_button_bg = mp3_button_bg
                theme_record.mp4_button_bg = mp4_button_bg

                # Save the updated record
                theme_record.save()
                root_css_path = os.path.join(BASE_FOLDER_DIR, 'static', 'website', 'css', 'root.css')

                # Create the new CSS content based on the updated theme settings
                css_content = f"""
:root {{
    --bg-light: {bg_light};
    --bg-dark: {bg_dark};
    --text-dark: {text_dark};
    --text-light: {text_light};
    --border-light: {border_light};
    --border-dark: {border_dark};
    --toggle-bg: {toggle_bg};
    --moon-color: {moon_color};
    --sun-color: {sun_color};
    --dropdown-bg-light: {dropdown_bg_light};
    --dropdown-bg-dark: {dropdown_bg_dark};
    --dropdown-hover-light: {dropdown_hover_light};
    --dropdown-hover-dark: {dropdown_hover_dark};
    --message-bg-light: {message_bg_light};
    --message-bg-dark: {message_bg_dark};
    --message-icon: {message_icon};
    --input-border: {input_border};
    --search-bg-light: {search_bg_light};
    --search-bg-dark: {search_bg_dark};
    --search-button-bg: {search_button_bg};
    --download-now-button-bg: {download_now_button_bg};
    --convert-another-button-bg: {convert_another_button_bg};
    --follow-us-button-bg: {follow_us_button_bg};
    --mp3-button-bg: {mp3_button_bg};
    --mp4-button-bg: {mp4_button_bg};
}}
                """

                # Write the updated content to the root.css file
                with open(root_css_path, 'w') as css_file:
                    css_file.write(css_content)

                # Return a success message
                return JsonResponse({'message': 'Theme saved successfully!'})
            else:
                # If no theme record exists in the database
                return JsonResponse({'error': 'No theme record found to update'}, status=404)

        else:
            # Only POST requests are allowed
            return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)

    except Exception as e:
        # Catch any exception that occurs and return an error message
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)
    



def logo_and_favicon(request):
    try:
        if request.method == 'POST':
            # File fields
            logo_light = request.FILES.get('logo_light')
            logo_dark = request.FILES.get('logo_dark')
            favicon_16 = request.FILES.get('favicon_16')
            favicon_32 = request.FILES.get('favicon_32')
            favicon_192 = request.FILES.get('favicon_192')
            favicon_512 = request.FILES.get('favicon_512')

            # Initialize file storage system
            fs = FileSystemStorage(location=os.path.join(BASE_FOLDER_DIR, 'static', 'website', 'images'))

            # Save or overwrite logo files
            if logo_light:
                logo_light_path = fs.save('logo.svg', logo_light)
            if logo_dark:
                logo_dark_path = fs.save('logo-dark.svg', logo_dark)

            # Save or overwrite favicon files
            if favicon_16:
                favicon_16_path = fs.save('favicon-16x16.png', favicon_16)
            if favicon_32:
                favicon_32_path = fs.save('favicon-32x32.png', favicon_32)
            if favicon_192:
                favicon_192_path = fs.save('android-chrome-192x192.png', favicon_192)
            if favicon_512:
                favicon_512_path = fs.save('android-chrome-512x512.png', favicon_512)

            # Return a success response
            return JsonResponse({'message': 'Logo and Favicon saved successfully!'})

        else:
            return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)

    except Exception as e:
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)




    

def api_global_header_update(request):
    try:
        if request.method == 'POST':
            content = request.POST.get("content")
            if not content:
                if content != "":
                    return JsonResponse({'error': 'Content not provided'}, status=400)
            
            global_header = GlobalHeader.objects.first()
            if not global_header:
                return JsonResponse({'error': 'Global header not found'}, status=404)
            
            global_header.header = content
            global_header.save()
            
            return JsonResponse({'message': 'Changes saved successfully!'})
        else:
            return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
    except Exception as e:
        return JsonResponse({'error': 'An error occurred: {}'.format(str(e))}, status=500)
    
def api_global_footer_update(request):
    try:
        if request.method == 'POST':
            content = request.POST.get("content")
            if not content:
                if content != "":
                    return JsonResponse({'error': 'Content not provided'}, status=400)
            
            global_footer = GlobalFooter.objects.first()
            if not global_footer:
                return JsonResponse({'error': 'Global header not found'}, status=404)
            
            global_footer.footer = content
            global_footer.save()
            
            return JsonResponse({'message': 'Changes saved successfully!'})
        else:
            return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
    except Exception as e:
        return JsonResponse({'error': 'An error occurred: {}'.format(str(e))}, status=500)

    
def api_redirect_create(request):
    if request.method == 'POST':
        path = request.POST.get('path')
        redirect_url = request.POST.get('redirect_url')
        http_status_code = request.POST.get('http_status_code')
        
        # Check if all fields are provided
        if not all([path, redirect_url, http_status_code]):
            return JsonResponse({'error': 'Missing data for one or more fields'}, status=400)
        
        # Check if the path already exists
        if Redirect.objects.filter(path=path).exists():
            return JsonResponse({'error': 'Redirect from path already exists'}, status=400)
        
        try:
            # Try to create the redirect instance
            redirect_instance = Redirect.objects.create(path=path, redirect_url=redirect_url, http_status_code=http_status_code)
            data = {
                'id': redirect_instance.id,
                'path': redirect_instance.path, 
                'redirect_url': redirect_instance.redirect_url, 
                'http_status_code': redirect_instance.http_status_code
            }
            return JsonResponse(data, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
    
@csrf_exempt
def api_redirect(request):
    if request.method == 'POST':
        path = request.POST.get('path')
        
        # Check if path is provided
        if not path:
            return JsonResponse({'error': 'Path is required'}, status=400)
        try:
            # Check if the redirect instance exists
            redirect_instance = Redirect.objects.get(path=path)
            data = {
                'path': redirect_instance.path, 
                'redirect_url': redirect_instance.redirect_url, 
                'http_status_code': redirect_instance.http_status_code
            }
            return JsonResponse(data)
        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Redirect with the provided path does not exist'}, status=404)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
    
@csrf_exempt
def api_redirect_delete(request):
    if request.method == 'POST':
        # Retrieve the primary key from the POST data
        pk = request.POST.get('id')
        
        # Check if pk is provided
        if not pk:
            return JsonResponse({'error': 'ID is required'}, status=400)
        
        try:
            # Check if the redirect instance exists
            redirect_instance = Redirect.objects.get(pk=pk)
            
            # Delete the redirect instance
            redirect_instance.delete()
            
            return JsonResponse({'message': 'Redirect deleted successfully'})
        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Redirect does not exist'}, status=404)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
    

@csrf_exempt
def api_direct_redirect_delete(request):
    if request.method == 'POST':
        # Retrieve the primary key from the POST data
        pk = request.POST.get('id')
        
        # Check if pk is provided
        if not pk:
            return JsonResponse({'error': 'ID is required'}, status=400)
        
        try:
            # Check if the redirect instance exists
            redirect_instance = DirectRedirect.objects.get(pk=pk)
            
            # Delete the redirect instance
            redirect_instance.delete()
            
            return JsonResponse({'message': 'Redirect deleted successfully'})
        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Redirect does not exist'}, status=404)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
    



def api_robots_dot_txt_update(request):
    if request.method == 'POST':
        if 'admin' not in request.session:
            return JsonResponse({'error': 'You are not logged in'}, status=401)
        
        new_content = request.POST.get('content')
        
        # Replace any non-standard line break format with '\n'
        new_content = new_content.replace('\r\n', '\n').replace('\r', '\n')        
        robots_dot_txt_path = os.path.join(BASE_FOLDER_DIR,'robots.txt')
        try:
            with open(robots_dot_txt_path, 'w') as file:
                file.write(new_content)  # Write the modified content
            return JsonResponse({'message': 'robots.txt updated successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)