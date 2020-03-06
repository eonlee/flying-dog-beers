import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
from plotly.subplots import make_subplots
from dash.dependencies import Input, Output
import requests
from bs4 import BeautifulSoup
import numpy as np


########### Define your variables

def get_codedf():
    url_main = 'http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13'
    code_df = pd.read_html(url_main, header=0)[0]
    code_df.종목코드 = code_df.종목코드.map('{:06d}'.format)
    code_df = code_df[['회사명', '종목코드']]
    code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'})
    return code_df


def get_codeandname():
    stock_name = get_codedf().name
    # stock_code = get_codedf().code
    # code_name = [i + " " + "(" + j + ")" for i, j in zip(stock_name, stock_code)]
    return stock_name






########### Initiate the app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = 'Hellooo'



def get_financeurl(item_name, code_df):
    code = code_df.query("name=='{}'".format(item_name))['code'].to_string(index=False).replace(" ", "")
    financeurl_sub = 'https://finance.naver.com/item/main.nhn?code={code}'.format(code=code)
    return financeurl_sub


def get_charturl(item_name, code_df):
    code = code_df.query("name=='{}'".format(item_name))['code'].to_string(index=False).replace(" ", "")
    url_sub = 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format(code=code)
    return url_sub


########### Set up the layout

app.layout = html.Div(
    html.Div([
        html.Div([
            html.H1(children='종목정보',
                    className="three columns"),

            html.Div([
                dcc.Dropdown(
                    id='demo-dropdown',
                    value='세중',
                    options=[
                        {'label': i, 'value': i} for i in get_codeandname()
                    ],
                    placeholder="Select a city"
                ),
            ], className="five columns"),

            html.Img(
                src=app.get_asset_url("blackdiamond.png"),
                className='four columns',
                style={
                    'height': '14%',
                    'width': '14%',
                    'float': 'right',
                    'position': 'relative',
                    'margin-top': 20,
                    'margin-right': 20
                },
            ),
            html.Div(children='''
                        Dash: A web application framework for Python.
                        ''',
                     className='nine columns',
                     style={'margin-top': '10'}
                     )
        ], className="row"),

        html.Div([
            # html.H1(children='종목정보2',
            # className="five columns"),

            html.Div([
                dcc.Graph(
                    id="my-figure2",
                    className="pretty_container twelve columns")
            ])
        ], className="row"),

        html.Div([
            html.Div([
                dcc.Graph(
                    id="my-figure3",
                    className="pretty_container five columns")
            ]),

            html.Div([
                dcc.Graph(
                    id="my-figure",
                    className="pretty_container six columns")
            ])
        ], className="row")
    ])
)

# 제무재표 차트
@app.callback(
    Output('my-figure', 'figure'),
    [Input('demo-dropdown', 'value')])
