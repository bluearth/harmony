from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Enodika app
    (r'^enodika/', include('harmony.enodika.urls')),
    # Auth
  	(r'^accounts/login/$', 'django.contrib.auth.views.login',{'template_name': 'login.html'}),
  	(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'template_name': 'logout.html'}),
    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)
