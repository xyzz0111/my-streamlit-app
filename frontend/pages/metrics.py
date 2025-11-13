"""
Analytics Dashboard - Frontend Module
Displays business insights and growth metrics
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from backend.analytics import generate_dashboard_data
from backend.storage import load_records

def render():
    st.title("📊 Analytics Dashboard")
    st.markdown("### Business Insights & Growth Metrics")
    
    # Load data
    records = load_records()
    
    if not records or len(records) <= 1:
        st.warning("⚠️ No data available for analytics")
        return
    
    # Generate dashboard data
    with st.spinner("Generating analytics..."):
        dashboard_data = generate_dashboard_data(records)
    
    # Key Metrics Row
    st.markdown("### 📈 Key Metrics")
    metrics = dashboard_data['basic_metrics']
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Loans", f"{metrics['total_loans']}")
        st.metric("Active Loans", f"{metrics['active_loans']}")
    
    with col2:
        st.metric("Closed Loans", f"{metrics['closed_loans']}")
        st.metric("Closure Rate", f"{metrics['closure_rate']}%")
    
    with col3:
        st.metric("Total Disbursed", f"₹{metrics['total_amount_disbursed']:,.2f}")
        st.metric("Active Amount", f"₹{metrics['active_amount']:,.2f}")
    
    with col4:
        st.metric("Avg Loan Amount", f"₹{metrics['avg_loan_amount']:,.2f}")
        st.metric("Expected Interest", f"₹{metrics['total_interest_expected']:,.2f}")
    
    st.markdown("---")
    
    # Growth Metrics
    growth = dashboard_data['growth_metrics']
    if growth['mom_growth_count'] != 0:
        st.markdown("### 📊 Growth Trend")
        gcol1, gcol2, gcol3 = st.columns(3)
        
        with gcol1:
            st.metric(
                "Month-over-Month (Count)", 
                f"{growth['mom_growth_count']:+.2f}%",
                delta=f"{growth['trend'].title()}"
            )
        
        with gcol2:
            st.metric(
                "Month-over-Month (Amount)", 
                f"{growth['mom_growth_amount']:+.2f}%"
            )
        
        with gcol3:
            st.info(f"📅 Comparing {growth['current_month']} vs {growth['previous_month']}")
        
        st.markdown("---")
    
    # Charts Row 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📅 Monthly Disbursement Trend")
        monthly_data = dashboard_data['monthly_trend']
        if monthly_data:
            df_monthly = pd.DataFrame(monthly_data)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df_monthly['month'],
                y=df_monthly['amount'],
                name='Amount',
                marker_color='indianred',
                text=df_monthly['amount'].apply(lambda x: f'₹{x:,.0f}'),
                textposition='outside'
            ))
            
            fig.add_trace(go.Scatter(
                x=df_monthly['month'],
                y=df_monthly['count'],
                name='Count',
                yaxis='y2',
                mode='lines+markers',
                marker=dict(size=8, color='blue'),
                line=dict(width=2)
            ))
            
            fig.update_layout(
                yaxis=dict(title='Amount (₹)', side='left'),
                yaxis2=dict(title='Count', side='right', overlaying='y'),
                xaxis_title='Month',
                height=400,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No monthly data available")
    
    with col2:
        st.markdown("### 🏘️ Ward-wise Distribution")
        ward_data = dashboard_data['ward_distribution']
        if ward_data:
            df_ward = pd.DataFrame(ward_data[:10])  # Top 10 wards
            
            fig = px.bar(
                df_ward,
                x='total_amount',
                y='ward',
                orientation='h',
                text='total_loans',
                color='active_loans',
                color_continuous_scale='Viridis',
                labels={'total_amount': 'Total Amount (₹)', 'ward': 'Ward', 'active_loans': 'Active Loans'}
            )
            
            fig.update_traces(texttemplate='%{text} loans', textposition='outside')
            fig.update_layout(height=400)
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No ward data available")
    
    st.markdown("---")
    
    # Charts Row 2
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💰 Loan Amount Distribution")
        range_data = dashboard_data['loan_ranges']
        if range_data:
            df_ranges = pd.DataFrame(range_data)
            
            fig = px.pie(
                df_ranges,
                values='count',
                names='range',
                title='Loans by Amount Range',
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.RdBu
            )
            
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=400)
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No range data available")
    
    with col2:
        st.markdown("### 💵 Interest Analysis")
        interest = dashboard_data['interest_analysis']
        
        # Display interest metrics
        icol1, icol2 = st.columns(2)
        with icol1:
            st.metric("Total Expected Interest", f"₹{interest['total_interest_expected']:,.2f}")
            st.metric("Average Interest Rate", f"{interest['avg_interest_rate']:.2f}%")
        
        with icol2:
            st.metric("Active Loan Interest", f"₹{interest['active_interest']:,.2f}")
            st.metric("Closed Loan Interest", f"₹{interest['closed_interest']:,.2f}")
        
        # Interest by status pie chart
        if interest['interest_by_status']:
            fig = go.Figure(data=[go.Pie(
                labels=list(interest['interest_by_status'].keys()),
                values=list(interest['interest_by_status'].values()),
                hole=0.3
            )])
            fig.update_layout(title='Interest by Status', height=250)
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Year-wise Summary
    st.markdown("### 📆 Year-wise Summary")
    yearly = dashboard_data['yearly_summary']
    if yearly:
        df_yearly = pd.DataFrame(yearly)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Year-wise loan count
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df_yearly['year'],
                y=df_yearly['total_loans'],
                name='Total Loans',
                marker_color='lightblue',
                text=df_yearly['total_loans'],
                textposition='outside'
            ))
            fig.add_trace(go.Bar(
                x=df_yearly['year'],
                y=df_yearly['active_loans'],
                name='Active Loans',
                marker_color='darkblue',
                text=df_yearly['active_loans'],
                textposition='outside'
            ))
            fig.update_layout(
                title='Loans Count by Year',
                xaxis_title='Year',
                yaxis_title='Number of Loans',
                barmode='group',
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Year-wise amount
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df_yearly['year'],
                y=df_yearly['total_amount'],
                name='Total Amount',
                marker_color='lightcoral',
                text=df_yearly['total_amount'].apply(lambda x: f'₹{x/100000:.1f}L' if x >= 100000 else f'₹{x/1000:.0f}K'),
                textposition='outside'
            ))
            fig.add_trace(go.Bar(
                x=df_yearly['year'],
                y=df_yearly['active_amount'],
                name='Active Amount',
                marker_color='darkred',
                text=df_yearly['active_amount'].apply(lambda x: f'₹{x/100000:.1f}L' if x >= 100000 else f'₹{x/1000:.0f}K'),
                textposition='outside'
            ))
            fig.update_layout(
                title='Loan Amount by Year',
                xaxis_title='Year',
                yaxis_title='Amount (₹)',
                barmode='group',
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Year-wise table
        st.dataframe(
            df_yearly,
            column_config={
                'year': 'Year',
                'total_loans': 'Total Loans',
                'total_amount': st.column_config.NumberColumn('Total Amount', format="₹%.2f"),
                'active_loans': 'Active Loans',
                'active_amount': st.column_config.NumberColumn('Active Amount', format="₹%.2f")
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No yearly data available")
    
    st.markdown("---")
    
    # Recent Activity
    st.markdown("### 🕐 Recent Activity (Last 30 Days)")
    recent = dashboard_data['recent_activity']
    if recent:
        df_recent = pd.DataFrame(recent[:15])  # Show top 15
        st.dataframe(
            df_recent,
            column_config={
                'date': 'Date',
                'name': 'Borrower Name',
                'amount': st.column_config.NumberColumn('Amount', format="₹%.2f"),
                'ward': 'Ward'
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No recent activity in the last 30 days")
    
    st.markdown("---")
    
    # Top Borrowers
    st.markdown("### 🏆 Top Borrowers by Total Amount")
    top_borrowers = dashboard_data['top_borrowers']
    if top_borrowers:
        df_top = pd.DataFrame(top_borrowers)
        
        fig = px.bar(
            df_top,
            x='name',
            y='total_amount',
            text='total_loans',
            color='active_loans',
            color_continuous_scale='Blues',
            labels={'total_amount': 'Total Amount (₹)', 'name': 'Borrower', 'active_loans': 'Active Loans'}
        )
        
        fig.update_traces(texttemplate='%{text} loans', textposition='outside')
        fig.update_layout(height=400, xaxis_tickangle=-45)
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No borrower data available")
    
    # Export option
    st.markdown("---")
    st.markdown("### 📥 Export Analytics")
    
    if st.button("Download Full Report (CSV)"):
        # Prepare export data
        export_data = {
            'Metric': [],
            'Value': []
        }
        
        for key, value in metrics.items():
            export_data['Metric'].append(key.replace('_', ' ').title())
            export_data['Value'].append(value)
        
        df_export = pd.DataFrame(export_data)
        csv = df_export.to_csv(index=False)
        
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="loan_analytics_report.csv",
            mime="text/csv"
        )