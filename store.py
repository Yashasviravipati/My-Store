import streamlit as st
import pandas as pd
import os

# File path for persistent storage
DRINKS_FILE = "default_drinks.csv"

# Load default drinks from a file or initialize with defaults
if not os.path.exists(DRINKS_FILE):
    # Default drinks
    default_drinks = [
        "Coca Cola",
        "Pepsi",
        "Sprite",
        "Fanta",
        "Mountain Dew",
        "7 Up",
        "Dr Pepper",
        "Red Bull",
        "Monster Energy",
    ]
    # Save defaults to the file
    pd.DataFrame({"Drink": default_drinks}).to_csv(DRINKS_FILE, index=False)
else:
    # Load existing drinks from the file
    default_drinks = pd.read_csv(DRINKS_FILE)["Drink"].tolist()

# Initialize session state for the cart
if "cart" not in st.session_state:
    st.session_state["cart"] = []

# Title
st.title("Cool Drink Store Order Manager")
st.subheader("Easily manage your drink orders and stock!")

# Section: Add new drinks to the menu
st.header("Manage Your Drink Menu")
with st.form("add_drink_form"):
    new_drink = st.text_input("Enter a new drink name to add to the menu")
    add_drink = st.form_submit_button("Add to Menu")
    if add_drink:
        if new_drink and new_drink not in default_drinks:
            default_drinks.append(new_drink)
            # Save updated drinks to the file
            pd.DataFrame({"Drink": default_drinks}).to_csv(DRINKS_FILE, index=False)
            st.success(f"{new_drink} has been added to the menu!")
        elif not new_drink:
            st.error("Please enter a drink name!")
        else:
            st.warning(f"{new_drink} is already in the menu!")

# Section: Add drinks to the cart
st.header("Tap on Drinks to Add to Cart")
for drink in default_drinks:
    if st.button(f"Add {drink} to Cart"):
        st.session_state["cart"].append(drink)
        st.success(f"{drink} added to the cart!")

# Section: Display cart contents
st.header("Cart Contents")
if st.session_state["cart"]:
    cart_df = pd.DataFrame({"Drink": st.session_state["cart"]})
    cart_summary = cart_df["Drink"].value_counts().reset_index()
    cart_summary.columns = ["Drink", "Quantity"]
    st.table(cart_summary)

    # Download cart as CSV
    csv = cart_summary.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Cart as CSV",
        data=csv,
        file_name="drink_cart.csv",
        mime="text/csv",
    )
else:
    st.info("Your cart is empty. Start adding drinks!")

# Section: Clear cart button
if st.button("Clear Cart"):
    st.session_state["cart"] = []
    st.warning("Cart has been cleared!")

# Section: View current menu
st.header("Current Drink Menu")
if default_drinks:
    st.write(", ".join(default_drinks))
else:
    st.info("No drinks in the menu. Add some to get started!")
