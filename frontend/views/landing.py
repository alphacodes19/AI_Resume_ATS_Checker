import streamlit as st


def render() -> None:
    st.title("🎯 ATS Resume Scorer")
    st.markdown("### Find out how an Applicant Tracking System sees your resume")
    c1, c2, c3 = st.columns(3)
    c1.markdown("**📄 Upload**\n\nPDF or DOCX, up to 5 MB.")
    c2.markdown("**🤖 Analyze**\n\nNLP + AI score formatting, keywords, content and skills.")
    c3.markdown("**🛠️ Improve**\n\nGet prioritised fixes and a downloadable PDF report.")
    st.markdown("---")
    if st.button("Score my resume →", type="primary"):
        st.session_state.current_view = "scorer"
        st.rerun()
