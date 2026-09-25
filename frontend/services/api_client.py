"""
Same public functions/signatures as the original HTTP api_client, so
frontend/views/*.py don't need to change. Internally these now call the
analysis pipeline in-process (see local_backend.py) instead of making an
HTTP request to a separate FastAPI server.

`access_token` is kept as a parameter for compatibility with existing call
sites, but the user id (needed for saving/reading history) comes from
`st.session_state["user_id"]`, which is set at sign-in.
"""
from typing import Any, Dict, List

import streamlit as st

from frontend.services import local_backend


def _user_id() -> str:
    user_id = st.session_state.get("user_id")
    if not user_id:
        raise RuntimeError("Not signed in.")
    return user_id


def health_check() -> Dict[str, Any]:
    return local_backend.health_check()


def analyze_resume(resume_file, access_token: str, job_description: str = "") -> Dict[str, Any]:
    return local_backend.analyze_resume(resume_file, _user_id(), job_description)


def get_history(access_token: str) -> List[Dict[str, Any]]:
    return local_backend.get_history(_user_id())


def delete_history_entry(analysis_id: str, access_token: str) -> None:
    local_backend.delete_history_entry(analysis_id, _user_id())


def generate_pdf(analysis_data: Dict[str, Any], access_token: str) -> bytes:
    return local_backend.generate_pdf(analysis_data)


def get_history_pdf(analysis_id: str, access_token: str) -> bytes:
    return local_backend.get_history_pdf(analysis_id, _user_id())
