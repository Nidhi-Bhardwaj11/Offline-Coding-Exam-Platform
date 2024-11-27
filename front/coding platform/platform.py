import streamlit as st
import requests as r
import pandas as pd
from code_editor import code_editor
from io import StringIO
import datetime
import extra_streamlit_components as stx

backend_url = 'http://192.168.1.7:5000'
login_page_url = "http://192.168.1.7:8000"

st.set_page_config(layout="wide")
cookie_manager = stx.CookieManager()
query_params = st.query_params
username = query_params.get('username', '')
stored_username = cookie_manager.get('username')

if not username or (stored_username and int(stored_username) != int(username)):
    login_url = login_page_url
    st.markdown(f"""
        <meta http-equiv="refresh" content="0; url={login_url}">
    """, unsafe_allow_html=True)
    st.stop()


expiration_date = datetime.datetime.now() + datetime.timedelta(minutes=15)
if not stored_username:
    cookie_manager.set('username', username, expires_at=expiration_date)


dark_mode_style = """
<style>
    .main {
        padding-top: 0rem;
        background-color: #2e2e2e !important;
        color: #fff !important;
        font-family: 'Courier New', Courier, monospace;
    }
    .block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
        padding-left: 5rem;
        padding-right: 5rem;
    }
    .stButton>button {
        background-color: #66e862 !important;
        color: #4d0e0e !important;
        border-radius: 10px;
        padding: 10px 20px;
        font-size: 16px;
    }
    h1 {
        color: #47fffc; 
        text-align: center; 
        margin-top: 20px; 
        font-size: 4em; 
        text-shadow: 2px 2px 4px rgba(115, 255, 0, 0.636);
    }
    .problem-title {
        color: #ffcc00;
        background-color: #444;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        margin-bottom: 20px;
        font-size: 2.5em;
        text-shadow: 2px 2px 5px rgb(0, 0, 0);
    }
    .example-title {
        color: cyan;
        text-shadow: 2px 2px 5px rgb(0, 0, 0);
    }
    .constraint-label {
        color: red;
        text-shadow: 2px 2px 5px rgb(0, 0, 0);
    }
    .problem-details {
        color: #e0e0e0;
        text-shadow: 2px 2px 5px rgb(0, 0, 0);
    }
    .sidebar-message {
        color: cyan; 
        text-align: center;
        font-size: 1.1em;
        margin-bottom: 20px;
    }
    .sidebar-username {
        color: lightpink;
        font-size: 1.3em; 
        text-shadow: 2px 2px 4px rgba(0, 255, 255, 0.6); 
    }
</style>
"""

backend_url_submit = f"{backend_url}/submit"
backend_url_questions = f"{backend_url}/questions"

def fetch_problems(username):
    try:
        response = r.post(backend_url_questions, json={"username": username})
        response.raise_for_status()
        
        x_user_name = response.headers.get('X-User-Name', 'User')

        return pd.read_csv(StringIO(response.content.decode('utf-8'))), x_user_name
    except Exception as e:
        st.error(f"Failed to fetch the problems: {e}")
        return None, None


if 'problems_df' not in st.session_state:
    st.session_state.problems_df, st.session_state.user_name = fetch_problems(username)

user_name = st.session_state.user_name

st.sidebar.markdown(f"<div class='sidebar-message'>Hi <span class='sidebar-username'>{user_name}</span>, happy coding!</div>", unsafe_allow_html=True)

def persist_code(problem_title, language, code):
    st.session_state.saved_codes[f'{language}{problem_title}'] = code

def get_persisted_code(problem_title):
    return st.session_state.saved_codes.get(f'{language}{problem_title}', "")

st.markdown("<h1>🐈 CodeKitty</h1>", unsafe_allow_html=True)

