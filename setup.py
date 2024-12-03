import streamlit as st
def setup_style():
    # Inject CSS for background color
    st.markdown(
    """
    <style>
    .image {
        
    }
    """,
    unsafe_allow_html=True
    )
