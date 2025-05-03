import streamlit as st
import pandas as pd

# ========================
# 1. LOAD COMPANY DATA
# ========================
@st.cache_data
def load_company_data():
    try:
        df = pd.read_csv("com.csv")
        companies = []
        for _, row in df.iterrows():
            companies.append({
                "name": row['companies'],
                "cgpa": row['CGPA'],
                "languages": [lang.strip().lower() for lang in str(row['language']).split(',')],
                "internship": 1 if row['internship'] == 'Yes' else 0,
                "hss": row['HSS']
            })
        return companies
    except Exception as e:
        st.error(f"Error loading company data: {e}")
        return []

companies = load_company_data()

# ========================
# 2. ELIGIBILITY FUNCTION
# ========================
def check_eligibility(student):
    eligible_companies = []
    skill_suggestions = []

    student_languages = set(lang.strip().lower() for lang in student['language'].split(','))
    student_cgpa = student['CGPA']
    student_internships = student['Internships']
    student_hss = student.get("HSS", "Any").strip().lower()

    for company in companies:
        required_languages = set(company['languages'])
        missing_skills = required_languages - student_languages
        hss_ok = (company['hss'].lower() == 'any') or (company['hss'].lower() == student_hss)

        if (student_cgpa >= company['cgpa'] and
            student_internships >= company['internship'] and
            not missing_skills and
            hss_ok):
            eligible_companies.append(company['name'])
        elif missing_skills:
            skill_suggestions.append(f"Learn {', '.join(missing_skills)} for {company['name']}")

    placement_probability = min(100, 20 + (15 * len(eligible_companies)))

    return {
        "placement_eligibility": "Eligible" if eligible_companies else "Not Eligible",
        "placement_probability": f"{placement_probability}%",
        "eligible_companies": eligible_companies,
        "skill_enhancement_suggestions": skill_suggestions
    }

# ========================
# 3. STREAMLIT UI
# ========================
st.set_page_config(page_title="Placement Eligibility Checker", layout="centered")
st.title("🎯 Placement Eligibility Prediction System")

st.markdown("Enter your academic details below to check placement eligibility:")

cgpa = st.number_input("Enter CGPA (0 - 10)", min_value=0.0, max_value=10.0, step=0.1, value=7.0)
internship = st.selectbox("Internship", options=[("No internship", 0), ("Has internship", 1)])
languages = st.text_input("Known Programming Languages (comma-separated)", value="python")
hss = st.selectbox("HSS Background", options=["Any", "Science"])

if st.button("Check Eligibility"):
    student = {
        "CGPA": cgpa,
        "Internships": internship[1],
        "language": languages,
        "HSS": hss
    }
    result = check_eligibility(student)

    st.subheader("📋 Results:")
    st.markdown(f"**Eligibility Status:** {result['placement_eligibility']}")
    st.markdown(f"**Placement Probability:** {result['placement_probability']}")

    if result['eligible_companies']:
        st.markdown("### ✅ Eligible Companies:")
        for comp in result['eligible_companies']:
            st.write(f"- {comp}")
    else:
        st.info("No eligible companies found.")

    if result['skill_enhancement_suggestions']:
        st.markdown("### 📚 Skill Enhancement Suggestions:")
        for suggestion in result['skill_enhancement_suggestions']:
            st.write(f"- {suggestion}")
