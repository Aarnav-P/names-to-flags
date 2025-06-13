import streamlit as st
import random
import hashlib
import numpy as np
import matplotlib.pyplot as plt
import io
from PIL import Image

# Configure page
st.set_page_config(
    page_title="Name to Flag Converter",
    page_icon="🏳️",
    layout="centered"
)

# %% Custom CSS for better styling and tooltips

st.markdown("""
<style>
  
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
    }
    
    .info-tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
        color: #1f77b4;
        margin-left: 5px;
    }
    
    .info-tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: #333;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 8px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        font-size: 12px;
        opacity: 0;
        transition: opacity 0.3s;
    }
    
    .info-tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    
    .option-container {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #1f77b4;
    }
    
    .color-preview {
        border: 2px solid #ddd;
        border-radius: 5px;
        margin: 2px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stats-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1.5rem 1rem;
    border-radius: 15px;
    color: white;
    text-align: center;
    margin: 0.5rem 0;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    min-height: 120px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    width: 100%;
    box-sizing: border-box;
    }
    
    .stats-card h3 {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0 0 0.5rem 0;
        color: white;
        line-height: 1;
    }
    
    .stats-card p {
        font-size: 1rem;
        margin: 0;
        color: rgba(255, 255, 255, 0.9);
        font-weight: 500;
    }
    
    /* Ensure consistent column spacing */
    .stats-container {
        display: flex;
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .stats-container > div {
        flex: 1;
    }
    
    /* Override Streamlit's default column styles for stats */
    div[data-testid="column"] .stats-card {
        margin-left: 0;
        margin-right: 0;
    }
    
    /* Make input fields dark themed */
    div[data-baseweb="input"] {
        background-color: #2d2d2d !important;
        border-radius: 10px !important;
    }
    
    input {
        background-color: #2d2d2d !important;
        color: #f8f8f8 !important;
    }
    
    textarea {
        background-color: #2d2d2d !important;
        color: #f8f8f8 !important;
    }
    
    .stTextInput > div > div > input {
        background-color: #2d2d2d !important;
        color: #f8f8f8 !important;
    }
    
    .stSelectbox > div > div {
        background-color: #2d2d2d !important;
        color: #f8f8f8 !important;
    }

    /* Global dark background for all inputs */
    div.stTextInput > div > div {
        background-color: #2d2d2d !important;
        border: 1px solid #444 !important;
        border-radius: 10px !important;
        box-shadow: none !important;
    }
    
    div.stSelectbox > div > div {
        background-color: #2d2d2d !important;
        border: 1px solid #444 !important;
        border-radius: 10px !important;
        box-shadow: none !important;
    }
    
    div[data-testid="stForm"] {
        background-color: transparent !important;
    }
    
    /* Remove global box shadows for a cleaner dark theme */
    input, select, textarea {
        box-shadow: none !important;
        border: none !important;
    }
    
    /* Optional: darken the whole app container */
    .css-18e3th9 {
        background-color: #121212 !important;
    }

    .footer-style {
    text-align: center;
    padding: 2.5rem;
    background: linear-gradient(90deg, var(#2d2d2d) 0%, var(#4a4a4a) 100%);
    border-radius: 20px;
    margin-top: 3rem;
    color: var(#f8f8f8);
    box-shadow: 0 8px 32px rgba(45, 45, 45, 0.3);
    border: 2px solid var(#1a1a1a);
}
</style>
""", unsafe_allow_html=True)

# %% Functions

def create_tooltip(text):
    """Create a tooltip icon with hover text"""
    return f"""
    <span class="info-tooltip">ℹ️
        <span class="tooltiptext">{text}</span>
    </span>
    """

def brighten(finished_hexstring, amount):
    """Brighten the colors by adding to RGB values"""
    brightened = []
    for word in finished_hexstring:
        brightened_word = []
        for colour_block in word:
            rgb_vals = [colour_block[2*i:2*i+2] for i in range(3)]
            empty_string = []
            for colour in rgb_vals:
                colour_val = int(colour, 16)
                colour_val += amount
                colour_val = min(255, colour_val)
                colour_hex = hex(colour_val)[2:].zfill(2)
                empty_string.append(colour_hex)
            brightened_colour = ''.join(empty_string)
            brightened_word.append(brightened_colour)
        brightened.append(brightened_word)
    return brightened

