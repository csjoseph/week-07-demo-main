import pandas as pd
import streamlit as st

from helper_functions.utility import check_password
from logics.customer_query_handler import process_user_message


st.set_page_config(layout="centered", page_title="Course Q&A")

if not check_password():
    st.stop()

st.title("Course Q&A")
st.caption("Ask a question about the courses in the catalogue.")

with st.form(key="course_question"):
    user_prompt = st.text_area("Enter your question", height=160)
    submitted = st.form_submit_button("Submit")

if submitted:
    if not user_prompt.strip():
        st.warning("Enter a question to get started.")
    else:
        with st.spinner("Finding relevant course information..."):
            try:
                response, course_details = process_user_message(user_prompt)
            except RuntimeError as error:
                st.error(f"Course Q&A could not generate a response: {error}")
                st.stop()

        st.subheader("Response")
        st.markdown(response)

        if course_details:
            st.subheader("Relevant courses")
            course_table = pd.DataFrame(course_details)[
                ["name", "category", "duration", "rating", "price", "skills_covered"]
            ].rename(
                columns={
                    "name": "Course",
                    "category": "Category",
                    "duration": "Duration",
                    "rating": "Rating",
                    "price": "Price",
                    "skills_covered": "Skills",
                }
            )
            st.dataframe(course_table, use_container_width=True, hide_index=True)
