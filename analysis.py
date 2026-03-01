# analysis.py
import pandas as pd
import zipfile
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
import plotly.express as px
from datetime import date

# ------------------ Load Dataset ------------------ #
zip_path = r"C:\Users\hp\Desktop\glassdoor_project\archive.zip"
csv_name_in_zip = "glassdoor_comany.csv"

useful_columns = [
    "Company Name",
    "Company rating",
    "Company reviews",
    "Company salaries",
    "Location",
    "Number of Employees",
    "Industry Type",
    "Company Description"
]

@st.cache_data
def load_data():
    with zipfile.ZipFile(zip_path) as z:
        with z.open(csv_name_in_zip) as f:
            df = pd.read_csv(
                f,
                encoding="latin1",
                usecols=useful_columns,
                nrows=600
            )
    return df.dropna()

df_cleaned = load_data()
df_cleaned["Company rating"] = pd.to_numeric(df_cleaned["Company rating"], errors='coerce')
df_cleaned["Company salaries"] = pd.to_numeric(df_cleaned["Company salaries"], errors='coerce')

# ------------------ Streamlit Config ------------------ #
st.set_page_config(page_title="Glassdoor Analysis", layout="wide")

# ------------------ User Auth ------------------ #
USERS = {"admin@example.com": "password123", "user@example.com": "testpass"}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "profile_completed" not in st.session_state:
    st.session_state.profile_completed = False
if "profile_data" not in st.session_state:
    st.session_state.profile_data = {}

# ------------------ LOGIN PAGE ------------------ #
if not st.session_state.logged_in:
    st.title("🔐 Login")
    email = st.text_input("📧 Email")
    password = st.text_input("🔑 Password", type="password")

    if st.button("Login"):
        if email in USERS and USERS[email] == password:
            st.session_state.logged_in = True
            st.success("✅ Login successful!")
            st.rerun()
        else:
            st.error("❌ Invalid email or password.")

# ------------------ PROFILE PAGE ------------------ #
elif st.session_state.logged_in and not st.session_state.profile_completed:
    st.title("👤 Complete Your Profile")

    institute = st.text_input("🏫 Institute Name")
    course = st.text_input("🎓 Course Name")
    job_type = st.selectbox("💼 Job Type", ["Data Analyst", "Software Engineer", "Web Developer", "Marketing Executive"])
    dob = st.date_input(
        "📅 Date of Birth",
        value=date(2000, 1, 1),
        min_value=date(1950, 1, 1),
        max_value=date(2007, 12, 31)
    )
    skills = st.text_area("🛠️ Skills (comma separated)")
    experience = st.number_input("📊 Years of Experience", min_value=0, max_value=50, step=1)

    if st.button("Save Profile"):
        if dob > date(2007, 12, 31):
            st.error("❌ You must be born on or before 2007 to access the dashboard.")
        else:
            # Save profile in session
            st.session_state.profile_data = {
                "Institute": institute,
                "Course": course,
                "Job Type": job_type,
                "DOB": dob,
                "Skills": skills,
                "Experience": experience
            }
            st.session_state.profile_completed = True
            st.success("✅ Profile saved successfully!")
            st.rerun()

