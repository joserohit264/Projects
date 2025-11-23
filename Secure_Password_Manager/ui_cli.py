from storage import init_db, register_user, get_user, add_entry, view_entries, delete_entry
from password_generator import generate_password
from utils.clipboard import copy_to_clipboard
from utils.auth import hash_password, verify_password
from crypto_utils import derive_key, encrypt, decrypt
import base64
import os
import getpass

def running_in_docker():
    return os.path.exists('/.dockerenv')

def prompt_register():
    print("\n=== Register New User ===")
    username = input("Choose username: ").strip()

    if not username:
        print("Username cannot be empty.")
        return None

    # Hidden password input
    password = getpass.getpass("Choose master password: ").strip()
    confirm = getpass.getpass("Retype master password: ").strip()

    if not password or not confirm:
        print("Password fields cannot be empty.")
        return None

    if password != confirm:
        print("Passwords do not match. Try again.")
        return None

    # Hash & store
    pwd_hash_b64, salt_b64 = hash_password(password)

    try:
        user_id = register_user(username, pwd_hash_b64, salt_b64)
        print(f"User '{username}' registered successfully (id={user_id}). Please sign in.")
        return user_id
    except Exception as e:
        print("Failed to register user:", e)
        return None

        

def prompt_login():
    print("\n=== Sign In ===")
    username = input("Username: ").strip()
    password = getpass.getpass("Password: ").strip()

    user = get_user(username)
    if not user:
        print("User not found.")
        return None, None

    user_id, usern, stored_hash_b64, stored_salt_b64 = user

    if verify_password(password, stored_hash_b64, stored_salt_b64):
        salt_bytes = base64.b64decode(stored_salt_b64)
        key = derive_key(password, salt_bytes)
        print(f"Welcome, {usern}!")
        return user_id, key
    else:
        print("Incorrect password.")
        return None, None


def run_cli():
    print("\n🔐 Secure Password Manager (CLI)")
    print("---------------------------------")

    init_db()

    # Authentication loop
    current_user_id = None
    encryption_key = None

    while True:
        print("\n1) Sign In")
        print("2) Register")
        print("3) Exit")
        choice = input("Choose: ").strip()
        if choice == "1":
            uid, key = prompt_login()
            if uid:
                current_user_id = uid
                encryption_key = key
                break
        elif choice == "2":
            prompt_register()
        elif choice == "3":
            return
        else:
            print("Invalid option.")

    # Main user session
    while True:
        print("\nUser Menu")
        print("1. Add Password")
        print("2. View Passwords")
        print("3. Generate Password")
        print("4. Delete Entry")
        print("5. Logout")
        print("6. Exit")

        choice = input("\nChoose an option: ").strip()

        if choice == "1":
            site = input("Site: ").strip()
            user_field = input("Username: ").strip()
            pwd = input("Password (leave blank to generate): ").strip()
            if not pwd:
                pwd = generate_password()
                # show clipboard behavior
                if running_in_docker():
                    print(f"Generated Password (clipboard disabled in Docker): {pwd}")
                else:
                    if copy_to_clipboard(pwd):
                        print("Generated password copied to clipboard.")
                    else:
                        print("Could not copy to clipboard.")
            encrypted_pwd = encrypt(pwd, encryption_key)
            add_entry(current_user_id, site, user_field, encrypted_pwd, "")
            print("✔ Saved!")

        elif choice == "2":
            rows = view_entries(current_user_id)
            if not rows:
                print("No entries found.")
            else:
                print("\nID | SITE | USERNAME | PASSWORD")
                print("------------------------------------------")
                for r in rows:
                    try:
                        decrypted = decrypt(r[3], encryption_key).decode()
                    except Exception:
                        decrypted = "<decryption error>"
                    print(f"{r[0]} | {r[1]} | {r[2]} | {decrypted}")

        elif choice == "3":
            pwd = generate_password()
            if running_in_docker():
                print(f"Generated Password (clipboard disabled in Docker): {pwd}")
            else:
                copied = copy_to_clipboard(pwd)
                print(f"Generated Password: {pwd}")
                if copied:
                    print("(Copied to clipboard)")
                else:
                    print("(Could not copy)")

        elif choice == "4":
            eid = input("Enter ID to delete: ").strip()
            if eid.isdigit():
                delete_entry(current_user_id, int(eid))
                print("✔ Deleted (if existed).")
            else:
                print("Enter a numeric ID.")

        elif choice == "5":
            print("Logging out...")
            current_user_id = None
            encryption_key = None
            # go back to auth
            return run_cli()

        elif choice == "6":
            print("Exiting...")
            break

        else:
            print("Invalid choice.")
