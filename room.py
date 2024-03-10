import streamlit as st
import pandas as pd
from universal_component_for_campaign import load_and_process_data,process_usfeed_and_hmfeed_sku_on_ads_data,process_hk_cost_and_value_on_ads_data,\
    process_old_new_sku_2022_and_2023_on_ads_data,merged_spu_to_sku_on_ads_data,merged_imagelink_to_sku_on_ads_data,create_date_filtered_df,\
    output_groupby_df,out_date_range_data,add_groupby_sum_columns_to_list_df,create_dynamic_column_setting,add_custom_proportion_to_df,\
    add_custom_proportion_to_df_x100,format_first_two_rows,format_comparison,colorize_comparison,create_compare_summary_df,\
    create_sensor_gmv_filter_input,create_sensor_campaign_filter_input_df
st.set_page_config(layout="wide")
# ---------------------------------------------------------------------基础数据处理区开始---------------------------------------------------------------------------------------------------
sensor_url = 'https://docs.google.com/spreadsheets/d/1X0YPC6iAZn1Lu4szX67fi5h4B8HiVbfA-i68EyzpOq0/edit#gid=0'
ads_url = 'https://docs.google.com/spreadsheets/d/13G1sZWVLKa_kpScqGVmNp-5abCTkxmAFW0dxW29DMUY/edit#gid=0'
spu_index_url = "https://docs.google.com/spreadsheets/d/1bQTrtNC-o9etJ3xUwMeyD8m383xRRq9U7a3Y-gxjP-U/edit#gid=0"

ads_daily_df = load_and_process_data(ads_url,0)
sensor_daily = load_and_process_data(sensor_url,0)
spu_index = load_and_process_data(spu_index_url,455883801)
old_new = load_and_process_data(spu_index_url,666585210)
room = load_and_process_data(spu_index_url,2136048739)

# 批量GMV筛选框
and_tags,or_tags,exclude_tags = create_sensor_gmv_filter_input('美国GMV条件输入(广告系列筛选)')

ads_daily_df= process_usfeed_and_hmfeed_sku_on_ads_data(ads_daily_df,'MC ID',569301767,9174985,'SKU')
ads_daily_df= process_hk_cost_and_value_on_ads_data(ads_daily_df,'Currency','cost','ads value','HKD')
ads_daily_df = process_old_new_sku_2022_and_2023_on_ads_data(ads_daily_df,'customlabel1').drop(columns=['customlabel0','customlabel2','customlabel4'])
ads_daily_df['SKU'] = ads_daily_df['SKU'].str.strip().str.replace('\n', '').replace('\t', '').str.upper()
ads_daily_df = merged_spu_to_sku_on_ads_data(ads_daily_df,spu_index,'SKU', 'SPU')
old_new  = old_new.rename(columns={'SKU ID':'SKU'})

room = room.rename(columns={'三级类目':'Product Type 3','所属场景':'room'})
room['Product Type 3'] = room['Product Type 3'].str.lower()

sensor_daily  = sensor_daily.rename(columns={'行为时间':'Date'})
ads_daily_df = merged_imagelink_to_sku_on_ads_data(ads_daily_df,old_new,'SKU', 'imagelink')
ads_daily_df = merged_imagelink_to_sku_on_ads_data(ads_daily_df,old_new,'SKU', 'Sale Price')
ads_daily_df = merged_imagelink_to_sku_on_ads_data(ads_daily_df,room,'Product Type 3','room')
ads_daily_df = output_groupby_df(ads_daily_df,['SKU', 'SPU', 'Date','Product Type 3','room'], ['impression','cost','click','conversions','ads value'], 'sum').reset_index()
sensor_daily = merged_spu_to_sku_on_ads_data(sensor_daily,spu_index,'SKU', 'SPU')



with st.sidebar:
    selected_range = out_date_range_data(ads_daily_df,'Date',"自选日期范围")
    compare_selected_range = out_date_range_data(ads_daily_df,'Date',"对比数据日期范围")

