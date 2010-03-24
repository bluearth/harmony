from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',

    (r'^$', 'harmony.enodika.views.index'),
	# Static media
	(r'^asset/(?P<path>.*)$', 'django.views.static.serve',
		{'document_root':settings.STATIC_DOC_ROOT}),
	
	## Menu actions
	(r'^notavail$', 'harmony.enodika.views.not_avail'),
	(r'^createnota$', 'harmony.enodika.views.create_nota'),
	(r'^editnota/(?P<nota_id>\d+)$', 'harmony.enodika.views.edit_nota'),  
	(r'^send$', 'harmony.enodika.views.disposisi_nota'),
	(r'^forward/(?P<dispo_id>\d+)$', 'harmony.enodika.views.forward_dispo'),
	(r'^savedraft(/(?P<nota_id>\d+))?$', 'harmony.enodika.views.save_draft'),
	(r'^abandonedit$', 'harmony.enodika.views.abandon_edit'),
	(r'^drafts/(?P<sort_by>.*)(/(?P<asc>.*))*$', 'harmony.enodika.views.list_draft'),
	(r'^drafts/delmany$', 'harmony.enodika.views.discard_draft'),	
	(r'^dispos/view(/(?P<dispo_id>\d+))?$', 'harmony.enodika.views.view_dispo'),
	(r'^dispos/(?P<sort_by>.*)(/(?P<asc>.*))*$', 'harmony.enodika.views.list_dispo'),
)
