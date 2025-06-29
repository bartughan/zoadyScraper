import streamlit as st
import pandas as pd
import os
import json
from io import BytesIO
from Discord.discord_server_scraper import scrape_discordservers
from Reddit.subreddit_scraper import fetch_all_subreddits, filter_subreddit, get_subreddit_data
from Reddit.main import get_online_users_requests

st.set_page_config(page_title="Reddit & Discord Scraper", layout="wide")
st.title("Reddit & Discord Scraper")

TABS = ["Reddit", "Discord"]
tab = st.sidebar.radio("Platform Seçin", TABS)

if tab == "Reddit":
    st.header("Reddit Subreddit Scraper")
    # Reddit API credentials
    st.subheader("Reddit API Bilgileri")
    client_id = st.text_input("Client ID", type="default")
    client_secret = st.text_input("Client Secret", type="password")
    user_agent = st.text_input("User Agent", value="streamlit_app")
    creds_ready = all([client_id, client_secret, user_agent])
    if creds_ready:
        # Save credentials to config file for session use
        reddit_config = {
            "client_id": client_id,
            "client_secret": client_secret,
            "user_agent": user_agent
        }
        config_path = os.path.join("Reddit", "reddit_config.json")
        with open(config_path, "w") as f:
            json.dump(reddit_config, f)
    else:
        st.info("Lütfen Reddit API bilgilerinizi girin.")
    keyword = st.text_input("Anahtar Kelime", "gaming")
    min_subs = st.number_input("Minimum Abone Sayısı", min_value=-1, value=-1)
    max_subs = st.number_input("Maksimum Abone Sayısı", min_value=-1, value=-1)
    max_age_days = st.number_input("Son Gönderi Maksimum Yaş (gün)", min_value=-1, value=-1)
    search_limit = st.number_input("Aranacak Subreddit Limiti", min_value=-1, value=20)
    debug = st.checkbox("Debug Modu", value=False)
    if st.button("Reddit Subredditlerini Tara"):
        if not creds_ready:
            st.error("Reddit API bilgileri eksik!")
        else:
            with st.spinner("Subredditler taranıyor..."):
                checked = 0
                fieldnames = ['Title', 'Total Users', 'Online Users', 'Online Ratio', 'Description', 'Link', 'Kurallar']
                rows = []
                for sub in fetch_all_subreddits(debug=debug):
                    checked += 1
                    if search_limit != -1 and checked > search_limit:
                        break
                    if filter_subreddit(sub, keyword, min_subs, max_subs, max_age_days, debug=debug):
                        row = get_subreddit_data(sub, debug=debug)
                        online_users = get_online_users_requests(row['Link'])
                        row['Online Users'] = online_users
                        try:
                            total = int(row['Total Users'])
                            online = int(online_users) if online_users else 0
                            ratio = f"{(online/total*100):.2f}%" if total > 0 else ''
                        except Exception:
                            ratio = ''
                        row['Online Ratio'] = ratio
                        row.pop('Active Users', None)
                        rows.append(row)
                if rows:
                    df = pd.DataFrame(rows)
                    st.dataframe(df)
                    output = BytesIO()
                    df.to_excel(output, index=False, engine='openpyxl')
                    output.seek(0)
                    st.download_button("Excel Olarak İndir", output, file_name="reddit_subs.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                else:
                    st.warning("Hiçbir subreddit bulunamadı.")

elif tab == "Discord":
    st.header("Discord Sunucu Scraper")
    keyword = st.text_input("Anahtar Kelime", "oyun")
    max_loads = st.number_input("Kaç kez 'Load More Servers' tıklansın?", min_value=1, value=3)
    min_members = st.number_input("Minimum Üye Sayısı", min_value=-1, value=-1)
    max_members = st.number_input("Maksimum Üye Sayısı", min_value=-1, value=-1)
    debug = st.checkbox("Debug Modu", value=False, key="discord_debug")
    if st.button("Discord Sunucularını Tara"):
        with st.spinner("Sunucular taranıyor..."):
            servers = scrape_discordservers(keyword, max_loads, min_members, max_members, debug)
            if servers:
                df = pd.DataFrame(servers)
                st.dataframe(df)
                output = BytesIO()
                df.to_excel(output, index=False, engine='openpyxl')
                output.seek(0)
                st.download_button("Excel Olarak İndir", output, file_name="discord_servers.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            else:
                st.warning("Hiç sunucu bulunamadı.") 