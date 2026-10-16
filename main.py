import json
from pathlib import Path

import pandas as pd
import streamlit as st

from helper_functions.utility import check_password


st.set_page_config(layout="wide", page_title="Course Dashboard")

if not check_password():
    st.stop()


@st.cache_data
def load_courses():
    filepath = Path(__file__).parent / "data" / "courses-full.json"
    with filepath.open(encoding="utf-8") as file:
        return pd.DataFrame(json.load(file).values())


courses = load_courses()
courses["skills"] = courses["skills_covered"].apply(", ".join)

st.title("Course Catalogue Dashboard")
st.caption("Explore the courses available in the catalogue.")

with st.sidebar:
    st.header("Filters")
    categories = st.multiselect(
        "Category",
        options=sorted(courses["category"].unique()),
        default=sorted(courses["category"].unique()),
    )
    providers = st.multiselect(
        "Provider",
        options=sorted(courses["provider"].unique()),
        default=sorted(courses["provider"].unique()),
    )
    price_min = float(courses["price"].min())
    price_max = float(courses["price"].max())
    price_range = st.slider(
        "Price range",
        min_value=price_min,
        max_value=price_max,
        value=(price_min, price_max),
        step=25.0,
    )
    min_rating = st.slider("Minimum rating", min_value=1.0, max_value=5.0, value=1.0, step=0.1)

filtered_courses = courses[
    courses["category"].isin(categories)
    & courses["provider"].isin(providers)
    & courses["price"].between(*price_range)
    & (courses["rating"] >= min_rating)
]

total_courses = len(filtered_courses)
avg_rating = filtered_courses["rating"].mean()
avg_price = filtered_courses["price"].mean()

metric_columns = st.columns(4)
metric_columns[0].metric("Courses", total_courses)
metric_columns[1].metric("Categories", filtered_courses["category"].nunique())
metric_columns[2].metric("Average rating", f"{avg_rating:.1f}" if total_courses else "—")
metric_columns[3].metric("Average price", f"{avg_price:,.2f}" if total_courses else "—")

if filtered_courses.empty:
    st.info("No courses match the selected filters. Try adjusting them in the sidebar.")
else:
    category_counts = (
        filtered_courses.groupby("category", as_index=False)
        .size()
        .rename(columns={"size": "courses"})
    )
    category_prices = (
        filtered_courses.groupby("category", as_index=False)["price"]
        .mean()
        .rename(columns={"price": "average_price"})
    )
    course_ratings = filtered_courses[["name", "rating"]].sort_values("rating")

    chart_columns = st.columns(2)
    with chart_columns[0]:
        st.subheader("Courses by category")
        st.bar_chart(category_counts, x="category", y="courses")
    with chart_columns[1]:
        st.subheader("Average price by category")
        st.bar_chart(category_prices, x="category", y="average_price")

    st.subheader("Ratings by course")
    st.bar_chart(course_ratings, x="rating", y="name")

    st.subheader("Course details")
    st.dataframe(
        filtered_courses[
            ["name", "category", "provider", "duration", "rating", "price", "skills"]
        ].rename(
            columns={
                "name": "Course",
                "category": "Category",
                "provider": "Provider",
                "duration": "Duration",
                "rating": "Rating",
                "price": "Price",
                "skills": "Skills",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )
