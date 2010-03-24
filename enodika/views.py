import datetime
import re

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from harmony.enodika import settings
from harmony.enodika.models import NotaDinas, Draft, Disposisi


class ValidationMsg:
	elementId = ''
	description = ''
	
	def __init__(self, elemId, desc):
		self.elementId = elemId
		self.description = desc

# Main page
@login_required
def index(request):
	app_name = settings.APP_NAME
	return render_to_response('index.html',
		{
			'settings_app_name': settings.APP_NAME,
			'user' : request.user,
		})

#######
# Action handlers
#######

# Create Nota
@login_required
def create_nota(request):
	return render_to_response('create_nota.html',
		{
			'settings_app_name': settings.APP_NAME,
			'user' : request.user,			
		})

# Edit Nota
@login_required
def edit_nota(request,nota_id):

	nota = NotaDinas.objects.get(id=nota_id)

	return render_to_response('create_nota.html',
		{
			'settings_app_name': settings.APP_NAME,
			'user' : request.user,
			'nota' : nota,
		})
		
# Disposisi Nota
@login_required
def disposisi_nota(request):
	msg = []
	nota_index = None # replace with url pass GET vars
	
	l_subject = request.POST['subjectTxt']
	l_serial = request.POST['serialNoTxt']
	l_content = request.POST['contentTxa']
	l_recipients = request.POST['recipientList']
	l_ccrecipients = request.POST['ccRecipientList']	
	l_nota_date = datetime.datetime.now()
	
	if nota_index == None :					# If nota_id not in GET
		nota_index = request.POST['notaId']	# fetch nota id from POST instead
		print 'Got id from POST'
	
	## Create or update nota
	if nota_index <> None and nota_index.strip() <> '': 	# Update
		nota = NotaDinas.objects.get( id = nota_index )
		draft = Draft.objects.get(nota__id__exact = nota.id)
		print 'Updating nota ' + str(nota.id)
	else : 		# Create
		nota = NotaDinas()
		draft = Draft() 
		print 'Saving new nota'
		
	nota.subject = l_subject
	nota.serialno = l_serial
	nota.content = l_content 
	nota.author = request.user
	nota.create_date = l_nota_date
	nota.recipients = l_recipients
	nota.ccrecipients = l_ccrecipients
	nota.save()
					
	draft.nota = nota
	draft.last_edit = l_nota_date	
	draft.save()			
	####

	# Start disposisi
	dispatch_date = datetime.datetime.now()
	try:
		for recuser in split_recipients(l_recipients):
			dispo = Disposisi()
			dispo.nota = nota
			dispo.initiator = request.user.first_name + ' ' + request.user.last_name
			dispo.recipient = recuser
			dispo.dispatch_date = dispatch_date
			dispo.forwarded_from = None
			dispo.save()
	
		for ccrecuser in split_recipients(l_ccrecipients):
			dispo = Disposisi()
			dispo.nota = nota
			dispo.initiator = request.user.first_name + ' ' + request.user.last_name
			dispo.recipient = ccrecuser
			dispo.dispatch_date = dispatch_date
			dispo.forwarded_from = None			
			dispo.save()
			
	except ObjectDoesNotExist:
		msg.append( ValidationMsg(elemId='',desc='User tidak terdaftar.') )
		return render_to_response('index.html',
			{
				'settings_app_name': settings.APP_NAME,
				'user' : request.user,
				'action_result_msgs' : msg,
			})
		
	# Remove draft if exists
	drafts = Draft.objects.filter(nota__id__exact = nota.id)
	for draft in drafts:
		draft.delete()

	msg.append(	ValidationMsg(elemId='',desc='Nota terkirim.') )	
	
	return render_to_response('index.html',
		{
			'settings_app_name': settings.APP_NAME,
			'user' : request.user,
			'action_result_msgs' : msg,
		})

def split_recipients(recipient_list):
	recipient = []
	chunks = recipient_list.split(',')
	for chunk in chunks :
		m = re.match(r'(\w+)(\s)*(<([\w ]*)>)?',chunk.strip())
		if m:
			usrname = m.group(1)
			user = User.objects.get(username=usrname.strip())
			recipient.append(user)
		
	
	return recipient
	


