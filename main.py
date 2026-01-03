import streamlit as st
from openai import OpenAI
from datetime import datetime
import os
import requests
from PIL import Image
from io import BytesIO

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="GameMaster AI 🎮",
    page_icon="🎮",
    layout="wide"
)

# ------------------ API KEY CHECK ------------------
if "OPENAI_API_KEY" not in st.secrets:
    st.error("❌ OPENAI_API_KEY not found in Streamlit Secrets.")
    st.stop()

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ------------------ UI HEADER ------------------
st.title("🎮 GameMaster AI – The Ultimate Gaming Agent")
st.markdown(
    """
Your **AI Game Studio Partner**  
Concepts • Levels • NPC Logic • Strategy • Story • Avatars • Animations
"""
)

# ------------------ SIDEBAR ------------------
feature = st.sidebar.radio(
    "Select Agent Capability",
    [
        "Game Concept Generator",
        "Level & Environment Designer",
        "NPC Behavior Designer",
        "Game Strategy Assistant",
        "Dialogue & Story Scripting",
        "Avatar Creation for Games",
        "Game Animation Creation"
    ]
)

user_prompt = st.text_area(
    "Enter your idea / requirement:",
    height=160,
    placeholder="Example: A cyberpunk RPG boss character with emotional AI..."
)

generate = st.button("🚀 Generate Agent Output")

# ------------------ PROMPT ENGINE ------------------
def build_prompt(feature, user_input):
    base = "You are GameMaster AI, an expert game designer and game AI architect.\n\n"

    prompts = {
        "Game Concept Generator": """
Create a complete game concept including:
- Genre
- Core gameplay loop
- Story theme
- Unique mechanics
- Target audience
""",
        "Level & Environment Designer": """
Design a detailed game level including:
- Environment & terrain
- Player challenges
- Enemy placement
- Rewards & progression
""",
        "NPC Behavior Designer": """
Create NPC behavior logic including:
- NPC role
- Decision rules
- Emotional states
- Behavior tree (pseudo-code)
""",
        "Game Strategy Assistant": """
Analyze and improve gameplay strategy including:
- Balance fixes
- Player engagement
- Difficulty tuning
- Retention mechanics
""",
        "Dialogue & Story Scripting": """
Write immersive game narrative including:
- Characters
- Quests
- Branching dialogue
- Story arcs
""",
        "Avatar Creation for Games": """
Describe a game-ready avatar including:
- Visual appearance
- Personality traits
- Outfit & accessories
- Animation style
- Engine notes (Unity / Unreal)
""",
        "Game Animation Creation": """
Design game animation logic including:
- Animation types (idle, walk, combat, emote)
- Keyframe descriptions
- Timing & transitions
- Engine-ready logic
"""
    }

    return base + prompts[feature] + f"\n\nUser Input:\n{user_input}"

# ------------------ TEXT GENERATION ------------------
def generate_text(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a professional game development AI."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8
    )
    return response.choices[0].message.content

# ------------------ IMAGE GENERATION ------------------
def generate_image(prompt, prefix):
    img_prompt = f"High-quality game art, {prompt}, detailed, cinematic, concept art"
    img = client.images.generate(
        model="gpt-image-1",
        prompt=img_prompt,
        size="1024x1024"
    )
    img_url = img.data[0].url

    image_bytes = requests.get(img_url).content
    image = Image.open(BytesIO(image_bytes))

    os.makedirs("outputs", exist_ok=True)
    filename = f"outputs/{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    image.save(filename)

    return image, filename

# ------------------ FILE SAVE ------------------
def save_text(feature, content):
    os.makedirs("outputs", exist_ok=True)
    filename = f"outputs/{feature.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return filename

# ------------------ OUTPUT ------------------
if generate:
    if not user_prompt.strip():
        st.warning("⚠️ Please enter a prompt.")
    else:
        with st.spinner("GameMaster AI is working... 🎮"):

            final_prompt = build_prompt(feature, user_prompt)
            text_output = generate_text(final_prompt)
            text_file = save_text(feature, text_output)

            image = None
            image_file = None

            if feature in ["Avatar Creation for Games", "Game Animation Creation"]:
                image, image_file = generate_image(user_prompt, feature.replace(" ", "_"))

        st.subheader("🧠 Agent Output")
        st.markdown(text_output)

        # Text download
        with open(text_file, "rb") as f:
            st.download_button(
                "⬇️ Download Agent Text Output",
                f,
                file_name=os.path.basename(text_file),
                mime="text/plain"
            )

        # Image display + download
        if image:
            st.subheader("🎨 Generated Game Art")
            st.image(image, use_container_width=True)

            with open(image_file, "rb") as img:
                st.download_button(
                    "⬇️ Download Image",
                    img,
                    file_name=os.path.basename(image_file),
                    mime="image/png"
                )
