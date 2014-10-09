# oppia/preview/views.py
import codecs
import os
import re

from django.conf import settings
from django.shortcuts import render,render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from oppia.models import Course, Activity
from oppia.views import check_can_view
from oppia.course_xml_reader import CourseXML

def home_view(request):
    
    course_list = [] 
    # only get courses that are already published for preview
    for dir in os.listdir(settings.MEDIA_ROOT + "courses/"):
        try:
            if request.user.is_staff:
                course = Course.objects.get(is_archived=False, shortname=dir)
            else:
                course = Course.objects.filter(is_draft=False,is_archived=False, shortname=dir)
                
            course_list.append(course)
        except Course.NotFound:
            pass
        
    return render_to_response('oppia/preview/home.html',
                              {'course_list': course_list}, 
                              context_instance=RequestContext(request))

def course_home_view(request, id):
    course = check_can_view(request, id)
    return render_to_response('oppia/preview/course_home.html',
                              {'course': course }, 
                              context_instance=RequestContext(request))
    
def course_activity_view(request, course_id, activity_id):
    course = check_can_view(request, course_id)
    activity = Activity.objects.get(pk=activity_id)
    
    if activity.type == "page":
        activity_content_file = activity.get_content()
        
        with codecs.open(settings.MEDIA_ROOT + "courses/" + course.shortname + "/" + activity_content_file, "r", "utf-8") as f:
            s = f.read()
        
        template = re.compile('\<body(?P<body>.*?)>(?P<content>.*)\<\/body\>', re.DOTALL)
        
        activity_content = template.search(s).group('content')
        activity_content =  activity_content.replace("images/",settings.MEDIA_URL + "courses/" + course.shortname + "/images/")
        
        return render_to_response('oppia/preview/course_activity_page.html',
                                  {'course': course, 'activity': activity , 'content' : activity_content }, 
                                  context_instance=RequestContext(request))