# Save nota draft		
@login_required
def save_draft(request,nota_id):
	
	nota_index = nota_id
	l_subject = request.POST['subjectTxt']
	l_serial = request.POST['serialNoTxt']
	l_content = request.POST['contentTxa']
	l_recipients = request.POST['recipientList']
	l_ccrecipients = request.POST['ccRecipientList']	
	l_nota_date = datetime.datetime.now()
	
	if nota_index == None :					# If nota_id not in GET
		nota_index = request.POST['notaId']	# fetch nota id from POST instead
	
	if nota_index <> None and nota_index.strip() <> '':
		nota = NotaDinas.objects.get( id = nota_index )
		draft = Draft.objects.get(nota__id__exact = nota.id)
	else : 					
		nota = NotaDinas()
		draft = Draft() 

	nota.subject = l_subject
	nota.serialno = l_serial
	nota.content = l_content 
	nota.author = request.user
	nota.create_date = l_nota_date
	nota.recipients = l_recipients
	nota.ccrecipients = l_ccrecipients			
	nota.save()
					
	draft.nota = nota
	draft.last_edit = l_nota_date	
	draft.save()	
	
	msg = [
		ValidationMsg(elemId='',desc='Draft tersimpan.'),
	]	
	
	return render_to_response('index.html',
		{
			'settings_app_name': settings.APP_NAME,
			'user' : request.user,
			'action_result_msgs' : msg,
		})
		
# Abandon edit
@login_required
def abandon_edit(request):
	msg = [
		ValidationMsg(elemId='',desc='Pembuatan nota dibatalkan.'),
	]
	return render_to_response('index.html',
		{
			'settings_app_name': settings.APP_NAME,
			'user' : request.user,
			'action_result_msgs' : msg,
		})
		

## Draft

# List owned drafts
@login_required
def list_draft(request, sort_by, asc):
	
	owner = request.user
	drafts = Draft.objects.filter(nota__author__exact = owner.id)
	drafts = drafts.order_by('-nota__create_date')
	
	if sort_by == 'authdate' :
		drafts = drafts.order_by('-nota__create_date')
	elif sort_by == 'subject' :
		drafts = drafts.order_by('nota__subject')
	elif sort_by == 'serial' :
		drafts = drafts.order_by('nota__serialno')
	else :
		pass
		
	return render_to_response('drafts.html',
		{
			'settings_app_name': settings.APP_NAME,
			'user' : request.user,
			'drafts' : drafts
		})

####TODO###
# Discard draft(s)
@login_required
def discard_draft(request):	
	
	msg = [
		ValidationMsg(elemId='',desc='Konsep telah dihapus.'),
	]
	return render_to_response('drafts.html',
		{
			'settings_app_name': settings.APP_NAME,
			'user' : request.user,
			'action_result_msgs' : msg,
			'drafts' : drafts
		})

## Disposisi
# List incoming dispo
## Disposisi

# List incoming disposisi
@login_required
def list_dispo(request, sort_by, asc):
	
	l_recipient = request.user
	incoming_disp = Disposisi.objects.filter(recipient = l_recipient.id)
	incoming_disp = incoming_disp.order_by('-dispatch_date')
		
	return render_to_response('disps.html',
		{
			'settings_app_name': settings.APP_NAME,
			'user' : request.user,
			'dispos' : incoming_disp
		})

# View disposisi
@login_required
def view_dispo(request, dispo_id):
	l_recipient = request.user
	disposisi = Disposisi.objects.get(id = dispo_id)
	
	reclist = []
	otherdispos = Disposisi.objects.filter(nota__id__exact = disposisi.nota.id)
	for disp in otherdispos:
		reclist.append(disp.recipient)
	
	
	return render_to_response('prettyview.html',
		{
			'settings_app_name': settings.APP_NAME,
			'user' : request.user,
			'dispo' : disposisi,
			'recipients' : reclist
		})

# Forward disposisi
@login_required
def forward_dispo(request, dispo_id):
	msg = []
	l_recipients = request.POST['recipientList']
	l_message = request.POST['commentTxa']
	orig_dispo = Disposisi.objects.get(id = dispo_id)
	
	# Save actions and comment
	orig_dispo.comment = l_message
	orig_dispo.save()
	
	# Start disposisi
	dispatch_date = datetime.datetime.now()
	try:
		for recuser in split_recipients(l_recipients):
			fwd_dispo = Disposisi()
			fwd_dispo.nota = orig_dispo.nota
			fwd_dispo.initiator = request.user.first_name + ' ' + request.user.last_name
			fwd_dispo.recipient = recuser
			fwd_dispo.dispatch_date = dispatch_date
			fwd_dispo.forwarded_from = orig_dispo
			fwd_dispo.comment = ''
			fwd_dispo.save()
	except ObjectDoesNotExist:
		msg.append( ValidationMsg(elemId='',desc='User tidak terdaftar.') )
		return render_to_response('index.html',
			{
				'settings_app_name': settings.APP_NAME,
				'user' : request.user,
				'action_result_msgs' : msg,
			})
	
	msg.append( ValidationMsg(elemId='',desc='Terusan nota berhasil dikirim.') )
	return render_to_response('index.html',
		{
			'settings_app_name': settings.APP_NAME,
			'user' : request.user,
			'action_result_msgs' : msg,
		})


# Forward disposisi
@login_required
def not_avail(request):
	return render_to_response('underdevel.html',
		{
			'settings_app_name': settings.APP_NAME,
			'user' : request.user,	
		})

