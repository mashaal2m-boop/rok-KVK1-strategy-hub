import streamlit as st
from google import genai # THIS IS THE NEW IMPORT
from data import commander_db, pairing_db, scenario_db


# --- PAGE SETUP ---
st.set_page_config(page_title="RoK KvK 1 Meta Guide", layout="wide")

st.title("🛡️ Rise of Kingdoms: KvK 1 Strategy Hub")
st.write("The ultimate database for Season 1 Commanders and Pairings.")

# --- NAVIGATION ---
mode = st.sidebar.radio("Navigation", ["Commander Profiles", "Synergy Matrix", "Tactical Scenarios", "AI Battle Advisor"])

# ==========================================
# MODE 1: COMMANDER PROFILES
# ==========================================
if mode == "Commander Profiles":
    st.header("🔎 Commander Database")
    
    # Get a list of all names for the dropdown
    all_names = [c['name'] for c in commander_db]
    selected_name = st.selectbox("Select a Commander:", all_names)
    
    # Find the specific commander's data
    target = next((c for c in commander_db if c['name'] == selected_name), None)
    
    if target:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(f"{target['name']} ({target['rarity']})")
            st.info(f"**Role:** {target['role']}")
            st.write(f"**How to get:** {target['acquisition']}")
            st.write(f"**Summary:** {target['summary']}")
        
        with col2:
            st.success("**✅ Pros:**")
            for pro in target['pros']:
                st.write(f"- {pro}")
                
            st.error("**❌ Cons:**")
            for con in target['cons']:
                st.write(f"- {con}")

# ==========================================
# MODE 2: SYNERGY MATRIX (PAIRINGS)
# ==========================================
elif mode == "Synergy Matrix":
    st.header("🤝 The Meta Pairings")
    
    # Filter by a specific commander
    filter_name = st.selectbox("Search pairs for:", ["All"] + [c['name'] for c in commander_db])
    
    if filter_name == "All":
        results = pairing_db
    else:
        results = [p for p in pairing_db if p['primary'] == filter_name or p['secondary'] == filter_name]
    
    if results:
        for pair in results:
            with st.expander(f"{pair['primary']} + {pair['secondary']} ({pair['rating']})"):
                st.write(f"**March Type:** {pair['type']}")
                st.write(f"**Best Used For:** {', '.join(pair['tags'])}")
                st.write(f"**Synergy:** {pair['synergy']}")
    else:
        st.warning("No specific meta pairings found for this commander in the database.")

# ==========================================
# MODE 3: TACTICAL SCENARIOS
# ==========================================
elif mode == "Tactical Scenarios":
    st.header("🧠 What do you need to do?")
    
    situation = st.selectbox("Select a Scenario:", [s['scenario'] for s in scenario_db])
    
    solution = next((s for s in scenario_db if s['scenario'] == situation), None)
    
    if solution:
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="🏆 Absolute Best Option", value=solution['best_option'])
        with col2:
            st.metric(label="💰 Best F2P/Budget Option", value=solution['f2p_option'])
            
        st.info(f"**Strategy Breakdown:** {solution['description']}")
# ==========================================
# MODE 4: AI BATTLE ADVISOR (Powered by Modern Gemini)
# ==========================================
elif mode == "AI Battle Advisor":
    st.header("🤖 The War Room (AI Assistant)")
    
    # Initialize the new Gemini Client
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    
    # 1. Initialize the chat memory
    if "messages" not in st.session_state:
        # Give the AI its instructions and data
        system_instructions = f"""
        You are an expert Rise of Kingdoms strategist focusing strictly on KvK Season 1.
        Use this data to answer questions:
        Commanders: {commander_db}
        Pairs: {pairing_db}
        Scenarios: {scenario_db}
        Do not hallucinate commanders outside this data. Be direct and concise.
        """
        st.session_state.messages = [
            {"role": "model", "content": "Commander, the AI satellite is online. What is your tactical question?"}
        ]
        st.session_state.system_prompt = system_instructions

    # 2. Display previous chat messages
    for msg in st.session_state.messages:
        # Streamlit uses "assistant", Gemini uses "model"
        st_role = "assistant" if msg["role"] == "model" else "user"
        with st.chat_message(st_role):
            st.markdown(msg["content"])

    # 3. The Input Box
    if prompt := st.chat_input("Ask about KvK 1 strategies..."):
        
        # Add user's message to UI and memory
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # 4. Call the new Gemini API
        with st.chat_message("assistant"):
            try:
                # Combine instructions and prompt
                full_prompt = f"{st.session_state.system_prompt}\n\nUser Question: {prompt}"
                
                # The modern API call
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=full_prompt
                )
                ai_answer = response.text
                
                st.markdown(ai_answer)
                st.session_state.messages.append({"role": "model", "content": ai_answer})
                
            except Exception as e:

                st.error(f"API Error: {e}")