if st.session_state.problems_df is not None:
    df = st.session_state.problems_df
    problem_titles = df['title'].tolist()
    
    selected_problem = st.sidebar.selectbox(":orange[Select a problem]", problem_titles)
    language_mapping = {
        "Python": "python",
        "C": "c_cpp",
        "C++": "c_cpp",
        "Java": "java",
        "JavaScript": "javascript"
    }
    language = st.sidebar.selectbox(":blue[Select Language]", list(language_mapping.keys()))

    index = problem_titles.index(selected_problem)
    problem_details = {
        "description": df['description'].tolist()[index],
        "example_1": df['example 1'].tolist()[index],
        "example_2": df['example 2'].tolist()[index],
        "constraints": df['constraint'].tolist()[index]
    }

    if 'saved_codes' not in st.session_state:
        st.session_state.saved_codes = {}

    language_comments = {
        "Python": "# Write your Python code for {} here\n",
        "C": "// Write your C code for {} here\n",
        "C++": "// Write your C++ code for {} here\n",
        "Java": "// Write your Java code for {} here\n",
        "JavaScript": "// Write your JavaScript code for {} here\n"
    }

    persisted_code = get_persisted_code(f'{language}{selected_problem}')

    if f'{language}{selected_problem}' not in st.session_state.saved_codes:
        st.session_state.saved_codes[f'{language}{selected_problem}'] = persisted_code or language_comments[language].format(selected_problem)

    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown(f"""
            <div class="problem-title">{selected_problem}</div>
            <div class="problem-details">
                <p>{problem_details['description']}</p>
                <h4 class="example-title">Example 1:</h4>
                <p>{problem_details['example_1']}</p>
                <h4 class="example-title">Example 2:</h4>
                <p>{problem_details['example_2']}</p>
                <h4 class="constraint-label">Constraint</h4>
                <p>{problem_details['constraints']}</p>
            </div>
        """, unsafe_allow_html=True)
    st.markdown(dark_mode_style, unsafe_allow_html=True)
    with col2:
        editor_response = code_editor(
            code=st.session_state.saved_codes[f'{language}{selected_problem}'],
            lang=language_mapping[language],
            height='500px',
            theme='default',
            buttons=[
                {
                    "name": "Run",
                    "feather": "Play",
                    "primary": True,
                    "hasText": True,
                    "alwaysOn": True,
                    "showWithIcon": True,
                    "commands": ["submit"],
                    "style": {"bottom": "0.44rem", "right": "0.4rem", "background-color": "#4CAF50", "color": "white", "padding": "10px", "border": "none", "border-radius": "5px", "z-index": "1000"}
                },
                {
                    "name": "Save",
                    "feather": "Save",
                    "primary": False,
                    "hasText": True,
                    "alwaysOn": True,
                    "showWithIcon": True,
                    "commands": ["save", ["response", "saved"]],
                    "response": "saved",
                    "style": {"bottom": "0.44rem", "right": "5rem", "background-color": "#007bff", "color": "white", "padding": "10px", "border": "none", "border-radius": "5px", "z-index": "1000"}
                }
            ],
            focus=True
        )

        if editor_response.get("text", ""):
            st.session_state.saved_codes[f'{language}{selected_problem}'] = editor_response.get("text", "")
            persist_code(selected_problem, language, editor_response.get("text", ""))

        if editor_response.get("type") == 'submit':
            code_to_submit = editor_response.get("text", "")
            payload = {
                "code": code_to_submit,
                "language": language.lower(),
                "problem_title": selected_problem,
                "username": username,     
            }
            with st.spinner("Processing your code..."):
                try:
                    response = r.post(backend_url_submit, json=payload)

                    response.raise_for_status()
                    json_resp = response.json()

                    first_failed_test = next((result for result in json_resp['results'] if not result['pass']), None)

                    if first_failed_test:
                        input_data = first_failed_test['input']
                        expected_output = first_failed_test['expected']
                        actual_output = first_failed_test['output']

                        st.code(f"Input: {input_data}")
                        st.code(f"Expected Output: {expected_output}")
                        st.error(f"Your Output: {actual_output}")
                    else:
                        st.success("All test cases passed! 🎉")
                except Exception as e:
                    st.error(f"Error submitting the code: {e}")
else:
    st.error("please login to start test")