def darken(finished_hexstring, amount):
    """Darken the colors by subtracting from RGB values"""
    darkened = []
    for word in finished_hexstring:
        darkened_word = []
        for colour_block in word:
            rgb_vals = [colour_block[2*i:2*i+2] for i in range(3)]
            empty_string = []
            for colour in rgb_vals:
                colour_val = int(colour, 16)
                colour_val -= amount
                colour_val = max(0, colour_val)
                colour_hex = hex(colour_val)[2:].zfill(2)
                empty_string.append(colour_hex)
            darkened_colour = ''.join(empty_string)
            darkened_word.append(darkened_colour)
        darkened.append(darkened_word)
    return darkened

def adjust_saturation(finished_hexstring, factor):
    """Adjust color saturation - simplified version"""
    adjusted = []
    for word in finished_hexstring:
        adjusted_word = []
        for colour_block in word:
            # Simple saturation adjustment by interpolating with grayscale
            r = int(colour_block[:2], 16)
            g = int(colour_block[2:4], 16)
            b = int(colour_block[4:6], 16)
            
            # Calculate grayscale value
            gray = int(0.299 * r + 0.587 * g + 0.114 * b)
            
            # Interpolate between original and grayscale
            r = max(0, min(255, int(gray + factor * (r - gray))))
            g = max(0, min(255, int(gray + factor * (g - gray))))
            b = max(0, min(255, int(gray + factor * (b - gray))))
            
            # Convert back to hex
            hex_color = f"{r:02x}{g:02x}{b:02x}"
            adjusted_word.append(hex_color)
        adjusted.append(adjusted_word)
    return adjusted

def chunking(string, length):
    """Split string into chunks of specified length"""
    return [string[i:length+i] for i in range(0, len(string), length)]

def fill_colour_blocks(split_string, filler_string):
    """Fill incomplete color blocks with filler string"""
    finished_hexstring = []
    for name in split_string:
        finished_name = name.copy()
        if len(finished_name[-1]) < 6:
            joined = finished_name[-1] + filler_string
            finished_name[-1] = joined[:6]
        finished_hexstring.append(finished_name)
    return finished_hexstring

def flatten(xss):
    """Flatten nested list"""
    return [x for xs in xss for x in xs]

def generate_random_output(seed_string, length):
    """Generate deterministic random string from seed"""
    seed = int(hashlib.sha256(seed_string.encode('utf-8')).hexdigest(), 16)
    random.seed(seed)
    random_output = ''.join(random.choices('abcdef0123456789', k=length))
    return random_output

def split_into_chunks(string_list, length):
    """Split each string in list into chunks"""
    total_list = []
    for word in string_list:
        split_word = chunking(word, length)
        total_list.append(split_word)
    return total_list

def unicode_to_hex(input_string):
    """Convert string to hex using Unicode code points"""
    names = input_string.split()
    hex_representation = []
    
    for name in names:
        concatenated_name = name.replace('_', '')
        unicode_code_points = [ord(char) for char in concatenated_name]
        hex_name = [hex(code_point)[2:] for code_point in unicode_code_points]
        hex_name_joined = ''.join(hex_name)
        hex_representation.append(hex_name_joined)
    
    return hex_representation

def utf8_to_hex(input_string):
    """Convert string to hex using UTF-8 encoding"""
    names = input_string.split(" ")
    hex_representation = []
    
    for name in names:
        concatenated_name = name.replace('_', '')
        utf8_bytes = concatenated_name.encode('utf-8')
        hex_representation.append(utf8_bytes.hex())
    
    return hex_representation

def string_to_hex(input_string, mode):
    """Convert text to hexcode"""
    if mode == "UTF-8": 
        hexstring = utf8_to_hex(input_string)
    elif mode == "Unicode":
        hexstring = unicode_to_hex(input_string)
    
    seed_string = ''.join(hexstring)
    return hexstring, seed_string

