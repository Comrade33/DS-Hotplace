import streamlit as st
import streamlit.components.v1 as components
import plotly.express as px
from datetime import datetime, date
import requests
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import geopy
from geopy.geocoders import Nominatim
import folium
from folium import plugins
import time

###############################################################################
st.set_page_config(layout="wide")
###############################################################################

@st.cache_data
def read_data(file_path):
    df = pd.read_excel(file_path, sheet_name='data')
    
    df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
    df['Day_of_Week'] = df['date'].dt.day_name()
    day_of_week_labels = {
    'Monday': '월요일',
    'Tuesday': '화요일',
    'Wednesday': '수요일',
    'Thursday': '목요일',
    'Friday': '금요일',
    'Saturday': '토요일',
    'Sunday': '일요일'
    }
    df['Day_of_Week'] = df['Day_of_Week'].map(day_of_week_labels)

    day_mapping = {
    '월요일': 1,
    '화요일': 2,
    '수요일': 3,
    '목요일': 4,
    '금요일': 5,
    '토요일': 6,
    '일요일': 7
    }
    df['Day_of_Week_Num'] = df['Day_of_Week'].map(day_mapping)

    # time 시간대 변경
    def convert_time(time_str):
        time_str = time_str.zfill(4)
        hour = int(time_str[:2])
        minute = int(time_str[2:])
        return f"{hour}:{minute:02d}"

    df['time'] = df['time'].astype(str)
    df['time'] = df['time'].apply(convert_time)

    sex_mapping = {'Male': '남자', 'Female': '여자'}
    df['sex'] = df['sex'].map(sex_mapping)

# type 라벨 변경 필요
    type_mapping = { 1:'수원 행리단길', 2: '경주 황리단길', 3: '부산 해리단길', 4: '서울 망리단길', 5:'서울 서울숲길' }
    df['TYPE'] = df['TYPE'].map(type_mapping)

    return df

@st.cache_data
def load_all_data(file_urls):
    all_data = []
    for file_url in file_urls:
        df = read_data(file_url)
        all_data.append(df)
    return pd.concat(all_data, ignore_index=True)

# 데이터 업데이트 필요
file_urls = [
    'https://github.com/Comrade33/DS-Hotplace/raw/main/total_data_1.xlsx',
    'https://github.com/Comrade33/DS-Hotplace/raw/main/total_data_2.xlsx',
    'https://github.com/Comrade33/DS-Hotplace/raw/main/total_data_3.xlsx',
    'https://github.com/Comrade33/DS-Hotplace/raw/main/total_data_4.xlsx',
    'https://github.com/Comrade33/DS-Hotplace/raw/main/total_data_5.xlsx'
]

df = load_all_data(file_urls)

# age 60대까지만 불러오기
df = df[df['age'].isin(['10대', '20대', '30대', '40대', '50대', '60대'])]

###############################################################################
plt.rcParams['font.family'] = 'NanumGothic'
plt.rcParams['axes.unicode_minus'] = False
###############################################################################
# 제목
st.markdown("<h1 style='text-align: center;'>유동인구 분석</h1>", unsafe_allow_html=True)
#st.caption('유동인구 대시보드')
###############################################################################

# 분석 날짜 선택
#st.sidebar.header('분석 날짜 선택')
#options = ['선택해주세요'] + sorted(df['date'].astype(str).unique())
#start_date = st.sidebar.selectbox('시작 날짜를 선택해주세요.', options, key='selectbox0_1')
#end_date = st.sidebar.selectbox('종료 날짜를 선택해주세요.', options, key='selectbox0_2')

#if (start_date != '선택해주세요') and (end_date != '선택해주세요'):
#    start_date = datetime.strptime(start_date, '%Y-%m-%d')
#    end_date = datetime.strptime(end_date, '%Y-%m-%d')
#    if start_date > end_date:
#        st.sidebar.error('종료 날짜는 시작 날짜 이후여야 합니다.')
#else:
#    start_date = None
#    end_date = None

###############################################################################

st.sidebar.header('분석 날짜 선택')
start_date = st.sidebar.date_input('시작 날짜를 선택해주세요.', key='date_input0_1')
end_date = st.sidebar.date_input('종료 날짜를 선택해주세요.', key='date_input0_2')

start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

if start_date and end_date:
    if start_date > end_date:
        st.sidebar.error('종료 날짜는 시작 날짜 이후여야 합니다.')
    else:
        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

df_w1 = df[df['Day_of_Week_Num'].between(1, 4)]
df_w2 = df[df['Day_of_Week_Num'].between(5, 7)]

if start_date == datetime.today().date() and end_date == datetime.today().date():
    start_date = None
    end_date = None

