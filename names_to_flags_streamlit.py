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

# test change

# Custom CSS for better styling and tooltips
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
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem;
    }
    
    .footer-style {
        text-align: center;
        padding: 2rem;
        background-color: #f8f9fa;
        border-radius: 10px;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

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
    """Adjust color saturation"""
    adjusted = []
    for word in finished_hexstring:
        adjusted_word = []
        for colour_block in word:
            rgb_vals = [int(colour_block[2*i:2*i+2], 16) for i in range(3)]
            # Convert to HSV for saturation adjustment
            r, g, b = [x/255.0 for x in rgb_vals]
            max_val = max(r, g, b)
            min_val = min(r, g, b)
            diff = max_val - min_val
            
            if diff == 0:
                adjusted_word.append(colour_block)
                continue
                
            # Adjust saturation
            if max_val != 0:
                saturation = diff / max_val
                saturation = min(1.0, saturation * factor)
                
                # Convert back to RGB
                if saturation == 0:
                    r = g = b = max_val
                else:
                    delta = max_val * saturation
                    min_val = max_val - delta
                    
                    if r == max_val:
                        r = max_val
                        if g == max(rgb_vals[1]/255.0, rgb_vals[2]/255.0):
                            g = min_val + (g - min_val) * saturation / (diff / max_val) if diff > 0 else min_val
                            b = min_val
                        else:
                            b = min_val + (b - min_val) * saturation / (diff / max_val) if diff > 0 else min_val
                            g = min_val
            
            # Convert back to hex
            rgb_vals = [int(x * 255) for x in [r, g, b]]
            hex_vals = [hex(max(0, min(255, val)))[2:].zfill(2) for val in rgb_vals]
            adjusted_word.append(''.join(hex_vals))
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
    fig, ax = plt.subplots(figsize=(10, 6.67), facecolor='black')
    
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
            if mode == "horizontal":
                flag[i*stripe_height:(i+1)*stripe_height, :] = colour_array[i]
            elif mode == "vertical":
                flag[:, i*stripe_width:(i+1)*stripe_width, :] = colour_array[i]
    
    elif pattern == "checkerboard":
        # Create checkerboard pattern
        block_size = min(width // 8, height // 8)
        for y in range(0, height, block_size):
            for x in range(0, width, block_size):
                color_idx = ((x // block_size) + (y // block_size)) % colors_count
                flag[y:min(y+block_size, height), x:min(x+block_size, width)] = colour_array[color_idx]
    
    elif pattern == "diagonal":
        # Create diagonal stripes
        for y in range(height):
            for x in range(width):
                stripe_idx = int((x + y) / (width + height) * colors_count) % colors_count
                flag[y, x] = colour_array[stripe_idx]
    
    ax.axis('off')
    ax.imshow(flag)
    ax.set_title(f'Flag of {name}', color='white', fontsize=16, pad=20)
    
    plt.tight_layout()
    return fig

def fig_to_bytes(fig):
    """Convert matplotlib figure to bytes for download"""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=300, bbox_inches='tight', 
                facecolor='black', edgecolor='black')
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

# Main App
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
    - **Join words**: Use underscores (Eugene_Wigner vs Eugene Wigner)
    - **Non-english script**: Different writing systems will likely create more colors
    - **Try**: usernames, phrases, dates, or any text
    - **Reproducible**: Same input always creates the same flag
    """)

# Input section with better layout
st.markdown('<div class="option-container">', unsafe_allow_html=True)
st.subheader("Enter your name")

col1, col2 = st.columns([3, 1])

with col1:
    name_input = st.text_input(
        "Enter a name or text:", 
        placeholder="e.g., Robert_Fripp, ଆର୍ନଭ୍_ପଣ୍ଡା, King_of_Pirates"
    )

with col2:
    st.markdown("**Encoding method:**" + create_tooltip("Unicode: Each character becomes a hex value based on its Unicode code point. UTF-8: Characters are encoded as bytes then converted to hex."), unsafe_allow_html=True)
    encoding_mode = st.selectbox("", ["Unicode", "UTF-8"], label_visibility="collapsed")

st.markdown('</div>', unsafe_allow_html=True)

# Enhanced options section
st.markdown('<div class="option-container">', unsafe_allow_html=True)
st.subheader("Flag Customization")
st.markdown("__More flag designs coming soon!__")
# First row of options
col3, col4, col5 = st.columns(3)

with col3:
    st.markdown("**Stripe direction:**" + create_tooltip("Horizontal: Colors stack vertically. Vertical: Colors stack horizontally."), unsafe_allow_html=True)
    stripe_direction = st.selectbox("", ["horizontal", "vertical"], label_visibility="collapsed")

with col4:
    st.markdown("**Flag pattern:**" + create_tooltip("Stripes: Traditional flag stripes. Checkerboard: Chess-like pattern. Diagonal: Angled color bands."), unsafe_allow_html=True)
    flag_pattern = st.selectbox("", ["stripes", "checkerboard", "diagonal"], label_visibility="collapsed")

with col5:
    st.markdown("**Color adjustments:**" + create_tooltip("Choose how to modify the generated colors for better visibility."), unsafe_allow_html=True)
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
                fig = create_flag_image(flattened_hexstring, name_input, stripe_direction, flag_pattern)
                
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
                st.subheader("Flag Statistics")
                stat_col1, stat_col2, stat_col3 = st.columns(3)
                
                with stat_col1:
                    st.markdown(f"""
                    <div class="stats-card">
                        <h3>{color_stats['count']}</h3>
                        <p>Color Stripes</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with stat_col2:
                    st.markdown(f"""
                    <div class="stats-card">
                        <h3>{color_stats['brightness_category']}</h3>
                        <p>Overall Tone</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with stat_col3:
                    st.markdown(f"""
                    <div class="stats-card">
                        <h3>{encoding_mode}</h3>
                        <p>Encoding Used</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Enhanced color information
                with st.expander("Flag Analysis"):
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
    st.subheader("✨ Try these examples:")
    st.markdown("Click any example to see how different inputs create unique flags:")
    
    examples = [
        ("Alice", "Simple name"),
        ("John_Doe", "Name with underscore"), 
        ("龍", "Chinese character"),
        ("User123", "Username with numbers"),
        ("Hello_World", "Programming classic"),
        ("🚀🌟", "Emojis work too!")
    ]
    
    cols = st.columns(3)
    for i, (example, description) in enumerate(examples):
        with cols[i % 3]:
            if st.button(f"**{example}**\n{description}", key=f"example_{i}", use_container_width=True):
                st.experimental_set_query_params(example=example)
                st.rerun()

# Enhanced footer
st.markdown("---")
st.markdown("""
<div class="footer-style">
    <h4>🎨 About This Tool</h4>
    <p>Every name is unique. This website converts your lexical fingerprint into a flag to show off.</p>
    <p>Made using Streamlit • <a href="#" target="_blank">☕ Donate if you enjoy your flag :) </a></p>
    <p><small>Tip: Bookmark your favourite flags by saving the URL!</small></p>
</div>
""", unsafe_allow_html=True)
