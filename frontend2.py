import streamlit as st
import pandas as pd
import sqlite3
from streamlit_dynamic_filters import DynamicFilters
from ollama3 import response_to_user_query
import os
import tempfile
from image_cleaning import clean_single_image_bytes
from ocr_processor import perform_ocr_on_image_path
from parser import parse_multiple_invoices # Import parse_multiple_invoices for potential future use or consistency
from parser import parse_single_invoice_text
from data_insertion import insert_single_bill_data

st.set_page_config(layout="wide") # Use wide layout for better display
st.title("Expense Tracking Dashboard")

DB_NAME = "ocr_master.db"
TABLE_NAME = "ocr_line_items"

def load_data(): 
    try:
        con = sqlite3.connect(DB_NAME) 
        df = pd.read_sql_query(f"SELECT * FROM {TABLE_NAME}", con) 
        con.close() 
        
        # Handle potential None values in filter columns before passing to DynamicFilters
        # This prevents TypeError when sorting options in multiselect
        df['Category'] = df['Category'].fillna('Uncategorized')
        return df
        
    except sqlite3.Error as e:
        st.error(f"Error loading data from database: {e}")
        # Return an empty DataFrame instead of None to prevent errors in st.dataframe
        return pd.DataFrame() 
    
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return pd.DataFrame()

# Load and display the data
data_df = load_data()

# --- File Uploader Section ---
st.sidebar.header("Upload New Bill")
uploaded_file = st.sidebar.file_uploader("Choose an image file (JPG, JPEG, PNG)", type=["jpg", "jpeg", "png"])
 
