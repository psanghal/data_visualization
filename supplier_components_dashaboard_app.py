from supplier_components_dashaboard import supplier_dashaboard
# Call chart 
c = supplier_dashaboard(data = 'components_dashboard.csv',
                               col_x = 'weight',
                               col_y = 'cost', 
                               radio_button= 'bracket_pricing',
                               product_id = 'tube_assembly_id',
                               date = 'quote_date',
                               dropdown_1= 'comp_name', 
                               dropdown_2= 'supplier',
                               cutoff_option= 'cost')

# Plot streamlit chart : 
import streamlit as st
st.altair_chart(c, use_container_width=False)