def update_output2(value):
    # Importing Code from KRX
    url_main = 'http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13'
    code_df = pd.read_html(url_main, header=0)[0]
    code_df.종목코드 = code_df.종목코드.map('{:06d}'.format)
    code_df = code_df[['회사명', '종목코드']]
    code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'})

    # Using Item name and code to get the right URL
    item_name = value
    financecode_url = get_financeurl(item_name, code_df)

    main_url = financecode_url
    finance_url = requests.get(main_url)
    html = finance_url.text
    soup = BeautifulSoup(html, 'html.parser')
    finance_html = soup.select('div.section.cop_analysis div.sub_section')[0]

    # Selecting Appropriate Data and designating it
    th_data = [item.get_text().strip() for item in finance_html.select('thead th')]
    annual_date = th_data[3:7]
    quarter_date = th_data[7:13]

    # Designating Finance Date
    finance_date = annual_date + quarter_date
    finance_date = ' '.join(finance_date).replace('(E)', '').split()
    finance_date = pd.to_datetime(finance_date)

    # Designating Finance Index
    finance_index = [item.get_text().strip() for item in finance_html.select('th.h_th2')][3:14]

    # Collecting Finance Data
    finance_data = [item.get_text().strip() for item in finance_html.select('td')]
    finance_data = np.array(finance_data)
    finance_data.resize(len(finance_index), 10)

    # Assigning Header
    name_list = []
    for day in finance_date:
        name_list.append(day.strftime('%Y.%m' + 'M'))
    header = name_list

    # Allocating Data
    z = header[0:4]
    y = finance_data[0, 0:4]
    y2 = finance_data[1, 0:4]
    y3 = finance_data[2, 0:4]
    y4 = finance_data[3, 0:4]
    y5 = finance_data[4, 0:4]
    y6 = finance_data[6, 0:4]
    y7 = finance_data[8, 0:4]
    y8 = finance_data[10, 0:4]

    c = header[5:11]
    b = finance_data[0, 4:]
    b2 = finance_data[1, 4:]
    b3 = finance_data[2, 4:]
    b4 = finance_data[3, 4:]
    b5 = finance_data[4, 4:]
    b6 = finance_data[6, 4:]
    b7 = finance_data[8, 4:]
    b8 = finance_data[10, 4:]

    # Drawing Chart
    fig = make_subplots(2, 3, subplot_titles=(
    "매출액 (억원)", "영업이익+당기순이익 (억원)", "영업이익률+순이익률 (%)", "부채비율 (%)", "유보율 (%)", "ROE (%)"))
    # 1 번 차트 (1,1)
    fig.add_scatter(x=z, y=y,
                    mode='lines+markers',
                    name='매출액',
                    row=1, col=1,
                    line_color='blue',
                    showlegend=True,
                    visible=True)
    # 2번 차트 (1,1)
    fig.add_scatter(x=c, y=b,
                    mode='lines+markers',
                    name='매출액',
                    row=1, col=1,
                    line_color='blue',
                    showlegend=False,
                    visible='legendonly')
    # 1번 차트 (1,2)
    fig.add_scatter(x=z, y=y2,
                    mode='lines+markers',
                    name='영업이익',
                    row=1, col=2,
                    line_color='red',
                    showlegend=True,
                    visible=True)
    # 2번 차트 (1,2)
    fig.add_scatter(x=c, y=b2,
                    mode='lines+markers',
                    name='영업이익',
                    row=1, col=2,
                    line_color='red',
                    showlegend=False,
                    visible='legendonly')
    # 1번 차트 (1,2) 2번째
    fig.add_scatter(x=z, y=y3,
                    mode='lines+markers',
                    name='당기순이익',
                    row=1, col=2,
                    line_color='orange',
                    showlegend=True,
                    visible=True)
    # 2번 차트 (1,2) 2번째
    fig.add_scatter(x=c, y=b3,
                    mode='lines+markers',
                    name='당기순이익',
                    row=1, col=2,
                    line_color='orange',
                    showlegend=False,
                    visible='legendonly')
    # 1번 차트 (1,3)
    fig.add_scatter(x=z, y=y4,
                    mode='lines+markers',
                    name='영업이익률',
                    row=1, col=3,
                    line_color='green',
                    showlegend=True,
                    visible=True)
    # 2번 차트 (1,3)
    fig.add_scatter(x=c, y=b4,
                    mode='lines+markers',
                    name='영업이익률',
                    row=1, col=3,
                    line_color='green',
                    showlegend=False,
                    visible='legendonly')
    # 1번 차트 (1,3) 2번째
    fig.add_scatter(x=z, y=y5,
                    mode='lines+markers',
                    name='순이익률',
                    row=1, col=3,
                    line_color='lightgreen',
                    showlegend=True,
                    visible=True)
    # 2번 차트 (1,3) 2번째
    fig.add_scatter(x=c, y=b5,
                    mode='lines+markers',
                    name='순이익률',
                    row=1, col=3,
                    line_color='lightgreen',
                    showlegend=False,
                    visible='legendonly')
    # 1번 차트 (2,1)
    fig.add_scatter(x=z, y=y6,
                    mode='lines+markers',
                    name='부채비율',
                    row=2, col=1,
                    line_color='purple',
                    showlegend=True,
                    visible=True)

    # 2번 차트 (2,1)
    fig.add_scatter(x=c, y=b6,
                    mode='lines+markers',
                    name='부채비율',
                    row=2, col=1,
                    line_color='purple',
                    showlegend=False,
                    visible='legendonly')
    # 1번 차트 (2,2)
    fig.add_scatter(x=z, y=y7,
                    mode='lines+markers',
                    name='유보율',
                    row=2, col=2,
                    line_color='indigo',
                    showlegend=True,
                    visible=True)
    # 2번 차트 (2,2)
    fig.add_scatter(x=c, y=b7,
                    mode='lines+markers',
                    name='유보율',
                    row=2, col=2,
                    line_color='indigo',
                    showlegend=False,
                    visible='legendonly')
    # 1번 차트 (2,3)
    fig.add_scatter(x=z, y=y8,
                    mode='lines+markers',
                    name='ROE',
                    row=2, col=3,
                    line_color='pink',
                    showlegend=True,
                    visible=True)
    # 2번 차트 (2,3)
    fig.add_scatter(x=c, y=b8,
                    mode='lines+markers',
                    name='ROE',
                    row=2, col=3,
                    line_color='pink',
                    showlegend=False,
                    visible='legendonly')
    fig.update_layout(title_text="차트 분석")
    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                active=0,
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.1,
                xanchor="left",
                y=1.3,
                yanchor="top",
                buttons=list([
                    dict(label="연간",
                         method="update",
                         args=[
                             {"visible": [True, False, True, False, True, False, True, False, True, False, True, False,
                                          True, False, True, False]},
                             {'title': '연간 제무 미니차트'}
                         ]),

                    dict(label="분기",
                         method="update",
                         args=[
                             {"visible": [False, True, False, True, False, True, False, True, False, True, False, True,
                                          False, True, False, True]},
                             {'title': '분기 제무 미니차트'}
                         ]),

                ]),
            )
        ])
    return fig