if and_tags or or_tags or exclude_tags:
 sensor_daily = create_sensor_campaign_filter_input_df(sensor_daily,and_tags, or_tags, exclude_tags, 'Campaign')
 # 选择日期范围内的数据
 sensor_daily['Date'] = pd.to_datetime(sensor_daily['Date'])
 ads_daily_df['Date'] = pd.to_datetime(ads_daily_df['Date'])
 # 处理普通选择日期范围内的数据
 seonsor_daily_filtered_date_range_df = create_date_filtered_df(sensor_daily, 'Date', selected_range)
 ads_daily_filtered_date_range_df = create_date_filtered_df(ads_daily_df, 'Date', selected_range)
 ads_daily_filtered_date_range_df['日期范围'] = selected_range[0].strftime('%Y-%m-%d') + "至" + selected_range[
     1].strftime('%Y-%m-%d')
 seonsor_daily_filtered_date_range_df['日期范围'] = selected_range[0].strftime('%Y-%m-%d') + "至" + selected_range[
     1].strftime('%Y-%m-%d')
 # 处理对比日期范围内的数据
 compare_seonsor_daily_filtered_date_range_df = create_date_filtered_df(sensor_daily, 'Date', compare_selected_range)
 compare_ads_daily_filtered_date_range_df = create_date_filtered_df(ads_daily_df, 'Date', compare_selected_range)
 compare_ads_daily_filtered_date_range_df['日期范围'] = compare_selected_range[0].strftime('%Y-%m-%d') + "至" + \
                                                        compare_selected_range[1].strftime('%Y-%m-%d')
 compare_seonsor_daily_filtered_date_range_df['日期范围'] = compare_selected_range[0].strftime('%Y-%m-%d') + "至" + \
                                                            compare_selected_range[1].strftime('%Y-%m-%d')
 # 汇总神策SKU数据
 sensor_summary_df = output_groupby_df(seonsor_daily_filtered_date_range_df, ['SKU', 'Date', '日期范围'],
                                       ['saleuser', 'sale', 'GMV', 'AddtoCart', 'UV'], 'sum').reset_index()

 #  合并ads和神策数据
 category3_before_process_df = pd.merge(ads_daily_filtered_date_range_df, sensor_summary_df[
     ['SKU', 'Date', '日期范围', 'GMV', 'UV', 'AddtoCart', 'saleuser', 'sale']],
                                        on=['SKU', 'Date', '日期范围'], how='left')
 # ---------------------------------------------------------------------基础数据处理区结束---------------------------------------------------------------------------------------------------
 # ---------------------------------------------------------------------汇总数据表开始---------------------------------------------------------------------------------------------------
 # 汇总合并三级去日期数据
 category3_raw_summary_df = output_groupby_df(category3_before_process_df, ['room', '日期范围'],
                                              ['impression', 'cost', 'click', 'conversions', 'ads value', 'saleuser',
                                               'sale', 'GMV', 'UV', 'AddtoCart'], 'sum').reset_index()
 # 添加常用指标
 category3_raw_summary_df = add_custom_proportion_to_df(category3_raw_summary_df, 'GMV', 'cost', '神策ROI')
 category3_raw_summary_df = add_custom_proportion_to_df(category3_raw_summary_df, 'ads value', 'cost', 'ads ROI')
 category3_raw_summary_df = add_custom_proportion_to_df(category3_raw_summary_df, 'cost', 'click', 'CPC')
 category3_raw_summary_df = add_custom_proportion_to_df_x100(category3_raw_summary_df, 'click', 'impression', 'CTR')
 category3_raw_summary_df = add_custom_proportion_to_df_x100(category3_raw_summary_df, 'sale', 'UV', '神策转化率')
 category3_raw_summary_df = add_custom_proportion_to_df_x100(category3_raw_summary_df, 'AddtoCart', 'UV', '神策加购率')
 cost_sum = category3_raw_summary_df['cost'].sum()
 click_sum = category3_raw_summary_df['click'].sum()
 impression_sum = category3_raw_summary_df['impression'].sum()
 sale_sum = category3_raw_summary_df['sale'].sum()
 gmv_sum = category3_raw_summary_df['GMV'].sum()
 ads_value_sum = category3_raw_summary_df['ads value'].sum()
 category3_raw_summary_df['impression_sum'] = impression_sum
 category3_raw_summary_df['click_sum'] = click_sum
 category3_raw_summary_df['cost_sum'] = cost_sum
 category3_raw_summary_df['ads_value_sum'] = ads_value_sum
 category3_raw_summary_df['gmv_sum'] = gmv_sum
 category3_raw_summary_df['sale_sum'] = sale_sum
 # 添加占比指标
 category3_raw_summary_df = add_custom_proportion_to_df_x100(category3_raw_summary_df, 'impression', 'impression_sum',
                                                             'impression占比')
 category3_raw_summary_df = add_custom_proportion_to_df_x100(category3_raw_summary_df, 'cost', 'cost_sum', 'cost占比')
 category3_raw_summary_df = add_custom_proportion_to_df_x100(category3_raw_summary_df, 'click', 'click_sum',
                                                             'click占比')
 category3_raw_summary_df = add_custom_proportion_to_df_x100(category3_raw_summary_df, 'ads value', 'ads_value_sum',
                                                             'adsvalue占比')
 category3_raw_summary_df = add_custom_proportion_to_df_x100(category3_raw_summary_df, 'GMV', 'gmv_sum', 'gmv占比')
 category3_raw_summary_df = add_custom_proportion_to_df_x100(category3_raw_summary_df, 'sale', 'sale_sum', '销量占比')
 # 列格式指定
 category3_summary_column_config = create_dynamic_column_setting(category3_raw_summary_df, ['room'],
                                                                 [''],
                                                                 ['cost', 'conversions', 'ads value', 'GMV', '神策ROI',
                                                                  'ads ROI', 'CPC'],
                                                                 ['CTR', '神策转化率', '神策加购率', 'impression占比',
                                                                  'cost占比', 'click占比', 'adsvalue占比', 'gmv占比',
                                                                  '销量占比'],
                                                                 ['UV', 'click', 'impression', 'sale', 'saleuser',
                                                                  'AddtoCart'], None, None)
 st.subheader('美国汇总数据')
 category3_summary_options = st.multiselect(
     '选择三级类目汇总维度',
     category3_raw_summary_df.columns,
     ['room', 'impression', 'CPC', 'cost', 'GMV', '神策ROI', 'cost占比', 'click占比', '销量占比', 'gmv占比']
 )
 st.dataframe(category3_raw_summary_df[category3_summary_options].set_index('room'),
              column_config=category3_summary_column_config)
 # ---------------------------------------------------------------------汇总数据表结束---------------------------------------------------------------------------------------------------
 # ---------------------------------------------------------------------趋势数据表开始---------------------------------------------------------------------------------------------------
 # 汇总合并三级带日期数据
 category3_daily_df = output_groupby_df(category3_before_process_df, ['room', 'Date'],
                                        ['impression', 'cost', 'click', 'conversions', 'ads value', 'saleuser', 'sale',
                                         'GMV', 'UV', 'AddtoCart'], 'sum').reset_index()
 category3_daily_df['Date'] = category3_daily_df['Date'].dt.strftime('%Y-%m-%d')
 # 添加常用指标
 category3_daily_df = add_custom_proportion_to_df(category3_daily_df, 'GMV', 'cost', '神策ROI')
 category3_daily_df = add_custom_proportion_to_df(category3_daily_df, 'ads value', 'cost', 'ads ROI')
 category3_daily_df = add_custom_proportion_to_df(category3_daily_df, 'cost', 'click', 'CPC')
 category3_daily_df = add_custom_proportion_to_df_x100(category3_daily_df, 'click', 'impression', 'CTR')
 category3_daily_df = add_custom_proportion_to_df_x100(category3_daily_df, 'sale', 'UV', '神策转化率')
 category3_daily_df = add_custom_proportion_to_df_x100(category3_daily_df, 'AddtoCart', 'UV', '神策加购率')
 category3_daily_df.sort_values(by=['room', 'Date'], ascending=[True, True], inplace=True)
 category3_list_df = output_groupby_df(category3_daily_df, ['room'],
                                       ['Date', 'impression', 'cost', 'click', 'conversions', 'ads value', 'saleuser',
                                        'sale', 'GMV', 'UV', 'AddtoCart', '神策ROI', 'ads ROI', 'CPC', 'CTR',
                                        '神策转化率', '神策加购率'], list).reset_index()
 # 添加总和列,直接沿用list_df的groupby-list
 category3_list_df = add_groupby_sum_columns_to_list_df(category3_daily_df, category3_list_df, ['room'],
                                                        'cost', 'cost_sum')
 category3_list_df = add_groupby_sum_columns_to_list_df(category3_daily_df, category3_list_df, ['room'],
                                                        'GMV', 'gmv_sum')
 category3_list_df = add_groupby_sum_columns_to_list_df(category3_daily_df, category3_list_df, ['room'],
                                                        'ads value', 'ads_value_sum')
 category3_list_df = add_custom_proportion_to_df(category3_list_df, 'gmv_sum', 'cost_sum', '神策总ROI').round(2)
 category3_list_df = add_custom_proportion_to_df(category3_list_df, 'ads_value_sum', 'cost_sum', 'ads总ROI').round(2)
 # 列格式指定
 category3_list_column_config = create_dynamic_column_setting(category3_list_df, ['room', 'Date'],
                                                              [''],
                                                              ['cost_sum', 'gmv_sum', 'ads_value_sum', '神策总ROI',
                                                               'ads总ROI'], [''], [''], None, None)
 st.subheader('美国趋势数据')
 category3_trend_options = st.multiselect(
     '选择三级类目趋势维度',
     category3_list_df.columns,
     ['room', 'cost_sum', 'gmv_sum', '神策总ROI', 'ads总ROI', 'impression', 'CPC', 'cost', 'GMV']
 )
 st.dataframe(category3_list_df[category3_trend_options].set_index('room'),
              column_config=category3_list_column_config,
              width=1600, height=400)
 # ---------------------------------------------------------------------汇总数据表结束---------------------------------------------------------------------------------------------------
 # ---------------------------------------------------------------------占比数据表开始---------------------------------------------------------------------------------------------------

 # 创建占比基础数据df
 category3_sum_df = output_groupby_df(category3_before_process_df, ['Date'],
                                      ['impression', 'cost', 'click', 'conversions', 'ads value', 'saleuser', 'sale',
                                       'GMV', 'UV', 'AddtoCart'], 'sum').reset_index()
 category3_sum_df['Date'] = category3_sum_df['Date'].dt.strftime('%Y-%m-%d')
 category3_sum_df = category3_sum_df.rename(
     columns={'impression': 'sum_impression', 'cost': 'sum_cost', 'click': 'sum_click',
              'conversions': 'sum_conversions', 'ads value': 'sum_ads_value'
         , 'GMV': 'sum_GMV', 'sale': 'sum_sale', 'saleuser': 'sum_saleuser', 'UV': 'sum_UV',
              'AddtoCart': 'sum_AddtoCart'})

 category3_proportion_df = pd.merge(category3_daily_df, category3_sum_df[
     ['Date', 'sum_impression', 'sum_cost', 'sum_click', 'sum_conversions', 'sum_ads_value', 'sum_GMV',
      'sum_sale', 'sum_saleuser', 'sum_UV', 'sum_AddtoCart']], on=['Date'], how='left')
 category3_proportion_df = add_custom_proportion_to_df_x100(category3_proportion_df, 'impression', 'sum_impression',
                                                            'impression占比')
 category3_proportion_df = add_custom_proportion_to_df_x100(category3_proportion_df, 'cost', 'sum_cost', 'cost占比')
 category3_proportion_df = add_custom_proportion_to_df_x100(category3_proportion_df, 'click', 'sum_click', 'click占比')
 category3_proportion_df = add_custom_proportion_to_df_x100(category3_proportion_df, 'ads value', 'sum_ads_value',
                                                            'adsvalue占比')
 category3_proportion_df = add_custom_proportion_to_df_x100(category3_proportion_df, 'conversions', 'sum_conversions',
                                                            'conversion占比')
 category3_proportion_df = add_custom_proportion_to_df_x100(category3_proportion_df, 'GMV', 'sum_GMV', 'GMV占比')
 category3_proportion_df = add_custom_proportion_to_df_x100(category3_proportion_df, 'sale', 'sum_sale', '销量占比')
 category3_proportion_df = category3_proportion_df[
     ['room', 'Date', 'impression', 'cost', 'click', 'ads value', 'conversions', 'GMV', 'impression占比',
      'cost占比', 'click占比', 'adsvalue占比', 'conversion占比', 'GMV占比', '销量占比']]

 category3_proportion_list_df = output_groupby_df(category3_proportion_df, ['room'],
                                                  ['Date', 'impression', 'cost', 'click', 'ads value', 'conversions',
                                                   'GMV', 'impression占比', 'cost占比', 'click占比', 'adsvalue占比',
                                                   'conversion占比', 'GMV占比', '销量占比'], list).reset_index()
 category3_proportion_list_df = add_groupby_sum_columns_to_list_df(category3_daily_df, category3_proportion_list_df,
                                                                   ['room'], 'cost', 'cost_sum')
 category3_proportion_list_df = add_groupby_sum_columns_to_list_df(category3_daily_df, category3_proportion_list_df,
                                                                   ['room'], 'GMV', 'gmv_sum')
 category3_proportion_list_df = add_groupby_sum_columns_to_list_df(category3_daily_df, category3_proportion_list_df,
                                                                   ['room'], 'ads value', 'ads_value_sum')
 category3_proportion_list_df = add_custom_proportion_to_df(category3_proportion_list_df, 'gmv_sum', 'cost_sum',
                                                            '神策总ROI').round(2)
 category3_proportion_list_df = add_custom_proportion_to_df(category3_proportion_list_df, 'ads_value_sum', 'cost_sum',
                                                            'ads总ROI').round(2)
 category3_proportion_list_df = category3_proportion_list_df[
     ['room', 'cost_sum', 'gmv_sum', 'ads_value_sum', '神策总ROI', 'ads总ROI', 'Date', 'impression占比',
      'cost占比', 'click占比', 'adsvalue占比', 'conversion占比', 'GMV占比', '销量占比']]
 # 列格式指定
 category3_proportion_list_column_config = create_dynamic_column_setting(category3_proportion_list_df,
                                                                         ['room', 'Date'],
                                                                         [''], ['cost_sum', 'gmv_sum', 'ads_value_sum',
                                                                                '神策总ROI', 'ads总ROI'], [''], [''], 0,
                                                                         15)
 st.subheader('占比数据')
 category3_proportion_list_options = st.multiselect(
     '选择三级类目占比数据维度',
     category3_proportion_list_df.columns,
     ['room', 'cost_sum', 'gmv_sum', 'impression占比', 'cost占比', 'click占比', 'adsvalue占比',
      'conversion占比', 'GMV占比']
 )
 st.dataframe(category3_proportion_list_df[category3_proportion_list_options].set_index('room')
              , column_config=category3_proportion_list_column_config
              , width=1600, height=400)


 # ---------------------------------------------------------------------占比数据表结束---------------------------------------------------------------------------------------------------
 def compare_summary_df_output(summary_df, compare_summary_df, select_column):
     summary_df = output_groupby_df(summary_df, ['日期范围'],
                                    ['impression', 'cost', 'click', 'conversions', 'ads value', 'GMV', 'UV',
                                     'AddtoCart', 'saleuser', 'sale'], 'sum').reset_index()
     summary_df = add_custom_proportion_to_df(summary_df, 'GMV', 'cost', '神策ROI')
     summary_df = add_custom_proportion_to_df(summary_df, 'ads value', 'cost', 'ads ROI')
     summary_df = add_custom_proportion_to_df(summary_df, 'cost', 'conversions', 'ads CPA')
     summary_df = add_custom_proportion_to_df(summary_df, 'cost', 'click', 'CPC')
     summary_df = add_custom_proportion_to_df(summary_df, 'click', 'impression', 'CTR')
     summary_df = add_custom_proportion_to_df(summary_df, 'sale', 'UV', '神策转化率')
     summary_df = add_custom_proportion_to_df(summary_df, 'AddtoCart', 'UV', '神策加购率')
     summary_df = add_custom_proportion_to_df(summary_df, 'GMV', 'saleuser', '客单价')
     compare_summary_df = output_groupby_df(compare_summary_df, ['日期范围'],
                                            ['impression', 'cost', 'click', 'conversions', 'ads value', 'GMV', 'UV',
                                             'AddtoCart', 'saleuser', 'sale'], 'sum').reset_index()
     compare_summary_df = add_custom_proportion_to_df(compare_summary_df, 'GMV', 'cost', '神策ROI')
     compare_summary_df = add_custom_proportion_to_df(compare_summary_df, 'ads value', 'cost', 'ads ROI')
     compare_summary_df = add_custom_proportion_to_df(compare_summary_df, 'cost', 'conversions', 'ads CPA')
     compare_summary_df = add_custom_proportion_to_df(compare_summary_df, 'cost', 'click', 'CPC')
     compare_summary_df = add_custom_proportion_to_df(compare_summary_df, 'click', 'impression', 'CTR')
     compare_summary_df = add_custom_proportion_to_df(compare_summary_df, 'sale', 'UV', '神策转化率')
     compare_summary_df = add_custom_proportion_to_df(compare_summary_df, 'AddtoCart', 'UV', '神策加购率')
     compare_summary_df = add_custom_proportion_to_df(compare_summary_df, 'GMV', 'saleuser', '客单价')
     combined_df = create_compare_summary_df(summary_df, compare_summary_df, select_column)
     formatted_df = combined_df.head(2).copy()
     formatted_df[['sale', 'saleuser', 'UV', 'AddtoCart', 'impression', 'click']] = formatted_df[
         ['sale', 'saleuser', 'UV', 'AddtoCart', 'impression', 'click']].astype(int)
     for column in formatted_df.head():
         format_string = '{:.2f}' if column in ['cost', 'GMV', 'ads value', 'CPC', 'conversions', 'ads ROI', '神策ROI',
                                                'ads CPA', '客单价'] else '{}'
         format_string = '{:.2%}' if column in ['CTR', '神策转化率', '神策加购率'] else format_string
         formatted_df[column] = formatted_df[column].apply(format_first_two_rows, args=(format_string,))
     compare_data_df = combined_df.iloc[2:3].copy()
     compare_data_df[compare_data_df.columns[1:]] = compare_data_df[compare_data_df.columns[1:]].apply(pd.to_numeric,
                                                                                                       errors='coerce')
     combined_df.update(formatted_df)
     combined_df.update(compare_data_df)
     summary_options = st.multiselect(
         '选择汇总数据维度',
         combined_df.columns,
         ['日期范围', 'cost', 'click', 'GMV', 'ads value', 'CPC', 'conversions']
     )
     combined_df = combined_df[summary_options]
     combined_df = combined_df.apply(format_comparison, axis=1)
     combined_df = combined_df.style.apply(colorize_comparison, axis=1)
     st.subheader('对比数据')
     st.dataframe(combined_df,
                  width=1600, height=200)


 st.subheader('对比数据')
 unique_category_3 = compare_ads_daily_filtered_date_range_df['room'].unique()
 category3_options = st.multiselect(
     '选择三级类目',
     unique_category_3
 )
 # 汇总神策SKU数据
 compare_sensor_summary_df = output_groupby_df(compare_seonsor_daily_filtered_date_range_df,
                                               ['SKU', 'Date', '日期范围'],
                                               ['saleuser', 'sale', 'GMV', 'AddtoCart', 'UV'], 'sum').reset_index()
 #  合并ads和神策数据
 compare_category3_before_process_df = pd.merge(compare_ads_daily_filtered_date_range_df, compare_sensor_summary_df[
     ['SKU', 'Date', '日期范围', 'GMV', 'UV', 'AddtoCart', 'saleuser', 'sale']],
                                                on=['SKU', 'Date', '日期范围'], how='left')
 # 汇总合并三级去日期数据
 compare_category3_origin_summary_df = output_groupby_df(compare_category3_before_process_df,
                                                         ['room', '日期范围'],
                                                         ['impression', 'cost', 'click', 'conversions', 'ads value',
                                                          'saleuser', 'sale', 'GMV', 'UV', 'AddtoCart'],
                                                         'sum').reset_index()
 category3_origin_summary_df = output_groupby_df(category3_before_process_df, ['room', '日期范围'],
                                                 ['impression', 'cost', 'click', 'conversions', 'ads value', 'saleuser',
                                                  'sale', 'GMV', 'UV', 'AddtoCart'], 'sum').reset_index()
 if category3_options:
     category3_origin_summary_df = category3_origin_summary_df[
         category3_origin_summary_df['room'].isin(category3_options)].drop(columns=['room'])
     compare_category3_origin_summary_df = compare_category3_origin_summary_df[
         compare_category3_origin_summary_df['room'].isin(category3_options)].drop(columns=['room'])

     compare_summary_df_output(category3_origin_summary_df, compare_category3_origin_summary_df,
                               ['日期范围', 'impression', 'cost', 'click', 'conversions', 'ads value', 'GMV', 'UV',
                                'AddtoCart', 'saleuser', 'sale', '神策ROI', 'ads ROI', 'ads CPA', 'CPC', 'CTR',
                                '神策转化率', '神策加购率','客单价'])

