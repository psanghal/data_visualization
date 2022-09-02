
# Import libraries for python script: 
import pandas as pd
import datetime as dt
import altair as alt

# Build Supplier dashboard: Contains
# dropdown for suppliers and components
# radio button for pricing type
# slider option to see cut off of weight or prices
# add brush to see observed data points


def supplier_dashaboard(data = 'filename_csv', 
                                   col_x = 'weight',
                                   col_y = 'cost',
                                   radio_button ='bracket_pricing',
                                   product_id = 'tube_assembly_id',
                                   date = 'quote_date', 
                                   dropdown_1 = 'comp_name',
                                   dropdown_2 = 'supplier',
                                   cutoff_option = 'cost'):


    

    # Read data: 
    df = pd.read_csv(data, low_memory=False) 
    
    # Add dropdown_1: Component Names
    # sort components by weight count in descending order:
    df[dropdown_1].fillna('None', inplace= True) 
    component = (df.groupby([dropdown_1, dropdown_2])[col_x]
                 .nunique()
                 .sort_values(ascending = False)
                 .reset_index()[dropdown_1]
                 .unique()
                 .tolist())

    # Ignore None
    component = [x for x in component if x!='None']
    
    # create drowdown
    bind_comp = alt.binding_select(options = [None] + component,
                                   labels = ['All'] + component,
                                   name = f'Search by {dropdown_1}')
    
    # bind dropdown:  
    select_comp = alt.selection_single(fields=[dropdown_1],
                                       init = {dropdown_1: component[0]}, 
                                       bind = bind_comp)

    # Add dropdown_2 : Suppliers 
    # sort suppliers by weight count in descending order:
    df[dropdown_2].fillna('None', inplace = True)
    supplier = (df.groupby([dropdown_1, dropdown_2])[col_x]
                .nunique()
                .sort_values(ascending = False)
                .reset_index()[dropdown_2]
                .unique()
                .tolist())
    
    # get list 
    supplier = [x for x in supplier if x!='None']
    
    # create dropdown
    bind_supplier = alt.binding_select(options = [None] + supplier,
                                       labels=['All'] + supplier,
                                       name = f'Search by {dropdown_2}')
    
    # bind dropdown:
    select_supplier = alt.selection_single(fields=[dropdown_2],
                                           #init = {dropdown_2: supplier[0]}, # Commented out to search by 'All'
                                           bind = bind_supplier)
    
    # create highlight for dropdown_1 
    select_highlight = alt.selection_interval(empty = 'all')
    #highlight = alt.condition(select_highlight, alt.value('red'), alt.value('gray'))


    # Add Slider: Cutoff by weight or cost
    min_ = df[cutoff_option].min()
    max_ = df[cutoff_option].max()

    # create slider
    slider = alt.binding_range(max=max_, min=min_, name = f'cutoff_{cutoff_option}')

    # bind slider
    select_slider = alt.selection_single(bind = slider,
                                         fields =[f'cutoff_{cutoff_option}'],
                                         init= {f'cutoff_{cutoff_option}': max_})

    # Add Radio Button: Pricing type
    price = list(df[radio_button].unique())
    
    # create radio button:
    bind_price = alt.binding_radio(options = price, name = f'Search by {radio_button}')
    
    # bind radio button:
    select_price = alt.selection_single(fields=[radio_button], 
                                        init = {radio_button: price[0]},
                                        bind = bind_price)
    # Add Conditions: 
    # create color condition for two pricing types:
    color_condition = alt.condition(select_highlight&select_price, 
                                    alt.Color(radio_button, type = 'nominal'),
                                    alt.value('gray')) 
    
    # opacity:
    opacity_condition = alt.condition(select_highlight&select_price,
                                      alt.value(1), alt.value(0.4))
    
    # Add Brush and combine plots:
    # add brush: 
    brush = alt.selection_interval(encodings = ['x', 'y'], 
                                   init = {'x':[0, min(df[col_x]*100)], 
                                           'y':[0, max(df[col_y])]}, empty = 'none')
    
    # brush condition:
    brush_condition = alt.condition(brush, radio_button, alt.value(''))
    point_brush = (alt.Chart(df)
                   .mark_point()
                   .encode(x = alt.X(col_x, type = 'quantitative',
                                     scale = alt.Scale(type = 'symlog'), axis = alt.Axis(title = '', grid = True)), 
                           y = alt.Y(col_y, type = 'quantitative',
                                     scale = alt.Scale(type = 'symlog'), axis = alt.Axis(title='', grid = True)),
                           color = brush_condition) #brush_condition
                   .add_selection(brush)
                   .properties(width = 750, height = 80, title= {"text": "Supplier Assembly Interactive Dashboard",
                                                                 "subtitle": "Data Observations (Primary Drag & Select)",
                                                                 "color": "black",
                                                                 "subtitleColor": 'darkgrey'}))
 

    # Make Plots: 
    # circle:
    circle = (alt.Chart(df)
              .mark_point().add_selection(alt.selection_single())
              .encode(x = alt.X(col_x, type= 'quantitative', sort = 'y'),
                      y = alt.Y(col_y, type = 'quantitative',axis = alt.Axis(orient = 'left')), 
                      size = alt.Size(col_y, type = 'quantitative', scale = alt.Scale(range = [0, 500])), 
                      color = color_condition,
                      opacity = opacity_condition)) 
    
    # bar:
    bar = (alt.Chart(df)
           .mark_bar(size = 0.1).add_selection(alt.selection_single())
           .encode(x = alt.X(col_x, type= 'quantitative', sort = 'y'),
                   y = alt.Y(col_y, type= 'quantitative', axis = alt.Axis(orient = 'left')), 
                   color = color_condition)) 
    

    # circle_bar: (Use color_condition to first select items by price type
    #             Then highlight to further select items by dropdown)
    
    circle_bar = ((circle+bar)
                  .add_selection(select_comp, select_supplier, select_price, select_slider)
                  .transform_filter(alt.datum[cutoff_option]<select_slider[f'cutoff_{cutoff_option}'])
                  .transform_filter(select_comp)
                  .transform_filter(select_supplier)
                  .transform_filter(select_price)
                  .encode(color = color_condition, # color_condition
                          opacity = opacity_condition,
                          tooltip = [alt.Tooltip(field = product_id, type = 'nominal'),
                                     alt.Tooltip(field = dropdown_2, type = 'nominal'), 
                                     alt.Tooltip(field = dropdown_1, type ='nominal'),
                                     alt.Tooltip(field = col_y, type = 'quantitative'), 
                                     alt.Tooltip(field = col_x, type = 'quantitative'),
                                     alt.Tooltip(field = radio_button, type= 'nominal')])
                  .properties(width= 550, height= 300, title= 'Assembly Cost by Weight'))

    # Concat Plots: Hconcat
    # usage chart
    usage_supplier = (alt.Chart(df)
                 .mark_point(size = 40)
                 .transform_aggregate(groupby = [dropdown_1, radio_button, dropdown_2], cnt = 'count()')
                 .encode(y = alt.Y(dropdown_2, type = 'nominal', axis = alt.Axis(title='Supplier & Component', labelFontSize=8)),
                         x = alt.X('sum(cnt):Q', scale = alt.Scale(type = 'symlog'), axis = alt.Axis(title= 'Sum of count (Demand)')),
                         color = color_condition, # color_condition
                         opacity = opacity_condition,
                         tooltip = [alt.Tooltip(dropdown_1, type = 'nominal'), 
                                    #alt.Tooltip(dropdown_2, type = 'nominal'), 
                                    alt.Tooltip('sum(cnt):Q', title = 'Demand')])
                 .properties(width= 200, height = 300, title = {'text': 'Demand Supplier Components',
                                                                'subtitle': '(Secondary Drag and Select)', 
                                                                'color': 'black', 
                                                                'subtitleColor': 'darkgrey'}))
 
    
        
    usage_component = (alt.Chart(df)
                  .mark_bar(size = 10)
                  .transform_aggregate(groupby = [dropdown_1, radio_button, dropdown_2], cnt = 'count()')
                  .encode(y=alt.Y(dropdown_1, type = 'nominal', axis = alt.Axis(title = "")), 
                          x=alt.X('sum(cnt):Q'),
                          color = color_condition, 
                          opacity= opacity_condition,
                          tooltip = [alt.Tooltip(dropdown_1, type = 'nominal'),
                                    alt.Tooltip('sum(cnt):Q', title = 'Total Count')])
                  .properties(width = 200, height = 300))
    
    
    
    usage_text = (alt.Chart(df)
                  .mark_text(align= 'center',dy = 0, dx = 10, color='gray', size = 8)
                  .transform_aggregate(groupby = [dropdown_1, radio_button, dropdown_2], cnt = 'count()')
                  .encode(y=alt.Y(dropdown_1, type = 'nominal'),
                          x=alt.X('sum(cnt):Q'), 
                          text=alt.Text('sum(cnt):Q')))
                         
    
    
    # usage bar and text together
    usage_trend = usage_supplier+(usage_component+usage_text)

    
    # 4. Show Trends:
        
    # cost dots 
    cost_avg_dots = (alt.Chart(df)
                 .mark_circle(size = 100)
                 .encode(y = alt.Y(f'mean({col_y})', type = 'quantitative', axis  = alt.Axis(title = 'Mean Cost/Unit', orient = 'left')),
                         x = alt.X(f'year({date}):O'),
                         tooltip = [alt.Tooltip(f'year({date}):O', type = 'nominal'),
                                    alt.Tooltip(f'mean({col_y}):Q',
                                                type = 'quantitative',
                                                title = 'Average Cost',
                                                format = '0.2f')],   
                         color = color_condition, 
                         opacity = opacity_condition) 
                 .properties(width = 850, height = 300, title= 'Trend Average Cost/Unit'))
    
    # cost chart  
    cost_avg_line = (alt.Chart(df)
                 .mark_line(size = 3)
                 .encode(y = alt.Y(f'mean({col_y})', type = 'quantitative', axis  = alt.Axis(orient = 'left')),
                         x = alt.X(f'year({date}):O'),
                         color = color_condition, 
                         opacity = opacity_condition)                     
                 .properties(width = 850, height = 300))
    
    cost_scatter = (alt.Chart(df)
                 .mark_point()
                 .encode(y = alt.Y(col_y, 
                                   type = 'quantitative',
                                   axis  = alt.Axis(title = 'Cost/Unit', orient = 'right',
                                                    tickMinStep= 5), 
                                   scale = alt.Scale(type = 'symlog')),
                         x = alt.X(f'year({date}):O'), tooltip = alt.Tooltip(col_y, type = 'quantitative'),
                         color = color_condition, 
                         opacity = opacity_condition,
                         size= alt.Size(col_y, type = 'quantitative', scale = alt.Scale(range = [0, 500])))
                 .properties(width = 750, height = 300))
    
        
   
    # % total supplier spend by pricing type and component:
    spend_df = (df.groupby([dropdown_2, radio_button, dropdown_1])['total_cost'].sum()/df.groupby(dropdown_2)['total_cost'].sum().sum()).sort_values(ascending = False)*100
    spend_df = round(spend_df.reset_index(),2)
    spend = (alt.Chart(spend_df)
             .mark_bar()
             .encode(x = alt.X(dropdown_2, type = 'nominal'),
                     y = alt.Y('total_cost:Q', axis = alt.Axis(title = '% Spend')), 
                     color = color_condition, 
                     opacity= opacity_condition, 
                     tooltip =[alt.Tooltip(field = dropdown_2, type = 'nominal'),
                               alt.Tooltip(field= 'total_cost', type = 'quantitative', title = '% Supplier Spend')])
             .properties(width = 750, height = 300, title = "% Total Supplier Spend by Component"))
   
    # show cost_dots and cost_line together
    cost_trend = ((alt.layer(cost_avg_dots+cost_avg_line)+cost_scatter)
                  .resolve_scale(x = 'shared',y = 'shared'))    
       
    # Combine charts and apply brush: 
    # 1. hconcat show_supplier_components (left) with circle_bar plot:
    # add_selection(select_highlght) is used to select selection interval
    hconcat_plot_top = alt.hconcat(usage_trend.add_selection(select_highlight)
                               .transform_filter(alt.datum[cutoff_option]<select_slider[f'cutoff_{cutoff_option}'])
                               .transform_filter(select_comp)
                               .transform_filter(select_price)
                               .transform_filter(select_supplier)
                               , circle_bar)
    
    # 2. filter point observations by components and hconcat by brush to optimize compute: 
    vconcat_plot_1 = (alt.vconcat(point_brush.add_selection(select_highlight).transform_filter(select_comp),
                               hconcat_plot_top.transform_filter(brush)).add_selection(alt.selection_single()))
 
   
   # 3. vertically connect vconcat_plot_1 with cost_trend:
    vconcat_plot_2 = (alt.vconcat(vconcat_plot_1, cost_trend
                                 .transform_filter(alt.datum[cutoff_option]<select_slider[f'cutoff_{cutoff_option}'])
                                 .transform_filter(select_comp)
                                 .transform_filter(select_price)
                                 .transform_filter(select_supplier)
                                 .transform_filter(brush)))
                      
    # 4. vertically connect vconcat_plot_2 with supplier spend:
    vconcat_plot_2 = (alt.vconcat(vconcat_plot_2, spend
                                 .transform_filter(select_comp)
                                 .transform_filter(select_price)
                                 .transform_filter(select_supplier))
                      .resolve_scale(color= 'shared', x= 'independent')
                      .configure_view(strokeWidth =0)
                      .configure(background = '#f0f0f0')
                      .configure_axis(grid = True)
                      .configure_facet(spacing=0)
                      .add_selection(alt.selection_single()))
    
    return vconcat_plot_2 
