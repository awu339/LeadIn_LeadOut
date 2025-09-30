import streamlit as st
import pandas as pd
from datetime import datetime, date
import sys
import os

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_processor import DataProcessor
from calculations import MetricsCalculator

# Cache the data processing functions
@st.cache_data
def process_files(transaction_file, sp_file, sb_file, sd_file):
    """Process all files and cache the result"""
    data_processor = DataProcessor()
    
    # Process data
    transaction_df = data_processor.process_transaction_data(transaction_file)
    campaign_df = data_processor.process_campaign_data(sp_file, sb_file, sd_file)
    combined_data = data_processor.combine_data(transaction_df, campaign_df)
    
    return combined_data

def main():
    st.set_page_config(
        page_title="Prime Day Analysis",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Amazon Data Analysis")
    
    # Initialize calculator
    calculator = MetricsCalculator()
    
    # File uploads
    st.header("📁 Upload Files")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        transaction_file = st.file_uploader("Transaction Data", type=['xlsx', 'xls'], key="trans")
    with col2:
        sp_file = st.file_uploader("SP Campaign Data", type=['xlsx', 'xls'], key="sp")
    with col3:
        sb_file = st.file_uploader("SB Campaign Data", type=['xlsx', 'xls'], key="sb")
    with col4:
        sd_file = st.file_uploader("SD Campaign Data", type=['xlsx', 'xls'], key="sd")
    
    if all([transaction_file, sp_file, sb_file, sd_file]):
        try:
            # Process files (cached - only runs once per file set)
            with st.spinner("Processing files... This may take a moment for large files."):
                combined_data = process_files(
                    transaction_file.read(),
                    sp_file.read(),
                    sb_file.read(),
                    sd_file.read()
                )
            
            if not combined_data.empty:
                # Data Summary
                st.header("📊 Data Summary")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Orders", f"{int(combined_data['orders'].sum()):,}")
                with col2:
                    st.metric("Total Revenue", f"${combined_data['revenue'].sum():,.2f}")
                with col3:
                    st.metric("Total Spend", f"${combined_data['campaign_spend'].sum():,.2f}")
                with col4:
                    total_days = len(combined_data['date'].unique())
                    st.metric("Days of Data", total_days)
                
                # Calculate daily metrics table (also cached)
                with st.spinner("Generating daily metrics table..."):
                    daily_table = calculator.calculate_daily_table(combined_data)
                
                # Get date selections first for coloring
                st.header("📅 Select Date Ranges")
                
                available_dates = sorted(combined_data['date'].unique())
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.subheader("Lead In")
                    lead_in_dates = st.multiselect(
                        "Select Lead In dates:",
                        options=available_dates,
                        key="lead_in"
                    )
                
                with col2:
                    st.subheader("Discount Dates")
                    discount_dates = st.multiselect(
                        "Select Discount dates:",
                        options=available_dates,
                        key="discount"
                    )
                
                with col3:
                    st.subheader("Lead Out")
                    lead_out_dates = st.multiselect(
                        "Select Lead Out dates:",
                        options=available_dates,
                        key="lead_out"
                    )
                
                # Display the table with color coding
                st.header("📈 Daily Metrics Table")
                
                # Apply color coding based on selected dates
                def color_columns(col):
                    if col.name in lead_in_dates:
                        return ['background-color: #90EE90'] * len(col)  # Light green
                    elif col.name in discount_dates:
                        return ['background-color: #FFD700'] * len(col)  # Gold/Yellow
                    elif col.name in lead_out_dates:
                        return ['background-color: #FFB6C1'] * len(col)  # Light red/pink
                    else:
                        return [''] * len(col)
                
                # Apply styling
                styled_table = daily_table.style.apply(color_columns, axis=0)
                st.dataframe(styled_table, use_container_width=True)
                
                # Display filtered tables if dates are selected
                if lead_in_dates:
                    st.header("📊 Lead In Period")
                    lead_in_table = daily_table[lead_in_dates]
                    
                    # Apply green color to this table
                    styled_lead_in = lead_in_table.style.set_properties(**{'background-color': '#90EE90'})
                    st.dataframe(styled_lead_in, use_container_width=True)
                    
                    # Download button
                    csv = lead_in_table.to_csv()
                    st.download_button(
                        label="📄 Download Lead In CSV",
                        data=csv,
                        file_name=f"lead_in_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        key="download_lead_in"
                    )
                
                if discount_dates:
                    st.header("📊 Discount Dates Period")
                    discount_table = daily_table[discount_dates]
                    
                    # Apply yellow color to this table
                    styled_discount = discount_table.style.set_properties(**{'background-color': '#FFD700'})
                    st.dataframe(styled_discount, use_container_width=True)
                    
                    # Download button
                    csv = discount_table.to_csv()
                    st.download_button(
                        label="📄 Download Discount Dates CSV",
                        data=csv,
                        file_name=f"discount_dates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        key="download_discount"
                    )
                
                if lead_out_dates:
                    st.header("📊 Lead Out Period")
                    lead_out_table = daily_table[lead_out_dates]
                    
                    # Apply red color to this table
                    styled_lead_out = lead_out_table.style.set_properties(**{'background-color': '#FFB6C1'})
                    st.dataframe(styled_lead_out, use_container_width=True)
                    
                    # Download button
                    csv = lead_out_table.to_csv()
                    st.download_button(
                        label="📄 Download Lead Out CSV",
                        data=csv,
                        file_name=f"lead_out_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        key="download_lead_out"
                    )
        
        except Exception as e:
            st.error(f"Error processing data: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
    
    else:
        st.info("Please upload all four files to begin analysis")

if __name__ == "__main__":
    main()