import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from google.ads.googleads.client import GoogleAdsClient
import secrets

# Google Ads credentials
credentials = {
            "developer_token": developer_Token,
            "client_id": client_Id,
            "client_secret": client_Secret,
            "refresh_token": refresh_Token,
            "use_proto_plus": False,
            "login_customer_id": login_customer_Id
        }

client = GoogleAdsClient.load_from_dict(credentials)
customer_id=customer_Id

# Keyword + geo configuration
keyword_config = {
    "vakantiehuis_NL": {"keyword": "vakantiehuizen", "geo_code": "2528", "language_id":"1010"},   # Netherlands
    "vakantiehuis_BE": {"keyword": "vakantiehuizen", "geo_code": "2056",  "language_id":"1010"},   # Belgium
    "ferienhäuser_DE": {"keyword": "ferienhäuser", "geo_code": "2276", "language_id":"1001"} ,   # Germany
    "ferienhäuser_DK": {"keyword": "sommerhuse", "geo_code": "2208", "language_id":"1009"}    # Denmark
}

def fetch_data(client, keyword, geo_code,language_id):
    service = client.get_service("KeywordPlanIdeaService")
    request = client.get_type("GenerateKeywordHistoricalMetricsRequest")
    request.customer_id = customer_id
    request.keywords.append(keyword)
    request.geo_target_constants.append(client.get_service("GoogleAdsService").geo_target_constant_path(geo_code))
    request.language = client.get_service("GoogleAdsService").language_constant_path(language_id)
    request.keyword_plan_network = client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH

    response = service.generate_keyword_historical_metrics(request=request)

    data = []
    for res in response.results:
        for month in res.keyword_metrics.monthly_search_volumes:
            if 1 <= month.month <= 12:
                date = datetime.strptime(f"{month.year}-{month.month:02}", "%Y-%m")
                data.append({"Date": date, "Search Volume": month.monthly_searches, "Keyword": keyword})
    return pd.DataFrame(data)

def plot_altair(df, title):
    chart = alt.Chart(df).mark_line(point=True).encode(
        x=alt.X("Date:T", title="Date", axis=alt.Axis(format="%Y-%m")),
        y=alt.Y("Search Volume:Q", title="Avg. Monthly Searches"),
        tooltip=["Date:T", "Search Volume:Q"]
    ).properties(
        width=700,
        height=400,
        title=title
    ).interactive()
    return chart

# Streamlit layout
st.set_page_config(page_title="Keyword Trends", layout="wide")

col1, col2 = st.columns([4, 1])
with col1:
        st.title("📈 Average Monthly Searches Dashboard")
with col2:
        st.markdown("""
            <a href="https://www.linkedin.com/in/abhishek-kumawat-iitd/" target="_blank">
                <button style="background-color:#0077B5; color:white; border:none; padding:8px 16px; border-radius:5px; font-size:16px; cursor:pointer;">
                    Connect on LinkedIn
                </button>
            </a>
        """, unsafe_allow_html=True)


tabs = st.tabs(["📊 Vakantiehuizen NL", "📊 Vakantiehuizen BE", "📊 Ferienhäuser DE", "📊 Sommerhuse DK"])

with tabs[0]:
    df_nl = fetch_data(client, **keyword_config["vakantiehuis_NL"])
    st.altair_chart(plot_altair(df_nl, "Vakantiehuizen - Netherlands"), use_container_width=True)

with tabs[1]:
    df_be = fetch_data(client, **keyword_config["vakantiehuis_BE"])
    st.altair_chart(plot_altair(df_be, "Vakantiehuizen - Belgium"), use_container_width=True)

with tabs[2]:
    df_de = fetch_data(client, **keyword_config["ferienhäuser_DE"])
    st.altair_chart(plot_altair(df_de, "Ferienhäuser - Germany"), use_container_width=True)

with tabs[3]:
    df_dk = fetch_data(client, **keyword_config["ferienhäuser_DK"])
    st.altair_chart(plot_altair(df_dk, "Sommerhuse - Denmark"), use_container_width=True)

# with tabs[4]:
#     st.subheader("🔍 Search Any Keyword")
#     custom_kw = st.text_input("Enter a keyword:")
#     country = st.selectbox("Select a country:", {
#         "Netherlands": "2392",
#         "Belgium": "2056",
#         "Germany": "2276"
#     })
#     if st.button("Get Trend"):
#         if custom_kw:
#             df_custom = fetch_data(client, custom_kw, country)
#             if not df_custom.empty:
#                 st.altair_chart(plot_altair(df_custom, f"{custom_kw.title()} - Custom Search"), use_container_width=True)
#             else:
#                 st.warning("No data found for this keyword.")
#         else:
#             st.error("Please enter a keyword.")
