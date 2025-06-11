import streamlit as st
import random
import hashlib
import numpy as np
import matplotlib.pyplot as plt
import io
from PIL import Image

# Configure page
st.set_page_config(
    page_title="Name to Flag Generator",
    page_icon="🏳️",
    layout="centered"
)

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
                colour_hex = hex(colour_val)[2:].zfill(2)  # Ensure 2 digits
                empty_string.append(colour_hex)
            brightened_colour = ''.join(empty_string)
            brightened_word.append(brightened_colour)
        brightened.append(brightened_word)
    return brightened

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
    if mode == "utf-8": 
        hexstring = utf8_to_hex(input_string)
    elif mode == "unicode":
        hexstring = unicode_to_hex(input_string)
    
    seed_string = ''.join(hexstring)
    return hexstring, seed_string

def create_flag_image(flattened_hexstring, name, mode, width=600, height=400):
    """Create flag image using matplotlib"""
    fig, ax = plt.subplots(figsize=(10, 6.67), facecolor='black')
    
    flag = np.zeros((height, width, 3))
    stripes = len(flattened_hexstring)
    stripe_height = height // stripes
    stripe_width = width // stripes
    
    colour_array = np.empty((stripes, 3))
    
    for i in range(stripes):
        hex_vals = flattened_hexstring[i]
        R_val = int(hex_vals[:2], 16)
        G_val = int(hex_vals[2:4], 16)
        B_val = int(hex_vals[4:6], 16)
        colour_array[i] = np.array([R_val, G_val, B_val]) / 255
        
        if mode == "horizontal":
            flag[i*stripe_height:(i+1)*stripe_height, :] = colour_array[i]
        elif mode == "vertical":
            flag[:, i*stripe_width:(i+1)*stripe_width, :] = colour_array[i]
    
    ax.axis('off')
    ax.imshow(flag)
    ax.set_title(f'Flag for: {name}', color='white', fontsize=16, pad=20)
    
    plt.tight_layout()
    return fig

def fig_to_bytes(fig):
    """Convert matplotlib figure to bytes for download"""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=300, bbox_inches='tight', 
                facecolor='black', edgecolor='black')
    buf.seek(0)
    return buf.getvalue()

# Streamlit UI
st.title("🏳️ Name to Flag Generator")
st.markdown("Transform any name into a unique flag using hexadecimal color conversion!")

# Information expander
with st.expander("ℹ️ How it works & Tips"):
    st.markdown("""
    **How it works:**
    1. Your input text is converted to hexadecimal values
    2. These hex values become colors for flag stripes
    3. Each name gets a deterministic, unique flag
    
    **Tips:**
    - The program is **case-sensitive** (Aaron ≠ aaron)
    - Names are separated by spaces
    - Use underscores to join words (Aaron_Burr vs Aaron Burr)
    - Works with any characters, numbers, and symbols
    - Different scripts may produce more colors
    - Try usernames, phrases, or any text!
    """)

# Input section
col1, col2 = st.columns([2, 1])

with col1:
    name_input = st.text_input("Enter a name or text:", placeholder="e.g., John Doe, 龍, User123")

with col2:
    encoding_mode = st.selectbox("Encoding method:", ["unicode", "utf-8"])

# Options section
st.subheader("Flag Options")
col3, col4, col5 = st.columns(3)

with col3:
    stripe_direction = st.selectbox("Stripe direction:", ["horizontal", "vertical"])

with col4:
    brighten_flag = st.checkbox("Brighten colors")

with col5:
    if brighten_flag:
        brighten_amount = st.slider("Brightness boost:", 0, 100, 30)
    else:
        brighten_amount = 0

# Generate flag
if st.button("🎨 Generate Flag", type="primary"):
    if not name_input:
        st.warning("Please enter a name or text first!")
    else:
        with st.spinner("Creating your unique flag..."):
        try:
            # Convert to hex
            hexstring, seed_string = string_to_hex(name_input, encoding_mode)
            
            # Generate filler
            filler_string = generate_random_output(seed_string, 5)
            
            # Process hex strings
            split_hexstring = split_into_chunks(hexstring, 6)
            finished_hexstring = fill_colour_blocks(split_hexstring, filler_string)
            
            # Apply brightening if requested
            if brighten_flag and brighten_amount > 0:
                finished_hexstring = brighten(finished_hexstring, brighten_amount)
            
            # Flatten and create image
            flattened_hexstring = flatten(finished_hexstring)
            
            # Create the flag
            fig = create_flag_image(flattened_hexstring, name_input, stripe_direction)
            
            # Display the flag
            st.pyplot(fig)
            
            # Download button
            img_bytes = fig_to_bytes(fig)
            st.download_button(
                label="📥 Download Flag (PNG)",
                data=img_bytes,
                file_name=f"{name_input.replace(' ', '_')}_flag.png",
                mime="image/png"
            )
            
            # Show color information
            with st.expander("🎨 Color Details"):
                st.write(f"**Number of stripes:** {len(flattened_hexstring)}")
                st.write("**Colors (hex codes):**")
                cols = st.columns(min(len(flattened_hexstring), 6))
                for i, color in enumerate(flattened_hexstring):
                    col_idx = i % 6
                    with cols[col_idx]:
                        st.markdown(
                            f'<div style="background-color: #{color}; height: 30px; margin: 2px; border-radius: 3px;"></div>',
                            unsafe_allow_html=True
                        )
                        st.caption(f"#{color}")
            
            plt.close(fig)  # Clean up
            
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.error("Please check your input and try again.")

# Footer
st.markdown("---")
col_footer1, col_footer2, col_footer3 = st.columns([1, 2, 1])
with col_footer2:
    st.markdown(
        """
        <div style="text-align: center;">
            <p>Made with ❤️ | <a href="https://your-donation-link.com" target="_blank">☕ Buy me a coffee</a></p>
        </div>
        """, 
        unsafe_allow_html=True
    )

# Sample examples
if not name_input:
    st.subheader("✨ Try these examples:")
    examples = ["Alice", "John_Doe", "龍", "User123", "Hello World"]
    cols = st.columns(len(examples))
    for i, example in enumerate(examples):
        with cols[i]:
            if st.button(f"`{example}`", key=f"example_{i}"):
                st.rerun()
