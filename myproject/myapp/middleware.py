# watches/middleware.py
from datetime import datetime, timedelta
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import logout

class AutoLogout(MiddlewareMixin):
    def process_request(self, request):
        if not request.user.is_authenticated:
            return

        now = datetime.now()
        last_activity = request.session.get('last_activity')

        if last_activity:
            elapsed = now - datetime.fromisoformat(last_activity)
            if elapsed > timedelta(seconds=settings.SESSION_COOKIE_AGE):
                logout(request)
                request.session.flush()
                return

        request.session['last_activity'] = now.isoformat()
