from django.db import models
from harmony.enodika import settings
from django.contrib.auth.models import User

# Create your models here.

class NotaDinas(models.Model):
    subject = models.CharField('Perihal', max_length=200)
    serialno = models.CharField('Nomor Nota', max_length=200)
    content = models.CharField('Isi Nota', max_length=settings.NOTA_MAX_CHAR)
    create_date = models.DateTimeField('Waktu pembuatan')
    author = models.ForeignKey(User)
    recipients = models.CharField('Tujuan', max_length=1000)
    ccrecipients = models.CharField('Tembusan', max_length=1000)
    
    def __unicode__(self):
		return self.subject + '(' + str(self.id) + ')'

#class NotaDinas
    
class Draft(models.Model):
	nota = models.ForeignKey(NotaDinas)
	last_edit = models.DateTimeField('Waktu edit terakhir')
	
	def __unicode__(self):
		return self.nota.subject + '(' + str(self.id) + ')'

#class Draft

class Disposisi(models.Model):
	nota = models.ForeignKey(NotaDinas)
	forwarded_from = models.ForeignKey('self',null=True)
	initiator = models.CharField('Pengirim', max_length=200)
	recipient = models.ForeignKey(User)
	dispatch_date = models.DateTimeField('Waktu kirim')
	comment = models.CharField('Komentar', max_length=settings.NOTA_MAX_CHAR)
	action = models.CharField('Tindakan', max_length=500,null=True)
	
	def __unicode__(self):
		return self.nota.subject + '( from : ' + self.nota.author.username + \
			', sender : ' + self.initiator + \
			', to : ' + self.recipient.username + ')'

#class Disposisi
	
