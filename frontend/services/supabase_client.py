"""Supabase auth over plain REST (no SDK) — email/password + Google OAuth (PKCE)."""
import base64
import hashlib
import secrets
from typing import Any, Dict
from urllib.parse import urlencode

import requests
import streamlit as st

# PKCE verifiers must survive the redirect to Google and back, which starts a new
# Streamlit session. A process-level dict keyed by a random `sid` bridges that gap.
_PENDING_VERIFIERS: Dict[str, str] = {}


def _cfg() -> Dict[str, str]:
    try:
        s = st.secrets["supabase"]
        return {
            "url": s["url"].rstrip("/"),
            "key": s["anon_key"],
            "redirect": s.get("redirect_url", ""),
        }
    except (KeyError, FileNotFoundError):
        return {}


def _headers(key: str) -> Dict[str, str]:
    return {"apikey": key, "Content-Type": "application/json"}


def _session_result(data: Dict[str, Any]) -> Dict[str, Any]:
    user = data.get("user") or {}
    return {
        "access_token": data["access_token"],
        "refresh_token": data.get("refresh_token"),
        "user_id": user.get("id"),
        "email": user.get("email"),
    }


def _err(resp: requests.Response) -> Dict[str, str]:
    try:
        body = resp.json()
        msg = body.get("error_description") or body.get("msg") or body.get("message") or resp.text
    except ValueError:
        msg = resp.text
    return {"error": msg}


def sign_in_with_password(email: str, password: str) -> Dict[str, Any]:
    c = _cfg()
    if not c:
        return {"error": "Supabase is not configured in Streamlit secrets."}
    r = requests.post(
        f"{c['url']}/auth/v1/token?grant_type=password",
        json={"email": email, "password": password},
        headers=_headers(c["key"]), timeout=20,
    )
    return _session_result(r.json()) if r.ok else _err(r)


def sign_up_with_password(email: str, password: str) -> Dict[str, Any]:
    c = _cfg()
    if not c:
        return {"error": "Supabase is not configured in Streamlit secrets."}
    r = requests.post(
        f"{c['url']}/auth/v1/signup",
        json={"email": email, "password": password},
        headers=_headers(c["key"]), timeout=20,
    )
    if not r.ok:
        return _err(r)
    data = r.json()
    if data.get("access_token"):
        return _session_result(data)
    return {"pending_confirmation": True, "email": email}


def sign_out() -> None:
    c = _cfg()
    token = st.session_state.get("access_token")
    if not c or not token:
        return
    try:
        requests.post(
            f"{c['url']}/auth/v1/logout",
            headers={**_headers(c["key"]), "Authorization": f"Bearer {token}"}, timeout=10,
        )
    except requests.RequestException:
        pass


def google_oauth_url() -> Dict[str, str]:
    c = _cfg()
    if not c or not c["redirect"]:
        return {"error": "redirect_url not set in secrets"}
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    sid = secrets.token_urlsafe(8)
    _PENDING_VERIFIERS[sid] = verifier
    sep = "&" if "?" in c["redirect"] else "?"
    params = {
        "provider": "google",
        "redirect_to": f"{c['redirect']}{sep}sid={sid}",
        "code_challenge": challenge,
        "code_challenge_method": "s256",
    }
    return {"url": f"{c['url']}/auth/v1/authorize?{urlencode(params)}"}


def exchange_code_for_session(code: str) -> Dict[str, Any]:
    c = _cfg()
    if not c:
        return {"error": "Supabase is not configured."}
    verifier = _PENDING_VERIFIERS.pop(st.query_params.get("sid", ""), None)
    if not verifier:
        return {"error": "Login session expired — please try again."}
    r = requests.post(
        f"{c['url']}/auth/v1/token?grant_type=pkce",
        json={"auth_code": code, "code_verifier": verifier},
        headers=_headers(c["key"]), timeout=20,
    )
    return _session_result(r.json()) if r.ok else _err(r)