###############################################################################
# 사이드바
options = ['선택해주세요', '전체(지역 선택 안함)'] + list(df['TYPE'].unique())
selected_category = st.sidebar.selectbox('분석할 지역을 선택해주세요.', options, key='selectbox_category')
###############################################################################
#kosis 주민등록인구수 업데이트
#url = f'https://kosis.kr/openapi/Param/statisticsParameterData.do?method=getList&apiKey={API_KEY}&itmId=T2+&objL1=00+11+11110+11140+11170+11200+11215+11230+11260+11290+11305+11320+11350+11380+11410+11440+11470+11500+11530+11545+11560+11590+11620+11650+11680+11710+11740+26+26110+26140+26170+26200+26230+26260+26290+26320+26350+26380+26410+26440+26470+26500+26530+26710+27+27110+27140+27170+27200+27230+27260+27290+27710+27720+28+28110+28140+28170+28177+28185+28200+28237+28245+28260+28710+28720+29+29110+29140+29155+29170+29200+30+30110+30140+30170+30200+30230+31+31110+31140+31170+31200+31710+36+36110+41+41105+41110+41130+41150+41170+41190+41210+41220+41250+41270+41280+41290+41310+41360+41370+41390+41410+41430+41450+41460+41480+41500+41550+41570+41590+41610+41630+41650+41670+41730+41800+41820+41830+51+51105+51110+51130+51150+51170+51190+51210+51230+51720+51730+51750+51760+51770+51780+51790+51800+51810+51820+51830+43+43110+43130+43150+43710+43720+43730+43740+43745+43750+43760+43770+43800+44+44130+44150+44180+44200+44210+44230+44250+44270+44710+44730+44760+44770+44790+44800+44810+44825+44830+52+52110+52130+52140+52180+52190+52210+52710+52720+52730+52740+52750+52770+52790+52800+46+46110+46130+46150+46170+46230+46710+46720+46730+46770+46780+46790+46800+46810+46820+46830+46840+46860+46870+46880+46890+46900+46910+47+47110+47130+47150+47170+47190+47210+47230+47250+47280+47290+47720+47730+47750+47760+47770+47820+47830+47840+47850+47900+47920+47930+47940+48+48120+48170+48220+48240+48250+48270+48310+48330+48720+48730+48740+48820+48840+48850+48860+48870+48880+48890+50+50110+50130+&objL2=0+&objL3=&objL4=&objL5=&objL6=&objL7=&objL8=&format=json&jsonVD=Y&prdSe=M&startPrdDe={st_date}&endPrdDe={ed_date}&orgId=101&tblId=DT_1B04005N'

# 데이터 업데이트
API_KEY = 'MzI2MTk5ZTM3ZDEyZWVmMjNjYjBjOTVjY2EwNzVlMTA='
st_date = '202405'
ed_date = '202409'
ara='1120066000+1144069000+2635051000+4111574000+4713057000'

url = f'https://kosis.kr/openapi/Param/statisticsParameterData.do?method=getList&apiKey=MzI2MTk5ZTM3ZDEyZWVmMjNjYjBjOTVjY2EwNzVlMTA=&itmId=T2+&objL1=1120066000+1144069000+2635051000+4111574000+4713057000+&objL2=0+&objL3=&objL4=&objL5=&objL6=&objL7=&objL8=&format=json&jsonVD=Y&prdSe=M&startPrdDe=202405&endPrdDe=202409&orgId=101&tblId=DT_1B04005N'

response = requests.get(url, timeout=30)

if response.status_code == 200:
    resident_data = response.json()
    resident_df = pd.DataFrame(resident_data, columns=['PRD_DE', 'DT', 'C1', 'C1_NM'])
    resident_df = resident_df.rename(columns={'C1_NM': 'TYPE'})
else:
    print(f"Error: {response.status_code}")

# 지역 매핑 업데이트
location_dict = {
        '수원 행리단길': '행궁동',
        '경주 황리단길': '황남동',
        '부산 해리단길': '우제1동',
        '서울 망리단길': '망원제1동',
        '서울 서울숲길': '성수1가제2동'
    }


# 전체 주민등록인구수(api)
def population_all(resident_df, selected_category, start_date, end_date, location_dict):
    if selected_category == '전체(지역 선택 안함)':
        start_date = pd.to_datetime(start_date).strftime('%Y-%m')
        end_date = pd.to_datetime(end_date).strftime('%Y-%m')
        resident_df['PRD_DE'] = pd.to_datetime(resident_df['PRD_DE'], format='%Y%m')
        resident_population = resident_df[(resident_df['PRD_DE'] >= start_date) & (resident_df['PRD_DE'] <= end_date)]
        resident_population = resident_population[resident_population['TYPE'].isin(location_dict.values())]
        resident_population_sum = resident_population.groupby('TYPE')['DT'].sum().reset_index()
        resident_population_sum.columns = ['TYPE', 'sum_DT']
        resident_population_sum['TYPE'] = resident_population_sum['TYPE'].map({v: k for k, v in location_dict.items()})
        
        return resident_population_sum

