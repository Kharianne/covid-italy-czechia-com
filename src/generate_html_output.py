import os

import pandas as pd
import plotly
import plotly.graph_objects as go
from bs4 import BeautifulSoup
from plotly.subplots import make_subplots

pd.options.plotting.backend = 'plotly'

if os.name == 'nt':
    plotly.io.orca.config.executable = 'C:/Users/kharianne/AppData/Local/Programs/orca/orca.exe'
    conf_gl = pd.read_csv(
        "../COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")
    deaths_gl = pd.read_csv(
        "../COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv")
else:
    conf_gl = pd.read_csv(
        "COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")
    deaths_gl = pd.read_csv(
        "COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv")

base_country = ("Italy", 60480000)
countries_to_watch = {
    "Czechia": base_country[1] / 10650000,
    "Sweden": base_country[1] / 10230000,
    "US": base_country[1] / 328239523
}


def clear_transpose(df, state):
    num = df.index[0]
    df = df.drop(["Province/State", "Country/Region", "Lat", "Long"], axis=1)
    df = df.transpose()
    df = df.rename(columns={num: state})
    df = df[df[state] > 0]
    mapper = {}
    for i, date in enumerate(df.index.values.tolist()):
        mapper.update({date: i})
    df = df.rename(mapper, axis='index')
    return df


def slice_by_country(base_df, country):
    df = base_df[base_df["Country/Region"] == country]
    if not df.empty:
        df = clear_transpose(df, country)
        return df
    else:
        raise ValueError(f"{country} was not found in dataframe")


def concat_slices(slices):
    summary = pd.concat(slices, axis=1)
    return summary


def apply_ratio(df):
    for country in df.columns:
        if country == base_country[0]:
            continue
        df[country] = df[country].apply(
            lambda x: x * countries_to_watch[country])
    return df


def plot_plotly(df, info_dict, type='png'):
    fig = go.Figure()

    for column in df.columns:
        fig.add_trace(go.Scatter(y=df[column],
                                 mode='lines',
                                 name=column))
    fig.update_layout(
        title={
            'text': info_dict['title_text'],
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        xaxis_title=info_dict['xaxis_title'],
        yaxis_title=info_dict['yaxis_title'],
        paper_bgcolor='rgba(0, 0, 0, 0)')
    fig.show(type)
    return fig


def get_pct_change(df):
    pct_change_df = pd.DataFrame()
    for column in df.columns:
        pct_change_df[column] = df[column].pct_change(fill_method=None)
    return pct_change_df


def get_last_x_days(df, x):
    slices = []
    for column in df.columns:
        new = df[column].dropna(axis=0)
        slices.append(
            new[new.index.size - x - 1: new.index.size + 1].reset_index(
                drop=True))
    return concat_slices(slices)


country_slices_conf = [slice_by_country(conf_gl, base_country[0])]
for country in countries_to_watch:
    try:
        country_slices_conf.append(slice_by_country(conf_gl, country))
    except ValueError as e:
        print(e)
        continue

country_slices_deaths = [slice_by_country(deaths_gl, base_country[0])]
for country in countries_to_watch:
    try:
        country_slices_deaths.append(slice_by_country(deaths_gl, country))
    except ValueError as e:
        print(e)
        continue

figures = []

fig = make_subplots(rows=2, cols=2)
row = 1
col = 1
for i, slice in enumerate(country_slices_conf):
    fig.add_trace(go.Scatter(x=list(slice.index), y=slice[slice.columns[0]],
                             mode='lines',
                             name=slice.columns[0]),
                  row=row, col=col)
    if i % 2 == 0:
        col += 1
    else:
        row += 1
        col = 1
figures.append(fig)
fig.show("png")

summary = concat_slices(country_slices_conf)
summary = apply_ratio(summary)
plt = summary.plot.line()
figures.append(plt)
plt.show("png")

fig = make_subplots(rows=2, cols=2)
row = 1
col = 1
for i, slice in enumerate(country_slices_deaths):
    fig.add_trace(go.Scatter(x=list(slice.index), y=slice[slice.columns[0]],
                             mode='lines',
                             name=slice.columns[0]),
                  row=row, col=col)
    if i % 2 == 0:
        col += 1
    else:
        row += 1
        col = 1
figures.append(fig)
fig.show("png")

summary_deaths = concat_slices(country_slices_deaths)
summary_deaths = apply_ratio(summary_deaths)
plt = summary_deaths.plot.line()
figures.append(plt)
plt.show("png")

fig_summary = plot_plotly(summary, {
    'title_text': 'Number of cases comparison since first infected',
    'xaxis_title': 'Day number',
    'yaxis_title': 'Number of infected'
})

fig_summary_deaths = plot_plotly(summary_deaths, {
    'title_text': 'Deaths comparison since first death',
    'xaxis_title': 'Day number',
    'yaxis_title': 'Number of deaths'
})

fig_summary_pct_change = plot_plotly(get_pct_change(summary), {
    'title_text': 'Percentage change between days',
    'xaxis_title': 'Day number',
    'yaxis_title': 'Change'
}, type='png')

figures += [fig_summary, fig_summary_deaths, fig_summary_pct_change]

with open('generated.html', 'w') as f:
    full_html = True
    for i, fig in enumerate(figures[::-1]):
        fig.update_layout(paper_bgcolor='rgba(0, 0, 0, 0)')
        f.write(fig.to_html(full_html=full_html, include_plotlyjs='cdn'))
        if i == 0:
            full_html = False

with open('generated.html', 'r') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')
    header = soup.new_tag("h1", style="text-align:center;"
                                      "font-family: \"Open Sans\", verdana, "
                                         "arial, sans-serif;color: #545d5d;padding-top: 30px;")
    header.string = "Covid comparison graphs"
    soup.body.insert(0, header)
    container = soup.new_tag("div", style="display: flex;flex-direction: "
                                          "column;justify-content: "
                                          "center;align-items: center;"
                                          "gap: 4px;")
    desc_div = soup.new_tag("div", style="text-align:center;width:50%;"
                                         "font-family: \"Open Sans\", verdana, "
                                         "arial, sans-serif;")

    p1 = soup.new_tag("p")
    p1.string = ("Simple graphs that were created during COVID-19 pandemic. "
                 "Graphs compare Czechia, Italy, Sweden and USA. They should "
                 "track the trend from the first death and infected, to "
                 "compare how the pandemic was handled in the different states. "
                 "And take into account that the pandemic started in each "
                 "country in different time.")

    p2 = soup.new_tag("p")
    p2.string = ("This project is now archived and no new data are added. "
                 "Big thanks for sharing the data to: ")

    a = soup.new_tag("a", href="https://github.com/CSSEGISandData/COVID-19")
    a.string = ("Center for Systems Science and Engineering (CSSE) at Johns "
                "Hopkins University")

    p2.append(a)
    desc_div.append(p1)
    desc_div.append(p2)
    container.append(desc_div)
    soup.body.insert(1, container)
    soup.body['style'] = "background-color:#e9daf742;"

with open('../index.html', "w") as f:
    f.write(str(soup))
