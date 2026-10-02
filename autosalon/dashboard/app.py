import os

import streamlit as st
import pandas as pd
import plotly.express as px
import requests

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Автосалон — Аналитика", page_icon="🚗", layout="wide")
st.title("🚗 Автосалон — Панель руководителя")


# === АВТОРИЗАЦИЯ (JWT) ===
def login(username: str, password: str) -> bool:
    """Получаем access-токен от /api/auth/login/."""
    try:
        r = requests.post(
            f"{API_URL}/api/auth/login/",
            json={"username": username, "password": password},
            timeout=10,
        )
    except requests.RequestException as e:
        st.sidebar.error(f"API недоступен: {e}")
        return False
    if r.status_code == 200:
        st.session_state["token"] = r.json()["access"]
        st.session_state["user"] = r.json()["user"]
        return True
    st.sidebar.error("Неверный логин или пароль")
    return False


def headers() -> dict:
    """Заголовок Authorization с токеном."""
    return {"Authorization": f"Bearer {st.session_state.get('token', '')}"}


if "token" not in st.session_state:
    with st.sidebar:
        st.header("🔐 Вход")
        u = st.text_input("Логин")
        p = st.text_input("Пароль", type="password")
        if st.button("Войти") and login(u, p):
            st.rerun()
    st.info("Войдите в систему в боковой панели, чтобы увидеть аналитику.")
    st.stop()

# === БОКОВАЯ ПАНЕЛЬ ===
with st.sidebar:
    st.success(f"Вы вошли как {st.session_state['user']['username']}")
    st.header("⚙️ Фильтры")
    days = st.selectbox("Период", [7, 30, 90, 365], index=1,
                        format_func=lambda x: f"{x} дней")
    if st.button("🔄 Обновить"):
        st.cache_data.clear()
        st.rerun()
    if st.button("Выйти"):
        st.session_state.clear()
        st.rerun()


# === ФУНКЦИИ ЗАГРУЗКИ ДАННЫХ ИЗ API ===
def get(path: str, params: dict | None = None):
    r = requests.get(f"{API_URL}{path}", params=params, headers=headers(), timeout=15)
    r.raise_for_status()
    return r.json()


@st.cache_data(ttl=60)
def load_kpi(days, _token):
    return get("/api/reports/kpi/", {"days": days})


@st.cache_data(ttl=60)
def load_revenue(days, _token):
    return pd.DataFrame(get("/api/reports/revenue/", {"days": days}))


@st.cache_data(ttl=60)
def load_top_models(_token):
    return pd.DataFrame(get("/api/reports/top-models/"))


@st.cache_data(ttl=60)
def load_manager_load(days, _token):
    return pd.DataFrame(get("/api/reports/manager-load/", {"days": days}))


@st.cache_data(ttl=60)
def load_stock(_token):
    return pd.DataFrame(get("/api/reports/stock/"))


token = st.session_state["token"]

# === KPI-ПЛИТКИ ===
kpi = load_kpi(days, token)
c1, c2, c3, c4 = st.columns(4)
c1.metric("💰 Выручка", f"{kpi['revenue']:,.0f} ₽")
c2.metric("✅ Продаж", kpi["sales_count"])
c3.metric("🧾 Средний чек", f"{kpi['avg_check']:,.0f} ₽")
c4.metric("🚗 В наличии", kpi["in_stock"])

# === ГРАФИК ВЫРУЧКИ ===
st.header("📈 Динамика выручки")
revenue_df = load_revenue(days, token)
if not revenue_df.empty:
    fig = px.line(revenue_df, x="date", y="total", markers=True)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("За выбранный период завершённых продаж нет.")

# === 2 КОЛОНКИ ===
col1, col2 = st.columns(2)

with col1:
    st.header("🏆 Топ-5 моделей")
    top = load_top_models(token)
    if not top.empty:
        fig = px.bar(top, x="count", y="model", color="brand", orientation="h")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Нет данных о продажах.")

with col2:
    st.header("👔 Загрузка менеджеров")
    managers = load_manager_load(days, token)
    if not managers.empty:
        fig = px.pie(managers, values="orders", names="manager")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Нет заказов за период.")

# === СКЛАД ===
st.header("📦 Состояние склада")
stock = load_stock(token)
if not stock.empty:
    fig = px.pie(stock, values="count", names="status",
                 color="status",
                 color_discrete_map={"available": "green", "reserved": "orange", "sold": "red"})
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("В каталоге пока нет автомобилей.")
