# accounts/oauth.py
from django.conf import settings
from django.shortcuts import redirect

GOOGLE_SCOPES = ["openid", "email", "profile", "https://www.googleapis.com/auth/gmail.readonly"]

def google_start(request):
    """
    Build Google's OAuth URL and redirect.
    Store any needed state (e.g., special code) in session before calling this.
    """
    # TODO: implement using your OAuth library (google-auth, etc.)
    return redirect("/accounts/auth/callback/google?mock=1&email=test@example.com&name=Test%20User")

def google_finish(request):
    """
    Exchange code for tokens, return (email, name, tokens).
    """
    # TODO: parse "code" + exchange for tokens, return data
    email = request.GET.get("email")
    name = request.GET.get("name") or email
    tokens = {"access_token": "mock", "refresh_token": "mock", "expiry": None}
    return email, name, tokens
