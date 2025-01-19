import streamlit as st
import pandas as pd
import os
from datetime import datetime
from urllib.parse import quote

# Define the correct PIN for access
CORRECT_PIN = "1234"  # Change this to your desired PIN

# File paths for persistence
DRINKS_FILE = "default_drinks.csv"
ORDERS_FILE = "orders.csv"

# Initialize default drinks globally
if not os.path.exists(DRINKS_FILE):
    default_drinks = [
        "Coca Cola", "Pepsi", "Sprite", "Fanta",
        "Mountain Dew", "7 Up", "Dr Pepper",
        "Red Bull", "Monster Energy"
    ]
    pd.DataFrame({"Drink": default_drinks}).to_csv(DRINKS_FILE, index=False)
else:
    default_drinks = pd.read_csv(DRINKS_FILE)["Drink"].tolist()

# Initialize session state for authentication
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# Authentication Logic
if not st.session_state["authenticated"]:
    st.title("Cool Drink Store Management")
    st.subheader("Enter the PIN to access the app")
    ...


    # PIN input
    entered_pin = st.text_input("Enter PIN:", type="password")
    if st.button("Submit"):
        if entered_pin == CORRECT_PIN:
            st.session_state["authenticated"] = True
            st.success("Access granted! Welcome to the app.")
        else:
            st.error("Incorrect PIN. Please try again.")
else:
    # Main App Layout
    st.title("Cool Drink Store Management")
    st.sidebar.header("Navigation")
    tab = st.sidebar.radio("Go to", ["Create New Order", "Manage Drink Menu", "Current/Previous Orders"])

    # Tab 1: Create New Order
    if tab == "Create New Order":
        st.header("Create New Order")
        st.subheader("Tap on drinks to add them to your cart.")
        
        # Load default drinks
        if not os.path.exists(DRINKS_FILE):
            default_drinks = [
                "Coca Cola", "Pepsi", "Sprite", "Fanta",
                "Mountain Dew", "7 Up", "Dr Pepper",
                "Red Bull", "Monster Energy"
            ]
            pd.DataFrame({"Drink": default_drinks}).to_csv(DRINKS_FILE, index=False)
        else:
            default_drinks = pd.read_csv(DRINKS_FILE)["Drink"].tolist()

        # Initialize session state for the cart
        if "cart" not in st.session_state:
            st.session_state["cart"] = []

        for drink in default_drinks:
            if st.button(f"Add {drink} to Cart"):
                st.session_state["cart"].append(drink)
                st.success(f"{drink} added to the cart!")

        # Display cart contents
        st.subheader("Cart Contents")
        if st.session_state["cart"]:
            cart_df = pd.DataFrame({"Drink": st.session_state["cart"]})
            cart_summary = cart_df["Drink"].value_counts().reset_index()
            cart_summary.columns = ["Drink", "Quantity"]
            st.table(cart_summary)

            # Undo the last addition
            if st.button("Undo Last Addition"):
                if st.session_state["cart"]:
                    removed_item = st.session_state["cart"].pop()
                    st.warning(f"Removed the last added item: {removed_item}")
                else:
                    st.warning("No items in the cart to undo!")

            # Save order button
            if st.button("Save Order"):
                order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                order_number = len(pd.read_csv(ORDERS_FILE)) // len(cart_summary) + 1
                order_data = pd.DataFrame({
                    "Order Number": [f"Order {order_number}"] * len(cart_summary),
                    "Date": [order_date] * len(cart_summary),
                    "Drink": cart_summary["Drink"],
                    "Quantity": cart_summary["Quantity"]
                })
                order_data.to_csv(ORDERS_FILE, mode="a", header=False, index=False)
                st.session_state["cart"] = []
                st.success(f"Order {order_number} saved successfully on {order_date}!")

            # Clear cart
            if st.button("Clear Cart"):
                st.session_state["cart"] = []
                st.warning("Cart has been cleared!")
        else:
            st.info("Your cart is empty. Start adding drinks!")

    # Tab 2: Manage Drink Menu
    elif tab == "Manage Drink Menu":
        st.header("Manage Your Drink Menu")
        st.subheader("Add new drinks to the menu below.")
        
        with st.form("add_drink_form"):
            new_drink = st.text_input("Enter a new drink name")
            add_drink = st.form_submit_button("Add to Menu")
            if add_drink:
                if new_drink and new_drink not in default_drinks:
                    default_drinks.append(new_drink)
                    pd.DataFrame({"Drink": default_drinks}).to_csv(DRINKS_FILE, index=False)
                    st.success(f"{new_drink} has been added to the menu!")
                elif not new_drink:
                    st.error("Please enter a drink name!")
                else:
                    st.warning(f"{new_drink} is already in the menu!")

        # Display current menu
        st.subheader("Current Drink Menu")
        if default_drinks:
            st.write(", ".join(default_drinks))
        else:
            st.info("No drinks in the menu. Add some to get started!")

    # Tab 3: Current/Previous Orders
    elif tab == "Current/Previous Orders":
        st.header("Current and Previous Orders")

        # Load orders safely
        try:
            if os.path.exists(ORDERS_FILE):
                orders_df = pd.read_csv(ORDERS_FILE)
                if orders_df.empty:
                    raise ValueError("The orders file is empty.")
            else:
                # Create an empty DataFrame with required columns
                orders_df = pd.DataFrame(columns=["Order Number", "Date", "Drink", "Quantity"])
                orders_df.to_csv(ORDERS_FILE, index=False)
        except (pd.errors.EmptyDataError, ValueError):
            # Handle empty or invalid file by recreating it
            orders_df = pd.DataFrame(columns=["Order Number", "Date", "Drink", "Quantity"])
            orders_df.to_csv(ORDERS_FILE, index=False)

        if not orders_df.empty:
            grouped_orders = orders_df.groupby("Order Number")
            for order_number, group in grouped_orders:
                st.subheader(f"{order_number} (Date: {group['Date'].iloc[0]})")
                st.table(group[["Drink", "Quantity"]])
        else:
            st.info("No previous orders found.")