# 세부 지역 주민등록인구수(api)
def population(resident_df, selected_category, start_date, end_date, location_dict):
    if selected_category != '선택해주세요' and selected_category != '전체(지역 선택 안함)':
        start_date = pd.to_datetime(start_date).strftime('%Y-%m')
        end_date = pd.to_datetime(end_date).strftime('%Y-%m')
        selected_location = location_dict.get(selected_category)
        resident_df_final = resident_df[resident_df['TYPE'] == selected_location].copy()
        resident_df_final['TYPE'] = selected_category
        resident_df_final['PRD_DE'] = pd.to_datetime(resident_df_final['PRD_DE'], format='%Y%m')
        resident_population = resident_df_final[(resident_df_final['PRD_DE'] >= start_date) & (resident_df_final['PRD_DE'] <= end_date)]
        resident_population_sum = resident_population.groupby('TYPE')['DT'].sum().reset_index()
        resident_population_sum.columns = ['TYPE', 'sum_DT']
        resident_sum_dt = resident_population_sum[resident_population_sum['TYPE'] == selected_category]['sum_DT']

        return resident_sum_dt

###############################################################################

if selected_category == '전체(지역 선택 안함)':
    filtered_df = df

    type_grouped = filtered_df.groupby('TYPE')['count'].sum().reset_index()
    type_grouped['sum_count'] = type_grouped['count']
    population_all_df = population_all(resident_df, selected_category, start_date, end_date, location_dict)
    type_grouped = pd.merge(type_grouped, population_all_df, on='TYPE', how='left')

    fig0 = go.Figure()

    st.header('1. 주민등록인구수 및 유동인구수 비교')
    fig0.add_trace(go.Bar(
        x=type_grouped['TYPE'],
        y=type_grouped['sum_count'],
        name='유동인구수',
        marker_color='rgb(0, 0, 139)',
        marker_line_width=0
    ))
    fig0.add_trace(go.Scatter(
        x=type_grouped['TYPE'],
        y=type_grouped['sum_DT'],
        name='주민등록인구수',
        mode='lines+markers',
        line=dict(color='rgb(144, 238, 144)', width=2),
        marker=dict(size=6)
    ))
    fig0.update_traces(
        hovertemplate='지역: %{x}<br>유동인구수 합계: %{y:,}<extra></extra>',
        selector=dict(type='bar'))
    fig0.update_traces(
        hovertemplate='지역: %{x}<br>주민등록인구수 합계: %{y:,}<extra></extra>',
        selector=dict(type='scatter'))

    fig0.update_layout(
        width=900,
        height=500,
        title_text=f"<span style='color:blue; font-weight:bold'>지역별</span> 주민등록인구수 및 유동인구수",
        xaxis=dict(
            tickangle=0,
            tickfont=dict(size=10),
            title='지역'),
        yaxis=dict(
            tickformat=',',
            showticklabels=True,
            title='인구수 합계'))
    st.plotly_chart(fig0)
    
    # OSM을 사용하는 Nominatim 지오코더
    geolocator = Nominatim(user_agent="ggeopy_app")

#위치와 주소 매핑 필요
    location_names = {
        '수원 행리단길': "경기 수원시 팔달구 화서문로 43",
        '경주 황리단길': "경북 경주시 포석로 1080",
        '부산 해리단길': "부산 해운대구 우동 510-7",
        '서울 망리단길': "서울 마포구 망원동 403-7",
        '서울 서울숲길': "서울 성동구 성수동1가"
    }

    type_population = filtered_df.groupby('TYPE')['count'].sum().to_dict()

    locations = []
    for name, address in location_names.items():
        try:
            location = geolocator.geocode(address, timeout=10)
            if location:
                #st.write(f"{name} - 주소: {location.address}, 위도: {location.latitude}, 경도: {location.longitude}")
                locations.append({
                    "name": name,
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "population": type_population.get(name, 0)
                })
            else:
                st.write(f"위치 '{address}'에 대한 결과를 찾을 수 없습니다.")
        except Exception as e:
            st.write(f"Nominatim 요청 중 오류 발생: {e}")

    # Folium 지도 생성
    if locations:
        m = folium.Map(location=[locations[0]["latitude"], locations[0]["longitude"]], zoom_start=7)

        heat_data = []
        for loc in locations:
            popup_text = f"<b>지역:</b> {loc['name']}<br><b>유동인구수 합계:</b> {loc['population']:,}명"
            folium.Marker(
                location=[loc["latitude"], loc["longitude"]],
                popup=folium.Popup(popup_text, max_width=250)
            ).add_to(m)
            heat_data.append([loc["latitude"], loc["longitude"], loc["population"]])
        m.add_child(plugins.HeatMap(heat_data))

        m.save("map.html")
        with open("map.html", "r", encoding="utf-8") as f:
            html_data = f.read()
        st.components.v1.html(html_data, height=500)
    else:
        st.write("위치 정보를 다시 확인해주세요.")
        
