import streamlit as st
import yaml
import os

# ==============================================================================
#      Core Decoding Logic
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
            # Handle potential malformed entries in the YAML
            st.warning(f"Skipping a malformed field in YAML definition: Missing key {e}")

    return active_flags

# ==============================================================================
#      Streamlit User Interface
# ==============================================================================

# --- Page Configuration ---
st.set_page_config(
    page_title="Raceyard | SBG Decoder",
    layout="centered"
)

# --- Custom CSS for Raceyard CI ---
st.markdown("""
<style>
    /* Main App Styling */
    .stApp {
        background-color: #f0f0f0;
    }
    /* Button Styling */
    .stButton > button {
        background-color: #ff6600;
        color: #FFFFFF;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #e55b00;
        color: #FFFFFF;
    }
    /* Header Styling */
    h1 {
        color: #003366; /* Raceyard Dark Blue for main title */
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
st.title("SBG Status Decoder")
st.markdown("A tool for the Raceyard team to decode SBG Systems' status codes.")

if STATUS_CODES:
    # --- Input Section ---
    sorted_keys = sorted(STATUS_CODES.keys())
    
    col1, col2 = st.columns([2, 3])
    with col1:
        status_type = st.selectbox(
            "Select Status Type:",
            options=sorted_keys,
            label_visibility="collapsed"
        )
    with col2:
        decimal_code_input = st.text_input(
            "Enter Decimal Code:",
            placeholder="e.g., 273",
            label_visibility="collapsed"
        )

    st.caption(STATUS_CODES.get(status_type, {}).get("description", ""))

    st.write("") # Spacer

    if st.button("Decode Status", use_container_width=True):
        if not decimal_code_input:
            st.warning("Please enter a decimal code to decode.")
        else:
            try:
                decimal_code = int(decimal_code_input)
                
                # --- Decoding and Output ---
                st.subheader("Active Flags")
                results = decode_status(decimal_code, STATUS_CODES[status_type])
                
                if results:
                    # Use markdown for a clean, bulleted list
                    output_str = ""
                    for flag in results:
                        output_str += f"- {flag}\n"
                    st.markdown(output_str)
                else:
                    st.info("No active flags found for this code.")

            except (ValueError, TypeError):
                st.error("Invalid input. Please enter a valid integer.")
else:
    st.warning("Application cannot start because the status code definitions could not be loaded.")
