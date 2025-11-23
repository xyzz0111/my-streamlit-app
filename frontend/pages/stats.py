import streamlit as st
import pandas as pd
from backend.interest_calculator import (
    get_defaulters_by_interest_ratio,
    get_records_by_interest_threshold_custom,
    get_doubled_interest_alerts,
    get_records_with_interest_analysis
)

def render():
    """Render the interest statistics and analytics page (Admin only)"""
    
    st.title("📊 Loan Interest Statistics")
    st.markdown("**Admin Dashboard** - Interest Calculations & Defaulter Analysis")
    st.markdown("---")
    
    # Quick Stats Cards
    col1, col2, col3, col4 = st.columns(4)
    
    all_records = get_records_with_interest_analysis()
    defaulters = get_defaulters_by_interest_ratio()
    doubled_interest = get_doubled_interest_alerts()
    
    with col1:
        st.metric("📋 Total Loans", len(all_records))
    
    with col2:
        st.metric("⚠️ Interest > Principal", len(defaulters), 
                  delta=f"{len(defaulters)/len(all_records)*100:.1f}%" if all_records else "0%")
    
    with col3:
        st.metric("🚨 Interest Doubled (2x)", len(doubled_interest),
                  delta="Critical", delta_color="inverse")
    
    with col4:
        total_interest = sum(r['calculated_interest'] for r in all_records)
        st.metric("💰 Total Interest Accrued", f"₹{total_interest:,.2f}")
    
    st.markdown("---")
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs([
        "🔴 Critical Alerts (2x Interest)",
        "⚠️ Defaulters (Interest > Amount)",
        "🎯 Custom Threshold Filter"
    ])
    
    # TAB 1: Critical Alerts
    with tab1:
        st.subheader("🚨 Critical Defaulters - Interest Has Doubled")
        st.markdown("*Records where interest ≥ 200% of principal amount*")
        
        if doubled_interest:
            df_critical = pd.DataFrame(doubled_interest)
            
            # Select display columns
            display_cols = ['recordId', 'nameHindi', 'nameEnglish', 'mobile', 
                          'amount', 'calculated_interest', 'total_due', 
                          'months_elapsed', 'date', 'loanStatus']
            
            df_display = df_critical[display_cols].copy()
            df_display.columns = ['Record ID', 'Name (Hindi)', 'Name (English)', 
                                 'Mobile', 'Principal (₹)', 'Interest (₹)', 
                                 'Total Due (₹)', 'Months', 'Loan Date', 'Status']
            
            st.dataframe(df_display, use_container_width=True, height=400)
            
            # Summary
            st.markdown(f"**Total Principal:** ₹{df_critical['amount'].sum():,.2f}")
            st.markdown(f"**Total Interest:** ₹{df_critical['calculated_interest'].sum():,.2f}")
            st.markdown(f"**Total Amount Due:** ₹{df_critical['total_due'].sum():,.2f}")
            
        else:
            st.success("✅ No critical alerts! No loans have interest doubled yet.")
    
    # TAB 2: All Defaulters
    with tab2:
        st.subheader("⚠️ All Defaulters - Interest Exceeds Principal")
        st.markdown("*Records where interest > 100% of principal amount*")
        
        if defaulters:
            df_defaulters = pd.DataFrame(defaulters)
            
            # Add interest ratio
            df_defaulters['interest_ratio'] = (
                df_defaulters['calculated_interest'] / df_defaulters['amount'] * 100
            ).round(2)
            
            display_cols = ['recordId', 'nameHindi', 'nameEnglish', 'mobile', 
                          'amount', 'calculated_interest', 'interest_ratio',
                          'total_due', 'months_elapsed', 'loanStatus']
            
            df_display = df_defaulters[display_cols].copy()
            df_display.columns = ['Record ID', 'Name (Hindi)', 'Name (English)', 
                                 'Mobile', 'Principal (₹)', 'Interest (₹)', 
                                 'Interest Ratio (%)', 'Total Due (₹)', 
                                 'Months', 'Status']
            
            # Color code by severity using custom styling
            def highlight_risk(row):
                ratio = row['Interest Ratio (%)']
                if ratio >= 200:
                    color = 'background-color: #ff4444; color: white'
                elif ratio >= 150:
                    color = 'background-color: #ff6666'
                elif ratio >= 100:
                    color = 'background-color: #ffaa44'
                else:
                    color = ''
                return [color if col == 'Interest Ratio (%)' else '' for col in row.index]
            
            st.dataframe(
                df_display.style.apply(highlight_risk, axis=1),
                use_container_width=True,
                height=400
            )
            
            st.markdown(f"**Total Defaulter Principal:** ₹{df_defaulters['amount'].sum():,.2f}")
            st.markdown(f"**Total Defaulter Interest:** ₹{df_defaulters['calculated_interest'].sum():,.2f}")
            
        else:
            st.success("✅ No defaulters found where interest exceeds principal!")
    
    # TAB 3: Custom Threshold with Interest Rate Selector
    with tab3:
        st.subheader("🎯 Custom Interest Threshold Filter")
        st.markdown("*Configure default interest rate and filter by custom threshold*")
        
        # Two columns for controls
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### 📊 Filter Settings")
            
            # Default interest rate selector
            default_interest = st.number_input(
                "Default Interest Rate (%/month)",
                min_value=0.0,
                max_value=20.0,
                value=3.0,
                step=0.5,
                help="This rate will be used when 'interest' field is NA/empty in the sheet"
            )
            
            # Threshold selector
            threshold = st.number_input(
                "Interest Threshold (%)",
                min_value=0,
                max_value=500,
                value=100,
                step=10,
                help="Show loans where interest exceeds this % of principal amount"
            )
            
            st.info(f"**Filtering:** Interest ≥ {threshold}% of principal  \n**Default Rate:** {default_interest}% per month for NA values")
        
        with col2:
            st.markdown("#### 🔍 Results")
            
            # Use the custom function with default interest rate
            filtered_records = get_records_by_interest_threshold_custom(threshold, default_interest)
            
            if filtered_records:
                st.metric("📊 Records Found", len(filtered_records))
                
                df_filtered = pd.DataFrame(filtered_records)
                total_risk = df_filtered['total_due'].sum()
                st.metric("💰 Total Amount at Risk", f"₹{total_risk:,.2f}")
            else:
                st.warning(f"No records found with interest ≥ {threshold}%")
        
        # Display detailed table
        if filtered_records:
            st.markdown("---")
            st.markdown("### 📋 Detailed Records")
            
            df_filtered = pd.DataFrame(filtered_records)
            
            # Select columns with additional details
            display_cols = [
                'recordId', 'nameHindi', 'nameEnglish', 'mobile',
                'dairyNumber', 'pageNumber',
                'amount', 'interest', 'calculated_interest', 'interest_ratio_percentage',
                'total_due', 'months_elapsed', 'date', 'loanStatus'
            ]
            
            # Filter only available columns
            available_cols = [col for col in display_cols if col in df_filtered.columns]
            df_display = df_filtered[available_cols].copy()
            
            # Rename columns for display
            column_mapping = {
                'recordId': 'Record ID',
                'nameHindi': 'Name (Hindi)',
                'nameEnglish': 'Name (English)',
                'mobile': 'Mobile',
                'dairyNumber': 'Dairy #',
                'pageNumber': 'Page #',
                'amount': 'Principal (₹)',
                'interest': 'Rate (%)',
                'calculated_interest': 'Interest (₹)',
                'interest_ratio_percentage': 'Interest Ratio (%)',
                'total_due': 'Total Due (₹)',
                'months_elapsed': 'Months',
                'date': 'Loan Date',
                'loanStatus': 'Status'
            }
            
            df_display.rename(columns={k: v for k, v in column_mapping.items() if k in df_display.columns}, inplace=True)
            
            # Custom color styling
            def highlight_threshold(row):
                if 'Interest Ratio (%)' in row.index:
                    ratio = row['Interest Ratio (%)']
                    if ratio >= 200:
                        color = 'background-color: #ff4444; color: white'
                    elif ratio >= 150:
                        color = 'background-color: #ff6666'
                    elif ratio >= 100:
                        color = 'background-color: #ffaa44'
                    elif ratio >= 50:
                        color = 'background-color: #ffff44'
                    else:
                        color = ''
                    return [color if col == 'Interest Ratio (%)' else '' for col in row.index]
                return ['' for _ in row.index]
            
            st.dataframe(
                df_display.style.apply(highlight_threshold, axis=1),
                use_container_width=True,
                height=500
            )
            
            # Export option
            st.markdown("---")
            csv = df_display.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name=f"loan_threshold_{threshold}percent_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    # TAB 4: All Loans Overview - REMOVED
    
    # Footer with legend
    st.markdown("---")
    st.markdown("""
    ### 📌 Color Legend
    - 🔴 **Red (≥200%)**: Critical - Interest has doubled or more
    - 🟠 **Orange (100-199%)**: High Risk - Interest exceeds principal
    - 🟡 **Yellow (50-99%)**: Medium Risk - Interest approaching principal
    - ⚪ **White (<50%)**: Low Risk - Normal interest levels
    
    **Note:** Default interest rate is **3% per month** if not specified.
    """)