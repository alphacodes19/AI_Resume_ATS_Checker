import requests
import streamlit as st

from frontend.components.dashboard import display_results_dashboard
from frontend.services import api_client


def _show_backend_error(exc: Exception) -> None:
    if isinstance(exc, requests.ConnectionError):
        st.error("Could not reach the backend. It may be starting up — retry in a minute.")
    elif isinstance(exc, requests.HTTPError) and exc.response is not None:
        st.error(f"Backend returned {exc.response.status_code}: {exc.response.text}")
    else:
        st.error(f"Unexpected error: {exc}")


def render() -> None:
    st.title("🎯 ATS Scorer")
    token = st.session_state.get("access_token")
    if not token:
        st.warning("⚠️ Sign in from the sidebar to analyze a resume.")
        return

    resume = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx", "doc"])
    jd = st.text_area("Job description (optional)", height=180)

    if st.button("Analyze", type="primary", disabled=resume is None):
        with st.spinner("Analyzing… the first request after idle can take a minute."):
            try:
                st.session_state.last_analysis = api_client.analyze_resume(resume, token, jd)
            except requests.RequestException as exc:
                _show_backend_error(exc)
                return

    analysis = st.session_state.get("last_analysis")
    if analysis:
        display_results_dashboard(analysis)
        try:
            pdf = api_client.generate_pdf(analysis, token)
            st.download_button("⬇️ Download PDF report", pdf, "ats_report.pdf", "application/pdf")
        except requests.RequestException:
            st.caption("PDF report unavailable right now.")
