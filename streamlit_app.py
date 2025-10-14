import streamlit as st
import yaml
import os

# ==============================================================================
#    Core Decoding Logic (Unverändert)
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
                # Bitwise operation to extract the enum value
                enum_val = (decimal_code >> field['shift']) & field['mask']
                # Get the name from the values dictionary, with a fallback
                enum_name = field['values'].get(enum_val, f"Unbekannter Wert ({enum_val})")
                active_flags.append(f"{field['name']}: {enum_name}")
        except KeyError as e:
            # Handle potential malformed entries in the YAML
            st.warning(f"Ein fehlerhaftes Feld in der YAML-Definition wird übersprungen: Fehlender Schlüssel {e}")

    return active_flags

# ==============================================================================
#    Streamlit User Interface (Überarbeitet & Korrigiert)
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
        background-color: #f8f9fa; /* Lighter, cleaner background */
    }

    /* Main content container for a "card" effect */
    .main .block-container {
        background-color: #FFFFFF;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
    }
    
    /* Header & Logo Styling */
    h1 {
        color: #003366; /* Raceyard Dark Blue */
        text-align: center;
        font-weight: 700;
    }

    /* Subheader Styling (e.g., for "Ergebnisse") */
    h2 {
        color: #003366;
        border-bottom: 2px solid #f0f0f0;
        padding-bottom: 10px;
        margin-top: 2rem;
    }

    /* Button Styling */
    .stButton > button {
        background-color: #ff6600; /* Raceyard Orange */
        color: #FFFFFF;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: bold;
        font-size: 16px;
        transition: background-color 0.3s ease, transform 0.2s ease;
    }
    .stButton > button:hover {
        background-color: #e55b00; /* Darker orange on hover */
        transform: scale(1.02);
    }
    .stButton > button:active {
        background-color: #cc5200;
    }

    /* Input Fields Styling (Selectbox & Text Input) */
    .stSelectbox div[data-baseweb="select"] > div, .stTextInput > div > div > input {
        border: 1px solid #cccccc;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: border-color 0.3s ease, box-shadow 0.3s ease;
    }
    .stTextInput > div > div > input:focus, 
    .stSelectbox div[data-baseweb="select"] > div:focus-within {
         border-color: #ff6600; /* Highlight with accent color on focus */
         box-shadow: 0 0 0 3px rgba(255, 102, 0, 0.2);
    }
    
    /* Result list styling */
    div[data-testid="stMarkdown"] ul {
        list-style-type: none;
        padding-left: 0;
    }
    div[data-testid="stMarkdown"] ul li {
        background-color: #e9ecef;
        margin-bottom: 8px;
        padding: 12px 18px;
        border-radius: 5px;
        border-left: 5px solid #ff6600; /* Accent color bar */
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
        st.error(f"FATALER FEHLER: Die Konfigurationsdatei '{filename}' wurde nicht gefunden. "
                 "Bitte stellen Sie sicher, dass sie sich im selben Ordner wie die Anwendung befindet.")
        return None
    except yaml.YAMLError as e:
        st.error(f"FATALER FEHLER: Die YAML-Datei '{filename}' ist fehlerhaft. Details: {e}")
        return None

STATUS_CODES = load_definitions()

# --- App Layout ---
if STATUS_CODES:
    # --- Header ---
    # Centered Logo
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://www.raceyard.de/wp-content/uploads/2021/04/Raceyard_Logo_RGB-1.png", use_container_width=True) # <-- KORRIGIERT

    st.title("SBG Status Decoder")
    st.markdown("<p style='text-align: center;'>Ein Werkzeug für das Raceyard-Team zur Dekodierung von SBG Systems Status-Codes.</p>", unsafe_allow_html=True)

    st.write("---") # Visueller Trenner

    # --- Input Section ---
    sorted_keys = sorted(STATUS_CODES.keys())
    
    # Using columns for a cleaner layout
    col1, col2 = st.columns(2)
    with col1:
        status_type = st.selectbox(
            "**Status-Typ auswählen:**",
            options=sorted_keys,
        )
    with col2:
        decimal_code_input = st.text_input(
            "**Dezimalcode eingeben:**",
            placeholder="z.B. 273",
        )

    # Display description for selected status type
    st.caption(STATUS_CODES.get(status_type, {}).get("description", ""))

    st.write("") # Spacer

    if st.button("Dekodieren", use_container_width=True):
        if not decimal_code_input:
            st.warning("Bitte geben Sie einen Dezimalcode ein.")
        else:
            try:
                decimal_code = int(decimal_code_input)
                
                # --- Decoding and Output ---
                st.subheader("Ergebnisse der Dekodierung")
                results = decode_status(decimal_code, STATUS_CODES[status_type])
                
                if results:
                    # Use markdown for a clean, bulleted list
                    output_str = "".join([f"- {flag}\n" for flag in results])
                    st.markdown(output_str)
                else:
                    st.success("✅ Keine aktiven Flags für diesen Code gefunden.")

            except (ValueError, TypeError):
                st.error("Ungültige Eingabe. Bitte geben Sie eine gültige Ganzzahl ein.")
else:
    st.warning("Die Anwendung kann nicht gestartet werden, da die Definitionen der Status-Codes nicht geladen werden konnten.")
