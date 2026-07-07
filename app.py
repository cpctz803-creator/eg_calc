import streamlit as st
import math

# --- 1. ページ全体の初期設定 ---
st.set_page_config(page_title="総合設備省エネ診断ツール", page_icon="⚡", layout="wide")

st.title("⚡ 建築設備 総合省エネ改修ポテンシャル診断")
st.caption("川崎様 業務サポート専用ツール (照明・空調・換気 統合版)")
st.markdown("---")

# --- 2. サイドバー（インプットエリア） ---
st.sidebar.header("📋 入力条件設定")

# 建物用途の選択
building_type = st.sidebar.selectbox(
    "1. 建物用途を選択してください",
    ["事務所", "病院", "学校", "ホテル", "商業施設"]
)

# 延べ面積の入力（スライダーと数値入力を連動）
total_floor_area = st.sidebar.number_input(
    "2. 延べ面積 (㎡) を入力してください", 
    min_value=10, max_value=100000, value=3000, step=100
)

st.sidebar.markdown("---")
st.sidebar.header("🔍 現状の設備状況 (導入済みチェック)")
st.sidebar.write("すでに高効率（最新）機器になっているものにチェックを入れてください。")

# チェックボックス
has_led = st.sidebar.checkbox("照明：すでにLED化されている", value=False)
has_eco_hvac = st.sidebar.checkbox("空調：すでに高効率マルチ空調である", value=False)
has_total_heat_ex = st.sidebar.checkbox("換気：すでに全熱交換器(ロスナイ等)である", value=False)

# 料金単価の設定
electricity_rate = st.sidebar.slider("電気料金単価 (円/kWh)", min_value=10, max_value=50, value=28, step=1)

# --- 3. 計算ロジック部 ---
# {用途名: (LED負荷密度, LED時間, 空調kwh/m2年, 換気風量m3/h・m2, 換気時間)}
params = {
    "事務所":   (6.0, 3000, 35, 5.0,  3000),
    "病院":     (5.0, 5000, 75, 6.0,  5000),
    "学校":     (5.5, 2000, 25, 10.0, 2000),
    "ホテル":   (4.5, 6000, 80, 4.0,  6000),
    "商業施設": (9.0, 4000, 90, 8.0,  4000)
}

led_w_m2, led_hours, hvac_kwh_m2, vent_vol_m2, vent_hours = params[building_type]

# 照明の計算
new_lighting_kwh = (total_floor_area * led_w_m2 * led_hours) / 1000
current_lighting_kwh = new_lighting_kwh if has_led else new_lighting_kwh * 2.0
diff_lighting_kwh = current_lighting_kwh - new_lighting_kwh

# 換気・空調の計算
vent_units = math.ceil((total_floor_area * vent_vol_m2) / 500)
new_vent_kwh = (vent_units * 150 * vent_hours) / 1000
new_hvac_base = total_floor_area * hvac_kwh_m2
new_hvac_kwh = new_hvac_base

current_hvac_base = new_hvac_base if has_eco_hvac else new_hvac_base * 1.4

if has_total_heat_ex:
    current_vent_kwh = new_vent_kwh
    current_hvac_kwh = current_hvac_base
    hvac_saved_by_vent = 0
    diff_vent_kwh = 0
else:
    current_vent_kwh = (vent_units * 100 * vent_hours) / 1000
    current_hvac_kwh = current_hvac_base * 1.3
    hvac_saved_by_vent = current_hvac_base * 0.3
    diff_vent_kwh = (current_vent_kwh - new_vent_kwh) + hvac_saved_by_vent

diff_hvac_kwh = current_hvac_base - new_hvac_kwh

# 総合合算
current_total_kwh = current_lighting_kwh + current_hvac_kwh + current_vent_kwh
new_total_kwh = new_lighting_kwh + new_hvac_kwh + new_vent_kwh
total_diff_kwh = current_total_kwh - new_total_kwh
saved_cost = total_diff_kwh * electricity_rate

# --- 4. メイン画面（結果表示エリア） ---

# メトリック（主要成果指標）の表示
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="💡 年間総削減電力量", value=f"{round(total_diff_kwh):,} kWh")
with col2:
    st.metric(label="💰 年間電気代削減額 (目安)", value=f"¥{round(saved_cost):,} 円/年")
with col3:
    reduction_rate = round((total_diff_kwh / current_total_kwh) * 100, 1) if current_total_kwh > 0 else 0
    st.metric(label="📈 建物全体省エネ率", value=f"{reduction_rate} %")

st.markdown("### 📊 設備別 年間消費電力量 比較表")

# Markdown表の構築と表示
markdown_table = f"""
| 設備項目 | 現状の年間消費電力 | 対策後の年間消費電力 | 年間削減電力量（メリット） |
| :--- | :---: | :---: | :---: |
| **照明設備** | {round(current_lighting_kwh):,} kWh | {round(new_lighting_kwh):,} kWh | **{round(diff_lighting_kwh):,} kWh** |
| **空調設備** | {round(current_hvac_kwh):,} kWh | {round(new_hvac_kwh):,} kWh | **{round(diff_hvac_kwh):,} kWh** |
| **換気設備** | {round(current_vent_kwh):,} kWh | {round(new_vent_kwh):,} kWh | **{round(diff_vent_kwh):,} kWh** |
| **建物総合計** | **{round(current_total_kwh):,} kWh** | **{round(new_total_kwh):,} kWh** | **{round(total_diff_kwh):,} kWh** |
"""
st.markdown(markdown_table)

st.info("※換気設備の削減電力量には、全熱交換器導入による空調負荷低減効果（熱回収メリット）を含んでいます。")

# 提案書作成用のコピペ用テキストエリア
st.markdown("### 📝 コピペ用 報告書テキスト")
report_text = f"""【初期省エネ試算報告】
物件用途：{building_type}
対象面積：{total_floor_area:,} ㎡

現状の設備構成を踏まえ、主要3設備（LED照明・高効率空調・全熱交換換気）の更新ポテンシャルを試算いたしました。

■ 試算結果
・現状年間消費電力量合計：{round(current_total_kwh):,} kWh
・更新後年間消費電力量合計：{round(new_total_kwh):,} kWh
・年間総削減電力量（差分）：{round(total_diff_kwh):,} kWh
・年間電気代削減目安：約 {round(saved_cost):,} 円/年（{electricity_rate}円/kWh換算）

設備別の削減内訳については別途詳細比較表をご参照ください。"""

st.text_area("そのままメールや資料に貼り付けられます", report_text, height=250)