# 캔들차트 외
@app.callback(
    Output('my-figure2', 'figure'),
    [Input('demo-dropdown', 'value')])
def update_output3(value):
    # Importing Code from KRX
    url_main = 'http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13'
    code_df = pd.read_html(url_main, header=0)[0]
    code_df.종목코드 = code_df.종목코드.map('{:06d}'.format)
    code_df = code_df[['회사명', '종목코드']]
    code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'})

    # Using Item name and code to get the right URL
    item_name = value
    url = get_charturl(item_name, code_df)

    # Add data into df
    df = pd.DataFrame()

    for page in range(1, 25):
        pg_url = '{url}&page={page}'.format(url=url, page=page)
        df = df.append(pd.read_html(pg_url, header=0)[0], ignore_index=True)

    df = df.dropna()

    # Rename df
    df = df.rename(columns={'날짜': 'date', '종가': 'close', '전일비': 'diff',
                            '시가': 'open', '고가': 'high', '저가': 'low', '거래량': 'volume'})
    df[['close', 'diff', 'open', 'high', 'low', 'volume']] \
        = df[['close', 'diff', 'open', 'high', 'low', 'volume']].astype(int)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by=['date'], ascending=True)

    # 입력받은 값이 dataframe이라는 것을 정의해줌
    df = pd.DataFrame(df)

    # n일중 종가 중 최고가
    ndays_high = df.close.rolling(window=15, min_periods=1).max()
    # n일중 종가 중 최저가
    ndays_low = df.close.rolling(window=15, min_periods=1).min()
    # Fast%K 계산
    kdj_k = ((df.close - ndays_low) / (ndays_high - ndays_low)) * 100
    # Fast%D (=Slow%K) 계산
    kdj_d = kdj_k.ewm(span=8).mean()
    # EOM 계산
    eom_1 = ((((df.high + df.low) / 2) - ((df.high.shift(1) + df.low.shift(1)) / 2)) / (
            df.volume / (df.high - df.low)))
    # Eom AVG
    eom_2 = eom_1.rolling(60).mean()
    # Eom AVG's Avg
    eom_3 = eom_2.rolling(10).mean()

    # dataframe에 컬럼 추가
    df = df.assign(kdj_k=kdj_k, kdj_d=kdj_d, eom_1=eom_1, eom_2=eom_2, eom_3=eom_3).dropna()

    # Make Chart out of data
    fig = make_subplots(rows=5, cols=1, shared_xaxes=True, row_width=[0.2, 0.2, 0.2, 0.2, 0.4],
                        subplot_titles=("캔들차트", "", "거래량", "주가의 힘", "세력의 힘"))

    fig.add_trace(go.Candlestick(x=df.date,
                                 open=df.open,
                                 high=df.high,
                                 low=df.low,
                                 close=df.close,
                                 increasing_line_color='red', decreasing_line_color='blue', showlegend=False),
                  row=1, col=1)

    fig.add_trace(go.Bar(
        x=df.date,
        y=df['volume'],
        name="거래량"),
        row=3, col=1)

    fig.add_trace(go.Scatter(
        x=df.date,
        y=df['kdj_k'],
        fillcolor='red',
        stackgroup='one',
        line_color='black',
        legendgroup="group3",
        name="주가 강도 여부"),
        row=4, col=1)

    fig.add_trace(go.Scatter(
        x=df.date,
        y=df['kdj_d'],
        stackgroup='two',
        fillcolor='grey',
        line_color='black',
        showlegend=False),
        row=4, col=1)

    fig.add_trace(go.Scatter(
        x=df.date,
        y=df['eom_2'],
        name="세력 진입 여부",
        fillcolor='orange',
        stackgroup='one',
        line_color='yellow'),
        row=5, col=1)

    fig.add_trace(go.Scatter(
        x=df.date,
        y=df['eom_3'],
        name="Eom_3",
        stackgroup='two',
        fillcolor='grey',
        line_color='black',
        showlegend=False),
        row=5, col=1)

    fig.update_layout(title_text="차트 분석", height=800)
    return fig


