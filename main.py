import streamlit as st
import pandas as pd
from datetime import datetime, date
import sys
import os

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_processor import DataProcessor
from calculations import MetricsCalculator

# Cache the data processing functions with hash_funcs to avoid conflicts
@st.cache_data(show_spinner=False, max_entries=10)
def process_files(_transaction_bytes, _sp_bytes, _sb_bytes, _sd_bytes, _file_hash):
    """Process all files and cache the result"""
    data_processor = DataProcessor()
    
    # Process data
    transaction_df = data_processor.process_transaction_data(_transaction_bytes)
    campaign_df = data_processor.process_campaign_data(_sp_bytes, _sb_bytes, _sd_bytes)
    combined_data = data_processor.combine_data(transaction_df, campaign_df)
    
    return combined_data

def main():
    st.set_page_config(
        page_title="BrandTogether Prime Day Analysis",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Brand Together Prime Day Analysis")
    
    # Add a clear cache button
    col1, col2 = st.columns([11, 1])
    with col2:
        if st.button("Clear Cache"):
            st.cache_data.clear()
            st.rerun()
    
    # Initialize session state for user isolation
    if 'processed_data' not in st.session_state:
        st.session_state.processed_data = None
    
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
            # Reset file pointers to the beginning
            transaction_file.seek(0)
            sp_file.seek(0)
            sb_file.seek(0)
            sd_file.seek(0)
            
            # Read file bytes
            transaction_bytes = transaction_file.read()
            sp_bytes = sp_file.read()
            sb_bytes = sb_file.read()
            sd_bytes = sd_file.read()
            
            # Create a hash of the file contents to use as cache key
            import hashlib
            file_hash = hashlib.md5(
                transaction_bytes + sp_bytes + sb_bytes + sd_bytes
            ).hexdigest()
            
            # Process files (cached - only runs once per unique file set)
            with st.spinner("Processing files... This may take a moment for large files."):
                combined_data = process_files(
                    transaction_bytes,
                    sp_bytes,
                    sb_bytes,
                    sd_bytes,
                    _file_hash=file_hash
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
                        return ['background-color: #87CEEB'] * len(col)  # Sky blue
                    elif col.name in discount_dates:
                        return ['background-color: #4682B4'] * len(col)  # Steel blue
                    elif col.name in lead_out_dates:
                        return ['background-color: #00008B'] * len(col)  # Dark blue
                    else:
                        return [''] * len(col)
                
                # Apply styling
                styled_table = daily_table.style.apply(color_columns, axis=0)
                st.dataframe(styled_table, use_container_width=True)
                
                # Display filtered tables if dates are selected
                if lead_in_dates:
                    st.header("📊 Lead In Period")
                    lead_in_table = daily_table[lead_in_dates].copy()
                    
                    # Calculate summary and average rows
                    period_data = combined_data[combined_data['date'].isin(lead_in_dates)]
                    summary = calculator.calculate_summary_row(period_data)
                    average = calculator.calculate_average_row(period_data)
                    lead_in_table['TOTAL'] = summary
                    lead_in_table['AVERAGE'] = average
                    
                    # Apply sky blue color to this table
                    styled_lead_in = lead_in_table.style.set_properties(**{'background-color': '#87CEEB'})
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
                    discount_table = daily_table[discount_dates].copy()
                    
                    # Calculate summary and average rows
                    period_data = combined_data[combined_data['date'].isin(discount_dates)]
                    summary = calculator.calculate_summary_row(period_data)
                    average = calculator.calculate_average_row(period_data)
                    discount_table['TOTAL'] = summary
                    discount_table['AVERAGE'] = average
                    
                    # Apply steel blue color to this table
                    styled_discount = discount_table.style.set_properties(**{'background-color': '#4682B4', 'color': 'white'})
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
                    lead_out_table = daily_table[lead_out_dates].copy()
                    
                    # Calculate summary and average rows
                    period_data = combined_data[combined_data['date'].isin(lead_out_dates)]
                    summary = calculator.calculate_summary_row(period_data)
                    average = calculator.calculate_average_row(period_data)
                    lead_out_table['TOTAL'] = summary
                    lead_out_table['AVERAGE'] = average
                    
                    # Apply dark blue color to this table
                    styled_lead_out = lead_out_table.style.set_properties(**{'background-color': '#00008B', 'color': 'white'})
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
                
                # Display Lift Analysis if at least 2 periods are selected
                if sum([bool(lead_in_dates), bool(discount_dates), bool(lead_out_dates)]) >= 2:
                    st.header("📈 Lift Analysis")
                    
                    # Collect raw average summaries
                    summaries_raw = {}
                    if lead_in_dates:
                        period_data = combined_data[combined_data['date'].isin(lead_in_dates)]
                        summaries_raw['Lead In'] = calculator.calculate_average_row_raw(period_data)
                    if discount_dates:
                        period_data = combined_data[combined_data['date'].isin(discount_dates)]
                        summaries_raw['Discount'] = calculator.calculate_average_row_raw(period_data)
                    if lead_out_dates:
                        period_data = combined_data[combined_data['date'].isin(lead_out_dates)]
                        summaries_raw['Lead Out'] = calculator.calculate_average_row_raw(period_data)
                    
                    # Calculate lift
                    lift_table = calculator.calculate_lift(summaries_raw)
                    
                    if not lift_table.empty:
                        # Apply color styling to lift table
                        def color_lift_values(val):
                            """Color positive values green and negative values red"""
                            if isinstance(val, str) and val != "N/A":
                                # Extract the numeric value
                                try:
                                    numeric_val = float(val.replace('%', '').replace('+', ''))
                                    if numeric_val > 0:
                                        return 'background-color: #28a745'  # Darker green
                                    elif numeric_val < 0:
                                        return 'background-color: #dc3545'  # Darker red
                                except:
                                    pass
                            return ''
                        
                        styled_lift = lift_table.style.applymap(color_lift_values)
                        st.dataframe(styled_lift, use_container_width=True)
                        
                        # Download button for lift analysis
                        csv = lift_table.to_csv()
                        st.download_button(
                            label="📄 Download Lift Analysis CSV",
                            data=csv,
                            file_name=f"lift_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            key="download_lift"
                        )
        
        except Exception as e:
            st.error(f"Error processing data: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
    
    else:
        st.info("Please upload all four files to begin analysis")

if __name__ == "__main__":
    main()