##################################################################################################        
if selected_category not in ['선택해주세요', '전체(지역 선택 안함)']:
    filtered_df = df[df['TYPE'] == selected_category]
    if start_date and end_date:
        filtered_df = filtered_df[(filtered_df['date'] >= pd.to_datetime(start_date)) & (filtered_df['date'] <= pd.to_datetime(end_date))]
##################################################################################################        

    # 주민등록인구수 및 유동인구수 비교 그래프
    st.header('1. 주민등록인구수 및 유동인구수 비교')
    floating_population = filtered_df['count'].sum()
    
    population_data = int(population(resident_df, selected_category, start_date, end_date, location_dict).iloc[0])
    population_df = pd.DataFrame({
        '인구 유형': ['유동인구수', '주민등록인구수'],
        '인구 수': [floating_population, population_data]})

    col1, col2 = st.columns(2)
    with col1:
        box_style = """
            <style>
            .box {
                display: flex;
                justify-content: space-between;
                align-items: center;
                width: 100%;
                height: 100px;
                border: 2px solid black;
                margin: 20px 0;
                padding: 10px;
                font-weight: bold;
                font-size: 24px;
                box-sizing: border-box;}
            .box span {
                flex: 1;}
            .box span:last-child {
                text-align: right;}
            </style>"""
        st.markdown(box_style, unsafe_allow_html=True)
        st.markdown(f"<div class='box'><span>주민등록인구수</span><span>{population_data:,}명</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='box'><span>유동인구수</span><span>{floating_population:,}명</span></div>", unsafe_allow_html=True)
    with col2:
        fig = px.bar(
            population_df,
            x='인구 수',
            y='인구 유형',
            orientation='h',
            text='인구 수',
            labels={'인구 수': '인구수 합계'},)
        fig.update_traces(
            texttemplate='%{text:,}',
            textposition='auto',
            hovertemplate='인구수 합계: %{x:,}<extra></extra>',
            marker_color='navy',)
        fig.update_layout(
            xaxis_title=None,
            yaxis_title=None,
            xaxis_showgrid=False,
            yaxis_showgrid=False,
            xaxis_visible=False,
            yaxis_visible=True,
            plot_bgcolor='white',
            height=310,
            width=400,
            margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    ###############################################################################

# 기본 응답자 정보 - 첫번째 열
    st.header('2. 기본 응답자 정보')

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        color_map = {'남자': '#4776b4', '여자': '#800000'}
        fig1 = px.pie(
            filtered_df,
            names='sex',
            values='count',
            title=f"<span style='color:blue; font-weight:bold'>{selected_category}</span>의 유동인구 남녀비율",
            color='sex',
            color_discrete_map=color_map,
            width=300, height=300,
            hole=0.4)
        fig1.update_traces(
            textposition='inside',
            textinfo='percent',
            insidetextfont=dict(size=12),
            hovertemplate='성별=%{label}<br>유동인구수 합계=%{value:,}<extra></extra>')
        fig1.update_layout(
            plot_bgcolor='rgba(245, 245, 245, 0.5)',
            paper_bgcolor='rgba(245, 245, 245, 0.5)')
        st.plotly_chart(fig1)

    with col2:
        age_grouped = filtered_df.groupby('age')['count'].sum().reset_index()
        age_grouped['sum_count'] = age_grouped['count']

        fig2_1 = go.Figure(go.Bar(
            x=age_grouped['age'],
            y=age_grouped['sum_count'],
            name='연령대(10세 단위)',
            marker_color='rgb(0, 0, 139)',
            marker_line_width=0))

        fig2_1.update_traces(
            hovertemplate='연령대: %{x}<br>유동인구수 합계: %{y:,}<extra></extra>')

        fig2_1.update_layout(
            width=300, height=300,
            title_text=f"<span style='color:blue; font-weight:bold'>{selected_category}</span>의 유동인구 연령대비율",
            xaxis=dict(tickangle=0, tickfont=dict(size=10), title='연령대'),
            yaxis=dict(tickformat=',', showticklabels=False, title=None),
            plot_bgcolor='rgba(245, 245, 245, 0.5)',
            paper_bgcolor='rgba(245, 245, 245, 0.5)')
        st.plotly_chart(fig2_1)

    with col3:
        pyramid_data = filtered_df.groupby(['age', 'sex'])['count'].sum().unstack().fillna(0)
        pyramid_data['female'] = -pyramid_data.get('여자', 0)
        pyramid_data['male'] = pyramid_data.get('남자', 0)
        pyramid_data = pyramid_data.reset_index()

        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            y=pyramid_data['age'],
            x=pyramid_data['male'],
            name='남자',
            orientation='h',
            marker=dict(color='#4776b4'),
            text=pyramid_data['male'],
            textposition='auto',
            hovertemplate='남자 %{y}<br>유동인구수 합계: %{x:,}<extra></extra>'))
        fig3.add_trace(go.Bar(
            y=pyramid_data['age'],
            x=pyramid_data['female'],
            name='여자',
            orientation='h',
            marker=dict(color='#800000'),
            text=abs(pyramid_data['female']),
            textposition='auto',
            hovertemplate='여자 %{y}<br>유동인구수 합계: %{text:,}<extra></extra>'))
        fig3.update_layout(
            title=f"<span style='color:blue; font-weight:bold'>{selected_category}</span>의 성별/연령대별 피라미드",
            barmode='overlay',
            xaxis=dict(showticklabels=False, title=None),
            yaxis=dict(title=None),
            plot_bgcolor='rgba(245, 245, 245, 0.5)',
            paper_bgcolor='rgba(245, 245, 245, 0.5)',
            height=300,
            width=300)
        st.plotly_chart(fig3)

