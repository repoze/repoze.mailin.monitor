from webob import Response
from pyramid.chameleon_zpt import render_template_to_response
from pyramid.url import resource_url

def quarantine_status_view(quarantine, request):
    """
    Sends OK if quarantine is empty, otherwise sends ERROR.
    """
    if quarantine.empty():
        return Response('OK')

    return Response('ERROR')

def quarantine_list_view(quarantine, request):
    """
    Lists messages in quarantine.
    """
    messages = []
    for message_id, error_msg in quarantine:
        url = resource_url(quarantine.__parent__, request, 'messages',
                           message_id)
        messages.append({
            'message_id': message_id,
            'error_msg': error_msg,
            'url': url
            })

    return render_template_to_response(
        'templates/quarantine_list.pt',
        messages=messages
    )

def show_message_view(message, request):
    """
    Shows a message in the mail store.
    """
    return render_template_to_response(
        'templates/show_message.pt',
        message_id=message.message_id,
        raw=str(message.message)
        )

