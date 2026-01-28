import streamlit as st
import feedparser
from datetime import datetime

# ページ設定
st.set_page_config(page_title="Tochigi & Focused News", page_icon="🎯", layout="wide")

# カスタムCSS
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .keyword-badge {
        background-color: #ff4b4b;
        color: white;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 12px;
        margin-right: 5px;
    }
    .news-card {
        padding: 12px 0px;
        border-bottom: 1px solid #f0f2f6;
    }
    .news-title {
        font-size: 17px;
        font-weight: 600;
        text-decoration: none !important;
        color: #1e1e1e;
    }
    .news-title:hover { color: #ff4b4b; text-decoration: underline !important; }
    .source-tag {
        font-size: 11px;
        color: #999;
        margin-top: 4px;
    }
    .highlight-box {
        background-color: #fff5f5;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #ff4b4b;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 設定：巡回するRSSリスト（政治、栃木、スポーツ、経済に絞り込み）
RSS_SOURCES = [
    ("読売・政治", "https://assets.wor.jp/rss/yomiuri/politics.xml"),
    ("Yahoo・政治", "https://news.yahoo.co.jp/rss/categories/domestic.xml"), # 国内カテゴリから政治が主に出る
    ("下野新聞（栃木）", "https://www.shimotsuke.co.jp/list/rss/local"), # 栃木県内ニュース
    ("読売・経済", "https://assets.wor.jp/rss/yomiuri/economy.xml"),
    ("読売・スポーツ", "https://assets.wor.jp/rss/yomiuri/sports.xml"),
    ("Yahoo・スポーツ", "https://news.yahoo.co.jp/rss/categories/sports.xml"),
    ("Yahoo・経済", "https://news.yahoo.co.jp/rss/categories/business.xml"),
]

# 設定：抽出する特定のキーワード
WATCH_KEYWORDS = ["相撲", "大谷翔平", "野球", "物価高", "トランプ大統領"]

def fetch_all_news():
    all_entries = []
    for source_name, url in RSS_SOURCES:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            # 天気予報系（「晴れ」「曇り」など）を簡易的に除外
            if "の天気" in entry.title or "予報" in entry.title:
                continue
            entry['source_name'] = source_name
            all_entries.append(entry)
    return all_entries

st.title("🎯 Tochigi & Focused News Feed")
st.caption(f"キーワード: {', '.join(WATCH_KEYWORDS)} | 栃木県内ニュース対応")

# ニュース取得
with st.spinner('最新ニュースを解析中...'):
    all_news = fetch_all_news()

# 1. 特定キーワード記事と「栃木」記事の抽出
highlighted_news = []
tochigi_news = []
other_news = []

for entry in all_news:
    # 注目キーワード判定
    found_keywords = [kw for kw in WATCH_KEYWORDS if kw in entry.title]
    
    if found_keywords:
        entry['found_keywords'] = found_keywords
        highlighted_news.append(entry)
    elif "栃木" in entry.title or entry['source_name'] == "下野新聞（栃木）":
        tochigi_news.append(entry)
    else:
        other_news.append(entry)

# --- 表示セクション ---

# A. 注目トピック（特定のキーワード）
st.subheader("🔥 注目トピック")
if highlighted_news:
    st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
    seen_titles = set()
    for entry in highlighted_news:
        if entry.title not in seen_titles:
            kw_badges = "".join([f'<span class="keyword-badge">{kw}</span>' for kw in entry['found_keywords']])
            st.markdown(f"""
                <div class="news-card">
                    {kw_badges}
                    <a class="news-title" href="{entry.link}" target="_blank">{entry.title}</a>
                    <div class="source-tag">{entry.source_name} | {entry.get('published', '')}</div>
                </div>
                """, unsafe_allow_html=True)
            seen_titles.add(entry.title)
    st.markdown('</div>', unsafe_allow_html=True)

# B. 栃木県内のニュース
st.subheader("🍓 栃木県内のニュース")
if tochigi_news:
    seen_tochigi = set()
    for entry in tochigi_news[:20]:
        if entry.title not in seen_tochigi:
            st.markdown(f"""
                <div class="news-card">
                    <a class="news-title" href="{entry.link}" target="_blank">{entry.title}</a>
                    <div class="source-tag">{entry.source_name} | {entry.get('published', '')}</div>
                </div>
                """, unsafe_allow_html=True)
            seen_tochigi.add(entry.title)
else:
    st.write("栃木県に関する最新ニュースは見つかりませんでした。")

# C. その他（政治・経済・スポーツ）
st.subheader("🌐 その他（政治・経済・スポーツ）")
with st.expander("一覧を表示"):
    seen_titles_all = set()
    # すでに表示したものは除外して表示
    displayed_titles = set([e.title for e in highlighted_news] + [e.title for e in tochigi_news])
    for entry in other_news[:50]:
        if entry.title not in seen_titles_all and entry.title not in displayed_titles:
            st.markdown(f"""
                <div class="news-card">
                    <a class="news-title" href="{entry.link}" target="_blank">{entry.title}</a>
                    <div class="source-tag">{entry.source_name} | {entry.get('published', '')}</div>
                </div>
                """, unsafe_allow_html=True)
            seen_titles_all.add(entry.title)

# サイドバーに更新ボタン
if st.sidebar.button('今すぐ更新'):
    st.rerun() 