# 기본 응답자 정보 - 두번째 열
    col_left, col3, col4, col_right = st.columns([1, 2, 2, 1])

    with col3:
        filtered_df3_1 = filtered_df
        filtered_df3_1['time'] = pd.to_datetime(filtered_df3_1['time'], format='%H:%M')
        time_grouped = filtered_df3_1.groupby(filtered_df3_1['time'].dt.floor('30T'))['count'].sum().reset_index()
        time_grouped['time'] = time_grouped['time'].dt.strftime('%H:%M')
        time_grouped['sum_count'] = time_grouped['count']

        tickvals = [i for i in range(len(time_grouped['time'])) if i % 6 == 0]  # 3시간 단위
        ticktext = [time_grouped['time'][i] for i in tickvals]
        fig3 = px.bar(
            time_grouped,
            x='time',
            y='sum_count',
            title=f"<span style='color:blue; font-weight:bold'>{selected_category}</span> 시간대별 유동인구수",
            hover_data={'sum_count': ':,'})
        fig3.update_traces(
            hovertemplate='시간: %{x}<br>유동인구수 합계: %{y:,}<extra></extra>',
            marker_color='rgb(0, 0, 139)',
            marker_line_width=0)
        fig3.update_layout(
            xaxis=dict(title='시간대', tickvals=tickvals, ticktext=ticktext, tickangle=0, tickfont=dict(size=10)),
            yaxis=dict(tickformat=',', showticklabels=False, title=None),
            width=300, height=300,
            plot_bgcolor='rgba(245, 245, 245, 0.5)',
            paper_bgcolor='rgba(245, 245, 245, 0.5)')
        st.plotly_chart(fig3)

    with col4:
        filtered_df3_2 = filtered_df3_1
        day_grouped = filtered_df3_2.groupby(['Day_of_Week', 'Day_of_Week_Num'])['count'].sum().reset_index()
        day_grouped['sum_count'] = day_grouped['count']

        fig4 = px.bar(
            day_grouped,
            x='Day_of_Week',
            y='sum_count',
            title=f"<span style='color:blue; font-weight:bold'>{selected_category}</span> 요일별 유동인구수",
            hover_data={'sum_count': ':,'})
        fig4.update_traces(
            hovertemplate='요일: %{x}<br>유동인구수 합계: %{y:,}<extra></extra>',
            marker_color='rgb(0, 0, 139)',
            marker_line_width=0)
        fig4.update_layout(
            xaxis_title='요일',
            xaxis_tickangle=0,
            xaxis_tickfont=dict(size=10),
            yaxis=dict(tickformat=',', showticklabels=False, title=None),
            xaxis=dict(categoryorder='array', categoryarray=['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']),
            width=300, height=300,
            plot_bgcolor='rgba(245, 245, 245, 0.5)',
            paper_bgcolor='rgba(245, 245, 245, 0.5)')
        st.plotly_chart(fig4)

###############################################################################

# 주중(월-목) vs 주말(금-일) 유동인구 분석 그래프 전처리

df_w1['기간'] = '주중(월~목)'
df_w2['기간'] = '주말(금~일)'
df['기간'] = '전체'
df_combined = pd.concat([df, df_w1, df_w2], ignore_index=True)

def plot_combined_age_chart(data, title, width, height):
    age_grouped = data.groupby(['age', '기간'])['count'].sum().reset_index()
    age_grouped.rename(columns={'count': 'sum_count'}, inplace=True)
    
    fig = px.bar(
        age_grouped,
        x='age',
        y='sum_count',
        color='기간',
        category_orders={'기간': ['전체', '주중(월~목)', '주말(금~일)']},
        barmode='group',
        title=title,
        width=width,
        height=height,
        color_discrete_map={'전체': '#1f77b4', '주중(월~목)': '#007bff', '주말(금~일)': '#ffa500'})
    fig.update_traces(
        texttemplate='',  # 라벨 제거
        hovertemplate='연령대=%{x}<br>유동인구수 합계=%{y:,}<extra></extra>')
    fig.update_layout(
        yaxis=dict(tickformat=',', title='', showticklabels=False),
        xaxis=dict(title='연령대'),
        showlegend=True)
    return fig

