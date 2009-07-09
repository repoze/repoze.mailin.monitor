from webob import Response

def quarantine_status_view(quarantine, request):
    """
    Sends OK if quarantine is empty, otherwise sends ERROR.
    """
    if quarantine.empty():
        return Response('OK')

    return Response('ERROR')