# 제무재표 표
@app.callback(
    Output('my-figure3', 'figure'),
    [Input('demo-dropdown', 'value')])
def update_output(value):
    # Importing Code from KRX
    url_main = 'http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13'
    code_df = pd.read_html(url_main, header=0)[0]
    code_df.종목코드 = code_df.종목코드.map('{:06d}'.format)
    code_df = code_df[['회사명', '종목코드']]
    code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'})

    # Using Item name and code to get the right URL
    item_name = value
    financecode_url = get_financeurl(item_name, code_df)
    main_url = financecode_url
    finance_url = requests.get(main_url)
    html3 = finance_url.text
    soup = BeautifulSoup(html3, 'html.parser')
    finance_html = soup.select('div.section.cop_analysis div.sub_section')[0]

    # Selecting Appropriate Data and designating it
    th_data = [item.get_text().strip() for item in finance_html.select('thead th')]
    annual_date = th_data[3:7]
    quarter_date = th_data[7:13]

    # Designating Finance Date
    finance_date = annual_date + quarter_date
    finance_date.insert(0, '연간 주요 재무정보')
    finance_date.insert(5, '분기 주요 재무정보')

    # Designating Finance Index
    finance_index = [item.get_text().strip() for item in finance_html.select('th.h_th2')][3:14]

    # Collecting Finance Data
    finance_data = [item.get_text().strip() for item in finance_html.select('td')]
    finance_data = np.array(finance_data)
    finance_data.resize(len(finance_index), 10)
    finance_data = finance_data.T.tolist()

    # Assigning Value
    values2 = finance_index, finance_data[0], finance_data[1], finance_data[2], finance_data[3]
    values3 = finance_index, finance_data[4], finance_data[5], finance_data[6], finance_data[7], finance_data[8], \
              finance_data[9]

    fig = go.Figure()

    fig.add_trace(go.Table(
        columnwidth=[1, 1, 1, 1, 1],
        visible=True,
        header=dict(values=finance_date[0:5],
                    fill_color='black',
                    line_color='black',
                    align='center',
                    font=dict(color='white', size=12),
                    ),
        cells=dict(values=values2,
                   fill=dict(color=['black', 'grey']),
                   line_color='black',
                   align='center',
                   font=dict(color='white', size=12),
                   )))

    fig.add_trace(go.Table(
        columnwidth=[1, 1, 1, 1, 1, 1, 1],
        visible=False,
        header=dict(values=finance_date[5:12],
                    fill_color='black',
                    line_color='black',
                    align='center',
                    font=dict(color='white', size=12),
                    ),
        cells=dict(values=values3,
                   fill=dict(color=['black', 'grey']),
                   line_color='black',
                   align='center',
                   font=dict(color='white', size=12),
                   )))

    fig.update_layout(title_text="차트 분석")

    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                active=0,
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.1,
                xanchor="left",
                y=1.3,
                yanchor="top",
                buttons=list([
                    dict(label="연간",
                         method="update",
                         args=[{"visible": [True, False]}, {'title': '연간 제무재표'}
                               ]),

                    dict(label="분기",
                         method="update",
                         args=[{"visible": [False, True]}, {'title': '분기 제무재표'}
                               ]),

                ]),
            )
        ])
    return fig


if __name__ == '__main__':
    app.run_server()