def plot_stacked_time_chart(data, title, width, height):
    time_grouped = data.groupby(['time', '기간'])['count'].sum().reset_index()
    time_grouped.rename(columns={'count': 'sum_count'}, inplace=True)
    
    # 3시간 단위
    three_hour_intervals = sorted(set([time for time in time_grouped['time'] if time.endswith(('00:00', '03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00'))]))
    
    fig = px.bar(
        time_grouped,
        x='time',
        y='sum_count',
        color='기간',
        category_orders={'기간': ['전체', '주중(월~목)', '주말(금~일)']},
        barmode='stack',
        title=title,
        width=width,
        height=height,
        color_discrete_map={'전체': '#1f77b4', '주중(월~목)': '#007bff', '주말(금~일)': '#ffa500'})
    fig.update_traces(
        texttemplate='',
        hovertemplate='시간=%{x}<br>유동인구수 합계=%{y:,}<extra></extra>')
    fig.update_layout(
        yaxis=dict(tickformat=',', title='', showticklabels=False),
        xaxis=dict(
            title='시간대', 
            tickvals=three_hour_intervals,
            ticktext=three_hour_intervals,
            tickangle=0),
        showlegend=True)
    return fig

# 주중(월-목) vs 주말(금-일) 유동인구 분석 그래프

