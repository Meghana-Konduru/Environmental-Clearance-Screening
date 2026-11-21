
import streamlit as st
import requests

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Environmental Clearance Screening",
    page_icon="🌱",
    layout="wide"
)

# --------------------------------------------------
# CUSTOM STYLING
# --------------------------------------------------

st.markdown("""
<style>
    .main {
        background-color: #f7faf8;
    }

    .main-title {
        font-size: 32px;
        font-weight: 700;
        color: #176b45;
    }

    .subtitle {
        color: #64748b;
        font-size: 15px;
    }

    div.stButton > button {
        background-color: #176b45;
        color: white;
        border-radius: 8px;
        border: none;
        height: 45px;
        font-weight: 600;
        width: 100%;
    }

    div.stButton > button:hover {
        background-color: #125536;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown(
    '<div class="main-title">🌱 Environmental Clearance '
    'Pre-Screening Service</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Preliminary environmental and '
    'regulatory screening for proposed projects.</div>',
    unsafe_allow_html=True
)

st.divider()

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("🌿 Navigation")

st.sidebar.info(
    "Use this application to submit project details "
    "and obtain preliminary environmental screening results."
)

if st.sidebar.button("Check Backend Connection"):
    try:
        response = requests.get(
            f"{API_URL}/health",
            timeout=5
        )

        if response.status_code == 200:
            st.sidebar.success("Backend connected!")
        else:
            st.sidebar.error("Backend returned an error.")

    except requests.exceptions.RequestException:
        st.sidebar.error("Backend is unavailable.")

st.sidebar.caption("Environmental Clearance Screening v1.0")

# --------------------------------------------------
# PROJECT INFORMATION FORM
# --------------------------------------------------

st.header("1. Project Information")

st.write(
    "Enter the basic information about the proposed project."
)

with st.form("project_screening_form"):

    col1, col2 = st.columns(2)

    with col1:
        project_type = st.selectbox(
            "Project Type *",
            [
                "Industrial project",
                "Infrastructure project",
                "Mining project",
                "Construction project",
                "Power project",
                "Cement Plant",
                "Other"
            ]
        )

        project_location = st.text_input(
            "Project Location *",
            placeholder="Example: Karnataka"
        )

    with col2:
        proposed_activity = st.text_input(
            "Proposed Activity *",
            placeholder="Example: Manufacturing facility"
        )

        project_capacity = st.text_input(
            "Project Capacity *",
            placeholder="Example: 100 tonnes/day"
        )

    st.divider()

    st.header("2. Environmental Information")

    st.write(
        "Additional details help improve regulatory retrieval "
        "and preliminary risk identification."
    )

    col3, col4 = st.columns(2)

    with col3:
        land_requirement = st.text_input(
            "Land Requirement",
            placeholder="Example: 10 acres"
        )

        water_usage = st.text_input(
            "Water Usage",
            placeholder="Example: 50,000 litres/day"
        )

        waste_generation = st.text_input(
            "Waste Generation",
            placeholder="Describe expected waste"
        )

    with col4:
        emissions = st.text_input(
            "Emissions",
            placeholder="Describe expected emissions"
        )

        forest_land = st.selectbox(
            "Does the project involve forest land?",
            ["Not specified", "No", "Yes"]
        )

        protected_area_proximity = st.text_input(
            "Proximity to Protected Areas",
            placeholder="Example: Within 10 km / Unknown"
        )

    st.divider()

    submit = st.form_submit_button(
        "🔍 Run Environmental Screening"
    )

    # --------------------------------------------------
    # SUBMIT TO FASTAPI
    # --------------------------------------------------

    if submit:

        if not all([
            project_location.strip(),
            proposed_activity.strip(),
            project_capacity.strip()
        ]):
            st.error(
                "Please fill in all required project details."
            )

        else:

            project_details = {
                "project_type": project_type,
                "project_location": project_location.strip(),
                "proposed_activity": proposed_activity.strip(),
                "project_capacity": project_capacity.strip()
            }

            optional_fields = {
                "land_requirement": land_requirement,
                "water_usage": water_usage,
                "waste_generation": waste_generation,
                "emissions": emissions,
                "forest_land": (
                    None if forest_land == "Not specified"
                    else forest_land
                ),
                "protected_area_proximity": (
                    protected_area_proximity
                )
            }

            for key, value in optional_fields.items():
                if value and value.strip():
                    project_details[key] = value.strip()

            try:
                with st.spinner(
                    "Running environmental screening..."
                ):

                    response = requests.post(
                        f"{API_URL}/api/screen",
                        json=project_details,
                        timeout=180
                    )

                if response.status_code == 200:

                    result = response.json()

                    if result.get("success"):

                        st.session_state["screening_result"] = (
                            result.get("data", {})
                        )

                        st.success(
                            "Screening completed successfully!"
                        )

                    else:
                        st.error(
                            result.get("error", "Screening failed.")
                        )

                else:
                    st.error(
                        f"Backend error: HTTP "
                        f"{response.status_code}"
                    )
                    st.code(response.text)

            except requests.exceptions.Timeout:
                st.error(
                    "Screening timed out. Please check the "
                    "backend and try again."
                )

            except requests.exceptions.ConnectionError:
                st.error(
                    "Cannot connect to FastAPI. "
                    "Make sure your backend is running."
                )

            except requests.exceptions.RequestException as e:
                st.error(f"Request failed: {e}")

# --------------------------------------------------
# DISPLAY SCREENING RESULTS
# --------------------------------------------------

if "screening_result" in st.session_state:

    result = st.session_state["screening_result"]

    st.divider()

    st.header("3. Screening Results")

    st.success("Your preliminary screening results are ready.")

    # Project details
    with st.expander("Project Details", expanded=True):
        st.json(result.get("project_details", {}))

    # Screening observations
    screening = result.get("screening_result", {})

    st.subheader("Preliminary Screening Observations")

    observations = screening.get(
        "preliminary_screening_observations", []
    )

    if observations:
        for observation in observations:
            st.info(str(observation))
    else:
        st.write("No observations available.")

    # Missing information
    st.subheader("Missing Information")

    missing = screening.get("missing_information", [])

    if missing:
        for item in missing:
            st.warning(str(item))
    else:
        st.success("No missing information was identified.")

    # Regulatory context
    st.subheader("Regulatory Context")

    regulatory = result.get("regulatory_context", [])

    if regulatory:
        st.json(regulatory)
    else:
        st.info("No regulatory passages returned.")

    # Risk assessment
    st.subheader("Environmental Risk Assessment")

    risk = result.get("risk_assessment", {})

    if risk:
        st.json(risk)
    else:
        st.info("No risk assessment available.")

    # Final report
    st.subheader("Final Screening Report")

    report = result.get("final_report", {})

    if report:
        if isinstance(report, dict):
            for key, value in report.items():
                st.markdown(f"**{key.replace('_', ' ').title()}**")
                if isinstance(value, (dict, list)):
                    st.json(value)
                else:
                    st.write(value)
        else:
            st.write(report)
    else:
        st.info("No final report available.")

    # Workflow status
    st.divider()

    st.subheader("Workflow Status")

    st.write(
        "Current Step:",
        result.get("current_step", "Unknown")
    )

    errors = result.get("errors", [])

    if errors:
        st.warning("Workflow reported errors.")
        st.json(errors)
    else:
        st.success("No workflow errors reported.")

    # Download raw results
    st.download_button(
        label="📥 Download Screening Results (JSON)",
        data=__import__("json").dumps(
            result,
            indent=4,
            ensure_ascii=False
        ),
        file_name="environmental_screening_results.json",
        mime="application/json"
    )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Environmental Clearance Pre-Screening Service | "
    "Preliminary assessment only. Not a statutory "
    "environmental clearance or regulatory approval."
)