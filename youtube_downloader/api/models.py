from django.db import models

class Admin(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    def __str__(self):
        return self.email
    

class Redirect(models.Model):
    path = models.CharField(max_length=250, unique=True)
    redirect_url = models.TextField()
    http_status_code = models.PositiveIntegerField(default=301)
    def __str__(self):
        return self.path
    
class GlobalHeader(models.Model):
    header = models.TextField()

class GlobalFooter(models.Model):
    footer = models.TextField()


class Languages(models.Model):
    name =  models.TextField()
    lang =  models.TextField()
    dir =  models.TextField()
    page_name = models.TextField()
    slug = models.TextField()
    meta_title = models.TextField()
    meta_description = models.TextField()
    header = models.TextField()
    heading = models.TextField()
    tag_line = models.TextField()
    message_one = models.TextField()
    message_two = models.TextField()
    banner_ad_one = models.TextField()
    banner_ad_two = models.TextField()
    placeholder = models.TextField()
    form_button_text = models.TextField()
    content = models.TextField()

class DirectRedirect(models.Model):
    language = models.ForeignKey(Languages, on_delete=models.CASCADE, related_name="faqs")
    old_slug = models.TextField()


class Page(models.Model):
    language = models.ForeignKey(Languages, on_delete=models.CASCADE, related_name="dynamic_pages")
    page_name = models.TextField()
    slug = models.TextField()
    meta_title = models.TextField()
    meta_description = models.TextField()
    header = models.TextField()
    content = models.TextField()

    def __str__(self):
        return f"{self.page_name} ({self.language.name})"
    


class Settings(models.Model):
    iframe_url = models.TextField()
    cobalt_api_url = models.TextField()
    current_use = models.TextField()
    direct_ad = models.TextField()
    social_link = models.TextField()



class Theme(models.Model):
    bg_light = models.TextField(default="#FFFFFF")
    bg_dark = models.TextField(default="#293033")
    text_dark = models.TextField(default="black")
    text_light = models.TextField(default="white")
    border_light = models.TextField(default="#cccccc")
    border_dark = models.TextField(default="#444")
    toggle_bg = models.TextField(default="#111")
    moon_color = models.TextField(default="#f1c40f")
    sun_color = models.TextField(default="#f39c12")
    dropdown_bg_light = models.TextField(default="#f9f9f9")
    dropdown_bg_dark = models.TextField(default="#444")
    dropdown_hover_light = models.TextField(default="#e0e0e0")
    dropdown_hover_dark = models.TextField(default="#666")
    message_bg_light = models.TextField(default="#EDF7ED")
    message_bg_dark = models.TextField(default="#222")
    message_icon = models.TextField(default="#2e7d32")
    input_border = models.TextField(default="#666666ad")
    search_bg_light = models.TextField(default="#f8f8f8")
    search_bg_dark = models.TextField(default="#222")
    search_button_bg = models.TextField(default="#000000")
    download_now_button_bg = models.TextField(default="#000000")
    convert_another_button_bg = models.TextField(default="#000000")
    follow_us_button_bg = models.TextField(default="#000000")
    mp3_button_bg = models.TextField(default="#000000")
    mp4_button_bg = models.TextField(default="#000000")