def handle_uploaded_file(uploaded_file_obj):
    st.sidebar.info("Processing uploaded bill...")
    try:
        # Create a temporary directory for processing
        # Using a fixed temp directory for easier access if needed, but tempfile.TemporaryDirectory is safer
        # For simplicity and to avoid issues with Streamlit's rerun, let's use a session state for paths
        
        # Save original uploaded file to a temporary location for display
        original_image_path = os.path.join(tempfile.gettempdir(), f"original_{uploaded_file_obj.name}")
        with open(original_image_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        
        cleaned_image_path = os.path.join(tempfile.gettempdir(), f"cleaned_{uploaded_file.name}")

        st.sidebar.text("1. Cleaning image...")
        with st.spinner("Cleaning image..."):
            if not clean_single_image_bytes(uploaded_file_obj.getvalue(), cleaned_image_path):
                st.sidebar.error(f"Failed to clean image {uploaded_file_obj.name}.")
                return # Exit processing if cleaning fails

        st.sidebar.text("2. Performing OCR...")
        with st.spinner("Performing OCR..."):
            ocr_text = perform_ocr_on_image_path(cleaned_image_path)
            if not ocr_text:
                st.sidebar.error(f"Failed to extract text (OCR) from {uploaded_file_obj.name}.")
                return # Exit processing if OCR fails

        st.sidebar.text("3. Parsing and Categorizing data...")
        with st.spinner("Parsing and Categorizing data..."):
            structured_bill_data = parse_single_invoice_text(ocr_text, uploaded_file_obj.name)
            
            if not structured_bill_data or not structured_bill_data.get("line_items"):
                st.sidebar.error(f"Failed to parse structured data or no line items found from {uploaded_file.name}.")
                with st.sidebar.expander("View Raw OCR Text"):
                    st.code(ocr_text)
                return # Exit processing if parsing fails

        st.sidebar.success("Processing complete! Review extracted data below.")

        # --- Display Visual Feedback ---
        st.subheader("Uploaded Bill Details")
        col1, col2 = st.columns(2)
        with col1:
            st.image(original_image_path, caption="Original Image", use_column_width=True)
        with col2:
            st.image(cleaned_image_path, caption="Cleaned Image", use_column_width=True)
        
        with st.expander("View Raw OCR Text"):
            st.code(ocr_text, height=300)

        # --- Interactive Data Review and Correction ---
        st.subheader("Review and Correct Extracted Data")

        # Display main invoice details for editing
        st.markdown("##### Invoice Header Details")
        col_inv1, col_inv2, col_inv3 = st.columns(3)
        structured_bill_data["Invoice_No"] = col_inv1.text_input("Invoice No.", value=structured_bill_data.get("Invoice_No", ""))
        structured_bill_data["Issue_Date"] = col_inv2.text_input("Issue Date", value=structured_bill_data.get("Issue_Date", ""))
        structured_bill_data["Grand_Total"] = col_inv3.number_input("Grand Total", value=structured_bill_data.get("Grand_Total", 0.0), format="%.2f")

        col_inv4, col_inv5 = st.columns(2)
        structured_bill_data["billed_to"] = col_inv4.text_input("Billed To", value=structured_bill_data.get("billed_to", ""))
        structured_bill_data["billed_by"] = col_inv5.text_input("Billed By", value=structured_bill_data.get("billed_by", ""))
        structured_bill_data["source_file"] = uploaded_file_obj.name # Ensure source file is correct

        st.markdown("##### Line Items")
        # Convert line_items list of dicts to DataFrame for st.data_editor
        line_items_df = pd.DataFrame(structured_bill_data.get("line_items", []))
        
        # Ensure 'Amount' is numeric for editing
        if 'Amount' in line_items_df.columns:
            line_items_df['Amount'] = pd.to_numeric(line_items_df['Amount'], errors='coerce').fillna(0.0)

        edited_line_items_df = st.data_editor(
            line_items_df,
            num_rows="dynamic", # Allows adding/deleting rows
            use_container_width=True,
            key="line_items_editor"
        )

        if st.button("Confirm and Save to Database"):
            # Convert edited DataFrame back to list of dicts
            structured_bill_data["line_items"] = edited_line_items_df.to_dict(orient='records')
            
            with st.spinner("Inserting data into database..."):
                inserted_count = insert_single_bill_data(structured_bill_data)
                if inserted_count > 0:
                    st.success(f"Successfully processed and added {inserted_count} line items from {uploaded_file_obj.name}!")
                    data_df = load_data() # Reload data to update the displayed table
                    st.rerun() # Rerun to update the dataframe display
                else:
                    st.error(f"Failed to insert data for {uploaded_file.name}.")

    except Exception as e:
        st.sidebar.error(f"An error occurred during bill processing: {e}")
        st.sidebar.exception(e) # Display full exception for debugging

if uploaded_file is not None:
    handle_uploaded_file(uploaded_file)

st.sidebar.markdown("---") # Separator


#adding filter
filters_obj= DynamicFilters(
    data_df,
    filters= ['Category','Invoice_No']
)

with st.sidebar:
    st.header("Filter Expenses")
    # 2. Display the filter widgets in the sidebar
    filters_obj.display_filters()

st.dataframe(filters_obj.filter_df(), width='stretch')

st.title("Chat with your Expenses")
user_question = st.chat_input("Ask me anything about your expenses (e.g., 'what is the total of amount', 'show me all food expenses')")
if user_question:
    st.write(f"You asked: {user_question}")
    print(f"User question: {user_question}")
    
    with st.spinner("Generating SQL query..."):
        sql_query_generation = response_to_user_query(user_question)
    
    st.code(sql_query_generation, language="sql")
    print(f"Generated SQL: {sql_query_generation}")

    with st.spinner("Fetching information from database..."):
        try:
            con = sqlite3.connect(DB_NAME)
            output = pd.read_sql_query(sql_query_generation, con)
            print(f"Query Result:\n{output}")
            con.close()
            
            if not output.empty:
                st.chat_message("assistance").dataframe(output)
            else:
                st.chat_message("assistance").info("No results found for your query.")
        except Exception as e:
            st.chat_message("assistance").error(f"Error executing SQL query: {e}")
            print(f"Error executing SQL query: {e}")
