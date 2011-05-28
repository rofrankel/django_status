"""
Easily send e-mail messages using text (and optional additional HTML)
templates.

Set up:

1. Make an ``emails`` directory in your template.

2. Create a base text template which will be used as the base for each e-mail
   message (for example, ``emails/base.txt``)::

       {% block content %}{% endblock %}
       --
       http://glados.com

Create & use an email template:

1. Create a text template which will contain for each message (for example,
   ``emails/success.txt``). This should extend the base template, and have a
   line starting with ``SUBJECT:`` which contains the subject of the email::

       {% extends "emails/base.txt" %}
       SUBJECT: It was a triumph
       {% block content %}I'm making a note here: huge success.{% endblock %}

2. Optionally, create an HTML template which will contain the HTML part of the
   same message (following the example, ``emails/success.html``)

3. In your view, call ``send_mail_from_template(to, 'success', context)``,
   where ``to`` is a string containing an e-mail or a list of strings
   containing e-mails, and content is an (optional) dictionary containing
   context variables to use when rendering the template(s).

"""

from django.contrib.sites import models as site_models
from django.core import mail as django_mail
from django.template import loader, Context, TemplateDoesNotExist
from django.template.loaders.filesystem import Loader as FileSystemLoader
import re
import logging

# Due to http://code.djangoproject.com/ticket/11212
from email import Charset
Charset.add_charset('utf-8',Charset.SHORTEST,None,'utf-8')

RE_SUBJECT = re.compile(r'SUBJECT:\s*(.+)')

def send_mail_from_template(to, template_name, context=None,
                            fail_silently=True, from_email=None,
                            bcc=None):
    """
    Send an email based on a Django template.

    """
    msg = get_message_from_template(to, template_name, context,
                                    from_email=from_email, bcc=bcc)

    if fail_silently:
        try:
            logging.debug('New email being sent to %s with context: %s' 
                         % (to, unicode(repr(context).decode('utf-8'))))
            msg.send()
            logging.debug('Message sent')
        except Exception, e:
            logging.error(str(e))
    else:
        logging.debug('New email being sent to %s with context: %s' 
                      % (to, repr(context)))
        msg.send()
        logging.debug('Message sent')


def get_message_from_template(to, template_name, context=None, from_email=None,
                              bcc=None):
    """
    Build an e-mail message from a Django template, also looking for an
    optional additional HTML part.

    """
    # Build the context
    context = context or {}
    context['site'] = site_models.Site.objects.get_current()
    context.update({'site': site_models.Site.objects.get_current()})
    if not isinstance(context, Context):
        context = Context(context)
    context.autoescape = False
    
    # Get the text email body
    source, origin = FileSystemLoader().load_template_source('emails/%s.txt' % template_name)
    
    template = loader.get_template_from_string(source, origin, template_name)
    body = template.render(context)
    # Get the subject line
    match = RE_SUBJECT.search(source)
    if not match:
        raise ValueError('The email source did not contain a "SUBJECT:" line')
    subject_source = match.group(1)
    template = loader.get_template_from_string(subject_source, origin,
                                               template_name)
    subject = template.render(context)
    # Format the recipient and build the e-mail message
    if isinstance(to, basestring):
        to = [to]
    message = django_mail.EmailMultiAlternatives(subject, body, to=to, 
                                                 from_email=from_email,
                                                 bcc=bcc)
    
    # See if we've got an HTML component too
    try:
        html = loader.render_to_string('emails/%s.html' % template_name,
                                       context)
    except TemplateDoesNotExist:
        pass
    else:
        message.attach_alternative(html, "text/html")
    
    return message
