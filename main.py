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
        page_icon="BT",
        layout="wide"
    )
    
    st.title("Brand Together Prime Day Analysis")
    
    # Add a clear cache button
    col1, col2 = st.columns([12, 1])
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
                min_date = min(available_dates)
                max_date = max(available_dates)
                
                # Create columns for the main periods
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.subheader("Lead In")
                    use_range_lead_in = st.checkbox("Use date range selector", key="range_lead_in")
                    if use_range_lead_in:
                        lead_in_range = st.date_input(
                            "Select Lead In range:",
                            value=[],
                            min_value=min_date,
                            max_value=max_date,
                            key="lead_in_range"
                        )
                        if lead_in_range:
                            if isinstance(lead_in_range, (list, tuple)) and len(lead_in_range) == 2:
                                lead_in_dates = [d for d in available_dates if lead_in_range[0] <= d <= lead_in_range[1]]
                            else:
                                lead_in_dates = [lead_in_range] if lead_in_range in available_dates else []
                        else:
                            lead_in_dates = []
                    else:
                        lead_in_dates = st.multiselect(
                            "Select Lead In dates:",
                            options=available_dates,
                            key="lead_in"
                        )
                
                with col2:
                    st.subheader("Discount Dates")
                    use_range_discount = st.checkbox("Use date range selector", key="range_discount")
                    if use_range_discount:
                        discount_range = st.date_input(
                            "Select Discount range:",
                            value=[],
                            min_value=min_date,
                            max_value=max_date,
                            key="discount_range"
                        )
                        if discount_range:
                            if isinstance(discount_range, (list, tuple)) and len(discount_range) == 2:
                                discount_dates = [d for d in available_dates if discount_range[0] <= d <= discount_range[1]]
                            else:
                                discount_dates = [discount_range] if discount_range in available_dates else []
                        else:
                            discount_dates = []
                    else:
                        discount_dates = st.multiselect(
                            "Select Discount dates:",
                            options=available_dates,
                            key="discount"
                        )
                
                with col3:
                    st.subheader("Lead Out")
                    use_range_lead_out = st.checkbox("Use date range selector", key="range_lead_out")
                    if use_range_lead_out:
                        lead_out_range = st.date_input(
                            "Select Lead Out range:",
                            value=[],
                            min_value=min_date,
                            max_value=max_date,
                            key="lead_out_range"
                        )
                        if lead_out_range:
                            if isinstance(lead_out_range, (list, tuple)) and len(lead_out_range) == 2:
                                lead_out_dates = [d for d in available_dates if lead_out_range[0] <= d <= lead_out_range[1]]
                            else:
                                lead_out_dates = [lead_out_range] if lead_out_range in available_dates else []
                        else:
                            lead_out_dates = []
                    else:
                        lead_out_dates = st.multiselect(
                            "Select Lead Out dates:",
                            options=available_dates,
                            key="lead_out"
                        )
                
                # Calculate default Before Lead In and After Lead Out dates
                before_lead_in_default = []
                after_lead_out_default = []
                
                if lead_in_dates:
                    first_lead_in = min(lead_in_dates)
                    before_lead_in_default = [d for d in available_dates if d < first_lead_in]
                
                if lead_out_dates:
                    last_lead_out = max(lead_out_dates)
                    after_lead_out_default = [d for d in available_dates if d > last_lead_out]
                
                # Add Before/After sections
                st.divider()
                st.subheader("📊 Baseline Comparison Periods")
                
                col4, col5 = st.columns(2)
                
                with col4:
                    st.markdown("**Before Lead In**")
                    use_range_before = st.checkbox("Use date range selector", key="range_before")
                    if use_range_before:
                        before_range = st.date_input(
                            "Select Before Lead In range:",
                            value=[],
                            min_value=min_date,
                            max_value=max_date,
                            key="before_lead_in_range"
                        )
                        if before_range:
                            if isinstance(before_range, (list, tuple)) and len(before_range) == 2:
                                before_lead_in_dates = [d for d in available_dates if before_range[0] <= d <= before_range[1]]
                            else:
                                before_lead_in_dates = [before_range] if before_range in available_dates else []
                        else:
                            before_lead_in_dates = []
                    else:
                        before_lead_in_dates = st.multiselect(
                            "Select Before Lead In dates:",
                            options=available_dates,
                            default=before_lead_in_default,
                            key="before_lead_in"
                        )
                
                with col5:
                    st.markdown("**After Lead Out**")
                    use_range_after = st.checkbox("Use date range selector", key="range_after")
                    if use_range_after:
                        after_range = st.date_input(
                            "Select After Lead Out range:",
                            value=[],
                            min_value=min_date,
                            max_value=max_date,
                            key="after_lead_out_range"
                        )
                        if after_range:
                            if isinstance(after_range, (list, tuple)) and len(after_range) == 2:
                                after_lead_out_dates = [d for d in available_dates if after_range[0] <= d <= after_range[1]]
                            else:
                                after_lead_out_dates = [after_range] if after_range in available_dates else []
                        else:
                            after_lead_out_dates = []
                    else:
                        after_lead_out_dates = st.multiselect(
                            "Select After Lead Out dates:",
                            options=available_dates,
                            default=after_lead_out_default,
                            key="after_lead_out"
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
                if before_lead_in_dates:
                    st.header("📊 Before Lead In Period")
                    before_lead_in_table = daily_table[before_lead_in_dates].copy()
                    
                    # Calculate summary and average rows
                    period_data = combined_data[combined_data['date'].isin(before_lead_in_dates)]
                    summary = calculator.calculate_summary_row(period_data)
                    average = calculator.calculate_average_row(period_data)
                    before_lead_in_table['TOTAL'] = summary
                    before_lead_in_table['AVERAGE'] = average
                    
                    # Apply gray color to this table
                    styled_before_lead_in = before_lead_in_table.style.set_properties(**{'background-color': '#D3D3D3'})
                    st.dataframe(styled_before_lead_in, use_container_width=True)
                    
                    # Download button
                    csv = before_lead_in_table.to_csv()
                    st.download_button(
                        label="📄 Download Before Lead In CSV",
                        data=csv,
                        file_name=f"before_lead_in_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        key="download_before_lead_in"
                    )
                
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
                
                if after_lead_out_dates:
                    st.header("📊 After Lead Out Period")
                    after_lead_out_table = daily_table[after_lead_out_dates].copy()
                    
                    # Calculate summary and average rows
                    period_data = combined_data[combined_data['date'].isin(after_lead_out_dates)]
                    summary = calculator.calculate_summary_row(period_data)
                    average = calculator.calculate_average_row(period_data)
                    after_lead_out_table['TOTAL'] = summary
                    after_lead_out_table['AVERAGE'] = average
                    
                    # Apply gray color to this table
                    styled_after_lead_out = after_lead_out_table.style.set_properties(**{'background-color': '#D3D3D3'})
                    st.dataframe(styled_after_lead_out, use_container_width=True)
                    
                    # Download button
                    csv = after_lead_out_table.to_csv()
                    st.download_button(
                        label="📄 Download After Lead Out CSV",
                        data=csv,
                        file_name=f"after_lead_out_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        key="download_after_lead_out"
                    )
                
                # Display Lift Analysis if at least 2 periods are selected
                selected_periods = {
                    'Before Lead In': before_lead_in_dates,
                    'Lead In': lead_in_dates,
                    'Discount': discount_dates,
                    'Lead Out': lead_out_dates,
                    'After Lead Out': after_lead_out_dates
                }
                
                num_selected = sum([bool(dates) for dates in selected_periods.values()])
                
                if num_selected >= 2:
                    st.header("📈 Lift Analysis")
                    
                    # Collect raw average summaries for all selected periods
                    summaries_raw = {}
                    for period_name, dates in selected_periods.items():
                        if dates:
                            period_data = combined_data[combined_data['date'].isin(dates)]
                            summaries_raw[period_name] = calculator.calculate_average_row_raw(period_data)
                    
                    # Create dynamic comparison selector
                    st.subheader("Select Comparisons")
                    st.markdown("Choose which periods to compare (format: **Comparison Period → Baseline Period**)")
                    
                    available_periods = list(summaries_raw.keys())
                    
                    # Number of comparisons
                    num_comparisons = st.number_input(
                        "Number of comparisons:",
                        min_value=1,
                        max_value=10,
                        value=3,
                        help="How many period comparisons do you want to analyze?"
                    )
                    
                    # Collect comparison selections
                    comparisons = []
                    comparison_cols = st.columns(min(num_comparisons, 3))
                    
                    for i in range(num_comparisons):
                        col_idx = i % len(comparison_cols)
                        with comparison_cols[col_idx]:
                            st.markdown(f"**Comparison {i+1}**")
                            
                            baseline = st.selectbox(
                                "Baseline:",
                                options=available_periods,
                                key=f"baseline_{i}",
                                help="The period to compare against"
                            )
                            
                            comparison = st.selectbox(
                                "Compare to:",
                                options=available_periods,
                                key=f"comparison_{i}",
                                help="The period being evaluated"
                            )
                            
                            if baseline != comparison:
                                comparisons.append({
                                    'name': f"{comparison} → {baseline}",
                                    'baseline': baseline,
                                    'comparison': comparison
                                })
                    
                    # Calculate lift for selected comparisons
                    if comparisons:
                        lift_data = {}
                        for comp in comparisons:
                            if comp['baseline'] in summaries_raw and comp['comparison'] in summaries_raw:
                                lift_data[comp['name']] = calculator._calculate_lift_column(
                                    summaries_raw[comp['baseline']],
                                    summaries_raw[comp['comparison']]
                                )
                        
                        if lift_data:
                            lift_table = pd.DataFrame(lift_data)
                        if lift_data:
                            lift_table = pd.DataFrame(lift_data)
                            
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
                        else:
                            st.info("Please select valid period comparisons.")
                    else:
                        st.info("Please configure at least one comparison above.")
        
        except Exception as e:
            st.error(f"Error processing data: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
    
    else:
        st.info("Please upload all four files to begin analysis")

if __name__ == "__main__":
    main()