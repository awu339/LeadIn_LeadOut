import pandas as pd
import numpy as np
import streamlit as st

class MetricsCalculator:
    
    @st.cache_data(show_spinner=False, max_entries=10)
    def calculate_daily_table(_self, combined_data):
        """Create the daily metrics table with dates as columns and metrics as rows"""
        
        # Work with a copy to avoid reference issues
        data = combined_data.copy()
        
        # Get unique dates
        dates = sorted(data['date'].unique())
        
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
            day_data = data[data['date'] == date].iloc[0]
            
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
            
            # Basic metrics with formatting (show N/A if 0)
            metrics['Orders'].append(int(orders) if orders > 0 else "N/A")
            metrics['Order Quantity'].append(int(total_units) if total_units > 0 else "N/A")
            metrics['Revenue'].append(f"${revenue:,.2f}" if revenue > 0 else "N/A")
            metrics['Net Revenue'].append(f"${net_revenue:,.2f}" if net_revenue != 0 else "N/A")
            metrics['Item-Promotion-Discount'].append(f"${promotions:,.2f}" if promotions > 0 else "N/A")
            metrics['Impressions'].append(int(impressions) if impressions > 0 else "N/A")
            metrics['Clicks'].append(int(clicks) if clicks > 0 else "N/A")
            metrics['Campaign Orders'].append(int(campaign_orders) if campaign_orders > 0 else "N/A")
            metrics['Campaign Spend'].append(f"${campaign_spend:,.2f}" if campaign_spend > 0 else "N/A")
            metrics['Campaign Sales'].append(f"${campaign_sales:,.2f}" if campaign_sales > 0 else "N/A")
            
            # Calculated metrics using helper function
            ctr, cvr, cpa, cpc, roas, acos, tacos = _self._calculate_derived_metrics(
                impressions, clicks, campaign_orders, campaign_spend, campaign_sales, revenue
            )
            
            metrics['CTR'].append(f"{ctr:.2f}%" if ctr is not None else "N/A")
            metrics['CVR'].append(f"{cvr:.2f}%" if cvr is not None else "N/A")
            metrics['CPA'].append(f"${cpa:.2f}" if cpa is not None else "N/A")
            metrics['CPC'].append(f"${cpc:.2f}" if cpc is not None else "N/A")
            metrics['ROAS'].append(f"{roas:.2f}x" if roas is not None else "N/A")
            metrics['ACOS'].append(f"{acos:.2f}%" if acos is not None else "N/A")
            metrics['TACOS'].append(f"{tacos:.2f}%" if tacos is not None else "N/A")
        
        # Create DataFrame with dates as columns
        result_df = pd.DataFrame(metrics, index=dates).T
        
        return result_df
    
    def calculate_summary_row(self, period_data):
        """Calculate summary statistics for a period"""
        # Sum the totals
        orders = period_data['orders'].sum()
        total_units = period_data['total_units'].sum()
        revenue = period_data['revenue'].sum()
        net_revenue = period_data['net_revenue'].sum()
        promotions = period_data['item_promotion_discount'].sum()
        impressions = period_data['impressions'].sum()
        clicks = period_data['clicks'].sum()
        campaign_orders = period_data['campaign_orders'].sum()
        campaign_spend = period_data['campaign_spend'].sum()
        campaign_sales = period_data['campaign_sales'].sum()
        
        # Calculate derived metrics from totals
        ctr, cvr, cpa, cpc, roas, acos, tacos = self._calculate_derived_metrics(
            impressions, clicks, campaign_orders, campaign_spend, campaign_sales, revenue
        )
        
        # Return formatted summary row
        return pd.Series({
            'Orders': int(orders),
            'Order Quantity': int(total_units),
            'Revenue': f"${revenue:,.2f}",
            'Net Revenue': f"${net_revenue:,.2f}",
            'Item-Promotion-Discount': f"${promotions:,.2f}",
            'Impressions': int(impressions),
            'Clicks': int(clicks),
            'Campaign Orders': int(campaign_orders),
            'Campaign Spend': f"${campaign_spend:,.2f}",
            'Campaign Sales': f"${campaign_sales:,.2f}",
            'CTR': f"{ctr:.2f}%" if ctr is not None else "N/A",
            'CVR': f"{cvr:.2f}%" if cvr is not None else "N/A",
            'CPA': f"${cpa:.2f}" if cpa is not None else "N/A",
            'CPC': f"${cpc:.2f}" if cpc is not None else "N/A",
            'ROAS': f"{roas:.2f}x" if roas is not None else "N/A",
            'ACOS': f"{acos:.2f}%" if acos is not None else "N/A",
            'TACOS': f"{tacos:.2f}%" if tacos is not None else "N/A"
        })
    
    def calculate_average_row(self, period_data):
        """Calculate average statistics for a period"""
        num_days = len(period_data['date'].unique())
        
        # Average the totals
        orders = period_data['orders'].sum() / num_days
        total_units = period_data['total_units'].sum() / num_days
        revenue = period_data['revenue'].sum() / num_days
        net_revenue = period_data['net_revenue'].sum() / num_days
        promotions = period_data['item_promotion_discount'].sum() / num_days
        impressions = period_data['impressions'].sum() / num_days
        clicks = period_data['clicks'].sum() / num_days
        campaign_orders = period_data['campaign_orders'].sum() / num_days
        campaign_spend = period_data['campaign_spend'].sum() / num_days
        campaign_sales = period_data['campaign_sales'].sum() / num_days
        
        # Calculate derived metrics from averages
        ctr, cvr, cpa, cpc, roas, acos, tacos = self._calculate_derived_metrics(
            impressions, clicks, campaign_orders, campaign_spend, campaign_sales, revenue
        )
        
        # Return formatted average row
        return pd.Series({
            'Orders': f"{orders:.1f}",
            'Order Quantity': f"{total_units:.1f}",
            'Revenue': f"${revenue:,.2f}",
            'Net Revenue': f"${net_revenue:,.2f}",
            'Item-Promotion-Discount': f"${promotions:,.2f}",
            'Impressions': f"{impressions:.0f}",
            'Clicks': f"{clicks:.1f}",
            'Campaign Orders': f"{campaign_orders:.1f}",
            'Campaign Spend': f"${campaign_spend:,.2f}",
            'Campaign Sales': f"${campaign_sales:,.2f}",
            'CTR': f"{ctr:.2f}%" if ctr is not None else "N/A",
            'CVR': f"{cvr:.2f}%" if cvr is not None else "N/A",
            'CPA': f"${cpa:.2f}" if cpa is not None else "N/A",
            'CPC': f"${cpc:.2f}" if cpc is not None else "N/A",
            'ROAS': f"{roas:.2f}x" if roas is not None else "N/A",
            'ACOS': f"{acos:.2f}%" if acos is not None else "N/A",
            'TACOS': f"{tacos:.2f}%" if tacos is not None else "N/A"
        })
    
    def calculate_summary_row_raw(self, period_data):
        """Calculate summary statistics for a period (raw numeric values)"""
        # Sum the totals
        orders = period_data['orders'].sum()
        total_units = period_data['total_units'].sum()
        revenue = period_data['revenue'].sum()
        net_revenue = period_data['net_revenue'].sum()
        promotions = period_data['item_promotion_discount'].sum()
        impressions = period_data['impressions'].sum()
        clicks = period_data['clicks'].sum()
        campaign_orders = period_data['campaign_orders'].sum()
        campaign_spend = period_data['campaign_spend'].sum()
        campaign_sales = period_data['campaign_sales'].sum()
        
        # Calculate derived metrics
        ctr, cvr, cpa, cpc, roas, acos, tacos = self._calculate_derived_metrics(
            impressions, clicks, campaign_orders, campaign_spend, campaign_sales, revenue
        )
        
        # Return raw numeric values
        return pd.Series({
            'Orders': orders,
            'Order Quantity': total_units,
            'Revenue': revenue,
            'Net Revenue': net_revenue,
            'Item-Promotion-Discount': promotions,
            'Impressions': impressions,
            'Clicks': clicks,
            'Campaign Orders': campaign_orders,
            'Campaign Spend': campaign_spend,
            'Campaign Sales': campaign_sales,
            'CTR': ctr if ctr is not None else 0,
            'CVR': cvr if cvr is not None else 0,
            'CPA': cpa if cpa is not None else 0,
            'CPC': cpc if cpc is not None else 0,
            'ROAS': roas if roas is not None else 0,
            'ACOS': acos if acos is not None else 0,
            'TACOS': tacos if tacos is not None else 0
        })
    
    def calculate_average_row_raw(self, period_data):
        """Calculate average statistics for a period (raw numeric values)"""
        num_days = len(period_data['date'].unique())
        
        # Average the totals
        orders = period_data['orders'].sum() / num_days
        total_units = period_data['total_units'].sum() / num_days
        revenue = period_data['revenue'].sum() / num_days
        net_revenue = period_data['net_revenue'].sum() / num_days
        promotions = period_data['item_promotion_discount'].sum() / num_days
        impressions = period_data['impressions'].sum() / num_days
        clicks = period_data['clicks'].sum() / num_days
        campaign_orders = period_data['campaign_orders'].sum() / num_days
        campaign_spend = period_data['campaign_spend'].sum() / num_days
        campaign_sales = period_data['campaign_sales'].sum() / num_days
        
        # Calculate derived metrics from averages
        ctr, cvr, cpa, cpc, roas, acos, tacos = self._calculate_derived_metrics(
            impressions, clicks, campaign_orders, campaign_spend, campaign_sales, revenue
        )
        
        # Return raw numeric values
        return pd.Series({
            'Orders': orders,
            'Order Quantity': total_units,
            'Revenue': revenue,
            'Net Revenue': net_revenue,
            'Item-Promotion-Discount': promotions,
            'Impressions': impressions,
            'Clicks': clicks,
            'Campaign Orders': campaign_orders,
            'Campaign Spend': campaign_spend,
            'Campaign Sales': campaign_sales,
            'CTR': ctr if ctr is not None else 0,
            'CVR': cvr if cvr is not None else 0,
            'CPA': cpa if cpa is not None else 0,
            'CPC': cpc if cpc is not None else 0,
            'ROAS': roas if roas is not None else 0,
            'ACOS': acos if acos is not None else 0,
            'TACOS': tacos if tacos is not None else 0
        })
    
    def _calculate_derived_metrics(self, impressions, clicks, campaign_orders, campaign_spend, campaign_sales, revenue):
        """Calculate derived metrics from base values"""
        ctr = (clicks / impressions * 100) if impressions > 0 else None
        cvr = (campaign_orders / clicks * 100) if clicks > 0 else None
        cpa = (campaign_spend / campaign_orders) if campaign_orders > 0 else None
        cpc = (campaign_spend / clicks) if clicks > 0 else None
        roas = (campaign_sales / campaign_spend) if campaign_spend > 0 else None
        acos = (campaign_spend / campaign_sales * 100) if campaign_sales > 0 else None
        tacos = (campaign_spend / revenue * 100) if revenue > 0 else None
        
        return ctr, cvr, cpa, cpc, roas, acos, tacos
    
    def calculate_lift(self, summaries_raw):
        """Calculate lift between periods using raw numeric data"""
        lift_data = {}
        
        # Calculate lifts for each comparison
        if 'Lead In' in summaries_raw and 'Discount' in summaries_raw:
            lift_data['Discount → Lead In'] = self._calculate_lift_column(
                summaries_raw['Lead In'], summaries_raw['Discount']
            )
        
        if 'Lead In' in summaries_raw and 'Lead Out' in summaries_raw:
            lift_data['Lead Out → Lead In'] = self._calculate_lift_column(
                summaries_raw['Lead In'], summaries_raw['Lead Out']
            )
        
        if 'Discount' in summaries_raw and 'Lead Out' in summaries_raw:
            lift_data['Lead Out → Discount'] = self._calculate_lift_column(
                summaries_raw['Discount'], summaries_raw['Lead Out']
            )
        
        if lift_data:
            lift_df = pd.DataFrame(lift_data)
            return lift_df
        
        return pd.DataFrame()
    
    def _calculate_lift_column(self, baseline, comparison):
        """Calculate lift from baseline to comparison period"""
        lift_values = []
        
        for metric in baseline.index:
            baseline_val = baseline[metric]
            comparison_val = comparison[metric]
            
            if baseline_val != 0:
                lift_pct = ((comparison_val - baseline_val) / baseline_val) * 100
                lift_values.append(f"{lift_pct:+.2f}%")
            else:
                lift_values.append("N/A")
        
        return pd.Series(lift_values, index=baseline.index)
    
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
                
                # Calculate derived metrics using helper function
                ctr, cvr, cpa, cpc, roas, acos, tacos = self._calculate_derived_metrics(
                    impressions, clicks, campaign_orders, campaign_spend, campaign_sales, revenue
                )
                
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
                    'CTR': round(ctr, 2) if ctr is not None else 0,
                    'CVR': round(cvr, 2) if cvr is not None else 0,
                    'CPA': round(cpa, 2) if cpa is not None else 0,
                    'CPC': round(cpc, 2) if cpc is not None else 0,
                    'ROAS': round(roas, 2) if roas is not None else 0,
                    'ACOS': round(acos, 2) if acos is not None else 0,
                    'TACOS': round(tacos, 2) if tacos is not None else 0
                }
        
        return results