# ------------------ DASHBOARD ------------------ #
else:
    # Display Visual Profile Card
    if st.session_state.profile_completed:
        profile = st.session_state.profile_data
        st.markdown(f"""
        <div style="border-radius:12px; padding:20px; background:#f0f4f8; box-shadow:0 2px 8px rgba(0,0,0,0.2); margin-bottom:20px;">
            <h3 style="color:#0CAA41;">👤 Profile Summary</h3>
            <p>🏫 <b>Institute:</b> {profile['Institute']}</p>
            <p>🎓 <b>Course:</b> {profile['Course']}</p>
            <p>💼 <b>Job Type:</b> {profile['Job Type']}</p>
            <p>📅 <b>DOB:</b> {profile['DOB']}</p>
            <p>🛠️ <b>Skills:</b> {profile['Skills']}</p>
            <p>📊 <b>Experience:</b> {profile['Experience']} years</p>
        </div>
        """, unsafe_allow_html=True)

        # ------------------ Recommended Companies ------------------ #
        st.subheader("🏢 Recommended Companies for You")

        # Filter companies by Job Type (basic example mapping)
        if profile['Job Type'] == "Data Analyst":
            rec_df = df_cleaned[df_cleaned["Industry Type"].str.contains("Analytics|IT|Data", case=False, na=False)]
        elif profile['Job Type'] == "Software Engineer":
            rec_df = df_cleaned[df_cleaned["Industry Type"].str.contains("Software|IT|Technology", case=False, na=False)]
        elif profile['Job Type'] == "Web Developer":
            rec_df = df_cleaned[df_cleaned["Industry Type"].str.contains("Web|IT|Technology", case=False, na=False)]
        else:
            rec_df = df_cleaned.head(10)

        top_primary = rec_df.sort_values(by="Company rating", ascending=False).head(3)
        top_secondary = rec_df.sort_values(by="Company rating", ascending=False).iloc[3:8]

        st.markdown("**Top Picks:**")
        for _, row in top_primary.iterrows():
            st.markdown(f"""
            <div style="border-radius:12px; padding:15px; margin:5px 0; background:#d1f2eb; box-shadow:0 1px 4px rgba(0,0,0,0.1)">
                <h4 style="color:#0CAA41;">{row['Company Name']}</h4>
                ⭐ <b>{row['Company rating']}</b> | {row['Industry Type']} <br>
                📍 {row['Location']}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("**Other Recommendations:**")
        for _, row in top_secondary.iterrows():
            st.markdown(f"""
            <div style="border-radius:12px; padding:12px; margin:5px 0; background:#f8f9fa; box-shadow:0 1px 3px rgba(0,0,0,0.05)">
                <h5 style="color:#3498db;">{row['Company Name']}</h5>
                ⭐ <b>{row['Company rating']}</b> | {row['Industry Type']} <br>
                📍 {row['Location']}
            </div>
            """, unsafe_allow_html=True)

    st.sidebar.title("📂 Navigation")
    page = st.sidebar.radio(
        "Go to",
        ["Home", "Dataset", "Top 10 Companies", "Charts", "Compare Companies"]
    )

    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.profile_completed = False
        st.session_state.profile_data = {}
        st.rerun()

    # ------------------ HOME PAGE ------------------ #
    if page == "Home":
        st.title("🏠 Welcome to Glassdoor Company Analysis")
        st.markdown(
            "Explore insights on **ratings, reviews, salaries, company size, industry type, and more.**"
        )
        col1, col2, col3 = st.columns(3)
        col1.metric("🏢 Total Companies", len(df_cleaned))
        col2.metric("⭐ Avg Rating", round(df_cleaned["Company rating"].mean(), 2))
        col3.metric("💼 Industries", df_cleaned["Industry Type"].nunique())

    # ------------------ DATASET PAGE ------------------ #
    elif page == "Dataset":
        st.title("📊 Dataset")
        industries = st.sidebar.multiselect(
            "Filter by Industry",
            options=df_cleaned["Industry Type"].unique(),
            default=list(df_cleaned["Industry Type"].unique())
        )
        locations = st.sidebar.multiselect(
            "Filter by Location",
            options=df_cleaned["Location"].unique(),
            default=list(df_cleaned["Location"].unique())
        )

        filtered_df = df_cleaned[
            (df_cleaned["Industry Type"].isin(industries)) &
            (df_cleaned["Location"].isin(locations))
        ]

        st.subheader("Interactive Dataset")
        gb = GridOptionsBuilder.from_dataframe(filtered_df)
        gb.configure_pagination(paginationAutoPageSize=True)
        gb.configure_side_bar()
        gridOptions = gb.build()
        AgGrid(filtered_df, gridOptions=gridOptions, enable_enterprise_modules=True)

    # ------------------ TOP 10 COMPANIES ------------------ #
    elif page == "Top 10 Companies":
        st.title("⭐ Top 10 Companies by Rating")
        top_companies = df_cleaned.sort_values(by="Company rating", ascending=False).head(10)
        st.dataframe(top_companies[["Company Name", "Company rating", "Location", "Industry Type"]])

    # ------------------ CHARTS ------------------ #
    elif page == "Charts":
        st.title("📈 Visual Insights")
        top_companies = df_cleaned.sort_values(by="Company rating", ascending=False).head(10)
        fig1 = px.bar(top_companies, x="Company rating", y="Company Name", orientation="h",
                      color="Company rating", title="Top 10 Companies by Rating")
        st.plotly_chart(fig1, use_container_width=True)

    # ------------------ COMPARE ------------------ #
    elif page == "Compare Companies":
        st.title("🔍 Compare Companies")
        companies = st.multiselect("Select Companies to Compare", df_cleaned["Company Name"].unique())
        if companies:
            comp_df = df_cleaned[df_cleaned["Company Name"].isin(companies)]
            st.dataframe(comp_df[["Company Name", "Company rating", "Company reviews", "Company salaries", "Location", "Industry Type"]])
        else:
            st.info("Select companies from the dropdown to compare.")