if (selected_category not in ['선택해주세요', '전체(지역 선택 안함)']) and (not df_w1.empty):
    filtered_df_w1 = df_w1[df_w1['TYPE'] == selected_category]
    st.header('3. 주중(월-목) vs 주말(금-일) 유동인구 분석')

    col1, col2, col3 = st.columns(3)
    with col1:
        color_map = {'남자': '#4776b4', '여자': '#800000'}
        fig1 = px.pie(
            filtered_df_w1,
            names='sex',
            values='count',
            title=f"""<span style="color:blue; font-weight:bold">{selected_category}</span>의 유동인구 남녀비율<br>- 주중(월~목)""",
            color='sex',
            color_discrete_map=color_map,
            width=300, height=300,
            hole=0.4)
        fig1.update_traces(
            textposition='inside',
            textinfo='percent',
            insidetextfont=dict(size=12),
            hovertemplate='성별=%{label}<br>유동인구수 합계=%{value:,}<extra></extra>')
        fig1.update_layout(
            margin=dict(l=0, r=0, t=50, b=0),
            title=dict(y=0.9),
            showlegend=True)
        st.plotly_chart(fig1)

    with col2:
        filtered_df_w2 = df_w2[df_w2['TYPE'] == selected_category]
        fig4 = px.pie(
            filtered_df_w2,
            names='sex',
            values='count',
            title=f"""<span style="color:blue; font-weight:bold">{selected_category}</span>의 유동인구 남녀비율<br>- 주말(금~일)""",
            color='sex',
            color_discrete_map=color_map,
            width=300, height=300,
            hole=0.4)
        fig4.update_traces(
            textposition='inside',
            textinfo='percent',
            insidetextfont=dict(size=12),
            hovertemplate='성별=%{label}<br>유동인구수 합계=%{value:,}<extra></extra>')
        fig4.update_layout(
            margin=dict(l=0, r=0, t=50, b=0),
            title=dict(y=0.9),
            showlegend=True)
        st.plotly_chart(fig4)

    df['기간'] = '전체'
    filtered_df_w1 = df_w1[df_w1['TYPE'] == selected_category]
    filtered_df_w2 = df_w2[df_w2['TYPE'] == selected_category]
    filtered_df = df[df['TYPE'] == selected_category]

    combined_sex_grouped = pd.concat([filtered_df, filtered_df_w1, filtered_df_w2]).groupby(['sex', '기간'])['count'].sum().reset_index()

    with col3:
        color_map = {'전체': '#1f77b4', '주중(월~목)': '#007bff', '주말(금~일)': '#ffa500'}
        fig6 = px.bar(
            combined_sex_grouped,
            x='sex',
            y='count',
            color='기간',
            barmode='group',
            title=f"""<span style="color:blue; font-weight:bold">{selected_category}</span>의 성별 유동인구수<br>- (전체 vs 주중 vs 주말)""",
            color_discrete_map=color_map,
            category_orders={'기간': ['전체', '주중(월~목)', '주말(금~일)']},
            height=350,
            width=510)
        fig6.update_traces(
            hovertemplate='성별=%{x}<br>유동인구수 합계=%{y:,}<extra></extra>',
            marker_line_width=0)
        fig6.update_layout(
            margin=dict(l=20, r=40, t=50, b=0),
            title=dict(y=0.9),
            yaxis=dict(
                tickformat=',', 
                title=None, 
                showgrid=True,
                gridcolor='lightgray',
                zeroline=False,
                showticklabels=False),  
            xaxis=dict(
                title='성별',
                showticklabels=True, 
                showline=False,
                zeroline=False), 
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1))
        st.plotly_chart(fig6)

    col4, col5, col6 = st.columns(3)
    with col4:
        age_grouped_w1 = filtered_df_w1.groupby('age')['count'].sum().reset_index()
        age_grouped_w1['sum_count'] = age_grouped_w1['count']
        
        fig2_1 = go.Figure(go.Bar(
            x=age_grouped_w1['age'],
            y=age_grouped_w1['sum_count'],
            name='연령대(10세 단위)',
            marker_color='#007bff'))

        fig2_1.update_traces(
            hovertemplate='연령대: %{x}<br>유동인구수 합계: %{y:,}<extra></extra>')
        
        fig2_1.update_layout(
            width=350, height=350,
            title_text=f"""<span style="color:blue; font-weight:bold">{selected_category}</span>의 유동인구 연령대비율<br>- 주중(월~목)""",
            xaxis_title='연령대',
            yaxis=dict(tickformat=',', showticklabels=False),
            margin=dict(l=0, r=0, t=50, b=0))
        st.plotly_chart(fig2_1)

    with col5:
        age_grouped_w2 = filtered_df_w2.groupby('age')['count'].sum().reset_index()
        age_grouped_w2['sum_count'] = age_grouped_w2['count']
        
        fig2_2 = go.Figure(go.Bar(
            x=age_grouped_w2['age'],
            y=age_grouped_w2['sum_count'],
            name='연령대(10세 단위)',
            marker_color='#ffa500'))

        fig2_2.update_traces(
            hovertemplate='연령대: %{x}<br>유동인구수 합계: %{y:,}<extra></extra>')
        
        fig2_2.update_layout(
            width=350, height=350,
            title_text=f"""<span style="color:blue; font-weight:bold">{selected_category}</span>의 유동인구 연령대비율<br>- 주말(금~일)""",
            xaxis_title='연령대',
            yaxis=dict(tickformat=',', showticklabels=False),
            margin=dict(l=0, r=0, t=50, b=0))
        st.plotly_chart(fig2_2)

    with col6:
        filtered_df = df_combined[df_combined['TYPE'] == selected_category]
        fig_age = plot_combined_age_chart(filtered_df, f"""<span style="color:blue; font-weight:bold">{selected_category}</span>의 연령대별 유동인구수<br>- (전체 vs 주중 vs 주말)""", 500, 350)
        st.plotly_chart(fig_age)

    col7, col8, col9 = st.columns(3)
    with col7:
        filtered_df3_1_w1 = filtered_df_w1
        filtered_df3_1_w1['time'] = pd.to_datetime(filtered_df3_1_w1['time'], format='%H:%M')
        time_grouped_w1 = filtered_df3_1_w1.groupby('time')['count'].sum().reset_index()
        time_grouped_w1['time'] = time_grouped_w1['time'].dt.strftime('%H:%M')
        time_grouped_w1['sum_count'] = time_grouped_w1['count']
        
        # x축 라벨 3시간 단위
        three_hour_intervals = [time for time in time_grouped_w1['time'] if time.endswith(('00:00', '03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00'))]
        
        fig3_1 = px.bar(
            time_grouped_w1,
            x='time',
            y='sum_count',
            title=f"""<span style="color:blue; font-weight:bold">{selected_category}</span> 시간대별 유동인구수<br>- 주중(월~목)""",
            hover_data={'sum_count': ':,'})
        fig3_1.update_traces(
            hovertemplate='시간: %{x}<br>유동인구수 합계: %{y:,}<extra></extra>',
            marker_color='#007bff')
        fig3_1.update_layout(
            xaxis=dict(title='시간대', tickvals=three_hour_intervals, ticktext=three_hour_intervals, tickangle=0),
            yaxis=dict(showticklabels=False, title=''),
            width=350, height=350,
            margin=dict(l=0, r=0, t=50, b=0))
        st.plotly_chart(fig3_1)

    with col8:
        filtered_df3_1_w2 = filtered_df_w2
        filtered_df3_1_w2['time'] = pd.to_datetime(filtered_df3_1_w2['time'], format='%H:%M')
        time_grouped_w2 = filtered_df3_1_w2.groupby('time')['count'].sum().reset_index()
        time_grouped_w2['time'] = time_grouped_w2['time'].dt.strftime('%H:%M')
        time_grouped_w2['sum_count'] = time_grouped_w2['count']
        
        # x축 라벨 3시간 단위
        three_hour_intervals = [time for time in time_grouped_w2['time'] if time.endswith(('00:00', '03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00'))]
        
        fig3_2 = px.bar(
            time_grouped_w2,
            x='time',
            y='sum_count',
            title=f"""<span style="color:blue; font-weight:bold">{selected_category}</span> 시간대별 유동인구수<br>- 주말(금~일)""",
            hover_data={'sum_count': ':,'})
        fig3_2.update_traces(
            hovertemplate='시간: %{x}<br>유동인구수 합계: %{y:,}<extra></extra>',
            marker_color='#ffa500')
        fig3_2.update_layout(
            xaxis=dict(title='시간대', tickvals=three_hour_intervals, ticktext=three_hour_intervals, tickangle=0),
            yaxis=dict(showticklabels=False, title=''),
            width=350, height=350,
            margin=dict(l=0, r=0, t=50, b=0))
        st.plotly_chart(fig3_2)

    with col9:
        filtered_df['time'] = pd.to_datetime(filtered_df['time'], format='%H:%M').dt.strftime('%H:%M')
        fig_time = plot_stacked_time_chart(filtered_df, f"""<span style="color:blue; font-weight:bold">{selected_category}</span>의 시간대별 유동인구수<br>- (전체 vs 주중 vs 주말)""", 500, 350)
        fig_time.update_traces(texttemplate='')
        fig_time.update_layout(margin=dict(l=0, r=0, t=50, b=0), showlegend=True)
        st.plotly_chart(fig_time)

