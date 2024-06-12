import streamlit as st
import plotly.express as px
from datetime import datetime, date
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go

###############################################################################
# 배경 검정색으로 바꾸기
backgroundColor = "#131e35"
# 꽉찬 화면으로 바꾸기
st.set_page_config(layout="wide")
###############################################################################

@st.cache_data
def read_data(file_path):
    df = pd.read_excel(file_path, sheet_name='data')
    
    # 날짜형 데이터로 변환
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

    # 정렬을 위해 생성
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

    # 성별 라벨 변경
    sex_mapping = {'Male': '남자', 'Female': '여자'}
    df['sex'] = df['sex'].map(sex_mapping)

    # type 라벨 변경
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

# 5/3~5/9 데이터만 산출
start_date = pd.to_datetime('20240503', format='%Y%m%d')
end_date = pd.to_datetime('20240509', format='%Y%m%d')
df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

###############################################################################

#한글 폰트 설정
plt.rcParams['font.family'] = 'NanumGothic'
plt.rcParams['axes.unicode_minus'] = False

###############################################################################

# 제목
st.title("골목상권 유동인구 분석 (24/05/03~24/05/09)")
st.caption('골목상권 유동인구 대시보드')

###############################################################################
#1. 기본 응답자 정보 확인

# 색상 코드 목록
colors = ['#bd054e', '#0193bd']

# 드롭다운 메뉴 생성
st.sidebar.header('1. 기본 응답자 정보 확인')
options = ['선택해주세요'] + list(df['TYPE'].unique())
selected_category = st.sidebar.selectbox('골목상권을 선택해주세요:', options, key='selectbox1')
# '선택하세요'가 아닌 유효한 지역이 선택된 경우에만 제목과 차트를 생성
if selected_category != '선택해주세요':
    filtered_df = df[df['TYPE'] == selected_category]
    
    ### 성별 #############################################################
    st.header('1. 기본 응답자 정보 확인')
    colors=['#800000', '#4776b4']
    fig = px.pie(
        filtered_df,
        names='sex',
        values='count',
        title=f'<span style="color:blue; font-weight:bold">{selected_category}</span>의 유동인구 남녀비율', 
        color_discrete_sequence=colors
    )
    st.plotly_chart(fig)
    fig.update_traces(textposition='inside', textinfo='percent+label', insidetextfont=dict(size=18))

    ### 연령대(10세 단위) #############################################################
    # 연령대별 데이터 집계
    age_grouped = filtered_df.groupby('age')['count'].sum().reset_index()
    age_grouped['sum_count'] = age_grouped['count']
    
    colors = ['#6ccad0']
    fig2_1 = go.Figure(go.Bar(
        x=age_grouped['age'],
        y=age_grouped['sum_count'],
        name='연령대(10세 단위)'
    ))

    fig2_1.update_traces(
        hovertemplate='연령대: %{x}<br>유동인구수 합계: %{y:,}<extra></extra>'
    )
    
    fig2_1.update_layout(
        width=800, 
        height=400, 
        title_text=f'<span style="color:blue; font-weight:bold">{selected_category}</span>의 유동인구 연령대비율',
        yaxis=dict(tickformat=',')  # y축 형식 지정
    )
    st.plotly_chart(fig2_1)

    
###############################################################################
# 2. 골목상권별 시간대 분포

# 사이드바에 드롭다운 메뉴 생성
st.sidebar.header('2. 골목상권별 시간대/요일별 분포')
if selected_category != '선택해주세요':
    st.header('2. 골목상권별 시간대/요일별 분포')
    filtered_df3_1 = filtered_df     #sk 수정
    
    # 시간대별 데이터 집계
    time_grouped = filtered_df3_1.groupby('time')['count'].sum().reset_index()
    time_grouped['sum_count'] = time_grouped['count']
    
    # 시간대별 차트
    fig3 = px.bar(
        time_grouped, 
        x='time', 
        y='sum_count', 
        title=f'<span style="color:blue; font-weight:bold">{selected_category}</span> 시간대별 유동인구수',
        hover_data={'sum_count': ':,'}  # 추가: 숫자 형식 지정
    )
    fig3.update_traces(
        hovertemplate='시간: %{x}<br>유동인구수 합계: %{y}<extra></extra>'
    )
    fig3.update_layout(
        xaxis=dict(title='시간대', tickvals=filtered_df3_1['time'].unique(), ticktext=filtered_df3_1['time'].unique()),
        yaxis_title='유동인구수'
    )
    st.plotly_chart(fig3)
    
if selected_category != '선택해주세요':
    filtered_df3_2 = filtered_df3_1     #sk 수정
    
    # 요일별 데이터 집계
    day_grouped = filtered_df3_2.groupby('Day_of_Week')['count'].sum().reset_index()
    day_grouped['sum_count'] = day_grouped['count']
    
    # 요일별 차트
    fig4 = px.bar(
        day_grouped, 
        x='Day_of_Week', 
        y='sum_count', 
        title=f'<span style="color:blue; font-weight:bold">{selected_category}</span> 일별 유동인구수 추이',
        hover_data={'sum_count': ':,'}  # 추가: 숫자 형식 지정
    )
    fig4.update_traces(
        hovertemplate='요일: %{x}<br>유동인구수 합계: %{y}<extra></extra>'
    )
    fig4.update_layout(
        xaxis_title='요일', 
        yaxis_title='유동인구수'
    )
    st.plotly_chart(fig4)

###############################################################################
