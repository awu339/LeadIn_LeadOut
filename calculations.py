import pandas as pd
import numpy as np
import streamlit as st

class MetricsCalculator:
    
    @st.cache_data
    def calculate_daily_table(_self, combined_data):
        """Create the daily metrics table with dates as columns and metrics as rows"""
        
        # Convert to hashable format for caching
        combined_data_copy = combined_data.copy()
        
        # Get unique dates
        dates = sorted(combined_data_copy['date'].unique())
        
        # Create the metrics dictionary
        metrics = {
            'Orders': [],
            'Order Quantity': [],
            'Revenue': [],
            'Net Revenue': [],
            'Item-Promotion-Discount': [],
            'Impressions': [],
            'Clicks': [],
            'Campaign Orders': [],
            'Campaign Spend': [],
            'Campaign Sales': [],
            'CTR': [],
            'CVR': [],
            'CPA': [],
            'CPC': [],
            'ROAS': [],
            'ACOS': [],
            'TACOS': []
        }
        
        # Calculate metrics for each date
        for date in dates:
            day_data = combined_data_copy[combined_data_copy['date'] == date].iloc[0]
            
            # Use the exact values as they are
            orders = day_data['orders']
            total_units = day_data['total_units']
            revenue = day_data['revenue']
            net_revenue = day_data['net_revenue']
            promotions = day_data['item_promotion_discount']
            impressions = day_data['impressions']
            clicks = day_data['clicks']
            campaign_orders = day_data['campaign_orders']
            campaign_spend = day_data['campaign_spend']
            campaign_sales = day_data['campaign_sales']
            
            # Basic metrics with formatting
            metrics['Orders'].append(int(orders))
            metrics['Order Quantity'].append(int(total_units))
            metrics['Revenue'].append(f"${revenue:,.2f}")
            metrics['Net Revenue'].append(f"${net_revenue:,.2f}")
            metrics['Item-Promotion-Discount'].append(f"${promotions:,.2f}")
            metrics['Impressions'].append(int(impressions))
            metrics['Clicks'].append(int(clicks))
            metrics['Campaign Orders'].append(int(campaign_orders))
            metrics['Campaign Spend'].append(f"${campaign_spend:,.2f}")
            metrics['Campaign Sales'].append(f"${campaign_sales:,.2f}")
            
            # Calculated metrics
            ctr = (clicks / impressions * 100) if impressions > 0 else 0
            cvr = (campaign_orders / clicks * 100) if clicks > 0 else 0
            cpa = (campaign_spend / campaign_orders) if campaign_orders > 0 else 0
            cpc = (campaign_spend / clicks) if clicks > 0 else 0
            roas = (campaign_sales / campaign_spend) if campaign_spend > 0 else 0
            acos = (campaign_spend / campaign_sales * 100) if campaign_sales > 0 else 0
            tacos = (campaign_spend / revenue * 100) if revenue > 0 else 0
            
            metrics['CTR'].append(f"{ctr:.2f}%")
            metrics['CVR'].append(f"{cvr:.2f}%")
            metrics['CPA'].append(f"${cpa:.2f}")
            metrics['CPC'].append(f"${cpc:.2f}")
            metrics['ROAS'].append(f"{roas:.2f}x")
            metrics['ACOS'].append(f"{acos:.2f}%")
            metrics['TACOS'].append(f"{tacos:.2f}%")
        
        # Create DataFrame with dates as columns
        result_df = pd.DataFrame(metrics, index=dates).T
        
        return result_df
    
    def calculate_period_metrics(self, combined_data, periods):
        """Calculate metrics for selected periods"""
        results = {}
        
        for period_name, selected_dates in periods.items():
            if selected_dates:
                # Filter data for this period
                period_data = combined_data[combined_data['date'].isin(selected_dates)]
                
                # Sum the totals
                orders = period_data['orders'].sum()
                revenue = period_data['revenue'].sum()
                net_revenue = period_data['net_revenue'].sum()
                promotions = period_data['item_promotion_discount'].sum()
                impressions = period_data['impressions'].sum()
                clicks = period_data['clicks'].sum()
                campaign_orders = period_data['campaign_orders'].sum()
                campaign_spend = period_data['campaign_spend'].sum()
                campaign_sales = period_data['campaign_sales'].sum()
                
                # Calculate derived metrics
                ctr = (clicks / impressions * 100) if impressions > 0 else 0
                cvr = (campaign_orders / clicks * 100) if clicks > 0 else 0
                cpa = (campaign_spend / campaign_orders) if campaign_orders > 0 else 0
                cpc = (campaign_spend / clicks) if clicks > 0 else 0
                roas = (campaign_sales / campaign_spend) if campaign_spend > 0 else 0
                acos = (campaign_spend / campaign_sales * 100) if campaign_sales > 0 else 0
                tacos = (campaign_spend / revenue * 100) if revenue > 0 else 0
                
                results[period_name] = {
                    'Orders': int(orders),
                    'Sales': round(revenue, 2),
                    'Net Revenue': round(net_revenue, 2),
                    'Item-Promotion-Discount': round(promotions, 2),
                    'Impressions': int(impressions),
                    'Clicks': int(clicks),
                    'Campaign Orders': int(campaign_orders),
                    'Campaign Spend': round(campaign_spend, 2),
                    'Campaign Sales': round(campaign_sales, 2),
                    'CTR': round(ctr, 2),
                    'CVR': round(cvr, 2),
                    'CPA': round(cpa, 2),
                    'CPC': round(cpc, 2),
                    'ROAS': round(roas, 2),
                    'ACOS': round(acos, 2),
                    'TACOS': round(tacos, 2)
                }
        
        return results