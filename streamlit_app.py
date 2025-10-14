import streamlit as st
import yaml
import os

# ==============================================================================
#    Core Decoding Logic
# ==============================================================================

def decode_status(decimal_code, status_definition):
    """
    Decodes a decimal status code based on the definitions from the YAML file.
    Args:
        decimal_code (int): The integer value of the status code.
        status_definition (dict): The dictionary for a specific status type from the YAML.
    Returns:
        list: A list of strings, each describing an active flag.
    """
    active_flags = []
    fields_to_check = status_definition.get("fields", [])

    for field in fields_to_check:
        try:
            if field['type'] == 'mask':
                bit_value = 1 << field['bit']
                if (decimal_code & bit_value) == bit_value:
                    active_flags.append(field['name'])
            
            elif field['type'] == 'enum':
                enum_val = (decimal_code >> field['shift']) & field['mask']
                enum_name = field['values'].get(enum_val, f"Unknown Value ({enum_val})")
                active_flags.append(f"{field['name']}: {enum_name}")
        except KeyError as e:
            st.warning(f"Skipping a malformed field in YAML definition: Missing key {e}")

    return active_flags

# ==============================================================================
#    Streamlit User Interface
# ==============================================================================

# --- Page Configuration ---
st.set_page_config(
    page_title="Raceyard | SBG Decoder",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- Custom CSS for Raceyard CI ---
st.markdown("""
<style>
    /* Main App Styling & Background */
    .stApp {
        background-color: #0e1117; /* Dark background */
        color: #fafafa; /* Light text for the whole app */
    }

    /* Main content container for a "card" effect */
    .main .block-container {
        background-color: #1c1e24; /* Slightly lighter dark for the card */
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
        border: 1px solid #333;
    }
    
    /* Header & Logo Styling */
    h1 {
        text-align: center; /* Center the main title */
    }
    
    h1, h2 {
        color: #ffffff; /* White text for headers */
    }

    h2 {
        border-bottom: 2px solid #333; /* Darker border for subheaders */
        padding-bottom: 10px;
        margin-top: 2rem;
    }
    
    /* Caption text */
    .stCaption {
        color: #a0a0a0;
    }

    /* Button Styling (Orange stands out well) */
    .stButton > button {
        background-color: #ff6600;
        color: #FFFFFF;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: bold;
        font-size: 16px;
        transition: background-color 0.3s ease, transform 0.2s ease;
    }
    .stButton > button:hover {
        background-color: #e55b00;
        transform: scale(1.02);
    }

    /* Input Fields Styling (Selectbox & Text Input) */
    .stSelectbox div[data-baseweb="select"] > div, .stTextInput > div > div > input {
        background-color: #262730;
        color: #fafafa;
        border: 1px solid #555;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        transition: border-color 0.3s ease, box-shadow 0.3s ease;
    }
    .stTextInput > div > div > input:focus, 
    .stSelectbox div[data-baseweb="select"] > div:focus-within {
         border-color: #ff6600;
         box-shadow: 0 0 0 3px rgba(255, 102, 0, 0.2);
    }
    
    /* Result list styling */
    div[data-testid="stMarkdown"] ul {
        list-style-type: none;
        padding-left: 0;
    }
    div[data-testid="stMarkdown"] ul li {
        background-color: #262730;
        margin-bottom: 8px;
        padding: 12px 18px;
        border-radius: 5px;
        border-left: 5px solid #ff6600;
        font-size: 16px;
    }

</style>
""", unsafe_allow_html=True)

# --- Data Loading ---
@st.cache_data
def load_definitions():
    """Loads and caches the status code definitions from the YAML file."""
    filename = "status_codes.yaml"
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        st.error(f"FATAL ERROR: The configuration file '{filename}' was not found. "
                 "Please ensure it is in the same folder as the application.")
        return None
    except yaml.YAMLError as e:
        st.error(f"FATAL ERROR: The YAML file '{filename}' is malformed. Details: {e}")
        return None

STATUS_CODES = load_definitions()

# --- App Layout ---
if STATUS_CODES:
    st.title("SBG Status Decoder")
    st.markdown("<p style='text-align: center; color: #a0a0a0;'>A tool for the Raceyard team to decode SBG Systems' status codes.</p>", unsafe_allow_html=True)
    st.write("---")

    sorted_keys = sorted(STATUS_CODES.keys())
    
    col1, col2 = st.columns(2)
    with col1:
        status_type = st.selectbox(
            "**Select Status Type:**",
            options=sorted_keys,
        )
    with col2:
        decimal_code_input = st.text_input(
            "**Enter Decimal Code:**",
            placeholder="e.g., 273",
        )

    st.caption(STATUS_CODES.get(status_type, {}).get("description", ""))
    st.write("")

    if st.button("Decode", use_container_width=True):
        if not decimal_code_input:
            st.warning("Please enter a decimal code.")
        else:
            try:
                decimal_code = int(decimal_code_input)
                
                st.subheader("Decoding Results")
                results = decode_status(decimal_code, STATUS_CODES[status_type])
                
                if results:
                    output_str = "".join([f"- {flag}\n" for flag in results])
                    st.markdown(output_str)
                else:
                    st.success("✅ No active flags found for this code.")

            except (ValueError, TypeError):
                st.error("Invalid input. Please enter a valid integer.")
else:
    st.warning("Application cannot start because the status code definitions could not be loaded.")