def create_flag_image(flattened_hexstring, name, mode, pattern="stripes", width=600, height=400):
    """Create flag image using matplotlib with different patterns"""
    # Set matplotlib to use a non-interactive backend
    plt.ioff()
    
    fig, ax = plt.subplots(figsize=(10, 6.67))
    fig.patch.set_facecolor('black')  
    
    flag = np.zeros((height, width, 3))
    colors_count = len(flattened_hexstring)
    
    colour_array = np.empty((colors_count, 3))
    
    # Convert hex to RGB
    for i in range(colors_count):
        hex_vals = flattened_hexstring[i]
        R_val = int(hex_vals[:2], 16)
        G_val = int(hex_vals[2:4], 16)
        B_val = int(hex_vals[4:6], 16)
        colour_array[i] = np.array([R_val, G_val, B_val]) / 255
    
    if pattern == "stripes":
        stripe_height = height // colors_count
        stripe_width = width // colors_count
        
        for i in range(colors_count):
            if mode == "Horizontal":
                flag[i*stripe_height:(i+1)*stripe_height, :] = colour_array[i]
            elif mode == "Vertical":
                flag[:, i*stripe_width:(i+1)*stripe_width, :] = colour_array[i]
    
    elif pattern == "checkerboard":
        block_size = min(width // 8, height // 8)
        for y in range(0, height, block_size):
            for x in range(0, width, block_size):
                color_idx = ((x // block_size) + (y // block_size)) % colors_count
                flag[y:min(y+block_size, height), x:min(x+block_size, width)] = colour_array[color_idx]
    
    elif pattern == "diagonal":
        for y in range(height):
            for x in range(width):
                stripe_idx = int((x + y) / (width + height) * colors_count) % colors_count
                flag[y, x] = colour_array[stripe_idx]
    
    ax.axis('off')
    ax.imshow(flag)
    ax.set_title(f'Flag for: {name}', color='white', fontsize=16, pad=20)  
    
    plt.tight_layout()
    return fig

def fig_to_bytes(fig):
    """Convert matplotlib figure to bytes for download"""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='white')  # Changed to white
    buf.seek(0)
    return buf.getvalue()

def get_color_stats(flattened_hexstring):
    """Get statistics about the colors"""
    colors_count = len(flattened_hexstring)
    
    # Calculate average brightness
    total_brightness = 0
    for color in flattened_hexstring:
        r, g, b = int(color[:2], 16), int(color[2:4], 16), int(color[4:6], 16)
        brightness = (r + g + b) / 3
        total_brightness += brightness
    
    avg_brightness = total_brightness / colors_count if colors_count > 0 else 0
    
    return {
        "count": colors_count,
        "avg_brightness": avg_brightness,
        "brightness_category": "Dark" if avg_brightness < 85 else "Medium" if avg_brightness < 170 else "Bright"
    }

# %% MAIN APP

st.markdown("""
<div class="main-header">
    <h1>Name to Flag Converter</h1>
    <p>Transform any name into a unique flag!</p>
</div>
""", unsafe_allow_html=True)

# Information expander with enhanced content
with st.expander("How it works & Tips"):
    st.markdown("""
    **How it works:**
    1. Your input text is converted to hexadecimal values using Unicode or UTF-8 encoding
    2. These hex values become RGB color codes for flag elements
    3. Each input gets a deterministic, unique flag design - your flag is always the same!
    4. Additional visual effects and patterns can be applied, but you will lose uniquity.
    
    **Pro Tips:**
    - **Case-sensitive**: "Merlin" ≠ "merlin" (different flags!)
    - **Join words**: Use underscores to preserve uniqueness (Eugene_Wigner vs Eugene Wigner)
    - **Non-english script**: Different writing systems will likely create more colors
    - **Try**: usernames, phrases, dates, or any text
    - **Reproducible**: Same input always creates the same flag
    """)

# Input section with better layout
with st.container():
    st.markdown('<h3 style="margin-bottom: 0.5rem; color: white;">Enter your name</h3>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    name_input = st.text_input(
        "Enter a name or text:", 
        placeholder="e.g., Robert_Fripp, ଆର୍ନଭ୍_ପଣ୍ଡା, King_of_Pirates"
    )

with col2:
    tooltip_html = create_tooltip("Unicode: Uses character code points. UTF-8: Uses byte encoding. UTF-8 will typically produce more and more similar colours for non-english scripts.")
    st.markdown(f'<div style="margin-top: 0rem"><strong>Encoding standard</strong> {tooltip_html}</div>', unsafe_allow_html=True)
    encoding_mode = st.selectbox("", ["Unicode", "UTF-8"], label_visibility="collapsed")
    
st.markdown('</div>', unsafe_allow_html=True)

# Enhanced options section
with st.container(): 
    st.markdown('<h3 style="margin-bottom: 0; color: white;">Flag Customization</h3>', unsafe_allow_html=True)
    st.markdown('<p style="font-style: italic; font-size: 0.9rem; margin-bottom: 1rem; color: white;">More flag designs coming soon!</p>', unsafe_allow_html=True)

# First row of options
col3, col4, col5 = st.columns(3)

with col3:
    st.markdown("**Stripe direction:**" + create_tooltip("Horizontal: Colors stack vertically. Vertical: Colors stack horizontally."), unsafe_allow_html=True)
    stripe_direction = st.selectbox("", ["Horizontal", "Vertical"], label_visibility="collapsed")

with col4:
    st.markdown("**Flag pattern:**" + create_tooltip("Stripes: Traditional flag stripes. Checkerboard: Chess-like pattern. Diagonal: Angled color bands."), unsafe_allow_html=True)
    flag_pattern = st.selectbox("", ["Stripes", "Checkerboard", "Diagonal"], label_visibility="collapsed")

with col5:
    st.markdown("**Colour adjustments:**" + create_tooltip("Choose how to modify the generated colors for better visibility."), unsafe_allow_html=True)
    color_adjustment = st.selectbox("", ["None", "Brighten", "Darken", "Boost Saturation"], label_visibility="collapsed")

# Second row for adjustment amount
if color_adjustment != "None":
    col6, col7, col8 = st.columns([1, 2, 1])
    with col7:
        if color_adjustment == "Brighten":
            st.markdown("**Brightness boost:**" + create_tooltip("Increases RGB values to make colors lighter and more vibrant."), unsafe_allow_html=True)
            adjustment_amount = st.slider("", 0, 100, 30, label_visibility="collapsed")
        elif color_adjustment == "Darken":
            st.markdown("**Darkness amount:**" + create_tooltip("Decreases RGB values to make colors deeper and more subdued."), unsafe_allow_html=True)
            adjustment_amount = st.slider("", 0, 100, 30, label_visibility="collapsed")
        elif color_adjustment == "Boost Saturation":
            st.markdown("**Saturation multiplier:**" + create_tooltip("Multiplies color saturation to make colors more vivid and intense."), unsafe_allow_html=True)
            adjustment_amount = st.slider("", 0.5, 3.0, 1.5, 0.1, label_visibility="collapsed")
else:
    adjustment_amount = 0

st.markdown('</div>', unsafe_allow_html=True)

# Enhanced generation button
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    generate_button = st.button("🎨 Generate Your Unique Flag", type="primary", use_container_width=True)
with st.container():
    st.markdown('<p style="font-style: italic; margin-bottom: 0.5rem; color: white;"><small>Disclaimer: Your flag will be uniquely (but might not be conventionally) beautiful! Use "Colour Adjustments"" to make tweaks (though you will lose the uniqueness).</small></p>', unsafe_allow_html=True)
    
# Generate flag
if generate_button:
    if not name_input:
        st.warning("⚠️ Please enter a name or text first!")
    else:
        with st.spinner("🎨 Creating your unique flag..."):
            try:
                # Convert to hex
                hexstring, seed_string = string_to_hex(name_input, encoding_mode)
                
                # Generate filler
                filler_string = generate_random_output(seed_string, 5)
                
                # Process hex strings
                split_hexstring = split_into_chunks(hexstring, 6)
                finished_hexstring = fill_colour_blocks(split_hexstring, filler_string)
                
                # Apply color adjustments
                if color_adjustment == "Brighten" and adjustment_amount > 0:
                    finished_hexstring = brighten(finished_hexstring, adjustment_amount)
                elif color_adjustment == "Darken" and adjustment_amount > 0:
                    finished_hexstring = darken(finished_hexstring, adjustment_amount)
                elif color_adjustment == "Boost Saturation" and adjustment_amount != 1.0:
                    finished_hexstring = adjust_saturation(finished_hexstring, adjustment_amount)
                
                # Flatten and create image
                flattened_hexstring = flatten(finished_hexstring)
                
                # Get color statistics
                color_stats = get_color_stats(flattened_hexstring)
                
                # Create the flag
                fig = create_flag_image(flattened_hexstring, name_input, stripe_direction, flag_pattern.lower())
                
                # Display the flag
                st.pyplot(fig)
                
                # Enhanced download and stats section
                col_dl1, col_dl2, col_dl3 = st.columns([1, 2, 1])
                with col_dl2:
                    img_bytes = fig_to_bytes(fig)
                    st.download_button(
                        label="📥 Download Flag (High Quality PNG)",
                        data=img_bytes,
                        file_name=f"{name_input.replace(' ', '_').replace('/', '_')}_flag.png",
                        mime="image/png",
                        use_container_width=True
                    )
                
                # Stats cards
                st.subheader("📊 Flag Statistics")
                stat_col1, stat_col2, stat_col3 = st.columns(3, gap="medium")
                    
                with stat_col1:
                    st.markdown(f"""
                    <div class="stats-card">
                        <div style="font-size: 2.5rem; font-weight: bold; color: #d4d4d4; text-align: center; margin-bottom: 0.5rem;">{color_stats['count']}</div>
                        <div style="font-size: 1rem; color: rgba(255, 255, 255, 0.9); text-align: center;">Color Stripes</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with stat_col2:
                    st.markdown(f"""
                    <div class="stats-card">
                        <div style="font-size: 2.5rem; font-weight: bold; color: white; text-align: center; margin-bottom: 0.5rem;">{color_stats['brightness_category']}</div>
                        <div style="font-size: 1rem; color: rgba(255, 255, 255, 0.9); text-align: center;">Overall Tone</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with stat_col3:
                    st.markdown(f"""
                    <div class="stats-card">
                        <div style="font-size: 2.5rem; font-weight: bold; color: white; text-align: center; margin-bottom: 0.5rem;">{encoding_mode}</div>
                        <div style="font-size: 1rem; color: rgba(255, 255, 255, 0.9); text-align: center;">Encoding Used</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Enhanced color information
                with st.expander("🔍 Flag Analysis"):
                    st.write(f"**Generated from:** {len(hexstring)} word(s)")
                    st.write(f"**Total colors:** {len(flattened_hexstring)} stripes")
                    st.write(f"**Average brightness:** {color_stats['avg_brightness']:.1f}/255")
                    st.write(f"**Pattern:** {flag_pattern.title()} with {stripe_direction} orientation")
                    
                    st.write("**Color palette:**")
                    
                    # Display colors in a nicer grid
                    colors_per_row = 8
                    for i in range(0, len(flattened_hexstring), colors_per_row):
                        cols = st.columns(colors_per_row)
                        for j, color in enumerate(flattened_hexstring[i:i+colors_per_row]):
                            with cols[j]:
                                st.markdown(
                                    f'<div class="color-preview" style="background-color: #{color}; height: 40px; margin: 2px; border-radius: 5px;"></div>',
                                    unsafe_allow_html=True
                                )
                                st.caption(f"#{color}")
                
                plt.close(fig)  # Clean up
            
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
                st.error("Please check your input and try again.")

# Sample examples with better presentation
if not name_input:
    st.subheader("Try these examples:")
    st.markdown("Click any example to see how different inputs create unique flags:")
    
    examples = [
        "Nico",
        "Leonhard_Euler",  
        "織田 信長",
        "User123", 
        "⛰️😸☕"
    ]
    
    cols = st.columns(2)
    for i, example in enumerate(examples):
        with cols[i % 2]:
            if st.button(f"**{example}**", key=f"example_{i}", use_container_width=True):
                st.experimental_set_query_params(example=example)
                st.rerun()

# Enhanced footer
st.markdown("---")
st.markdown("""
<div class="footer-style">
    <h4>🎨 About This Tool</h4>
    <p>Every name is unique. This website converts your lexical fingerprint into a flag to show off.</p>
    <p>Made using <a href='https://streamlit.io/' Streamlit </a> • Your flag is 100% free :) </p>
    <p>Designed and created by Aarnav Panda, please send feedback and ideas to aarnavpanda11@gmail.com
    <p><small>Tip: Bookmark this URL to quickly generate a flag for any situation!</small></p>
</div>
""", unsafe_allow_html=True)
