# app.py
from flask import Flask, render_template, request, session, redirect, url_for
import os
from datetime import datetime
from crypto_utils import (
    generate_private_key, serialize_public_key, serialize_private_key,
    load_private_key, load_public_key, derive_shared_key,
    encrypt_message, decrypt_message
)

app = Flask(__name__)
app.secret_key = os.urandom(32)

def ensure_keys():
    if "alice_priv" not in session:
        a = generate_private_key()
        session["alice_priv"] = serialize_private_key(a)
        session["alice_pub"] = serialize_public_key(a.public_key())
    if "bob_priv" not in session:
        b = generate_private_key()
        session["bob_priv"] = serialize_private_key(b)
        session["bob_pub"] = serialize_public_key(b.public_key())

    session.setdefault("cipher_ab", "")     # Alice → Bob ciphertext
    session.setdefault("cipher_ba", "")     # Bob → Alice ciphertext
    session.setdefault("result_ab", "")     # Bob decrypted result
    session.setdefault("result_ba", "")     # Alice decrypted result

@app.route("/", methods=["GET"])
def index():
    ensure_keys()
    return render_template(
        "index.html",
        alice_pub=session["alice_pub"],
        alice_priv=session["alice_priv"],
        bob_pub=session["bob_pub"],
        bob_priv=session["bob_priv"],
        cipher_ab=session["cipher_ab"],
        cipher_ba=session["cipher_ba"],
        result_ab=session["result_ab"],
        result_ba=session["result_ba"],
    )

@app.route("/send", methods=["POST"])
def send():
    ensure_keys()
    sender = request.form["sender"]
    msg = request.form["message"].strip()

    alice_priv = load_private_key(session["alice_priv"])
    bob_priv   = load_private_key(session["bob_priv"])
    alice_pub  = load_public_key(session["alice_pub"])
    bob_pub    = load_public_key(session["bob_pub"])

    if sender == "alice":
        shared = derive_shared_key(alice_priv, bob_pub)
        cipher = encrypt_message(shared, msg.encode())
        session["cipher_ab"] = cipher
        session["result_ab"] = ""   # reset decrypted
    else:
        shared = derive_shared_key(bob_priv, alice_pub)
        cipher = encrypt_message(shared, msg.encode())
        session["cipher_ba"] = cipher
        session["result_ba"] = ""

    return redirect(url_for("index"))

@app.route("/decrypt", methods=["POST"])
def decrypt():
    ensure_keys()
    user = request.form["user"]

    alice_priv = load_private_key(session["alice_priv"])
    bob_priv   = load_private_key(session["bob_priv"])
    alice_pub  = load_public_key(session["alice_pub"])
    bob_pub    = load_public_key(session["bob_pub"])

    if user == "bob":   # Bob decrypts Alice→Bob message
        cipher = session["cipher_ab"]
        try:
            shared = derive_shared_key(bob_priv, alice_pub)
            pt = decrypt_message(shared, cipher).decode()
            session["result_ab"] = pt
        except:
            session["result_ab"] = "<Error decrypting>"
    else:  # Alice decrypts Bob→Alice
        cipher = session["cipher_ba"]
        try:
            shared = derive_shared_key(alice_priv, bob_pub)
            pt = decrypt_message(shared, cipher).decode()
            session["result_ba"] = pt
        except:
            session["result_ba"] = "<Error decrypting>"

    return redirect(url_for("index"))

@app.route("/reset", methods=["POST"])
def reset():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
