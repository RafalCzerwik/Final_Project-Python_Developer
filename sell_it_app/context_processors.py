from sell_it_app.models import Messages, Newsletter


def unread_messages(request):
    user = request.user
    ctx = {}
    if user.is_authenticated:
        id = user.id
        user_unread_messages = Messages.objects.filter(to_user_id=id).filter(status='Unread').count()

        ctx = {
            'user_unread_messages': user_unread_messages,
        }
        return ctx
    return ctx
