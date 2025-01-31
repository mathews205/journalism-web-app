import streamlit as st
import requests
from datetime import datetime

# Apply Twitter-style theme
st.markdown(
    """
    <style>
        /* Background color (Twitter Blue) */
        .stApp {
            background-color: #15202B; /* Twitter Dark Mode Background */
            color: #FFFFFF; /* White text */
        }
 
        /* Change text color */
        h1, h2, h3, h4, h5, h6, p, label {
            color: #FFFFFF !important;
        }
 
        /* Style the input fields */
        .stTextInput>div>div>input, .stTextArea>div>textarea, .stTextInput input, .stTextArea textarea {
            background-color: #192734; /* Darker Twitter Blue */
            color: white;
            border-radius: 20px;
            padding: 10px;
        }
 
        /* Style the buttons */
        .stButton>button {
            background-color: #1DA1F2; /* Twitter Blue */
            color: white;
            border-radius: 25px;
            padding: 10px 20px;
            font-size: 16px;
            border: none;
        }
        
        /* Change button hover effect */
        .stButton>button:hover {
            background-color: #0D8DD8; /* Darker Twitter Blue */
            color: white;
        }
 
        /* Rounded profile pictures */
        .profile-pic {
            border-radius: 50%;
            width: 50px;
            height: 50px;
            object-fit: cover;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state variables
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_data" not in st.session_state:
    st.session_state.user_data = None

# FastAPI backend URL
FASTAPI_URL = "http://127.0.0.1:8000"

# Apply Custom CSS for Rounded Profile Image
st.markdown(
    """
    <style>
    .profile-pic {
        border-radius: 50%;
        width: 50px;
        height: 50px;
        object-fit: cover;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def calculate_maturity(timestamp):
    """Calculate profile maturity in days and assign a label."""
    try:
        if not timestamp:  # If timestamp is missing
            return "🟢 Noobie"

        registered_date = datetime.fromisoformat(timestamp)
        days_active = (datetime.utcnow() - registered_date).days

        if days_active == 0:
            return "👼 Noobie"
        elif days_active <= 1:
            return "👶 Beginner"
        elif days_active <= 30:
            return "🟡 Intermediate"
        elif days_active <= 90:
            return "🟠 Advanced"
        else:
            return "🔴 Expert"

    except Exception:
        return "Unknown"

# Function to handle login
def login(username, password):
    data = {"username": username, "password": password}
    response = requests.post(f"{FASTAPI_URL}/login", data=data)

    if response.status_code == 200:
        st.session_state.logged_in = True
        st.session_state.user_data = response.json()["user_data"]

        st.success("Login successful!")
        st.rerun()
    else:
        st.error("Invalid username or password.")

def get_user_image_stats(user_id):
    """Fetch user's real and fake image upload count."""
    try:
        response = requests.get(f"{FASTAPI_URL}/user/image-stats/{user_id}")
        if response.status_code == 200:
            return response.json()
        return {"real_images": 0, "fake_images": 0}  # Default if no data
    except Exception:
        return {"real_images": 0, "fake_images": 0}

# Function to handle registration
def register(username, email, password, profile_image):
    files = {"profile_image": profile_image}
    data = {"username": username, "email": email, "password": password}

    response = requests.post(f"{FASTAPI_URL}/register", data=data, files=files)

    if response.status_code == 200:
        st.success("Registration successful! You can now log in.")
    else:
        st.error(response.json()["detail"])

# Function to create a post
def create_post(content, image):
    try:
        user_id = st.session_state.user_data["id"]  # Get current user ID from session
    except KeyError:
        st.error("User not found, please log in again.")
        return

    files = {"image": image}
    data = {"user_id": user_id, "content": content}

    response = requests.post(f"{FASTAPI_URL}/posts", data=data, files=files)

    if response.status_code == 200:
        st.success("Post created successfully!")
        st.rerun()
    else:
        st.error(response.json()["detail"])

# Function to get posts
def get_posts():
    response = requests.get(f"{FASTAPI_URL}/posts")
    if response.status_code == 200:
        return response.json()
    return []

# Login/Register Page with Tabs
def login_page():
    st.markdown(
        """
        <div style="
            text-align: center;
            background-color: #1DA1F2;
            color: white;
            padding: 15px;
            border-radius: 10px;
            font-size: 32px;
            font-weight: bold;
            width: 200px;
            margin: auto;">
            TruePix
        </div>
        """,
        unsafe_allow_html=True
    )

    # Tabs for Login and Register
    tabs = st.tabs(["Login", "Register"])

    with tabs[0]:  # Login Tab
        st.subheader("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", key="login_button"):
            login(username, password)

    with tabs[1]:  # Register Tab
        st.subheader("Register")
        username = st.text_input("Username", key="register_username")
        email = st.text_input("Email", key="register_email")
        password = st.text_input("Password", type="password", key="register_password")
        profile_image = st.file_uploader("Upload Profile Image", type=["png", "jpg", "jpeg"], key="register_image")

        if st.button("Register", key="register_button"):
            if not username or not email or not password or not profile_image:
                st.warning("All fields are required!")
            else:
                register(username, email, password, profile_image)

# Dashboard Page
def dashboard():
    # Apply Global Styles (Improved Layout)
    st.markdown(
        """
        <style>
        /* General Styling */
        body {
            background-color: #121212;
            font-family: 'Arial', sans-serif;
        }
 
        /* Centered Title */
        .title-box {
            text-align: center;
            background: linear-gradient(135deg, #1DA1F2, #0D8DD8);
            color: white;
            padding: 12px;
            border-radius: 10px;
            font-size: 28px;
            font-weight: bold;
            width: 250px;
            margin: auto;
            box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.2);
        }
 
        /* Profile Section */
        .profile-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 15px;
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(5px);
            text-align: center;
            margin-bottom: 20px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
        }
 
        .profile-pic {
            border-radius: 50%;
            width: 90px;
            height: 90px;
            object-fit: cover;
            border: 3px solid white;
            margin-bottom: 10px;
        }
 
        .username {
            font-size: 18px;
            font-weight: bold;
            color: white;
        }
 
        /* Post Box */
        .post-container {
            background: #192555;
            padding: 15px;
            border-radius: 12px;
            margin-bottom: 20px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s ease-in-out;
        }
 
        .post-container:hover {
            transform: scale(1.02);
        }
 
        .post-content {
            color: white;
            font-size: 16px;
            padding: 5px 0;
        }
 
        .post-user {
            font-weight: bold;
            color: white;
            font-size: 18px;
        }
 
        /* Logout Button */
        .logout-btn {
            background-color: #1DA1F2;
            color: white;
            padding: 12px 15px;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            cursor: pointer;
            margin-top: 20px;
            width: 100%;
            transition: 0.3s;
        }
 
        .logout-btn:hover {
            background-color: #0D8BF0;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
 
    ### **Header: App Title**
    st.markdown('<div class="title-box">TruePix</div>', unsafe_allow_html=True)

    user = st.session_state.user_data

    with st.sidebar:
        st.markdown(
            f"""
            <div class="profile-container">
                <img src="{user['profile_image_url']}" class="profile-pic">
                <span class="username">{user['username']} 👋</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Proper Streamlit Logout Button
        if st.button("Logout", key="logout_button"):
            # Clear session state
            st.session_state.logged_in = False
            st.session_state.user_data = None

            # Redirect to Login Page
            st.rerun()

        # Redirect to Login Page

        st.subheader(f"Welcome, {user['username']}! 👋")

        # Calculate and display profile maturity
        profile_maturity = calculate_maturity(user.get("timestamp", ""))
        st.write(f"**Maturity Level:** {profile_maturity}")

        # Fetch and display real vs fake image count
        image_stats = get_user_image_stats(user["id"])
        st.write(f"📸 **Real Images Uploaded:** {image_stats['real_images']}")
        st.write(f"🤖 **Fake Images Uploaded:** {image_stats['fake_images']}")


    # Create Post Section
    st.subheader("Create a Post 📝")
    content = st.text_area("What's on your mind?", key="post_content")  # Unique key
    image = st.file_uploader("Upload an image for your post", type=["png", "jpg", "jpeg"], key="post_image")  # Unique key

    if st.button("Post", key="post_button"):
        if content and image:
            create_post(content, image)
        else:
            st.warning("Post content and image are required!")

    # Display Posts
    st.subheader("All Posts 📢")
    posts = get_posts()

    if not posts:
        st.info("No posts available.")
    else:
        for idx, post in enumerate(posts):  # Loop with index for unique keys
            col1, col2 = st.columns([1, 5])  # Layout for user profile image & post content

            # Column 1: Profile Image (Rounded)
            with col1:
                st.markdown(f'<img src="{post["user_profile_image_url"]}" class="profile-pic">', unsafe_allow_html=True)
            
            # Column 2: Post Content
            with col2:
                st.write(f"**{post['username']}** posted:")
                st.write(post["content"])
                
                # Show Post Image
                st.image(post["post_image_url"], use_container_width=True)

                # Display Post Status
                if post["status"]:
                    st.success(f"✔️ Real", icon="✅")
                else:
                    st.error(f"❌ Fake", icon="🚨")

            st.divider()

# Main Application
if st.session_state.logged_in:
    dashboard()
else:
    login_page()