elif (selected_category not in ['선택해주세요', '전체(지역 선택 안함)']) and df_w1.empty:
    st.header("3-1. 주중(월~목)에 해당하는 데이터가 없습니다.")
elif (selected_category not in ['선택해주세요', '전체(지역 선택 안함)']) and df_w2.empty:
    st.header("3-2. 주말(금~일)에 해당하는 데이터가 없습니다.")
    
###############################################################################

# 유동인구 히트맵
if selected_category not in ['선택해주세요', '전체(지역 선택 안함)']:
    filtered_df4 = df[df['TYPE'] == selected_category]
    st.header('4. 유동인구 히트맵')

    filtered_df4['time'] = filtered_df4['time'].astype(str)
    day_grouped = filtered_df4.groupby(['Day_of_Week', 'Day_of_Week_Num', 'time'])['count'].sum().reset_index()
    pivot_table = day_grouped.pivot(index='Day_of_Week', columns='time', values='count').fillna(0)

    x_labels = sorted(pivot_table.columns, key=lambda x: pd.to_datetime(x, format='%H:%M'))
    y_labels = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']

    pivot_table = pivot_table.reindex(columns=x_labels, fill_value=0)
    pivot_table = pivot_table.reindex(y_labels)

    # 1시간 단위 x축 라벨 설정
    tickvals = [i for i in range(len(x_labels)) if x_labels[i].endswith(':00')]
    ticktext = [x_labels[i] for i in tickvals]

    fig5 = go.Figure(data=go.Heatmap(
        z=pivot_table.values,
        x=[str(x) for x in x_labels],
        y=y_labels,
        colorscale='Blues',
        text=pivot_table.values,
        texttemplate='%{text:.0f}',
        textfont={"size":10},
        hovertemplate='시간=%{x}<br>요일=%{y}<br>유동인구수 합계=%{z:,}<extra></extra>'))

    fig5.update_layout(
        title=f"<span style='color:blue; font-weight:bold'>{selected_category}</span> 요일별 시간대 유동인구수 히트맵",
        xaxis_title='시간대',
        yaxis_title='요일',
        width=1200, height=600,
        yaxis=dict(categoryorder='array', categoryarray=y_labels, autorange='reversed'),
        xaxis=dict(
            tickmode='array', 
            tickvals=tickvals, 
            ticktext=ticktext, 
            tickangle=0,
            showticklabels=True))
    st.plotly_chart(fig5)

    time_age_grouped = filtered_df4.groupby(['time', 'age'])['count'].sum().reset_index()
    pivot_table_age = time_age_grouped.pivot(index='time', columns='age', values='count').fillna(0)

    x_labels_age = sorted(pivot_table_age.columns)
    y_labels_time = sorted(pivot_table_age.index, key=lambda x: pd.to_datetime(x, format='%H:%M'))

    pivot_table_age = pivot_table_age.reindex(columns=x_labels_age, fill_value=0)
    pivot_table_age = pivot_table_age.reindex(y_labels_time, fill_value=0)

    # 1시간 단위 y축 라벨
    tickvals_time = [i for i in range(len(y_labels_time)) if y_labels_time[i].endswith(':00')]
    ticktext_time = [y_labels_time[i] for i in tickvals_time]

    fig6 = go.Figure(data=go.Heatmap(
        z=pivot_table_age.values,
        x=x_labels_age,
        y=[str(y) for y in y_labels_time],
        colorscale='Blues',
        text=pivot_table_age.values,
        texttemplate='%{text:.0f}',
        textfont={"size":10},
        hovertemplate='연령대=%{x}<br>시간=%{y}<br>유동인구수 합계=%{z:,}<extra></extra>'))

    fig6.update_layout(
        title=f"<span style='color:blue; font-weight:bold'>{selected_category}</span> 시간대별 연령대 유동인구수 히트맵",
        xaxis_title='연령대',
        yaxis_title='시간대',
        width=1200, height=600,
        xaxis=dict(categoryorder='array', categoryarray=x_labels_age),
        yaxis=dict(
            tickmode='array',
            tickvals=tickvals_time,
            ticktext=ticktext_time,
            tickangle=0,
            showticklabels=True,
            autorange='reversed'))
    st.plotly_chart(fig6)