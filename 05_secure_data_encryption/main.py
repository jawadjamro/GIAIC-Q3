import streamlit as st
import hashlib
from cryptography.fernet import Fernet

# Generate encryption key and initialize session states
if 'KEY' not in st.session_state:
    st.session_state.KEY = Fernet.generate_key()

cipher = Fernet(st.session_state.KEY)

if 'stored_data' not in st.session_state:
    st.session_state.stored_data = {}

if 'failed_attempts' not in st.session_state:
    st.session_state.failed_attempts = 0

# Utility functions
def hash_passkey(passkey):
    return hashlib.sha256(passkey.encode()).hexdigest()

def encrypt_data(text):
    return cipher.encrypt(text.encode()).decode()

def decrypt_data(encrypted_text, passkey):
    hashed_passkey = hash_passkey(passkey)

    for item in st.session_state.stored_data.values():
        if item["encrypted_text"] == encrypted_text and item["passkey"] == hashed_passkey:
            st.session_state.failed_attempts = 0
            return cipher.decrypt(encrypted_text.encode()).decode()
    
    st.session_state.failed_attempts += 1
    return None

# App UI
st.title("🔐 Data Locker Vault")

nav_options = ["Dashboard", "Secure Entry", "Unlock Data", "Admin Access"]
nav_choice = st.sidebar.selectbox("📁 Menu", nav_options)

if nav_choice == "Dashboard":
    st.subheader("🚀 Welcome to Your Private Vault")
    st.markdown("Easily encrypt and safeguard your sensitive text. Restore it anytime with your secret key!")

elif nav_choice == "Secure Entry":
    st.subheader("🗂️ Encrypt & Lock")
    user_text = st.text_area("🔏 Type your confidential message:")
    user_pass = st.text_input("🔑 Choose a secret key:", type="password")

    if st.button("🔒 Lock It"):
        if user_text and user_pass:
            encrypted_text = encrypt_data(user_text)
            hashed_key = hash_passkey(user_pass)
            st.session_state.stored_data[encrypted_text] = {
                "encrypted_text": encrypted_text,
                "passkey": hashed_key
            }
            st.success("🧊 Your message is now encrypted and saved securely.")
            st.text_area("📋 Save this Encrypted Code to retrieve later:", value=encrypted_text, height=100)
        else:
            st.error("⚠️ Both fields are required!")

elif nav_choice == "Unlock Data":
    st.subheader("🔓 Decrypt Your Message")

    if st.session_state.failed_attempts >= 3:
        st.warning("🚫 Too many wrong attempts. Please verify through admin access.")
        st.switch_page("Admin Access")

    cipher_input = st.text_area("🔐 Paste Encrypted Text:")
    pass_input = st.text_input("🔑 Enter your Key:", type="password")

    if st.button("🧪 Unlock"):
        if cipher_input and pass_input:
            result = decrypt_data(cipher_input, pass_input)

            if result:
                st.success("🎉 Decryption Successful!")
                st.code(result)
            else:
                remaining_attempts = 3 - st.session_state.failed_attempts
                st.error(f"❌ Wrong Key! Attempts remaining: {remaining_attempts}")
                if st.session_state.failed_attempts >= 3:
                    st.warning("Redirecting to Admin...")
                    st.rerun()
        else:
            st.error("⚠️ Please enter both encrypted text and key.")

elif nav_choice == "Admin Access":
    st.subheader("🛡️ Administrator Login")
    admin_input = st.text_input("🔐 Enter Master Key:", type="password")

    if st.button("🧿 Verify"):
        if admin_input == "admin123":
            st.session_state.failed_attempts = 0
            st.success("✅ Access restored. Try decryption again.")
        else:
            st.error("🚫 Invalid master key.")