else:
    # 选择日期范围内的数据
    sensor_daily['Date'] = pd.to_datetime(sensor_daily['Date'])
    ads_daily_df['Date'] = pd.to_datetime(ads_daily_df['Date'])
    # 处理普通选择日期范围内的数据
    seonsor_daily_filtered_date_range_df = create_date_filtered_df(sensor_daily,'Date',selected_range)
    ads_daily_filtered_date_range_df = create_date_filtered_df(ads_daily_df,'Date',selected_range)
    ads_daily_filtered_date_range_df['日期范围'] = selected_range[0].strftime('%Y-%m-%d')+"至"+selected_range[1].strftime('%Y-%m-%d')
    seonsor_daily_filtered_date_range_df['日期范围'] = selected_range[0].strftime('%Y-%m-%d')+"至"+selected_range[1].strftime('%Y-%m-%d')
    # 处理对比日期范围内的数据
    compare_seonsor_daily_filtered_date_range_df = create_date_filtered_df(sensor_daily,'Date',compare_selected_range)
    compare_ads_daily_filtered_date_range_df = create_date_filtered_df(ads_daily_df,'Date',compare_selected_range)
    compare_ads_daily_filtered_date_range_df['日期范围'] = compare_selected_range[0].strftime('%Y-%m-%d')+"至"+compare_selected_range[1].strftime('%Y-%m-%d')
    compare_seonsor_daily_filtered_date_range_df['日期范围'] = compare_selected_range[0].strftime('%Y-%m-%d')+"至"+compare_selected_range[1].strftime('%Y-%m-%d')
    # 汇总神策SKU数据
    sensor_summary_df = output_groupby_df(seonsor_daily_filtered_date_range_df, ['SKU','Date','日期范围'], ['saleuser','sale','GMV','AddtoCart','UV'], 'sum').reset_index()

    #  合并ads和神策数据
    category3_before_process_df = pd.merge(ads_daily_filtered_date_range_df,sensor_summary_df[['SKU', 'Date','日期范围', 'GMV', 'UV', 'AddtoCart', 'saleuser', 'sale']],
                                           on=['SKU', 'Date','日期范围'], how='left')
    # ---------------------------------------------------------------------基础数据处理区结束---------------------------------------------------------------------------------------------------
    # ---------------------------------------------------------------------汇总数据表开始---------------------------------------------------------------------------------------------------
    # 汇总合并三级去日期数据
    category3_raw_summary_df = output_groupby_df(category3_before_process_df, ['room','日期范围'],
                ['impression','cost','click','conversions','ads value','saleuser','sale','GMV','UV','AddtoCart'], 'sum').reset_index()
    # 添加常用指标
    category3_raw_summary_df = add_custom_proportion_to_df(category3_raw_summary_df,'GMV','cost','神策ROI')
    category3_raw_summary_df = add_custom_proportion_to_df(category3_raw_summary_df,'ads value','cost','ads ROI')
    category3_raw_summary_df = add_custom_proportion_to_df(category3_raw_summary_df,'cost','click','CPC')
    category3_raw_summary_df = add_custom_proportion_to_df_x100(category3_raw_summary_df,'click','impression','CTR')
    category3_raw_summary_df = add_custom_proportion_to_df_x100(category3_raw_summary_df,'sale','UV','神策转化率')
    category3_raw_summary_df = add_custom_proportion_to_df_x100(category3_raw_summary_df,'AddtoCart','UV','神策加购率')
    cost_sum = category3_raw_summary_df['cost'].sum()
    click_sum = category3_raw_summary_df['click'].sum()
    impression_sum = category3_raw_summary_df['impression'].sum()
    sale_sum = category3_raw_summary_df['sale'].sum()
    gmv_sum = category3_raw_summary_df['GMV'].sum()
    ads_value_sum = category3_raw_summary_df['ads value'].sum()
    category3_raw_summary_df['impression_sum'] = impression_sum
    category3_raw_summary_df['click_sum'] = click_sum
    category3_raw_summary_df['cost_sum'] = cost_sum
    category3_raw_summary_df['ads_value_sum'] = ads_value_sum
    category3_raw_summary_df['gmv_sum'] = gmv_sum
    category3_raw_summary_df['sale_sum'] = sale_sum
    # 添加占比指标
    category3_raw_summary_df = add_custom_proportion_to_df_x100(category3_raw_summary_df,'impression','impression_sum','impression占比')
    category3_raw_summary_df = add_custom_proportion_to_df_x100(category3_raw_summary_df,'cost','cost_sum','cost占比')
    category3_raw_summary_df = add_custom_proportion_to_df_x100(category3_raw_summary_df,'click','click_sum','click占比')
    category3_raw_summary_df = add_custom_proportion_to_df_x100(category3_raw_summary_df,'ads value','ads_value_sum','adsvalue占比')
    category3_raw_summary_df = add_custom_proportion_to_df_x100(category3_raw_summary_df,'GMV','gmv_sum','gmv占比')
    category3_raw_summary_df = add_custom_proportion_to_df_x100(category3_raw_summary_df,'sale','sale_sum','销量占比')
    # 列格式指定
    category3_summary_column_config = create_dynamic_column_setting(category3_raw_summary_df,['room'],
    [''], ['cost','conversions','ads value','GMV','神策ROI','ads ROI','CPC'],
    ['CTR','神策转化率','神策加购率','impression占比','cost占比','click占比','adsvalue占比','gmv占比','销量占比'],
    ['UV','click','impression','sale','saleuser','AddtoCart'],None,None)
    st.subheader('美国汇总数据')
    category3_summary_options = st.multiselect(
    '选择三级类目汇总维度',
    category3_raw_summary_df.columns,
    ['room','impression', 'CPC', 'cost', 'GMV','神策ROI','cost占比','click占比','销量占比','gmv占比']
    )
    st.dataframe(category3_raw_summary_df[category3_summary_options].set_index('room'),
                 column_config=category3_summary_column_config)
    # ---------------------------------------------------------------------汇总数据表结束---------------------------------------------------------------------------------------------------
    # ---------------------------------------------------------------------趋势数据表开始---------------------------------------------------------------------------------------------------
    # 汇总合并三级带日期数据
    category3_daily_df = output_groupby_df(category3_before_process_df, ['room','Date'],
     ['impression','cost','click','conversions','ads value','saleuser','sale','GMV','UV','AddtoCart'], 'sum').reset_index()
    category3_daily_df['Date'] = category3_daily_df['Date'].dt.strftime('%Y-%m-%d')
    # 添加常用指标
    category3_daily_df = add_custom_proportion_to_df(category3_daily_df,'GMV','cost','神策ROI')
    category3_daily_df= add_custom_proportion_to_df(category3_daily_df,'ads value','cost','ads ROI')
    category3_daily_df = add_custom_proportion_to_df(category3_daily_df,'cost','click','CPC')
    category3_daily_df = add_custom_proportion_to_df_x100(category3_daily_df,'click','impression','CTR')
    category3_daily_df= add_custom_proportion_to_df_x100(category3_daily_df,'sale','UV','神策转化率')
    category3_daily_df = add_custom_proportion_to_df_x100(category3_daily_df,'AddtoCart','UV','神策加购率')
    category3_daily_df.sort_values(by=['room', 'Date'], ascending=[True, True], inplace=True)
    category3_list_df = output_groupby_df(category3_daily_df, ['room'],
    ['Date','impression','cost','click','conversions','ads value','saleuser','sale','GMV','UV','AddtoCart','神策ROI','ads ROI','CPC','CTR','神策转化率','神策加购率'], list).reset_index()
    # 添加总和列,直接沿用list_df的groupby-list
    category3_list_df = add_groupby_sum_columns_to_list_df(category3_daily_df,category3_list_df ,['room'],'cost','cost_sum')
    category3_list_df = add_groupby_sum_columns_to_list_df(category3_daily_df,category3_list_df ,['room'],'GMV','gmv_sum')
    category3_list_df = add_groupby_sum_columns_to_list_df(category3_daily_df,category3_list_df ,['room'],'ads value','ads_value_sum')
    category3_list_df = add_custom_proportion_to_df(category3_list_df,'gmv_sum','cost_sum','神策总ROI').round(2)
    category3_list_df = add_custom_proportion_to_df(category3_list_df,'ads_value_sum','cost_sum','ads总ROI').round(2)
    # 列格式指定
    category3_list_column_config = create_dynamic_column_setting(category3_list_df,['room','Date'],
    [''], ['cost_sum', 'gmv_sum','ads_value_sum','神策总ROI','ads总ROI'], [''], [''],None,None)
    st.subheader('美国趋势数据')
    category3_trend_options = st.multiselect(
    '选择三级类目趋势维度',
    category3_list_df.columns,
    ['room', 'cost_sum', 'gmv_sum', '神策总ROI', 'ads总ROI', 'impression', 'CPC', 'cost', 'GMV']
    )
    st.dataframe(category3_list_df[category3_trend_options].set_index('room'),
                 column_config=category3_list_column_config,
                 width = 1600, height = 400)
    # ---------------------------------------------------------------------汇总数据表结束---------------------------------------------------------------------------------------------------
    # ---------------------------------------------------------------------占比数据表开始---------------------------------------------------------------------------------------------------

    # 创建占比基础数据df
    category3_sum_df = output_groupby_df(category3_before_process_df, ['Date'],
                ['impression','cost','click','conversions','ads value','saleuser','sale','GMV','UV','AddtoCart'], 'sum').reset_index()
    category3_sum_df['Date'] = category3_sum_df['Date'].dt.strftime('%Y-%m-%d')
    category3_sum_df = category3_sum_df.rename(columns={'impression':'sum_impression','cost':'sum_cost','click':'sum_click','conversions':'sum_conversions','ads value':'sum_ads_value'
    ,'GMV':'sum_GMV','sale':'sum_sale','saleuser':'sum_saleuser','UV':'sum_UV','AddtoCart':'sum_AddtoCart'})

    category3_proportion_df = pd.merge(category3_daily_df,category3_sum_df[['Date','sum_impression','sum_cost','sum_click','sum_conversions','sum_ads_value','sum_GMV',
    'sum_sale','sum_saleuser','sum_UV','sum_AddtoCart']],on=['Date'],how='left')
    category3_proportion_df = add_custom_proportion_to_df_x100(category3_proportion_df,'impression','sum_impression','impression占比')
    category3_proportion_df = add_custom_proportion_to_df_x100(category3_proportion_df,'cost','sum_cost','cost占比')
    category3_proportion_df = add_custom_proportion_to_df_x100(category3_proportion_df,'click','sum_click','click占比')
    category3_proportion_df = add_custom_proportion_to_df_x100(category3_proportion_df,'ads value','sum_ads_value','adsvalue占比')
    category3_proportion_df = add_custom_proportion_to_df_x100(category3_proportion_df,'conversions','sum_conversions','conversion占比')
    category3_proportion_df = add_custom_proportion_to_df_x100(category3_proportion_df,'GMV','sum_GMV','GMV占比')
    category3_proportion_df = add_custom_proportion_to_df_x100(category3_proportion_df,'sale','sum_sale','销量占比')
    category3_proportion_df = category3_proportion_df[['room','Date','impression','cost','click','ads value','conversions','GMV','impression占比','cost占比','click占比','adsvalue占比','conversion占比','GMV占比','销量占比']]

    category3_proportion_list_df = output_groupby_df(category3_proportion_df, ['room'],
    ['Date','impression','cost','click','ads value','conversions','GMV','impression占比','cost占比','click占比','adsvalue占比','conversion占比','GMV占比','销量占比'], list).reset_index()
    category3_proportion_list_df = add_groupby_sum_columns_to_list_df(category3_daily_df,category3_proportion_list_df,['room'],'cost','cost_sum')
    category3_proportion_list_df = add_groupby_sum_columns_to_list_df(category3_daily_df,category3_proportion_list_df ,['room'],'GMV','gmv_sum')
    category3_proportion_list_df = add_groupby_sum_columns_to_list_df(category3_daily_df,category3_proportion_list_df ,['room'],'ads value','ads_value_sum')
    category3_proportion_list_df = add_custom_proportion_to_df(category3_proportion_list_df,'gmv_sum','cost_sum','神策总ROI').round(2)
    category3_proportion_list_df = add_custom_proportion_to_df(category3_proportion_list_df,'ads_value_sum','cost_sum','ads总ROI').round(2)
    category3_proportion_list_df = category3_proportion_list_df[['room','cost_sum', 'gmv_sum','ads_value_sum','神策总ROI','ads总ROI','Date','impression占比','cost占比','click占比','adsvalue占比','conversion占比','GMV占比','销量占比']]
    # 列格式指定
    category3_proportion_list_column_config = create_dynamic_column_setting(category3_proportion_list_df,['room','Date'],
    [''], ['cost_sum', 'gmv_sum','ads_value_sum','神策总ROI','ads总ROI'], [''], [''],0,15)
    st.subheader('占比数据')
    category3_proportion_list_options = st.multiselect(
    '选择三级类目占比数据维度',
    category3_proportion_list_df.columns,
    ['room', 'cost_sum', 'gmv_sum','impression占比','cost占比','click占比','adsvalue占比','conversion占比','GMV占比']
    )
    st.dataframe(category3_proportion_list_df[category3_proportion_list_options].set_index('room')
                 ,column_config=category3_proportion_list_column_config
                 ,width = 1600, height = 400)
    # ---------------------------------------------------------------------占比数据表结束---------------------------------------------------------------------------------------------------
    def compare_summary_df_output(summary_df,compare_summary_df,select_column):
        summary_df = output_groupby_df(summary_df,['日期范围'],
        ['impression', 'cost', 'click', 'conversions', 'ads value', 'GMV', 'UV', 'AddtoCart','saleuser', 'sale'], 'sum').reset_index()
        summary_df = add_custom_proportion_to_df(summary_df, 'GMV', 'cost', '神策ROI')
        summary_df = add_custom_proportion_to_df(summary_df, 'ads value', 'cost', 'ads ROI')
        summary_df = add_custom_proportion_to_df(summary_df, 'cost', 'conversions', 'ads CPA')
        summary_df = add_custom_proportion_to_df(summary_df, 'cost', 'click', 'CPC')
        summary_df = add_custom_proportion_to_df(summary_df, 'click', 'impression', 'CTR')
        summary_df = add_custom_proportion_to_df(summary_df, 'sale', 'UV', '神策转化率')
        summary_df = add_custom_proportion_to_df(summary_df, 'AddtoCart', 'UV', '神策加购率')
        summary_df = add_custom_proportion_to_df(summary_df, 'GMV', 'saleuser', '客单价')
        compare_summary_df = output_groupby_df(compare_summary_df,['日期范围'],
        ['impression', 'cost', 'click', 'conversions', 'ads value', 'GMV', 'UV', 'AddtoCart','saleuser', 'sale'], 'sum').reset_index()
        compare_summary_df = add_custom_proportion_to_df(compare_summary_df, 'GMV', 'cost', '神策ROI')
        compare_summary_df = add_custom_proportion_to_df(compare_summary_df, 'ads value', 'cost', 'ads ROI')
        compare_summary_df = add_custom_proportion_to_df(compare_summary_df, 'cost', 'conversions', 'ads CPA')
        compare_summary_df = add_custom_proportion_to_df(compare_summary_df, 'cost', 'click', 'CPC')
        compare_summary_df = add_custom_proportion_to_df(compare_summary_df, 'click', 'impression', 'CTR')
        compare_summary_df = add_custom_proportion_to_df(compare_summary_df, 'sale', 'UV', '神策转化率')
        compare_summary_df = add_custom_proportion_to_df(compare_summary_df, 'AddtoCart', 'UV', '神策加购率')
        compare_summary_df = add_custom_proportion_to_df(compare_summary_df, 'GMV', 'saleuser', '客单价')
        combined_df = create_compare_summary_df(summary_df,compare_summary_df,select_column)
        formatted_df = combined_df.head(2).copy()
        formatted_df[['sale', 'saleuser', 'UV', 'AddtoCart', 'impression','click']] = formatted_df[['sale', 'saleuser', 'UV', 'AddtoCart', 'impression','click']].astype(int)
        for column in formatted_df.head():
            format_string = '{:.2f}' if column in ['cost', 'GMV', 'ads value', 'CPC', 'conversions','ads ROI','神策ROI','ads CPA','客单价'] else '{}'
            format_string = '{:.2%}' if column in ['CTR', '神策转化率', '神策加购率'] else format_string
            formatted_df[column] = formatted_df[column].apply(format_first_two_rows, args=(format_string,))
        compare_data_df = combined_df.iloc[2:3].copy()
        compare_data_df[compare_data_df.columns[1:]] = compare_data_df[compare_data_df.columns[1:]].apply(pd.to_numeric,errors='coerce')
        combined_df.update(formatted_df)
        combined_df.update(compare_data_df)
        summary_options = st.multiselect(
            '选择汇总数据维度',
            combined_df.columns,
            ['日期范围', 'cost', 'click', 'GMV', 'ads value', 'CPC', 'conversions']
        )
        combined_df = combined_df[summary_options]
        combined_df = combined_df.apply(format_comparison, axis=1)
        combined_df = combined_df.style.apply(colorize_comparison, axis=1)
        st.subheader('对比数据')
        st.dataframe(combined_df,
                     width=1600, height=200)

    st.subheader('对比数据')
    unique_category_3 = compare_ads_daily_filtered_date_range_df['room'].unique()
    category3_options = st.multiselect(
    '选择三级类目',
    unique_category_3
    )
    # 汇总神策SKU数据
    compare_sensor_summary_df = output_groupby_df(compare_seonsor_daily_filtered_date_range_df, ['SKU','Date','日期范围'], ['saleuser','sale','GMV','AddtoCart','UV'], 'sum').reset_index()
    #  合并ads和神策数据
    compare_category3_before_process_df = pd.merge(compare_ads_daily_filtered_date_range_df,compare_sensor_summary_df[['SKU', 'Date', '日期范围','GMV', 'UV', 'AddtoCart', 'saleuser', 'sale']],
                                           on=['SKU', 'Date','日期范围'], how='left')
    # 汇总合并三级去日期数据
    compare_category3_origin_summary_df = output_groupby_df(compare_category3_before_process_df, ['room','日期范围'],
                ['impression','cost','click','conversions','ads value','saleuser','sale','GMV','UV','AddtoCart'], 'sum').reset_index()
    category3_origin_summary_df = output_groupby_df(category3_before_process_df, ['room','日期范围'],
                ['impression','cost','click','conversions','ads value','saleuser','sale','GMV','UV','AddtoCart'], 'sum').reset_index()
    if category3_options:
        category3_origin_summary_df = category3_origin_summary_df[category3_origin_summary_df['room'].isin(category3_options)].drop(columns=['room'])
        compare_category3_origin_summary_df = compare_category3_origin_summary_df[compare_category3_origin_summary_df['room'].isin(category3_options)].drop(columns=['room'])

        compare_summary_df_output(category3_origin_summary_df, compare_category3_origin_summary_df,['日期范围', 'impression', 'cost', 'click', 'conversions', 'ads value', 'GMV', 'UV',
        'AddtoCart', 'saleuser', 'sale', '神策ROI', 'ads ROI', 'ads CPA', 'CPC', 'CTR', '神策转化率','神策加购率','客单价'])
