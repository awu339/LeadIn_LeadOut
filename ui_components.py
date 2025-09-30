import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import io

class UIComponents:
    def __init__(self):
        pass
    
    def display_upload_status(self, files_status):
        """Display the status of file uploads"""
        st.subheader("📋 Upload Status")
        
        for file_name, status in files_status.items():
            if status:
                st.success(f"✅ {file_name} uploaded")
            else:
                st.warning(f"⏳ {file_name} pending")
    
    def display_data_summary(self, transaction_df, campaign_df, combined_df):
        """Display summary statistics of the loaded data"""
        st.header("📊 Data Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Transaction Records", 
                len(transaction_df),
                help="Number of transaction data points"
            )
        
        with col2:
            st.metric(
                "Campaign Records", 
                len(campaign_df) if not campaign_df.empty else 0,
                help="Number of campaign data points"
            )
        
        with col3:
            st.metric(
                "Date Range", 
                f"{len(combined_df['date'].unique())} days",
                help="Number of unique dates in the dataset"
            )
        
        with col4:
            revenue_total = combined_df['revenue'].sum()
            st.metric(
                "Total Revenue",
                f"${revenue_total:,.2f}",
                help="Total revenue from transactions or campaign sales"
            )
        
        # Display date range
        if not combined_df.empty:
            min_date = combined_df['date'].min()
            max_date = combined_df['date'].max()
            st.info(f"📅 Data spans from **{min_date}** to **{max_date}**")
        
        # Show detailed breakdown
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💰 Revenue Breakdown")
            transaction_revenue = transaction_df['revenue'].sum() if 'revenue' in transaction_df.columns else 0
            campaign_sales = campaign_df['campaign-sales'].sum() if not campaign_df.empty and 'campaign-sales' in campaign_df.columns else 0
            
            st.write(f"**Transaction Revenue**: ${transaction_revenue:,.2f}")
            st.write(f"**Campaign Sales**: ${campaign_sales:,.2f}")
            st.write(f"**Final Revenue Used**: ${combined_df['revenue'].sum():,.2f}")
            
            if transaction_revenue == 0 and campaign_sales > 0:
                st.info("💡 Using campaign sales as revenue proxy")
        
        with col2:
            st.subheader("📈 Campaign Performance")
            if not campaign_df.empty:
                total_spend = campaign_df['campaign-spend'].sum()
                total_impressions = campaign_df['impressions'].sum()
                total_clicks = campaign_df['clicks'].sum()
                
                st.write(f"**Total Spend**: ${total_spend:,.2f}")
                st.write(f"**Total Impressions**: {total_impressions:,}")
                st.write(f"**Total Clicks**: {total_clicks:,}")
                
                if total_spend > 0 and campaign_sales > 0:
                    roas = campaign_sales / total_spend
                    st.write(f"**Overall ROAS**: {roas:.2f}x")
        
        # Show data preview
        with st.expander("🔍 Preview Combined Data"):
            # Show key columns only for readability
            display_columns = ['date', 'orders', 'revenue', 'campaign-spend', 'campaign-sales', 'impressions', 'clicks']
            available_columns = [col for col in display_columns if col in combined_df.columns]
            
            preview_df = combined_df[available_columns].head(10)
            
            # Format the preview for better readability
            formatted_preview = preview_df.copy()
            for col in ['revenue', 'campaign-spend', 'campaign-sales']:
                if col in formatted_preview.columns:
                    formatted_preview[col] = formatted_preview[col].apply(lambda x: f"${x:,.2f}")
            
            for col in ['impressions', 'clicks', 'orders']:
                if col in formatted_preview.columns:
                    formatted_preview[col] = formatted_preview[col].apply(lambda x: f"{int(x):,}")
            
            st.dataframe(formatted_preview, use_container_width=True)
    
    def create_date_selection_interface(self, available_dates):
        """Create interface for selecting lead-in, lead-out, and other date ranges"""
        st.markdown("Select date ranges for analysis:")
        
        # Convert dates to datetime for better widget handling
        available_dates = [pd.to_datetime(d).date() if not isinstance(d, date) else d for d in available_dates]
        min_date = min(available_dates)
        max_date = max(available_dates)
        
        date_selections = {}
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Lead-In Period")
            lead_in_dates = st.date_input(
                "Select Lead-In dates:",
                value=[],
                min_value=min_date,
                max_value=max_date,
                key="lead_in",
                help="Select the dates for the lead-in analysis period"
            )
            
            if lead_in_dates:
                if isinstance(lead_in_dates, (list, tuple)):
                    date_selections['Lead-In'] = list(lead_in_dates)
                else:
                    date_selections['Lead-In'] = [lead_in_dates]
        
        with col2:
            st.subheader("📉 Lead-Out Period")
            lead_out_dates = st.date_input(
                "Select Lead-Out dates:",
                value=[],
                min_value=min_date,
                max_value=max_date,
                key="lead_out",
                help="Select the dates for the lead-out analysis period"
            )
            
            if lead_out_dates:
                if isinstance(lead_out_dates, (list, tuple)):
                    date_selections['Lead-Out'] = list(lead_out_dates)
                else:
                    date_selections['Lead-Out'] = [lead_out_dates]
        
        # Additional custom periods
        st.subheader("🎯 Custom Periods")
        
        num_custom_periods = st.number_input(
            "Number of additional periods:", 
            min_value=0, 
            max_value=5, 
            value=0,
            help="Add custom date ranges for comparison"
        )
        
        for i in range(num_custom_periods):
            st.write(f"**Custom Period {i+1}:**")
            custom_dates = st.date_input(
                f"Select dates for Custom Period {i+1}:",
                value=[],
                min_value=min_date,
                max_value=max_date,
                key=f"custom_{i}",
                help=f"Select dates for custom analysis period {i+1}"
            )
            
            if custom_dates:
                if isinstance(custom_dates, (list, tuple)):
                    date_selections[f'Custom-{i+1}'] = list(custom_dates)
                else:
                    date_selections[f'Custom-{i+1}'] = [custom_dates]
        
        return date_selections
    
    def display_results(self, results, date_selections):
        """Display the calculated results"""
        if not results:
            st.warning("⚠️ No results to display. Please select date ranges.")
            return
        
        st.header("📊 Analysis Results")
        
        # Create results table
        results_df = pd.DataFrame(results).T
        
        # Format numerical columns
        numeric_columns = results_df.select_dtypes(include=['float64', 'int64']).columns
        
        # Apply formatting
        formatted_df = results_df.copy()
        
        for col in numeric_columns:
            if col in ['CTR', 'CVR', 'ACOS', 'TACOS']:
                formatted_df[col] = formatted_df[col].apply(lambda x: f"{x:.2f}%")
            elif col in ['CPA', 'CPC', 'Sales', 'Campaign Spend', 'Campaign Sales', 'Item-Promotion-Discount']:
                formatted_df[col] = formatted_df[col].apply(lambda x: f"${x:,.2f}")
            elif col in ['ROAS']:
                formatted_df[col] = formatted_df[col].apply(lambda x: f"{x:.2f}x")
            elif col in ['Orders', 'Campaign Orders', 'Impressions', 'Clicks']:
                formatted_df[col] = formatted_df[col].apply(lambda x: f"{int(x):,}")
        
        st.dataframe(formatted_df, use_container_width=True)
        
        # Create visualizations
        self.create_comparison_charts(results_df)
    
    def create_comparison_charts(self, results_df):
        """Create comparison charts for the results"""
        st.subheader("📈 Performance Comparison")
        
        # Key metrics for comparison
        key_metrics = ['Orders', 'Total Units', 'Sales', 'Campaign Spend', 'ROAS', 'ACOS', 'CTR', 'CVR']
        
        # Create tabs for different chart types
        tab1, tab2, tab3 = st.tabs(["📊 Bar Charts", "📈 Line Charts", "🥧 Pie Charts"])
        
        with tab1:
            # Bar charts for key metrics
            for metric in key_metrics[:4]:  # Show first 4 metrics
                if metric in results_df.columns:
                    fig = px.bar(
                        x=results_df.index,
                        y=results_df[metric],
                        title=f"{metric} Comparison",
                        labels={'x': 'Period', 'y': metric}
                    )
                    fig.update_layout(showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            # Line chart for percentage metrics
            percentage_metrics = ['CTR', 'CVR', 'ACOS', 'TACOS']
            available_metrics = [m for m in percentage_metrics if m in results_df.columns]
            
            if available_metrics:
                fig = go.Figure()
                for metric in available_metrics:
                    fig.add_trace(go.Scatter(
                        x=results_df.index,
                        y=results_df[metric],
                        mode='lines+markers',
                        name=metric
                    ))
                
                fig.update_layout(
                    title="Percentage Metrics Comparison",
                    xaxis_title="Period",
                    yaxis_title="Percentage (%)"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            # Pie chart for spend distribution
            if 'Campaign Spend' in results_df.columns:
                fig = px.pie(
                    values=results_df['Campaign Spend'],
                    names=results_df.index,
                    title="Campaign Spend Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    def create_download_button(self, results):
        """Create download button for results"""
        st.subheader("💾 Export Results")
        
        # Convert results to DataFrame
        results_df = pd.DataFrame(results).T
        
        # Create CSV
        csv_buffer = io.StringIO()
        results_df.to_csv(csv_buffer)
        csv_data = csv_buffer.getvalue()
        
        # Create Excel
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            results_df.to_excel(writer, sheet_name='Analysis Results', index=True)
        excel_data = excel_buffer.getvalue()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                label="📄 Download CSV",
                data=csv_data,
                file_name=f"amazon_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col2:
            st.download_button(
                label="📊 Download Excel",
                data=excel_data,
                file_name=f"amazon_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )