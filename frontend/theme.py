# theme.py
# Shared dark purple theme for all pages

def apply_dark_theme():
    import streamlit as st
    st.markdown("""
<style>
    /* Hide streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main background */
    .stApp {
        background-color: #0d0b14 !important;
    }
    
    /* Sidebar background */
    [data-testid="stSidebar"] {
        background-color: #13111c !important;
        border-right: 0.5px solid #2d2b3d !important;
    }
    
    /* Sidebar text */
    [data-testid="stSidebar"] * {
        color: #e2d9f3 !important;
    }
    
    /* Navigation links */
    [data-testid="stSidebarNav"] a {
        color: #AFA9EC !important;
    }
    
    [data-testid="stSidebarNav"] a:hover {
        color: #e2d9f3 !important;
        background: #1e1a2e !important;
    }
    
    /* Active nav item */
    [data-testid="stSidebarNav"] a[aria-current="page"] {
        background: #1e1a2e !important;
        border-left: 3px solid #7F77DD !important;
        color: #e2d9f3 !important;
    }
    
    /* All text */
    .stApp p, .stApp span, .stApp label,
    .stApp div, .stApp h1, .stApp h2,
    .stApp h3 {
        color: #e2d9f3;
    }
    
    /* Input boxes */
    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox select {
        background-color: #1e1a2e !important;
        border: 0.5px solid #2d2b3d !important;
        color: #e2d9f3 !important;
        border-radius: 8px !important;
    }
    
    .stTextInput input:focus,
    .stTextArea textarea:focus {
        border-color: #7F77DD !important;
        box-shadow: none !important;
    }
    
    /* Selectbox */
    [data-testid="stSelectbox"] > div > div {
        background-color: #1e1a2e !important;
        border: 0.5px solid #2d2b3d !important;
        color: #e2d9f3 !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: #1e1a2e !important;
        border: 0.5px solid #534AB7 !important;
        color: #AFA9EC !important;
        border-radius: 8px !important;
    }
    
    .stButton > button:hover {
        background: #2d2b3d !important;
        border-color: #7F77DD !important;
        color: #e2d9f3 !important;
    }
    
    /* Primary button */
    .stButton > button[kind="primary"] {
        background: #534AB7 !important;
        color: #e2d9f3 !important;
    }
    
    /* Expander */
    [data-testid="stExpander"] {
        background: #13111c !important;
        border: 0.5px solid #2d2b3d !important;
        border-radius: 10px !important;
    }
    
    /* Expander header */
    [data-testid="stExpander"] summary {
        color: #e2d9f3 !important;
    }
    
    /* Success/Error/Info boxes */
    [data-testid="stAlert"] {
        background: #1e1a2e !important;
        border: 0.5px solid #2d2b3d !important;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #7F77DD !important;
    }
    
    /* Dataframe */
    [data-testid="stDataFrame"] {
        background: #13111c !important;
    }
    
    /* Divider */
    hr {
        border-color: #2d2b3d !important;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: #7F77DD !important;
    }
    
    /* Slider */
    .stSlider > div > div {
        color: #AFA9EC !important;
    }
    
    /* Tabs */
    .stTabs [data-testid="stTab"] {
        background: #13111c !important;
        color: #6b6783 !important;
        border-bottom: 2px solid transparent !important;
    }
    
    .stTabs [data-testid="stTab"][aria-selected="true"] {
        color: #AFA9EC !important;
        border-bottom: 2px solid #7F77DD !important;
    }
    
    /* Download button */
    [data-testid="stDownloadButton"] button {
        background: #1e1a2e !important;
        border: 0.5px solid #534AB7 !important;
        color: #AFA9EC !important;
    }
    
    /* Checkbox */
    .stCheckbox label {
        color: #e2d9f3 !important;
    }
    
    /* Caption text */
    .stCaption {
        color: #6b6783 !important;
    }
    
    /* Link buttons */
    [data-testid="stLinkButton"] a {
        background: #1e1a2e !important;
        border: 0.5px solid #534AB7 !important;
        color: #AFA9EC !important;
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        background: #1e1a2e !important;
        border: 0.5px solid #2d2b3d !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)


def handle_resume_upload():
    """
    Smart resume handler using session state.
    Upload once → works across all pages.
    Change Resume button to swap resumes.
    """
    import streamlit as st
    import tempfile
    import os

    st.sidebar.markdown(
        '<p style="color:#6b6783; font-size:10px; '
        'text-transform:uppercase; letter-spacing:1px; '
        'margin-top:16px; margin-bottom:8px;">'
        'YOUR RESUME</p>',
        unsafe_allow_html=True
    )

    # ─────────────────────────────────────
    # CHANGING RESUME MODE
    # User clicked Change Resume button
    # ─────────────────────────────────────
    if st.session_state.get("changing_resume", False):
        st.sidebar.info("Upload new resume:")

        uploaded_file = st.sidebar.file_uploader(
            "Upload Resume (PDF)",
            type=["pdf"],
            key="resume_uploader_change"
        )

        if st.sidebar.button(
            "Cancel",
            key="cancel_change_btn"
        ):
            st.session_state["changing_resume"] = False
            st.rerun()

        if uploaded_file is not None:
            file_bytes = uploaded_file.getvalue()
            st.session_state["resume_bytes"] = file_bytes
            st.session_state["resume_name"] = (
                uploaded_file.name)
            st.session_state["changing_resume"] = False

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".pdf"
            ) as tmp:
                tmp.write(file_bytes)
                st.session_state["resume_path"] = tmp.name

            st.sidebar.success(
                f"✅ {uploaded_file.name} loaded!")
            st.rerun()

        return st.session_state.get("resume_path")

    # ─────────────────────────────────────
    # CASE 1: Resume already in session
    # ─────────────────────────────────────
    if "resume_bytes" in st.session_state:
        resume_name = st.session_state.get(
            "resume_name", "resume.pdf")

        st.sidebar.success(f"✅ {resume_name}")

        if st.sidebar.button(
            "🔄 Change Resume",
            key="change_resume_btn"
        ):
            st.session_state["changing_resume"] = True
            st.rerun()

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as tmp:
            tmp.write(st.session_state["resume_bytes"])
            tmp_path = tmp.name

        st.session_state["resume_path"] = tmp_path
        return tmp_path

    # ─────────────────────────────────────
    # CASE 2: Local resume.pdf exists
    # Running on laptop - load automatically
    # ─────────────────────────────────────
    if os.path.exists("resume.pdf"):
        with open("resume.pdf", "rb") as f:
            file_bytes = f.read()

        st.session_state["resume_bytes"] = file_bytes
        st.session_state["resume_name"] = "resume.pdf"

        st.sidebar.success("✅ resume.pdf")

        if st.sidebar.button(
            "🔄 Change Resume",
            key="change_resume_btn"
        ):
            st.session_state["changing_resume"] = True
            st.rerun()

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        st.session_state["resume_path"] = tmp_path
        return tmp_path

    # ─────────────────────────────────────
    # CASE 3: No resume - show upload button
    # First time on deployed version
    # ─────────────────────────────────────
    st.sidebar.warning(
        "⚠️ Upload your resume!")

    uploaded_file = st.sidebar.file_uploader(
        "Upload Resume (PDF)",
        type=["pdf"],
        key="resume_uploader_first",
        help="Upload once - works for all agents!"
    )

    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        st.session_state["resume_bytes"] = file_bytes
        st.session_state["resume_name"] = (
            uploaded_file.name)

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        st.session_state["resume_path"] = tmp_path
        st.sidebar.success(
            f"✅ {uploaded_file.name} loaded!")
        st.rerun()

    return None