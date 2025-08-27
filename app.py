import streamlit as st
from supabase import create_client, Client

# --- Supabase Configuration ---
SUPABASE_URL = "https://vzdbyhrvjmoxicbuoqqq.supabase.co"
SUPABASE_KEY = "sb_publishable_YfQLA5GZ1qPPqLcH1ACcTg_Wf-kHrcJ"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Streamlit App ---

st.set_page_config(layout="wide")

# --- Improved Header Section with Columns and Emojis ---
header_col1, header_col2 = st.columns([0.8, 0.2])
with header_col1:
    st.title("Integrated Surveillance Intelligence System")
    st.subheader("🕵️ Real-time Event Dashboard")
with header_col2:
    st.image("https://upload.wikimedia.org/wikipedia/commons/e/e0/Wp-surveillance-camera.png")

# --- Main App Logic ---

# Use a sidebar for search and filtering
with st.sidebar:
    st.header("🔎 Filters")
    search_query = st.text_input("Search for keywords:")

# --- Data Fetching Function (Optimized & Filtered) ---
@st.cache_data(show_spinner=False)
def fetch_events(query):
    """Fetches a limited number of events, filtered by the query."""
    try:
        # Start with the base query
        base_query = supabase.from_("events").select("*, cameras(name), people(name)")
        
        # Add the filter condition if a search query exists
        if query:
            base_query = base_query.or_(
                f"event_type.ilike.%{query}%, log_text.ilike.%{query}%, people.name.ilike.%{query}%"
            )

        # Apply ordering and limit
        response = base_query.order("event_time", desc=True).limit(10).execute()

        events_data = []
        if response.data:
            for item in response.data:
                events_data.append({
                    "id": item.get("id"),
                    "event_type": item.get("event_type"),
                    "camera_name": item.get("cameras", {}).get("name"),
                    "person_name": item.get("people", {}).get("name"),
                    "log_text": item.get("log_text"),
                    "photo_url": item.get("photo_url"),
                    "event_time": item.get("event_time"),
                })
        
        return events_data, None
    except Exception as e:
        return [], str(e)


# Fetch and display the events
events, error = fetch_events(search_query)

if error:
    st.error(f"Error fetching data: {error}")
elif not events:
    st.warning("No events found. Please populate your database.")
else:
    st.subheader("Recent Events")
    columns = st.columns(3)
    col_idx = 0
    
    for event in events:
        with columns[col_idx]:
            st.info(f"**{event.get('event_type').replace('_', ' ').title()}**")
            st.image(event["photo_url"], use_column_width=True)
            
            st.markdown(f"**Person:** {event.get('person_name', 'N/A')}")
            st.markdown(f"**Camera:** {event.get('camera_name', 'N/A')}")
            st.markdown(f"**Time:** {event.get('event_time')}")
            st.markdown(f"**Log:** *{event.get('log_text')}*")
            
        col_idx = (col_idx + 1) % 3
