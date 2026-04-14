import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
from streamlit_option_menu import option_menu

# CẤU HÌNH LIGHT THEME & TRANG
st.set_page_config(
    page_title="Finance Business Partner", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Light styling
st.markdown("""
<style>
    /* Metricalist Dense Dashboard Theme */
    [data-testid="stAppViewContainer"] { background-color: #E9ECEF; color: #1E1E1E; }
    [data-testid="stSidebar"] { background-color: #0B5C57 !important; border-right: none; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] label, [data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] { color: #F8F9F9 !important; }
    [data-testid="stHeader"] { background-color: transparent; }
    
    .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; max-width: 98% !important; }
    
    /* Metricalist Custom Cards */
    .met-top-row { display: flex; gap: 10px; width: 100%; margin-bottom: 15px; }
    .met-card { 
        flex: 1; background: white; padding: 15px 10px; text-align: center;
        border-top: 3px solid #D5D8DC; box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .met-label { font-size: 14px; font-weight: 600; color: #5D6D7E; text-transform: uppercase; margin-bottom: 5px; }
    .met-val { font-size: 38px; font-weight: 300; line-height: 1.1; margin-bottom: 5px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .met-val.teal { color: #1ABC9C; }
    .met-val.red { color: #E74C3C; }
    .met-goal { font-size: 11px; color: #34495E; font-weight: 500; }
    
    /* Panel Assets HTML */
    .met-panel { background: white; border: 1px solid #E5E8E8; padding: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); display: flex; height: 280px; box-sizing: border-box; }
    .met-grid { flex: 2; display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; padding-right: 15px;}
    .met-grid-dark { color: #2C3E50; font-size: 20px; font-weight: 600; margin-bottom: -5px;}
    .met-grid-sub { color: #1ABC9C; font-size: 13px; margin-bottom: 15px;}
    .met-grid-sub.red { color: #E74C3C; }
    .met-highlight-teal { flex: 1; background: #1ABC9C; display: flex; flex-direction: column; justify-content: center; align-items: center; color: white; padding: 10px;}
    .met-highlight-red { flex: 1; background: #E74C3C; display: flex; flex-direction: column; justify-content: center; align-items: center; color: white; padding: 10px;}
    .met-hl-val { font-size: 26px; font-weight: 700; margin-bottom: 0px;}
    .met-hl-text { font-size: 14px; font-weight: 400; text-align: center;}
</style>
""", unsafe_allow_html=True)

# CẤU HÌNH ĐƯỜNG DẪN DỮ LIỆU TĨNH (OFFLINE)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data_snapshot")

@st.cache_data
def load_local_data(ticker):
    file_path = os.path.join(DATA_DIR, f"{ticker}_snapshot.xlsx")
    if os.path.exists(file_path):
        try:
            with pd.ExcelFile(file_path) as xls:
                sheets = xls.sheet_names
                return {
                    'Price': pd.read_excel(xls, 'Price') if 'Price' in sheets else pd.DataFrame(),
                    'IncomeStatement': pd.read_excel(xls, 'IncomeStatement') if 'IncomeStatement' in sheets else pd.DataFrame(),
                    'BalanceSheet': pd.read_excel(xls, 'BalanceSheet') if 'BalanceSheet' in sheets else pd.DataFrame(),
                    'Ratios': pd.read_excel(xls, 'Ratios') if 'Ratios' in sheets else pd.DataFrame()
                }
        except Exception as e:
            return None
    return None

def get_available_tickers():
    base_list = ["FPT", "HPG", "REE", "ACB", "BCM", "BID", "BVH", "CTG", "GVR", "HDB", "MBB", "MSN", "MWG", "PLX", "POW", "SAB", "SHB", "SSB", "SSI", "STB", "TCB", "TPB", "VCB", "VHM", "VIB", "VIC", "VJC", "VND", "VPB", "VRE"]
    if os.path.exists(DATA_DIR):
        local_files = [f.replace("_snapshot.xlsx", "") for f in os.listdir(DATA_DIR) if f.endswith("_snapshot.xlsx")]
        merged = sorted(list(set(base_list + local_files)))
        return [x for x in merged if x not in ['VNINDEX', 'VN30']]
    return sorted(base_list)

def download_ticker_data(ticker):
    import time
    from vnstock import Vnstock
    from datetime import datetime, timedelta
    stock = Vnstock()
    END_DATE = datetime.now().strftime('%Y-%m-%d')
    START_DATE = (datetime.now() - timedelta(days=1095)).strftime('%Y-%m-%d')
    
    data_dict = {}
    stock_obj = stock.stock(symbol=ticker, source='VCI')
    try: data_dict['Price'] = stock_obj.quote.history(start=START_DATE, end=END_DATE)
    except: pass
    time.sleep(2)
    try: data_dict['IncomeStatement'] = stock_obj.finance.income_statement(period='yearly')
    except: data_dict['IncomeStatement'] = pd.DataFrame()
    time.sleep(2)
    try: data_dict['BalanceSheet'] = stock_obj.finance.balance_sheet(period='yearly')
    except: data_dict['BalanceSheet'] = pd.DataFrame()
    time.sleep(2)
    try: data_dict['Ratios'] = stock_obj.finance.ratio()
    except: data_dict['Ratios'] = pd.DataFrame()
    
    os.makedirs(DATA_DIR, exist_ok=True)
    file_path = os.path.join(DATA_DIR, f"{ticker}_snapshot.xlsx")
    with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
        for sheet_name, df in data_dict.items():
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = [c[-1] if isinstance(c, tuple) else c for c in df.columns]
                df.to_excel(writer, sheet_name=sheet_name, index=False)

# --- LANGUAGE TRANSLATION DICTIONARY ---
_LANG = {
    'Kích hoạt Auto-downloader: Đang tải dữ liệu gốc BCTC từ Internet... (Chờ khoảng 10 giây)': 'Activating Auto-downloader: Fetching financial data from the Internet... (Wait ~10 seconds)',
    '❌ Không tìm thấy dữ liệu Báo cáo Tài chính. Thử lại sau.': '❌ Financial statement data not found. Please try again later.',
    'Chuyển đổi dữ liệu kế toán thành quyết định chiến lược (Strategic Advisor)': 'Transforming accounting data into strategic decisions (Strategic Advisor)',
    '**📂 Nguồn dữ liệu Offline:**': '**📂 Offline Data Source:**',
    'Chọn Doanh nghiệp Phân tích:': 'Select Company for Analysis:',
    'CFO Workspace': 'CFO Workspace',
    '1. Cấu Trúc Lợi Nhuận (KPI Trees)': '1. Profit Structure (KPI Trees)',
    '2. Mô Hình Kịch Bản Chiến Lược (Cases)': '2. Strategic Scenario Modeling (Cases)',
    '3. Tái Cân Bằng Danh Mục (Rebalancing)': '3. Portfolio Rebalancing',
    '3. Portfolio Wealth Management': '3. Portfolio Wealth Management',
    'Doanh Thu Thuần': 'Net Revenue',
    'Lợi Nhuận Ròng': 'Net Profit',
    'Biên LN Gộp': 'Gross Margin',
    'Biên LN Ròng': 'Net Margin',
    '🌊 Sơ đồ Dòng chảy Tiền tệ (Sankey Diagram)': '🌊 Money Flow Visualization (Sankey Diagram)',
    'Trực quan hóa Dòng tiền: Doanh thu đi về đâu? Điểm rò rỉ (Leakage) của dòng vốn ở đâu?': 'Visualizing Cash Flow: Where does revenue go? Where are the capital leakages?',
    '🤖 Cố vấn Chiến lược (Diagnostic Insights)': '🤖 Strategic Advisor (Diagnostic Insights)',
    '⚙️ Thiết lập Tham số (Tùy chỉnh Thủ công)': '⚙️ Parameter Setup (Manual Tuning)',
    '🎛️ Nạp Kịch Bản Nhanh (Scenario Presets)': '🎛️ Quick Scenario Presets',
    '🟢 Kịch bản Tích cực (Best Case)': '🟢 Best Case Scenario',
    '⚪ Kịch bản Cơ sở (Base Case)': '⚪ Base Case Scenario',
    '🔴 Kịch bản Xấu (Worst Case)': '🔴 Worst Case Scenario',
    '📉 Biến động Giá Vốn (%)': '📉 COGS Fluctuation (%)',
    '📈 Tăng trưởng Doanh thu (%)': '📈 Revenue Growth (%)',
    '🏢 Biến động Chi phí HĐ (%)': '🏢 SG&A Fluctuation (%)',
    '📊 Chênh lệch Kịch Bản (Financial Impact)': '📊 Scenario Variance (Financial Impact)',
    '🛒 Xây dựng Danh mục': '🛒 Build Portfolio',
    'Chọn các mã gia nhập Danh mục của bạn:': 'Select tickers to add to your Portfolio:',
    '**Quá khứ (Thực tế năm nay)**': '**Historical (Actual This Year)**',
    '**Tương lai (Dự phóng năm sau)**': '**Future (Projected Next Year)**',
    'Doanh thu': 'Revenue',
    'Giá vốn': 'COGS',
    '### 🛡️ Chiến lược Giảm thiểu rủi ro (Mitigation Strategies)': '### 🛡️ Risk Mitigation Strategies',
    '**Phân bổ tỷ trọng vốn (Weights):**': '**Capital Allocation Weights:**',
    'Tỷ trọng': 'Weight',
    'Vui lòng chọn ít nhất 2 mã cổ phiếu để cấu trúc một danh mục chống rủi ro hệ thống.': 'Please select at least 2 stocks to build an unsystematic risk-hedged portfolio.',
    'Tổng tỷ trọng phải bằng 100%. Vui lòng điều chỉnh lại.': 'Total weights must equal 100%. Please adjust.',
    '🎯 Khám sức khỏe Danh mục (MPT Assessment)': '🎯 Portfolio Health Assessment (MPT)',
    'Lợi nhuận Kỳ vọng (Năm)': 'Expected Return (Annual)',
    'Mức độ Biến động (Rủi ro)': 'Volatility (Risk)',
    'Sharpe Ratio (Hiệu quả Vốn)': 'Sharpe Ratio (Capital Efficiency)',
    '### 🔄 Khuyến nghị Tái cân bằng (Rebalancing Robot)': '### 🔄 Rebalancing Robot Recommendation',
    
    # AI Forecasting Module
    'Dự báo & Xu hướng (AI Forecasting)': 'Forecasting & Trends (AI)',
    'Sử dụng Hồi quy Tuyến tính (Linear Regressor ML) dò tìm chu kỳ và dự phóng 3 mốc tiếp theo.': 'Using Linear Regression (ML) to detect cycles and project the next 3 points.',
    'Thực tế': 'Actual',
    'Vùng Kịch bản': 'Scenario Band',
    'Dự báo': 'Forecast',
    'Dự báo Doanh thu (3 kỳ tới)': 'Revenue Forecast (Next 3 Periods)',
    'Dự báo Lợi nhuận Ròng (3 kỳ tới)': 'Net Profit Forecast (Next 3 Periods)',
    'Tăng trưởng / Mở rộng': 'Growth / Expansion',
    'Giảm sút / Cảnh báo': 'Decline / Warning',
    'Mở rộng': 'Expanding',
    'Thu hẹp': 'Contracting',
    'Nhận định từ Mô Hình Dự Báo (AI Insights):': 'Insights from Forecasting Model (AI Insights):',
    'Dựa trên quỹ đạo dữ liệu hồi quy tuyến tính (Linear Regression) quét qua thời gian, hệ thống ML nhận thấy chu kỳ Doanh thu của doanh nghiệp đang cho thấy trạng thái': 'Based on the trajectory of linear regression over time, the ML system observes the company\'s Revenue cycle is showing a state of',
    'gia tốc': 'acceleration',
    'T/kỳ': 'Billion/period',
    'Dự phóng tại phần ngọn T+3, Doanh thu có thể tịnh tiến tới ngưỡng': 'Projected at the T+3 mark, Revenue could smoothly reach the threshold of',
    'T': 'Billion VND',
    'Song song đó, Lợi nhuận Ròng có quỹ đạo cốt lõi': 'Simultaneously, Net Profit\'s core trajectory is',
    'Mô hình vạch ra vùng kịch bản dung sai Biên độ 10-15% (Vùng dải màu nhạt) bám sát theo độ lệch chuẩn tương lai thay vì cắm thẳng 1 con số vô hồn.': 'The model outlines a scenario tolerance band of 10-15% (light shaded area) closely tracking future standard deviation rather than fixing a rigid number.',
    'Cần ít nhất 2 kỳ dữ liệu thực tế để mô hình AI thiết lập lưới dự báo.': 'At least 2 periods of historical data are required for the AI model to establish the forecasting grid.',
    
    # Text dài Module 1
    '**🔍 Câu hỏi đặt ra cho {} từ Góc nhìn Quản trị:**': '**🔍 Management Perspective Questions for {}:**',
    '* "Tại sao doanh thu ghi nhận {} T nhưng lợi nhuận thực tế lõi chỉ đổ về {} T?"': '* "Why is recorded revenue {} T, but core profit realization is only {} T?"',
    '* "Chi phí giá vốn chiếm tỷ trọng {}%. Đây là rào cản Kỹ thuật năng suất hay do Giá nguyên vật liệu chuỗi cung ứng tăng?"': '* "COGS accounts for {}%. Is this a productivity bottleneck or driven by rising supply chain material costs?"',
    '* "Tỷ lệ hao hụt từ Lợi nhuận gộp xuống Lợi nhuận ròng là rất lớn. Giải pháp thắt chặt dòng rò rỉ này ở đâu mà không làm ảnh hưởng tăng trưởng dài hạn?"': '* "The leakage from Gross Profit to Net Profit is severe. Where can we tighten this flow without damaging long-term growth?"',
    '*➔ Vai trò của FP&A: Khác với Kế toán chỉ công bố con số {} T. Là một Business Partner, hệ thống đề xuất ban lãnh đạo tập trung Review lại hạng mục Chi phí SG&A.*': '*➔ FP&A Role: Unlike Accounting which merely reports the {} T figure, as a Business Partner, the system recommends leadership review SG&A expenses.*',
    
    # Text dài Module 2
    '⚠️ CẢNH BÁO SUY THOÁI LỢI NHUẬN: Kịch bản rủi ro làm thất thoát {} T lợi nhuận.': '⚠️ PROFIT RECESSION WARNING: The risk scenario causes a leakage of {} T in profit.',
    '**Trigger Points & Kế hoạch hành động:**': '**Trigger Points & Action Plan:**',
    '- **Quản trị tỷ suất:** Rà soát lại rổ sản phẩm hiện tại, sản phẩm nào chỉ tạo doanh thu ảo nhưng không đóng góp Biên lợi nhuận thì mạnh tay cắt bỏ.': '- **Margin Management:** Review the current product portfolio; aggressively cut products that generate vanity revenue without contributing to margins.',
    '- **Quản trị chi phí:** Giải phóng nhân sự dôi dư (Freeze Hiring), cắt giảm ngân sách Marketing chưa ra chuyển đổi.': '- **Cost Control:** Release redundant personnel (Hiring Freeze), cut Marketing budgets that yield no conversion.',
    '- **Tái đàm phán:** Khẩn cấp làm việc với chuỗi cung ứng để ép giá vốn (COGS) xuống mức an toàn.': '- **Renegotiation:** Urgently negotiate with the supply chain to compress COGS to safe levels.',
    
    '✅ KỊCH BẢN TĂNG TRƯỞNG LÝ TƯỞNG: Lợi nhuận đột phá thêm {} Tỷ VNĐ.': '✅ IDEAL GROWTH SCENARIO: Profit breaks out with an additional {} Billion VND.',
    '**Khuyến nghị Phân bổ Vốn (Capital Allocation):**': '**Capital Allocation Recommendation:**',
    '- Trích lập quỹ dự phòng cho chu kỳ sóng gió kế tiếp.': '- Establish reserve funds for the next volatile cycle.',
    '- Đẩy mạnh R&D (Phát triển sản phẩm) nhằm nới rộng Con hào kinh tế (Moat).': '- Accelerate R&D (Product Development) to widen the Economic Moat.',
    '- Trả cổ tức tiền mặt để duy trì niềm tin Cổ đông.': '- Distribute cash dividends to sustain Shareholder confidence.',
    
    # Text Module 2 - Modeling
    '2. Các Bảng tính phụ trợ (Supporting Schedules)': '2. Supporting Schedules',
    'Để các con số trong 3 báo cáo trên chính xác, bạn cần các bảng tính chi tiết bên dưới:': 'For the numbers in the financial statements to be accurate, you need the detailed schedules below:',
    'Bảng khấu hao (Depreciation & Amortization)': 'Depreciation & Amortization Schedule',
    'Tính toán giá trị tài sản hao mòn theo thời gian.': 'Calculates asset depreciation over time.',
    'Bảng tính nợ (Debt Schedule)': 'Debt Schedule',
    'Theo dõi số dư nợ gốc và lãi vay phải trả.': 'Tracks principal balance and interest payable.',
    'Bảng vốn lưu động (Working Capital Schedule)': 'Working Capital Schedule',
    'Quản lý các khoản phải thu, phải trả và hàng tồn kho.': 'Manages receivables, payables, and inventory.',
    'Năm': 'Year',
    'Giá trị Tài sản đầu kỳ': 'Beginning Asset Value',
    'Khấu hao trong kỳ': 'Depreciation Expense',
    'Giá trị Tài sản cuối kỳ': 'Ending Asset Value',
    'Nợ đầu kỳ': 'Beginning Debt',
    'Trả nợ gốc': 'Principal Repayment',
    'Lãi vay (10%)': 'Interest Expense (10%)',
    'Nợ cuối kỳ': 'Ending Debt',
    'Khoản phải thu (AR)': 'Accounts Receivable (AR)',
    'Hàng tồn kho (INV)': 'Inventory (INV)',
    'Khoản phải trả (AP)': 'Accounts Payable (AP)',
    'Vốn lưu động ròng': 'Net Working Capital (NWC)',
    
    # Valuation & Outputs
    '3. Định giá và Phân tích kết quả (Valuation & Outputs)': '3. Valuation & Outputs',
    'Sau khi có dự báo, chúng ta cần biết doanh nghiệp "đáng giá" bao nhiêu.': 'After forecasting, we need to know how much the business is "worth".',
    '**DCF (Discounted Cash Flow)**: Phương pháp chiết khấu dòng tiền để tìm giá trị hiện tại của doanh nghiệp.': '**DCF (Discounted Cash Flow)**: Discount rate method to find the intrinsic present value of the business.',
    '**Các chỉ số tài chính**: Tính toán các tỷ số như ROE, ROA dự phóng.': '**Financial Metrics**: Calculate projected ratios such as ROE, ROA.',
    'Tỷ suất chiết khấu (r - Discount Rate) %': 'Discount Rate (r) %',
    'Tăng trưởng dài hạn (g - Terminal Growth) %': 'Terminal Growth (g) %',
    'Giá trị Nội tại (Intrinsic Value / PV)': 'Intrinsic Value (PV)',
    'ROE Kỳ vọng': 'Expected ROE',
    'ROA Kỳ vọng': 'Expected ROA',
    '🔍 Xem chi tiết thông số đầu vào (Calculation Breakdown)': '🔍 View Calculation Breakdown',
    'Dòng tiền Dự Kiến (CF1, CF2...)': 'Expected Cash Flows (CF1, CF2...)',
    'Giá trị Thanh lý (Terminal Value - TV)': 'Terminal Value (TV)',
    'Vốn Chủ Sở Hữu (Equity)': 'Equity',
    'Tổng Tài Sản (Total Assets)': 'Total Assets',
    '⚠️ Cảnh báo Đốt tiền (Cash Burn): Dòng tiền dự phóng bị âm dẫn đến DCF vô nghĩa. Giá trị Nội tại đã được tự động chuyển sang Phương pháp Tài sản Ròng (NAV - dựa trên Vốn CSH).': '⚠️ Cash Burn Warning: Projected cash flow is negative making DCF irrelevant. Intrinsic Value defaults to Net Asset Value (NAV - based on Equity).',
    'Lưu ý chuẩn Institutional Grade': 'Institutional Grade Note',
    'Mô hình đang định giá dựa trên tài sản do hiệu quả hoạt động (ROE/ROA) chưa đạt kỳ vọng. NAV theo lý thuyết = Giá trị thị trường Tài sản - Nợ phải trả, tuy nhiên nếu giá trị sổ sách sát với thực tế, việc dùng Vốn chủ sở hữu làm NAV là hoàn toàn hợp lý.': 'The model is valuing based on assets because operational efficiency (ROE/ROA) has not met expectations. Theoretical NAV = Market Value of Assets - Liabilities. However, if book value is close to reality, using Equity as NAV is perfectly reasonable.',
    'Chỉ số P/B (Price-to-Book)': 'P/B Ratio (Price-to-Book)',
    'Vốn hóa thị trường hiện tại': 'Current Market Capitalization',
    'rẻ hơn': 'cheaper (undervalued)',
    'đắt hơn': 'more expensive (overvalued)',
    'so với Giá trị sổ sách (NAV)': 'compared to Book Value (NAV)',
    'Tỷ lệ P/B': 'P/B Ratio',
    
    # Sensitivity Analysis 
    '4. Phân tích Độ nhạy (Sensitivity Analysis)': '4. Sensitivity Analysis (Risk Matrix)',
    'Mô phỏng rủi ro đặc thù theo từng nhóm ngành khi 2 biến số vĩ mô/vi mô thay đổi đồng thời (Tác động lên Lợi nhuận Ròng).': 'Simulates sector-specific risks when 2 macro/micro variables change simultaneously (Impact on Net Profit).',
    'Tăng trưởng Doanh thu / Cầu (%)': 'Revenue / Demand Growth (%)',
    'Biến động Chi phí / Cung (%)': 'Cost / Supply Fluctuation (%)',
    'Tăng trưởng Tín dụng (%)': 'Credit Growth (%)',
    'Biến động NIM (%)': 'NIM Fluctuation (%)',
    'Tỷ lệ Hấp thụ Dự án (%)': 'Project Absorption Rate (%)',
    'Lãi suất Vay (%)': 'Borrowing Interest Rate (%)',
    'Giá bán Đầu ra (%)': 'Selling Price (%)',
    'Giá Nguyên liệu Đầu vào (%)': 'Input Material Cost (%)',
    'Tăng trưởng SSS/Sức mua (%)': 'SSS / Purchasing Power Growth (%)',
    'Biến động Chi phí SG&A (%)': 'SG&A Expense Fluctuation (%)',
    'Hệ số Lấp đầy (Load Factor) (%)': 'Load Factor (%)',
    'Giá Nhiên liệu (Jet A1) (%)': 'Fuel Price (Jet A1) (%)',
    'Doanh thu Chuyển đổi số (%)': 'Digital Transformation Revenue (%)',
    'Chi phí Nhân sự IT (%)': 'IT Personnel Cost (%)',
    'Xấu nhất': 'Worst',
    'Nền': 'Base',
    'Tối ưu': 'Best',
    'Đột phá (>+10%)': 'Breakthrough (>+10%)',
    'Tăng trưởng': 'Growth',
    'Cơ sở (Base)': 'Base Case',
    'Suy giảm': 'Decline',
    'Thua lỗ (<0)': 'Loss (<0)',
    'Chú giải màu sắc:': 'Color Legend:',
    
    # Text dài Module 3
    '3. Portfolio Wealth Management': '3. Portfolio Wealth Management',
    '🛒 Xây dựng Danh mục': '🛒 Portfolio Construction',
    'Chọn các mã gia nhập Danh mục của bạn:': 'Select tickers to join your Portfolio:',
    'Vui lòng chọn ít nhất 2 mã cổ phiếu để cấu trúc một danh mục chống rủi ro hệ thống.': 'Please select at least 2 stocks to construct a system-risk-proof portfolio.',
    '**Phân bổ tỷ trọng vốn (Weights):**': '**Capital Allocation (Weights):**',
    'Tỷ trọng': 'Weight',
    'Tổng tỷ trọng phải bằng 100%. Vui lòng điều chỉnh lại.': 'Total weight must equal 100%. Please adjust.',
    
    '🎯 Tình trạng Danh mục (Current Portfolio Status)': '🎯 Current Portfolio Status',
    'Tỷ trọng Hiện tại (Current Allocation)': 'Current Allocation',
    'Ma trận Tương quan Rủi ro (Correlation Heatmap)': 'Correlation Heatmap',
    'Đường cong Markowitz (Monte Carlo: 5000 Kịch bản)': 'Markowitz Frontier (Monte Carlo: 5000 Scenarios)',
    'Danh mục Ngẫu nhiên': 'Random Portfolios',
    'Danh mục của bạn': 'Your Portfolio',
    'Điểm Tối ưu (Max Sharpe)': 'Optimal Point (Max Sharpe)',
    '🔄 Cố vấn Tái cơ cấu & Quản trị Rủi ro (Rebalancing)': '🔄 Rebalancing & Risk Advisory',
    'Gợi ý Danh mục Tối ưu (Max Sharpe Ratio)': 'Max Sharpe Portfolio Recommendation',
    'Mã CP': 'Ticker',
    'Hiện tại': 'Current',
    'Tối ưu (Gợi ý)': 'Optimal (Suggested)',
    'Tính toán Phí Chuyển đổi (Rebalancing Costs)': 'Rebalancing Cost Calculation',
    'NÊN ĐẢO DANH MỤC!': 'SHOULD REBALANCE!',
    'Lợi nhuận kỳ vọng tăng': 'Expected return increases',
    'trong khi chi phí cơ cấu (Thuế+Phí) ước tính chỉ tốn': 'while switching cost (Fee+Tax) is roughly',
    'CÂN NHẮC KỸ!': 'CONSIDER CAREFULLY!',
    'Biên lợi nhuận phụ trội': 'The extra expected return',
    'gần như bị ăn mòn hết bởi chi phí xào chẻ danh mục': 'is largely consumed by the friction cost of rebalancing',
    'Bạn nên Hold (Giữ nguyên).': 'You should Hold.',
    'HOÀN HẢO!': 'PERFECT!',
    'Danh mục của bạn hiện đã nằm ở mức hiệu quả cao nhất của đường chân trời Markowitz.': 'Your portfolio is optimally positioned on the Markowitz efficient frontier.',
    '📉 Khảo nghiệm Sức chịu đựng (Stress Testing)': '📉 Stress Testing (Historical Crises)',
    'Mô phỏng thảm họa Thiên nga đen (Black Swan):': 'Black Swan Event Simulation:',
    'Với độ nhạy rủi ro hệ thống (Beta Proxy) ước tính  ≈ ': 'With an estimated systemic risk sensitivity (Beta Proxy) ≈ ',
    'thuật toán AI ước lượng Mức sụt giảm tối đa (Max Drawdown) mà bạn có thể phải gánh chịu là:': 'the AI estimates the Maximum Drawdown you might incur is:',
    'Khủng hoảng Vĩ mô / Bắt bớ (Kịch bản 2022):': 'Macro Crisis / Arrests (2022 Scenario):',
    'Đại suy thoái Toàn cầu (Kịch bản 2008):': 'Global Great Recession (2008 Scenario):',
    '🪄 Tự động Áp dụng Tỷ trọng Tối ưu': '🪄 Auto-Apply Optimal Weights',
    
    '- Cổ phiếu mang trọng số cao nhất hiện tại là **{}** ({}%).': '- The highest weighted stock is currently **{}** ({}%).',
    '⚠️ RỦI RO LỆCH TÂM: Khuyến nghị chốt lời bớt {} và mua bù các mã khác để đưa tỷ trọng về mức an toàn (< 50%).': '⚠️ CONCENTRATION RISK: Recommend taking partial profits on {} and reallocating to other tickers to restore safe weights (< 50%).',
    '✅ Danh mục đang được phân bổ khá đồng đều, an toàn trước các cú sốc ngành cục bộ.': '✅ Portfolio is well-diversified, hedged against local sector shocks.',
    '💡 Strategic Insight: Trong kỷ nguyên AI, \'Không bỏ tất cả trứng vào một rổ\' chưa đủ, Cố vấn tài chính phải biết tốc độ va đập của những quả trứng trong rổ đó (Hỗ trợ hệ số tương quan Covariance).': '💡 Strategic Insight: In the AI era, \'Don\'t put all your eggs in one basket\' is not enough. A financial advisor must know the collision velocity of the eggs inside the basket (Supported by Correlation).',
    'Không đủ dữ liệu giá đóng cửa Offline để tính toán cho một số mã đã chọn.': 'Insufficient Offline close price data to compute portfolio for some selected tickers.',
    
    'Strategic Insights (Gợi ý chiến lược):': 'Strategic Insights:',
    'Giá trị Nội tại (Intrinsic Value) trả lời câu hỏi: Doanh nghiệp này thực sự đáng giá bao nhiêu tiền dựa trên khả năng sinh lời hoặc tài sản cốt lõi? Nếu Giá thị trường đang thấp hơn Giá trị Nội tại, đồng thời P/B < 1.0, đây thường là Vùng mua an toàn (Margin of Safety).': 'Intrinsic Value answers the question: How much is this business truly worth based on its earning power or core assets? If the Market Price is below the Intrinsic Value and P/B < 1.0, this is typically a Margin of Safety buying zone.',
    'Công cụ Quản trị Rủi ro (Risk Matrix) trả lời câu hỏi "Chuyện gì xảy ra nếu...?". Vùng màu đỏ đại diện cho các kịch bản đe dọa trực tiếp đến cấu trúc vốn. Hãy đặc biệt chú ý đến biến trục Y (Core driver), vì chỉ một thay đổi nhỏ cũng có thể khiến lợi nhuận bốc hơi nhanh chóng.': 'The Risk Matrix answers the question "What happens if...?". Red zones represent scenarios that directly threaten the capital structure. Pay special attention to the Y-axis variable (Core driver), as even a minor change can cause profits to rapidly evaporate.',
    'Khoảng cách giữa Danh mục Hiện tại (Ngôi sao đỏ) và Điểm Tối ưu (Kim cương vàng) chính là phần lợi nhuận bạn đang bỏ quên trên bàn do phân bổ vốn chưa hợp lý. Hãy sử dụng Cố vấn Tái cơ cấu bên dưới để thu hồi phần lợi nhuận này.': 'The gap between your Current Portfolio (Red Star) and the Optimal Point (Yellow Diamond) is the profit you are leaving on the table due to inefficient capital allocation. Use the Rebalancing Advisor below to reclaim this profit.',
    
    'Tương quan Dương (+1)': 'Positive Correlation (+1)',
    'Hai mã di chuyển cùng chiều. Nếu bạn mua HPG và HSG, bạn không hề đa dạng hóa, bạn chỉ đang nhân đôi rủi ro.': 'Two stocks move in the same direction. If you buy HPG and HSG, you are not diversifying, you are simply doubling the risk.',
    'Tương quan Bằng 0 (0)': 'Zero Correlation (0)',
    'Hai mã không có mối liên hệ nào. Trạng thái tốt để giảm rủi ro hệ thống.': 'No connection between two stocks. Good state to reduce systemic risk.',
    'Tương quan Âm (-1)': 'Negative Correlation (-1)',
    'Hai mã di chuyển ngược chiều. Đây là chén thánh trong hedging. Khi mã này giảm, mã kia tăng để bù đắp lại.': 'Stocks move in opposite directions. This is the holy grail in hedging. When one drops, the other rises to compensate.',
    
    'Lượt truy cập Web': 'Web Visitors',
    
    '📌 Lưu ý: Chuyên trang này được tối ưu hóa để phân tích báo cáo cho nhóm Ngành lớn & VN30.': '📌 Note: This specialized page is optimized for analyzing reports of Large Caps & VN30 group.',
    '🗓️ Cập nhật Dữ liệu (Offline Mode): Toàn bộ dữ liệu biểu đồ, định giá và báo cáo tài chính trên hệ thống được chốt cố định đến hết giao dịch ngày hiện tại nhằm phục vụ chấm điểm năng lực thuật toán.': '🗓️ Data Update (Offline Mode): All charts, valuations, and financial report data on the system are firmly frozen at the end of the current trading day to benchmark algorithmic performance.',
    '⚖️ DỰ ÁN CÁ NHÂN (PORTFOLIO PROJECT): Trang web này là một dự án Mã nguồn mở mang tính chất Học thuật & Giáo dục (Data Science & Machine Learning Portfolio). Tuyên bố miễn trừ trách nhiệm: Các dữ liệu và phân tích (AI/ML) trên Dashboard này chỉ mang tính chất tham khảo, mô phỏng học thuật và không phải là lời khuyên đầu tư tài chính. Nguồn dữ liệu thô: Vnstock.': '⚖️ PORTFOLIO PROJECT: This website is an open-source project for Academic & Educational purposes (Data Science & Machine Learning Portfolio). Disclaimer: Data and analysis (AI/ML) on this Dashboard are for reference and academic simulation only, and do not constitute financial investment advice. Raw data source: Vnstock.',
    '👉 **Nếu bạn muốn xem thêm dự án khác hãy [nhấp vào đây](https://hoanhkhoa.vercel.app)**': '👉 **If you want to view more projects, please [click here](https://hoanhkhoa.vercel.app)**',
    
    # 4. About Me
    'Liên hệ': 'Contact',
    'Giới thiệu bản thân': 'About Me',
    'Xin chào, tôi là Khoa.': 'Hello, I am Khoa.',
    'Chào mừng bạn đến với dự án cá nhân của tôi — một hệ thống được ấp ủ và phát triển từ niềm đam mê sâu sắc với thị trường tài chính Việt Nam.': 'Welcome to my personal project — a system nurtured and developed from a deep passion for the Vietnamese financial market.',
    'Để tối ưu hóa quá trình xây dựng, tôi đã ứng dụng Google Antigravity. Nền tảng phát triển AI thế hệ mới này giúp tôi vượt qua những rào cản của việc viết code thủ công, từ đó dồn toàn bộ tâm trí vào việc định hình ý tưởng và hoàn thiện logic phân tích cốt lõi.': 'To optimize the development process, I utilized Google Antigravity. This next-generation AI development platform helped me overcome the barriers of manual coding, allowing me to fully focus on shaping ideas and perfecting the core analytical logic.',
    'Nếu bạn ghé thăm trang web này từ CV của tôi, hy vọng hệ thống này sẽ là minh chứng rõ nét nhất: với tôi, kiến thức không chỉ nằm trên giấy tờ, mà phải được chuyển hóa thành năng lực thực thi và sản phẩm vận hành thực tế.': 'If you are visiting this site from my CV, I hope this system serves as the clearest proof: for me, knowledge doesn\'t just reside on paper, but must be transformed into execution capability and practical, operational products.',
    'Trân trọng,': 'Sincerely,',
    
    # Text mở rộng C-Level CFO Dashboard
    'Hồ sơ Sức khỏe Tài chính (Financial Health)': 'Financial Health Profile',
    'DOANH THU': 'REVENUE',
    'TỔNG GIÁ VỐN': 'Total COGS',
    'LỢI NHUẬN GỘP': 'Gross Profit',
    'BIÊN LN GỘP %': 'Gross Profit %',
    'LỢI NHUẬN RÒNG': 'Net Profit',
    'BIÊN LN RÒNG %': 'Net Profit %',
    'Mục tiêu:': 'Goal:',
    'Thu nhập Hoạt động qua các năm': 'Operating Profit Over Time',
    'Lợi nhuận Ròng qua các năm': 'Net Profit Over Time',
    'Giá vốn': 'COGS',
    'Doanh thu': 'Revenue',
    'Tài sản & Nguồn vốn': 'Assets & Liabilities',
    'Tổng Tài sản': 'Total Assets',
    'Tiền & TĐ Tiền': 'Cash & Bank Bal.',
    'Tổng Nợ phải trả': 'Liabilities Total',
    'Vốn Chủ Sở Hữu': 'Equity',
    'Tài sản Ngắn hạn': 'Current Assets',
    'Ký quỹ, Tạm ứng..': 'Deposits, Adv..',
    'Nợ Ngắn hạn': 'Current Liab',
    'Nợ Dài hạn': 'Long-term Liab',
    'Tài sản Cố định': 'Fixed Assets',
    'Tài sản Dài hạn': 'Non-Current Assets',
    'Tổng Nguồn vốn': 'Total Resources',
    'Phải thu Khách hàng': 'Trade Receivables',
    'Phải trả Người bán': 'Trade Payables',
    'Cơ cấu Tổng Chi phí': 'Total Expenses Breakdown',
    'Giá vốn Hàng bán': 'Cost of Sales',
    'Chi phí Quản lý': 'Admin Expenses',
    'Chi phí Bán hàng': 'Selling Expenses',
    'Chi phí Tài chính': 'Financial Expenses',
    'Chi phí Khác': 'Other Expenses',
    'Bộ lọc Thời gian': 'Time Filter',
    'Khoảng thời gian:': 'Time Range:',
    'Toàn thời gian (4 Kỳ)': 'All Time (4 Periods)',
    '2 Kỳ gần nhất': 'Last 2 Periods',
    '1 Kỳ gần nhất': 'Most Recent Period',
    'Khoan sâu Phân tích (Drill-down Pane)': 'Drill-down Analysis View',
    'Click vào bất kỳ cột biểu đồ nào ở trên (Thu nhập Hoạt động) để mở tính năng Drill-down.': 'Click any bar above (in Operating Profit over Time) to open Drill-down features.',
    'CHI PHÍ TRẢ LÃI': 'Interest Expenses',
    'THU NHẬP LÃI THUẦN': 'Net Interest Income',
    'TỶ LỆ LÃI THUẦN %': 'Net Int. Margin %',
    'Chi phí lãi': 'Int. Expenses',
    'Tài sản Sinh lãi & Nguồn huy động': 'Earning Assets & Funding Sources',
    'Chỉ số sinh lời (Profitability)': 'Profitability Metrics',
    'Tăng trưởng Doanh thu (YoY)': 'Revenue Growth (YoY)',
    'Tiền mặt (Cash)': 'Cash Balance',
    '2. Phân tích Biến động (Variance Analysis: BvA)': '2. Variance Analysis (BvA)',
    'Giả lập Ngân sách (Budget) = Thực tế năm trước x 115%': 'Simulated Budget = Prior Year Actuals * 115%',
    'Khác biệt so với Ngân sách': 'Variance to Budget',
    'Vượt ngân sách': 'Above Budget',
    'Hụt ngân sách': 'Below Budget',
    '3. Quản lý Chi phí vận hành (OpEx Management)': '3. Operating Expenses Management',
    'Chi phí Bán hàng (Selling)': 'Selling Expenses',
    'Chi phí Quản lý (G&A)': 'General & Admin (G&A)',
    'Tỷ lệ SG&A trên Doanh thu (%)': 'SG&A to Revenue Ratio (%)',
    '4. Dự báo và Xu hướng (Forecasting & Trends)': '4. Forecasting & Trends',
    'Lịch sử và Dự phóng Doanh thu / Lợi nhuận': 'Historical & Projected Revenue / Profit',
    'Dự phóng (Trendline)': 'Projected (Trendline)',
    '5. Các Chỉ số đặc thù theo Cấu trúc Ngành (Operational Metrics)': '5. Industry Operational Metrics',
    'Chỉ số Ngân hàng (Banking)': 'Banking Metrics',
    'Chỉ số Sản xuất/Bán lẻ (Manufacturing/Retail)': 'Manufacturing/Retail Metrics',
    'Chỉ số Công nghệ/Dịch vụ (Tech/Services)': 'Tech/Services Metrics',
    'Vòng quay Tồn kho (Lần)': 'Inventory Turnover (Times)',
    'Tốc độ thu hồi công nợ (Ngày)': 'Days Sales Outstanding (Days)',
    'Biên EBIT (%)': 'EBIT Margin (%)',
    
    # New Modules: BvA & Cashflow
    '2. Phân tích Biến động (BvA)': '2. Variance Analysis (BvA)',
    '3. Dự báo Dòng tiền (Cashflow Forecasting)': '3. Cashflow Forecasting',
    'Thực tế so với Ngân sách (Budget vs Actual)': 'Budget vs Actual (BvA) Analysis',
    'Chênh lệch (Variance)': 'Variance',
    'Vượt ngân sách (Favorable)': 'Favorable',
    'Hụt ngân sách (Unfavorable)': 'Unfavorable',
    'Giải thích chênh lệch (Waterfall Chart)': 'Variance Explanation (Waterfall Chart)',
    'Ngân sách (Lãi ròng)': 'Budget (Net Profit)',
    'Vượt/hụt Doanh thu': 'Revenue Variance',
    'Tiết kiệm/Lạm Giá vốn': 'COGS Variance',
    'Tiết kiệm/Lạm Chi phí HĐ': 'SG&A Variance',
    'Khác': 'Other',
    'Thực tế (Lãi ròng)': 'Actual (Net Profit)',
    'Dự báo Dòng tiền & Thanh khoản': 'Cashflow & Liquidity Forecasting',
    'Ngân sách Đầu tư tài sản (CAPEX) - Tỷ VND': 'Capital Expenditure Budget (CAPEX) - Bn VND',
    'Chu kỳ thu tiền (Days Sales Outstanding - DSO)': 'Days Sales Outstanding (DSO)',
    'Chu kỳ thanh toán (Days Payable - DPO)': 'Days Payable Outstanding (DPO)',
    'Dòng tiền Hoạt động (OCF)': 'Operating Cash Flow (OCF)',
    'Dòng tiền Đầu tư (ICF)': 'Investing Cash Flow (ICF)',
    'Dòng tiền Tự do (FCF)': 'Free Cash Flow (FCF)',
    'Số dư Tiền mặt Cuối kỳ': 'Ending Cash Balance',
    'Cảnh báo ĐỎ: Nguy cơ phá sản thanh khoản! Dòng tiền rơi xuống mức âm.': 'RED Warning: Liquidity bankruptcy risk! Cashflow dropped below zero.',
    'Cảnh báo CAM: Quỹ tiền mặt đã chạm ngưỡng rủi ro (dưới mức Safety Stock định trước). Hãy rà soát lại kế hoạch vốn.': 'ORANGE Warning: Cash balance hit risk threshold (below Safety Stock). Review capital plan.',
    'An toàn: Quỹ tiền mặt đảm bảo khả năng thanh toán và duy trì trên mức Safety Stock.': 'Safe: Cash reserve covers obligations and stays above Safety Stock.',
    'Ngưỡng Tiền mặt An toàn (Tỷ VND)': 'Safety Stock of Cash (Bn VND)',
    '(Công thức % BvA = Thực tế/Ngân sách - 1. Nếu là hạng mục Chi phí, số Âm thể hiện sự Tiết kiệm so với Ngân sách và là Tín hiệu Tốt).': '(Formula % BvA = Actual/Budget - 1. For expense items, a Negative number shows Savings vs Budget and is a Good Signal).',
    
    # BvA module - additional translations
    'Giả lập Ngân sách: Vì dữ liệu Báo cáo Tài chính tự động không có số liệu Ngân sách, hệ thống giả định Ngân sách năm nay = Thực tế năm trước * % Tăng trưởng kế hoạch.': 'Simulated Budget: Since financial statement data has no Budget figures, the system assumes Budget = Prior Year Actuals * % Target Growth.',
    'Mục tiêu Tăng trưởng Doanh thu (%)': 'Revenue Growth Target (%)',
    'Ngân sách Giá vốn (% so năm trước)': 'COGS Budget (% vs Prior Year)',
    'Ngân sách Chi phí QLDN/BH (% so năm trước)': 'SG&A Budget (% vs Prior Year)',
    'Hạng mục': 'Line Item',
    'Thực tế': 'Actual',
    'Ngân sách': 'Budget',
    'Chênh lệch (Abs)': 'Variance (Abs)',
    'Đánh giá': 'Rating',
    'Lợi nhuận Gộp': 'Gross Profit',
    'Chi phí HĐKD (SG&A)': 'SG&A Expenses',
    'Lợi nhuận Ròng': 'Net Profit',
    
    # Cashflow module - additional translations
    'Áp dụng phương pháp Gián tiếp (Indirect Method) để dự phóng dòng tiền dựa trên Lợi nhuận kỳ vọng và Cấp vốn Lưu động.': 'Using the Indirect Method to forecast cashflow based on Expected Profit and Working Capital changes.'
}

def t(text):
    if st.session_state.get('lang', '🇻🇳 Tiếng Việt') == '🇬🇧 English':
        return _LANG.get(text, text)
    return text

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    lang_choice = st.radio("🌍 Ngôn ngữ / Language:", ['🇻🇳 Tiếng Việt', '🇬🇧 English'], horizontal=True)
    st.session_state.lang = lang_choice
    
    st.markdown(f"### 👔 {t('CFO Workspace')}")
    selected_module = option_menu(
        menu_title=None, 
        options=["1. FP&A Dashboard", "2. Variance Analysis (BvA)", "3. Cashflow Forecast", "4. Financial Modeling", "5. Wealth Management", "6. About Me"], 
        icons=["diagram-3", "bar-chart-steps", "cash-coin", "calculator", "pie-chart", "person-badge"], 
        default_index=0,
        styles={
            "container": {"background-color": "transparent"},
            "nav-link": {"font-size": "14px", "font-weight": "500", "color": "#1E293B", "--hover-color": "#E2E8F0"},
            "nav-link-selected": {"background-color": "#2563EB", "color": "white", "font-weight": "bold"},
            "icon": {"color": "#64748B"}
        }
    )
    
    st.markdown("---")
    st.markdown(t("**📂 Nguồn dữ liệu Offline:**"))
    tickers = get_available_tickers()
    global_ticker = st.selectbox(t("Chọn Doanh nghiệp Phân tích:"), tickers, index=tickers.index('FPT') if 'FPT' in tickers else 0)

    st.markdown("---")
    
    # --- HIT COUNTER (Cloud-safe) ---
    counter_file = os.path.join(DATA_DIR, "visits.txt")
    if 'visited' not in st.session_state:
        try:
            if os.path.exists(counter_file):
                with open(counter_file, "r") as f:
                    try: count = int(f.read().strip())
                    except ValueError: count = 0
            else: count = 0
            count += 1
            with open(counter_file, "w") as f:
                f.write(str(count))
        except (PermissionError, OSError):
            count = "N/A"
        st.session_state.visited = count
    else:
        count = st.session_state.visited
            
    st.metric(f"👁️ {t('Lượt truy cập Web')}", count)

st.markdown('<div class="main-title">💼 Finance Business Partner</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-title">{t("Chuyển đổi dữ liệu kế toán thành quyết định chiến lược (Strategic Advisor)")}</div>', unsafe_allow_html=True)

# ----------------- HEADER (Hiển thị cố định ở đầu mọi trang) -----------------
t_footer_1 = t('📌 Lưu ý: Chuyên trang này được tối ưu hóa để phân tích báo cáo cho nhóm Ngành lớn & VN30.')
t_footer_2 = t('🗓️ Cập nhật Dữ liệu (Offline Mode): Toàn bộ dữ liệu biểu đồ, định giá và báo cáo tài chính trên hệ thống được chốt cố định đến hết giao dịch ngày hiện tại nhằm phục vụ chấm điểm năng lực thuật toán.')
t_footer_3 = t('⚖️ DỰ ÁN CÁ NHÂN (PORTFOLIO PROJECT): Trang web này là một dự án Mã nguồn mở mang tính chất Học thuật & Giáo dục (Data Science & Machine Learning Portfolio). Tuyên bố miễn trừ trách nhiệm: Các dữ liệu và phân tích (AI/ML) trên Dashboard này chỉ mang tính chất tham khảo, mô phỏng học thuật và không phải là lời khuyên đầu tư tài chính. Nguồn dữ liệu thô: Vnstock.')

st.info(t_footer_1)
st.success(t_footer_2)
st.warning(t_footer_3)
st.markdown(t("👉 **Nếu bạn muốn xem thêm dự án khác hãy [nhấp vào đây](https://hoanhkhoa.vercel.app)**"))
st.markdown("---")

# HỆ THỐNG AUTO-DOWNLOADER (Cloud-safe)
file_path = os.path.join(DATA_DIR, f"{global_ticker}_snapshot.xlsx")
if not os.path.exists(file_path):
    try:
        with st.spinner(t("Kích hoạt Auto-downloader: Đang tải dữ liệu gốc BCTC từ Internet... (Chờ khoảng 10 giây)")):
            download_ticker_data(global_ticker)
            st.cache_data.clear()
    except Exception as e:
        st.warning(f"⚠️ Auto-download failed: {e}")

# THÔNG TIN DỮ LIỆU CỐT LÕI
data = load_local_data(global_ticker)

if not data or data.get('IncomeStatement', pd.DataFrame()).empty:
    st.error(t("❌ Không tìm thấy dữ liệu Báo cáo Tài chính. Thử lại sau."))
    st.stop()

# Xử lý làm sạch tên cột theo Dictionary tiêu chuẩn
is_df = data['IncomeStatement'].copy()
bs_df = data['BalanceSheet'].copy()
rt_df = data['Ratios'].copy()

# Hàm lấy dữ liệu mảng (TimeSeries) 5 năm gần nhất
def get_series(df, keys, max_len=5):
    if df.empty: return []
    cols = {str(c).strip().lower(): c for c in df.columns}
    for k in keys:
        for low_c, orig_c in cols.items():
            if k.lower() in low_c and 'yoy' not in low_c:
                return pd.to_numeric(df[orig_c].head(max_len), errors='coerce').fillna(0).values[::-1].tolist()
    return []

# Hàm lấy nhãn thời gian thực tế (Quý/Năm hoặc Năm)
def get_time_labels(df, max_len=5):
    if df.empty: return [f"T-{i}" for i in range(max_len-1, -1, -1)]
    cols = {str(c).strip().lower(): c for c in df.columns}
    if 'yearreport' in cols:
        yr_list = df[cols['yearreport']].head(max_len).values[::-1]
        if 'lengthreport' in cols:
            q_list = df[cols['lengthreport']].head(max_len).values[::-1]
            labels = []
            for y, q in zip(yr_list, q_list):
                if q in [1, 2, 3, 4]: labels.append(f"Q{int(q)}/{int(y)}")
                else: labels.append(str(int(y)))
            return labels
        return [str(int(y)) for y in yr_list]
    return [f"T-{i}" for i in range(max_len-1, -1, -1)]

# Hàm lấy dữ liệu mảng Cộng dồn (Ví dụ: Chi phí bán hàng + Quản lý Doanh nghiệp)
def get_series_sum(df, keys, max_len=5):
    if df.empty: return []
    cols = {str(c).strip().lower(): c for c in df.columns}
    res = None
    added_cols = set()
    for k in keys:
        for low_c, orig_c in cols.items():
            if k.lower() in low_c and 'yoy' not in low_c and orig_c not in added_cols:
                arr = pd.to_numeric(df[orig_c].head(max_len), errors='coerce').fillna(0).values[::-1]
                if res is None: res = arr
                else: res = res + arr
                added_cols.add(orig_c)
    return res.tolist() if res is not None else []

# Hàm lấy giá trị 1 điểm thời gian (Mới nhất)
def get_val(df, keys):
    if df.empty: return 0.0
    cols = {str(c).strip().lower(): c for c in df.columns}
    for k in keys:
        for low_c, orig_c in cols.items():
            if k.lower() in low_c and 'yoy' not in low_c:
                try: 
                    val = df[orig_c].iloc[0]
                    if pd.notna(val): return float(val)
                except: pass
    return 0.0

def get_val_sum(df, keys):
    if df.empty: return 0.0
    cols = {str(c).strip().lower(): c for c in df.columns}
    total = 0.0
    found = False
    added_cols = set()
    for k in keys:
        for low_c, orig_c in cols.items():
            if k.lower() in low_c and 'yoy' not in low_c and orig_c not in added_cols:
                try: 
                    val = df[orig_c].iloc[0]
                    if pd.notna(val): 
                        total += float(val)
                        found = True
                        added_cols.add(orig_c)
                except: pass
    return total if found else 0.0

# ----------------- PARSE DỮ LIỆU CỐT LÕI (GLOBAL) -----------------
# Detector Ngành (Sector Detector) - Tự động thiết lập Mẫu hình Dashboard (Templates)
is_bank = False
is_sec = False
for c in [str(x).strip().lower() for x in is_df.columns]:
    if 'net interest income' in c or 'thu nhập lãi thuần' in c or 'interest and similar' in c:
        is_bank = True
        break
    if 'brokerage' in c or 'môi giới' in c or 'doanh thu nghiệp vụ' in c or 'chứng khoán' in c or 'fvtpl' in c:
        is_sec = True
        break

rev_keys = ['net sales', 'doanh thu thuần', 'total operating revenue', 'tổng thu nhập hoạt động', 'revenue']
cogs_keys = ['cost of sales', 'giá vốn', 'interest and similar expenses', 'chi phí trả lãi']
gp_keys = ['gross profit', 'lợi nhuận gộp', 'net interest income', 'thu nhập lãi thuần']
sga_keys = ['selling', 'general', 'chi phí bán hàng', 'chi phí quản lý doanh nghiệp', 'operating expenses', 'chi phí hoạt động']
np_keys = ['net profit', 'lợi nhuận sau thuế']

rev = get_val(is_df, rev_keys)
cogs = abs(get_val(is_df, cogs_keys))
gross_profit = get_val(is_df, gp_keys)

if not is_bank:
    if cogs == 0 and gross_profit > 0 and rev > 0:
        cogs = abs(rev - gross_profit)
    if gross_profit == 0 and cogs > 0 and rev > 0:
        gross_profit = rev - cogs
sga = abs(get_val_sum(is_df, sga_keys))
net_profit = get_val(is_df, np_keys)
other_expenses = max(0, gross_profit - sga - net_profit)

# ----------------- PARSE LỊCH SỬ 5 NĂM / DÒNG TIỀN / BIÊN LỢI NHUẬN -----------------
time_len = 5
if selected_module == "1. FP&A Dashboard":
    st.sidebar.markdown(f"### ⏳ {t('Bộ lọc Thời gian')}")
    time_filter_opt = st.sidebar.radio(t("Khoảng thời gian:"), [t("Toàn thời gian (4 Kỳ)"), t("2 Kỳ gần nhất"), t("1 Kỳ gần nhất")])
    if t("1 Kỳ") in time_filter_opt: time_len = 1
    elif t("2 Kỳ") in time_filter_opt: time_len = 2
    else: time_len = 5

rev_series = get_series(is_df, rev_keys, time_len)
np_series = get_series(is_df, np_keys, time_len)
sga_series = get_series_sum(is_df, sga_keys, time_len)
cogs_series = [abs(x) for x in get_series(is_df, cogs_keys, time_len)]
gp_series = get_series(is_df, gp_keys, time_len)

if not is_bank:
    if len(cogs_series) == 0 and len(gp_series) == len(rev_series):
        cogs_series = [abs(r - g) for r, g in zip(rev_series, gp_series)]
    elif len(gp_series) == 0 and len(cogs_series) == len(rev_series):
        gp_series = [r - c for r, c in zip(rev_series, cogs_series)]

y_labels = get_time_labels(is_df, len(rev_series)) if len(rev_series) > 0 else []

ebitda = get_val(rt_df, ['ebitda'])
roe = get_val(rt_df, ['roe (%)', 'roe'])
roa = get_val(rt_df, ['roa (%)', 'roa'])
cash = get_val(bs_df, ['cash and cash equivalents', 'tiền và các khoản tương đương'])

# ================= ROUTING TỚI CÁC PHÂN HỆ =================
if selected_module == "1. FP&A Dashboard":
    # Tính các con số YoY/Goal cho Metricalist Cards
    rev_prev = rev_series[-2] if len(rev_series)>1 else rev
    rev_yoy = ((rev/rev_prev)-1)*100 if rev_prev>0 else 0
    cogs_prev = cogs_series[-2] if len(cogs_series)>1 else cogs
    cogs_yoy = ((cogs/cogs_prev)-1)*100 if cogs_prev>0 else 0
    gp_pct = (gross_profit/rev)*100 if rev>0 else 0
    np_pct = (net_profit/rev)*100 if rev>0 else 0
    
    # Sector Routing Labels
    lbl_rev = t("DOANH THU")
    lbl_cogs = t("CHI PHÍ HĐ ĐẦU TƯ") if is_sec else (t("CHI PHÍ TRẢ LÃI") if is_bank else t("TỔNG GIÁ VỐN"))
    lbl_gp = t("LỢI NHUẬN GỘP") if is_sec else (t("THU NHẬP LÃI THUẦN") if is_bank else t("LỢI NHUẬN GỘP"))
    lbl_gp_pct = t("BIÊN LN GỘP %") if is_sec else (t("TỶ LỆ LÃI THUẦN %") if is_bank else t("BIÊN LN GỘP %"))
    lbl_np = t("LỢI NHUẬN RÒNG")
    lbl_np_pct = t("BIÊN LN RÒNG %")
    lbl_cogs_chart = t("Chi phí Đầu tư") if is_sec else (t("Chi phí lãi") if is_bank else t("Giá vốn"))
    lbl_gp_pct_chart = t("BIÊN LN GỘP %") if is_sec else (t("TỶ LỆ LÃI THUẦN %") if is_bank else t("BIÊN LN GỘP %"))
    
    # 1. TOP 6 METRICS (Metricalist Style)
    html_cards = f"""
    <div class="met-top-row">
        <div class="met-card">
            <div class="met-label">{lbl_rev}</div>
            <div class="met-val teal">{rev/1e9:,.0f} T</div>
            <div class="met-goal">{t("Mục tiêu:")} {rev_prev/1e9:,.0f} T ({rev_yoy:+.2f}%)</div>
        </div>
        <div class="met-card">
            <div class="met-label">{lbl_cogs}</div>
            <div class="met-val red">{cogs/1e9:,.0f} T</div>
            <div class="met-goal">{t("Mục tiêu:")} {cogs_prev/1e9:,.0f} T ({cogs_yoy:+.2f}%)</div>
        </div>
        <div class="met-card">
            <div class="met-label">{lbl_gp}</div>
            <div class="met-val teal">{gross_profit/1e9:,.0f} T</div>
            <div class="met-goal">{t("Mục tiêu:")} {(rev_prev*0.3)/1e9:,.0f} T</div>
        </div>
        <div class="met-card">
            <div class="met-label">{lbl_gp_pct}</div>
            <div class="met-val teal">{gp_pct:.2f}%</div>
            <div class="met-goal">{t("Mục tiêu:")} 30.00%</div>
        </div>
        <div class="met-card">
            <div class="met-label">{lbl_np}</div>
            <div class="met-val {'red' if net_profit<0 else 'teal'}">{net_profit/1e9:,.0f} T</div>
            <div class="met-goal">{t("Mục tiêu:")} {(rev_prev*0.1)/1e9:,.0f} T</div>
        </div>
        <div class="met-card">
            <div class="met-label">{lbl_np_pct}</div>
            <div class="met-val {'red' if np_pct<0 else 'teal'}">{np_pct:.2f}%</div>
            <div class="met-goal">{t("Mục tiêu:")} 10.00%</div>
        </div>
    </div>
    """
    st.markdown(html_cards, unsafe_allow_html=True)
    
    # 2. TWO MIDDLE CHARTS
    mc1, mc2 = st.columns(2)
    with mc1:
        st.markdown(f"<div style='text-align: center; font-weight: 600; margin-bottom: 5px; color: #2C3E50;'>{t('Thu nhập Hoạt động qua các năm')}</div>", unsafe_allow_html=True)
        fig_op = go.Figure()
        fig_op.add_trace(go.Bar(x=y_labels, y=rev_series, name=t("Doanh thu"), marker_color="#1ABC9C"))
        
        # SỬ DỤNG CHUỖI COGS THỰC TẾ thay vì giả lập
        if len(cogs_series) == len(rev_series) and len(cogs_series) > 0:
            real_cogs_series = cogs_series
        else:
            real_cogs_series = [0 for r in rev_series] # Trả về 0 nếu công ty (Ngân hàng) ko tính COGS
            
        fig_op.add_trace(go.Bar(x=y_labels, y=real_cogs_series, name=lbl_cogs_chart, marker_color="#E74C3C"))
        sim_gp_pct = [((r - c)/r)*100 if r>0 else 0 for r, c in zip(rev_series, real_cogs_series)]
        fig_op.add_trace(go.Scatter(x=y_labels, y=sim_gp_pct, mode='lines+markers+text', name=lbl_gp_pct_chart, yaxis="y2", line=dict(color='black', dash='dash'), text=[f"{v:.1f}%" for v in sim_gp_pct], textposition="top center", cliponaxis=False))
        
        y2_min_op, y2_max_op = (min(sim_gp_pct) if sim_gp_pct else 0), (max(sim_gp_pct) if sim_gp_pct else 100)
        fig_op.update_layout(height=280, margin=dict(t=50, b=10, l=10, r=10), barmode='group', plot_bgcolor='rgba(0,0,0,0)',
            yaxis2=dict(overlaying='y', side='right', showgrid=False, range=[y2_min_op - 5, y2_max_op + 15]), showlegend=True, legend=dict(orientation="h", y=1.2, x=0.5, xanchor='center'))
        # Gắn cảm biến Drill-down on_select vào Biểu đồ
        event_op = st.plotly_chart(fig_op, use_container_width=True, on_select="rerun", selection_mode="points", key="op_chart_click")
        
    with mc2:
        st.markdown(f"<div style='text-align: center; font-weight: 600; margin-bottom: 5px; color: #2C3E50;'>{t('Lợi nhuận Ròng qua các năm')}</div>", unsafe_allow_html=True)
        fig_np = go.Figure()
        colors = ['#E74C3C' if v<0 else '#1ABC9C' for v in np_series]
        fig_np.add_trace(go.Bar(x=y_labels, y=np_series, name=t("LỢI NHUẬN RÒNG"), marker_color=colors))
        sim_np_pct = [(n/r)*100 if r>0 else 0 for n, r in zip(np_series, rev_series)]
        fig_np.add_trace(go.Scatter(x=y_labels, y=sim_np_pct, mode='lines+markers+text', name=t("BIÊN LN RÒNG %"), yaxis="y2", line=dict(color='black', dash='dash'), text=[f"{v:.1f}%" for v in sim_np_pct], textposition="top center", cliponaxis=False))
        
        y2_min_np, y2_max_np = (min(sim_np_pct) if sim_np_pct else 0), (max(sim_np_pct) if sim_np_pct else 100)
        fig_np.update_layout(height=280, margin=dict(t=50, b=10, l=10, r=10), plot_bgcolor='rgba(0,0,0,0)',
            yaxis2=dict(overlaying='y', side='right', showgrid=False, range=[y2_min_np - 5, y2_max_np + 15]), showlegend=True, legend=dict(orientation="h", y=1.2, x=0.5, xanchor='center'))
        st.plotly_chart(fig_np, use_container_width=True)

    # 3. BOTTOM ROW
    bc1, bc2 = st.columns(2)
    with bc1:
        st.markdown(f"<div style='text-align: center; font-weight: 600; margin-bottom: 5px; color: #2C3E50;'>{t('Cơ cấu Tài sản & Nguồn vốn Đặc thù')}</div>", unsafe_allow_html=True)
        if is_bank:
            tot_ass = get_val(bs_df, ['total assets', 'tổng cộng tài sản'])
            loans = get_val(bs_df, ['loans and advances to customers', 'cho vay khách hàng'])
            deposits = get_val(bs_df, ['deposits from customers', 'tiền gửi của khách hàng', 'tiền gửi khách hàng'])
            interbank = get_val(bs_df, ['deposits and borrowings from other credit institutions', 'tiền gửi và vay các tctd khác'])
            tot_liab = get_val(bs_df, ['liabilities (bn. vnd)', 'tổng nợ phải trả', 'nợ phải trả', 'liabilities'])
            equity = get_val(bs_df, ['equity', "owner's equity", 'vốn chủ sở hữu'])
            securities = get_val(bs_df, ['investment securities', 'chứng khoán đầu tư', 'trading securities'])
            cash = get_val(bs_df, ['cash and cash', 'tiền và các khoản'])

            assets_html = f"""
            <div class="met-panel">
                <div class="met-grid" style="grid-template-columns: 1fr 1fr;">
                    <div>
                        <div class="met-grid-dark">{tot_ass/1e9:,.0f}</div><div class="met-grid-sub">{t("Tổng Tài sản")}</div>
                        <div class="met-grid-dark">{cash/1e9:,.0f}</div><div class="met-grid-sub">{t("Tiền & TĐ Tiền")}</div>
                        <div style="margin-top:20px;"></div>
                        <div class="met-grid-dark">{tot_liab/1e9:,.0f}</div><div class="met-grid-sub red">{t("Tổng Nợ phải trả")}</div>
                        <div class="met-grid-dark">{equity/1e9:,.0f}</div><div class="met-grid-sub red">{t("Vốn Chủ Sở Hữu")}</div>
                    </div>
                    <div>
                        <div class="met-grid-dark">{loans/1e9:,.0f}</div><div class="met-grid-sub">{t("Cho vay Khách hàng")}</div>
                        <div class="met-grid-dark">{securities/1e9:,.0f}</div><div class="met-grid-sub">{t("Chứng khoán Đầu tư")}</div>
                        <div style="margin-top:20px;"></div>
                        <div class="met-grid-dark">{deposits/1e9:,.0f}</div><div class="met-grid-sub red">{t("TG Khách hàng")}</div>
                        <div class="met-grid-dark">{interbank/1e9:,.0f}</div><div class="met-grid-sub red">{t("Vay các TCTD khác")}</div>
                    </div>
                </div>
                <div style="display: flex; flex-direction: column; gap: 10px; flex: 1;">
                    <div class="met-highlight-teal"><div class="met-hl-val">{(loans/tot_ass)*100 if tot_ass>0 else 0:.1f}%</div><div class="met-hl-text">{t("Tỷ trọng Cho vay")}</div></div>
                    <div class="met-highlight-red"><div class="met-hl-val">{(deposits/tot_liab)*100 if tot_liab>0 else 0:.1f}%</div><div class="met-hl-text">{t("Tỷ trọng Huy động")}</div></div>
                </div>
            </div>
            """
        elif is_sec:
            tot_ass = get_val(bs_df, ['total assets', 'tổng cộng tài sản'])
            cur_ass = get_val(bs_df, ['current assets', 'tài sản ngắn hạn'])
            fvtpl = get_val(bs_df, ['fvtpl', 'tài sản tài chính ghi nhận qua lãi/lỗ'])
            afs_htm = get_val(bs_df, ['afs', 'sẵn sàng để bán', 'htm', 'giữ đến ngày đáo hạn', 'chứng khoán đầu tư', 'đầu tư ngắn hạn'])
            margin = get_val(bs_df, ['margin', 'cho vay', 'loans', 'phải thu'])
            cash = get_val(bs_df, ['cash and cash', 'tiền và các khoản'])
            tot_liab = get_val(bs_df, ['liabilities', 'nợ phải trả'])
            equity = get_val(bs_df, ['equity', 'vốn chủ sở hữu'])
            
            assets_html = f"""
            <div class="met-panel">
                <div class="met-grid" style="grid-template-columns: 1fr 1fr;">
                    <div>
                        <div class="met-grid-dark">{tot_ass/1e9:,.0f}</div><div class="met-grid-sub">{t("Tổng Tài sản")}</div>
                        <div class="met-grid-dark">{cash/1e9:,.0f}</div><div class="met-grid-sub">{t("Tiền & TĐ Tiền")}</div>
                        <div style="margin-top:20px;"></div>
                        <div class="met-grid-dark">{tot_liab/1e9:,.0f}</div><div class="met-grid-sub red">{t("Tổng Nợ phải trả")}</div>
                        <div class="met-grid-dark">{equity/1e9:,.0f}</div><div class="met-grid-sub red">{t("Vốn Chủ Sở Hữu")}</div>
                    </div>
                    <div>
                        <div class="met-grid-dark">{fvtpl/1e9:,.0f}</div><div class="met-grid-sub">{t("Tự doanh (FVTPL)")}</div>
                        <div class="met-grid-dark">{afs_htm/1e9:,.0f}</div><div class="met-grid-sub">{t("Đầu tư Trái phiếu")}</div>
                        <div style="margin-top:20px;"></div>
                        <div class="met-grid-dark">{margin/1e9:,.0f}</div><div class="met-grid-sub">{t("Cho vay Margin")}</div>
                        <div class="met-grid-dark">{(tot_ass - cur_ass)/1e9:,.0f}</div><div class="met-grid-sub">{t("Tài sản Dài hạn")}</div>
                    </div>
                </div>
                <div style="display: flex; flex-direction: column; gap: 10px; flex: 1;">
                    <div class="met-highlight-teal"><div class="met-hl-val">{(margin/tot_ass)*100 if tot_ass>0 else 0:.1f}%</div><div class="met-hl-text">{t("Tỷ trọng Margin/TS")}</div></div>
                    <div class="met-highlight-red"><div class="met-hl-val">{(fvtpl/tot_ass)*100 if tot_ass>0 else 0:.1f}%</div><div class="met-hl-text">{t("Tỷ trọng Tự doanh")}</div></div>
                </div>
            </div>
            """
        else:
            tot_ass = get_val(bs_df, ['total assets', 'tổng cộng tài sản'])
            cur_ass = get_val(bs_df, ['current assets', 'tài sản ngắn hạn'])
            fix_ass = get_val(bs_df, ['fixed assets', 'tài sản cố định'])
            receivables = get_val(bs_df, ['accounts receivable', 'các khoản phải thu ngắn hạn'])
            tot_liab = get_val(bs_df, ['liabilities (bn. vnd)', 'tổng nợ phải trả', 'nợ phải trả', 'liabilities'])
            cur_liab = get_val(bs_df, ['current liabilities', 'nợ ngắn hạn'])
            cash = get_val(bs_df, ['cash and cash', 'tiền và các khoản'])
            equity = get_val(bs_df, ['equity', 'vốn chủ sở hữu'])
            payables = get_val(bs_df, ['trade payables', 'phải trả người bán'])
            retained = get_val(bs_df, ['undistributed earnings', 'lợi nhuận sau thuế chưa phân phối', 'lợi nhuận chưa phân phối'])
            
            # Khắc phục lỗi "Phải trả người bán = 0"
            if payables == 0 and retained > 0:
                red_box_val = retained / 1e9
                red_box_lbl = t("LN Chưa phân phối")
            else:
                red_box_val = payables / 1e9
                red_box_lbl = t("Phải trả Người bán")
                
            assets_html = f"""
            <div class="met-panel">
                <div class="met-grid">
                    <div>
                        <div class="met-grid-dark">{tot_ass/1e9:,.0f}</div><div class="met-grid-sub">{t("Tổng Tài sản")}</div>
                        <div class="met-grid-dark">{cash/1e9:,.0f}</div><div class="met-grid-sub">{t("Tiền & TĐ Tiền")}</div>
                        <div style="margin-top:20px;"></div>
                        <div class="met-grid-dark">{tot_liab/1e9:,.0f}</div><div class="met-grid-sub red">{t("Tổng Nợ phải trả")}</div>
                        <div class="met-grid-dark">{equity/1e9:,.0f}</div><div class="met-grid-sub red">{t("Vốn Chủ Sở Hữu")}</div>
                    </div>
                    <div>
                        <div class="met-grid-dark">{cur_ass/1e9:,.0f}</div><div class="met-grid-sub">{t("Tài sản Ngắn hạn")}</div>
                        <div class="met-grid-dark">{(cur_ass-max(cash,0)-max(receivables,0))/1e9:,.0f}</div><div class="met-grid-sub">{t("Hàng tồn kho")}</div>
                        <div style="margin-top:20px;"></div>
                        <div class="met-grid-dark">{cur_liab/1e9:,.0f}</div><div class="met-grid-sub red">{t("Nợ Ngắn hạn")}</div>
                        <div class="met-grid-dark">{(tot_liab-cur_liab)/1e9:,.0f}</div><div class="met-grid-sub red">{t("Nợ Dài hạn")}</div>
                    </div>
                    <div>
                        <div class="met-grid-dark">{fix_ass/1e9:,.0f}</div><div class="met-grid-sub">{t("Tài sản Cố định")}</div>
                        <div class="met-grid-dark">{(tot_ass-cur_ass)/1e9:,.0f}</div><div class="met-grid-sub">{t("Tài sản Dài hạn")}</div>
                        <div style="margin-top:20px;"></div>
                        <div class="met-grid-dark">{tot_ass/1e9:,.0f}</div><div class="met-grid-sub red">{t("Tổng Nguồn vốn")}</div>
                    </div>
                </div>
                <div style="display: flex; flex-direction: column; gap: 10px; flex: 1;">
                    <div class="met-highlight-teal"><div class="met-hl-val">{receivables/1e9:,.0f}</div><div class="met-hl-text">{t("Phải thu Khách hàng")}</div></div>
                    <div class="met-highlight-red"><div class="met-hl-val">{red_box_val:,.0f}</div><div class="met-hl-text">{red_box_lbl}</div></div>
                </div>
            </div>
            """
        st.markdown(assets_html, unsafe_allow_html=True)
        
    with bc2:
        st.markdown(f"<div style='text-align: center; font-weight: 600; margin-bottom: 5px; color: #2C3E50;'>{t('Cơ cấu Tổng Chi phí')}</div>", unsafe_allow_html=True)
        # Tornado Chart cho cấu trúc dòng phí
        if is_bank:
            cogs_val = abs(cogs)
            prov_exp = abs(get_val(is_df, ['provision', 'chi phí dự phòng']))
            op_exp = abs(get_val(is_df, ['operating expenses', 'chi phí hoạt động', 'general & admin']))
            bank_other_exp = abs(get_val(is_df, ['other expenses', 'chi phí khác']))
            exp_names = [t("Chi phí Trả lãi"), t("Chi phí Dự phòng"), t("Chi phí Hoạt động"), t("Chi phí Khác")]
            exp_vals = [cogs_val, prov_exp, op_exp, bank_other_exp]
        elif is_sec:
            cogs_val = abs(cogs)
            admin_exp = abs(get_val_sum(is_df, ['general & admin', 'chi phí quản lý doanh nghiệp', 'chi phí quản lý', 'chi phí hoạt động']))
            fin_exp = abs(get_val(is_df, ['financial expenses', 'chi phí tài chính']))
            sec_other_exp = abs(get_val(is_df, ['other expenses', 'chi phí khác']))
            exp_names = [t("Chi phí HĐ Đầu tư"), t("Chi phí Quản lý"), t("Chi phí Tài chính"), t("Chi phí Khác")]
            exp_vals = [cogs_val, admin_exp, fin_exp, sec_other_exp]
        else:
            fin_exp = abs(get_val(is_df, ['financial expenses', 'chi phí tài chính']))
            cogs_val = abs(cogs)
            sell_exp = abs(get_val(is_df, ['selling', 'chi phí bán hàng']))
            admin_exp = abs(get_val(is_df, ['general & admin', 'chi phí quản lý doanh nghiệp']))
            exp_names = [t("Giá vốn Hàng bán"), t("Chi phí Quản lý"), t("Chi phí Bán hàng"), t("Chi phí Tài chính"), t("Chi phí Khác")]
            exp_vals = [cogs_val, admin_exp, sell_exp, fin_exp, abs(other_expenses)]
        # Lọc bỏ các dòng phí bằng 0
        final_names = []
        final_vals = []
        for n, v in zip(exp_names, exp_vals):
            if v > 0:
                final_names.append(n)
                final_vals.append(v)
        
        # In Tornado, we use horizontal bar chart with red color and text inside
        fig_exp = go.Figure()
        fig_exp.add_trace(go.Bar(
            y=final_names[::-1], x=final_vals[::-1], orientation='h',
            marker_color="#C0392B", text=[f"{v/1e9:,.0f}" for v in final_vals[::-1]], textposition="inside"
        ))
        fig_exp.update_layout(height=280, margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor='white', plot_bgcolor='white', xaxis=dict(showgrid=False, showticklabels=False))
        st.plotly_chart(fig_exp, use_container_width=True)

    # 4. DRILL-DOWN PANE (Interactive Response)
    st.markdown("---")
    drill_title = f"🔍 {t('Khoan sâu Phân tích (Drill-down Pane)')}"
    if event_op and event_op.get("selection") and event_op["selection"].get("points"):
        pt = event_op["selection"]["points"][0]
        pt_idx = pt.get("pointIndex")
        
        # Sửa lỗi: Nếu click vào đường gân biên lợi nhuận (Scatter/Line), Streamlit sẽ không trả về list index
        # Thay vào đó ta đối chiếu tọa độ x (Ví dụ: 'T-2') vào trục y_labels để dò ra index bị ẩn.
        if pt_idx is None:
            pt_x = pt.get("x")
            if pt_x in y_labels:
                pt_idx = y_labels.index(pt_x)
            else:
                pt_idx = len(y_labels) - 1 # Fallback an toàn về Qúy gần nhất
        
        # Mảng rev_series bị lộn ngược so với is_df (cũ nhất ở index 0)
        # Bắt buộc phải ánh xạ ngược pt_idx -> df_idx
        df_idx = len(rev_series) - 1 - pt_idx
        
        if df_idx >= 0 and df_idx < len(is_df):
            st.markdown(f"### {drill_title}: {y_labels[pt_idx]}")
            drill_df = is_df.iloc[[df_idx]]
            
            dr_rev = get_val(drill_df, rev_keys)
            dr_cogs = abs(get_val(drill_df, cogs_keys))
            dr_gp = dr_rev - dr_cogs
            dr_sga = get_val_sum(drill_df, sga_keys)
            dr_np = get_val(drill_df, np_keys)
            dr_fin = get_val(drill_df, ['financial expenses', 'chi phí tài chính'])
            
            # Khởi tạo dữ liệu Treemap
            labels = [t('DOANH THU'), t('LỢI NHUẬN GỘP'), t('GIÁ VỐN'), t('LỢI NHUẬN RÒNG'), t('CHI PHÍ QUẢN LÝ (SGA)'), t('CHI PHÍ TÀI CHÍNH')]
            parents = ["", t('DOANH THU'), t('DOANH THU'), t('LỢI NHUẬN GỘP'), t('LỢI NHUẬN GỘP'), t('LỢI NHUẬN GỘP')]
            values = [dr_rev, dr_gp, dr_cogs, max(0, dr_np), dr_sga, dr_fin]
            
            fig_tree = go.Figure(go.Treemap(
                labels=labels, parents=parents, values=values,
                textinfo="label+value+percent parent"
            ))
            fig_tree.update_layout(margin=dict(t=10, b=10, r=10, l=10), height=350)
            
            dc1, dc2 = st.columns([1.2, 1])
            with dc1:
                st.plotly_chart(fig_tree, use_container_width=True)
            with dc2:
                # Transpose to show vertically as a Key-Value pair list
                show_df = drill_df.T.dropna()
                show_df.columns = [t("Giá trị Hạch toán")]
                
                if getattr(st.session_state, 'lang', '🇻🇳 Tiếng Việt') == '🇻🇳 Tiếng Việt':
                    field_dict = {
                        'ticker': 'Mã Cổ phiếu', 'yearreport': 'Năm/Quý Báo cáo', 'lengthreport': 'Độ dài (Kỳ)',
                        'revenue yoy (%)': 'Doanh thu YoY (%)', 'revenue (bn. vnd)': 'Doanh thu (T)',
                        'net revenue': 'Doanh thu Thuần', 'attribute to parent company (bn. vnd)': 'LNST Công ty mẹ (T)',
                        'attribute to parent company yoy (%)': 'LNST Cty mẹ YoY (%)', 'gross profit': 'Lợi nhuận Gộp',
                        'gross profit margin (%)': 'Biên LN Gộp (%)', 'operating expenses': 'Chi phí HĐKD',
                        'selling expenses': 'Chi phí Bán hàng', 'general & admin': 'Chi phí Quản lý',
                        'general & administrative expenses': 'Chi phí Quản lý', 'financial income': 'Doanh thu Tài chính',
                        'income from investments': 'Thu nhập từ Đầu tư', 'interest expenses': 'Chi phí Lãi vay',
                        'financial expenses': 'Chi phí Tài chính', 'provision': 'Chi phí Dự phòng',
                        'ebitda': 'EBITDA (LN trước thuế & khấu hao)', 'net profit': 'Lợi nhuận Ròng',
                        'pre-tax profit': 'LN Trước Thuế', 'tax expenses': 'Thuế TNDN',
                        'interest income': 'Thu nhập từ Lãi', 'net interest income': 'Thu nhập Lãi Thuần',
                        'other income': 'Thu nhập Khác', 'other non-interest income': 'Thu nhập ngoài Lãi',
                        'profit before tax': 'LN Trước Thuế',
                        'net profit for the year': 'Lợi nhuận Ròng trong năm',
                        'business income tax - current': 'Thuế TNDN - Hiện hành',
                        'business income tax - deferred': 'Thuế TNDN - Hoãn lại',
                        'attributable to parent company': 'LNST Phân bổ cho Cty mẹ',
                        'minority interest': 'Lợi ích Cổ đông thiểu số',
                        'net income from associated companies': 'LN từ Cty liên kết/liên doanh',
                        'other income/expenses': 'Thu nhập/Chi phí khác',
                        'net other income/expenses': 'LN Thuần từ HĐ khác',
                        'cost of sales': 'Giá vốn Hàng bán',
                        'sales deductions': 'Các khoản Giảm trừ DT'
                    }
                    show_df.index = [field_dict.get(str(idx).strip().lower(), str(idx)) for idx in show_df.index]
                
                st.dataframe(show_df, height=350, use_container_width=True)
    else:
        st.info(f"👆 {t('Click vào bất kỳ cột biểu đồ nào ở trên (Thu nhập Hoạt động) để mở tính năng Drill-down.')}")
        
    # 5. DỰ BÁO VÀ XU HƯỚNG (AI FORECASTING)
    st.markdown("---")
    st.markdown(f"### 🤖 {t('Dự báo & Xu hướng (AI Forecasting)')}")
    st.markdown(f"<p style='color: #7F8C8D; font-size: 14px;'>{t('Sử dụng Hồi quy Tuyến tính (Linear Regressor ML) dò tìm chu kỳ và dự phóng 3 mốc tiếp theo.')}</p>", unsafe_allow_html=True)
    
    y_rev = np.array(rev_series)
    y_nps = np.array(np_series)
    x = np.arange(len(y_rev))
    
    if len(y_rev) >= 2:
        # Linear Regression (Bậc 1)
        z_rev = np.polyfit(x, y_rev, 1)
        p_rev = np.poly1d(z_rev)
        
        z_nps = np.polyfit(x, y_nps, 1)
        p_nps = np.poly1d(z_nps)
        
        # Extrapolate 3 quarters
        x_future = np.arange(len(y_rev), len(y_rev) + 3)
        future_rev = p_rev(x_future)
        future_nps = p_nps(x_future)
        
        # Ngăn số âm vô lý với Doanh thu
        future_rev = [max(0, val) for val in future_rev]
        # Dynamic Labeling (Q/YYYY or YYYY)
        future_labels = []
        try:
            last_lbl = str(y_labels[-1])
            if "Q" in last_lbl and "/" in last_lbl:
                q_part, y_part = last_lbl.split("/")
                current_q = int(q_part.replace("Q", ""))
                current_y = int(y_part)
                for _ in range(3):
                    current_q += 1
                    if current_q > 4:
                        current_q = 1
                        current_y += 1
                    future_labels.append(f"Q{current_q}/{current_y}")
            elif last_lbl.isdigit():
                current_y = int(last_lbl)
                for _ in range(3):
                    current_y += 1
                    future_labels.append(str(current_y))
            else:
                future_labels = [f"T+{i}" for i in range(1, 4)]
        except Exception:
            future_labels = [f"T+{i}" for i in range(1, 4)]
        
        fc1, fc2 = st.columns(2)
        with fc1:
            fig_fc_rev = go.Figure()
            fig_fc_rev.add_trace(go.Scatter(x=y_labels, y=y_rev, mode='lines+markers', name=t('Thực tế'), line=dict(color='#8E44AD', width=3)))
            x_fc_rev = [y_labels[-1]] + future_labels
            y_fc_rev = [y_rev[-1]] + list(future_rev)
            
            y_upper = [val * 1.1 for val in y_fc_rev]
            y_lower = [val * 0.9 for val in y_fc_rev]
            
            fig_fc_rev.add_trace(go.Scatter(x=x_fc_rev, y=y_upper, fill=None, mode='lines', line_color='rgba(0,0,0,0)', showlegend=False, hoverinfo='skip'))
            fig_fc_rev.add_trace(go.Scatter(x=x_fc_rev, y=y_lower, fill='tonexty', mode='lines', line_color='rgba(0,0,0,0)', fillcolor='rgba(142, 68, 173, 0.15)', name=t('Vùng Kịch bản')))
            
            fig_fc_rev.add_trace(go.Scatter(x=x_fc_rev, y=y_fc_rev, mode='lines+markers+text', name=t('Dự báo'), line=dict(color='#8E44AD', width=2, dash='dot'), text=[""] + [f"{v/1e9:,.0f}T" for v in future_rev], textposition="top center", cliponaxis=False))
            
            all_rev_max = max(max(y_rev), max(y_upper))
            fig_fc_rev.update_layout(height=300, margin=dict(t=40, b=10, l=10, r=10), plot_bgcolor='rgba(0,0,0,0)', showlegend=True, legend=dict(orientation="h", y=1.1, x=0.5, xanchor='center'), yaxis=dict(showgrid=False, range=[0, all_rev_max * 1.2]))
            st.markdown(f"<div style='text-align: center; font-weight: 600; margin-bottom: 5px; color: #2C3E50;'>{t('Dự báo Doanh thu (3 kỳ tới)')}</div>", unsafe_allow_html=True)
            st.plotly_chart(fig_fc_rev, use_container_width=True)

        with fc2:
            fig_fc_np = go.Figure()
            fig_fc_np.add_trace(go.Scatter(x=y_labels, y=y_nps, mode='lines+markers', name=t('Thực tế'), line=dict(color='#2980B9', width=3)))
            x_fc_np = [y_labels[-1]] + future_labels
            y_fc_np = [y_nps[-1]] + list(future_nps)
            
            y_upper_np = [val + abs(val)*0.15 for val in y_fc_np]
            y_lower_np = [val - abs(val)*0.15 for val in y_fc_np]
            
            fig_fc_np.add_trace(go.Scatter(x=x_fc_np, y=y_upper_np, fill=None, mode='lines', line_color='rgba(0,0,0,0)', showlegend=False, hoverinfo='skip'))
            fig_fc_np.add_trace(go.Scatter(x=x_fc_np, y=y_lower_np, fill='tonexty', mode='lines', line_color='rgba(0,0,0,0)', fillcolor='rgba(41, 128, 185, 0.15)', name=t('Vùng Kịch bản')))
            
            fig_fc_np.add_trace(go.Scatter(x=x_fc_np, y=y_fc_np, mode='lines+markers+text', name=t('Dự báo'), line=dict(color='#2980B9', width=2, dash='dot'), text=[""] + [f"{v/1e9:,.0f}T" for v in future_nps], textposition="top center", cliponaxis=False))
            
            all_np_max = max(max(y_nps), max(y_upper_np))
            all_np_min = min(min(y_nps), min(y_lower_np))
            fig_fc_np.update_layout(height=300, margin=dict(t=40, b=10, l=10, r=10), plot_bgcolor='rgba(0,0,0,0)', showlegend=True, legend=dict(orientation="h", y=1.1, x=0.5, xanchor='center'), yaxis=dict(showgrid=False, range=[all_np_min - abs(all_np_min)*0.2 - 5, all_np_max * 1.2 + 5]))
            st.markdown(f"<div style='text-align: center; font-weight: 600; margin-bottom: 5px; color: #2C3E50;'>{t('Dự báo Lợi nhuận Ròng (3 kỳ tới)')}</div>", unsafe_allow_html=True)
            st.plotly_chart(fig_fc_np, use_container_width=True)
            
        rev_trend = t('Tăng trưởng / Mở rộng') if z_rev[0] > 0 else t('Giảm sút / Cảnh báo')
        np_trend = t('Mở rộng') if z_nps[0] > 0 else t('Thu hẹp')
        
        insight_html = f'''
        <div style="background-color: #E8F8F5; border-left: 4px solid #1ABC9C; padding: 15px; border-radius: 4px; margin-top: 10px;">
            <strong style="color: #117A65;">🤖 {t('Nhận định từ Mô Hình Dự Báo (AI Insights):')}</strong><br>
            {t('Dựa trên quỹ đạo dữ liệu hồi quy tuyến tính (Linear Regression) quét qua thời gian, hệ thống ML nhận thấy chu kỳ Doanh thu của doanh nghiệp đang cho thấy trạng thái')} <b>{rev_trend}</b> 
            ({t('gia tốc')} ≈ {z_rev[0]/1e9:,.1f} {t('T/kỳ')}). {t('Dự phóng tại phần ngọn T+3, Doanh thu có thể tịnh tiến tới ngưỡng')} <b>~{future_rev[-1]/1e9:,.0f} {t('T')}</b>.<br>
            {t('Song song đó, Lợi nhuận Ròng có quỹ đạo cốt lõi')} <b>{np_trend}</b>. {t('Mô hình vạch ra vùng kịch bản dung sai Biên độ 10-15% (Vùng dải màu nhạt) bám sát theo độ lệch chuẩn tương lai thay vì cắm thẳng 1 con số vô hồn.')}
        </div>
        '''
        st.markdown(insight_html, unsafe_allow_html=True)
    else:
        st.info(t("Cần ít nhất 2 kỳ dữ liệu thực tế để mô hình AI thiết lập lưới dự báo."))
 
elif selected_module == "2. Variance Analysis (BvA)":
    st.markdown(f'<div class="section-title">📊 {t("2. Phân tích Biến động (BvA)")}</div>', unsafe_allow_html=True)
    st.markdown(f"### {t('Thực tế so với Ngân sách (Budget vs Actual)')}")
    
    st.markdown(f"> **{t('Giả lập Ngân sách: Vì dữ liệu Báo cáo Tài chính tự động không có số liệu Ngân sách, hệ thống giả định Ngân sách năm nay = Thực tế năm trước * % Tăng trưởng kế hoạch.')}**")
    
    col_bgt1, col_bgt2, col_bgt3 = st.columns(3)
    with col_bgt1:
        rev_target_pct = st.number_input(t("Mục tiêu Tăng trưởng Doanh thu (%)"), min_value=-50, max_value=200, value=15)
    with col_bgt2:
        cogs_target_pct = st.number_input(t("Ngân sách Giá vốn (% so năm trước)"), min_value=-50, max_value=200, value=10)
    with col_bgt3:
        sga_target_pct = st.number_input(t("Ngân sách Chi phí QLDN/BH (% so năm trước)"), min_value=-50, max_value=200, value=5)
        
    st.markdown(f"*{t('(Công thức % BvA = Thực tế/Ngân sách - 1. Nếu là hạng mục Chi phí, số Âm thể hiện sự Tiết kiệm so với Ngân sách và là Tín hiệu Tốt).')}*")

    rev_act = rev
    cogs_act = cogs
    sga_act = sga
    gp_act = gross_profit
    
    rev_prev_1 = rev_series[-2] if len(rev_series) > 1 else rev
    cogs_prev_1 = abs(cogs_series[-2]) if len(cogs_series) > 1 else cogs
    sga_prev_1 = abs(sga_series[-2]) if len(sga_series) > 1 else sga
    
    rev_budget = rev_prev_1 * (1 + rev_target_pct/100.0)
    cogs_budget = cogs_prev_1 * (1 + cogs_target_pct/100.0)
    sga_budget = sga_prev_1 * (1 + sga_target_pct/100.0)
    gp_budget = rev_budget - cogs_budget
    np_budget = gp_budget - sga_budget - other_expenses
    
    def calc_var(act, bgt, is_expense=False):
        var = act - bgt
        pct = (var / bgt) * 100 if bgt != 0 else 0
        is_fav = (var < 0) if is_expense else (var >= 0)
        return var, pct, is_fav
        
    v_rev, p_rev, f_rev = calc_var(rev_act, rev_budget)
    v_cogs, p_cogs, f_cogs = calc_var(cogs_act, cogs_budget, is_expense=True)
    v_gp, p_gp, f_gp = calc_var(gp_act, gp_budget)
    v_sga, p_sga, f_sga = calc_var(sga_act, sga_budget, is_expense=True)
    v_np, p_np, f_np = calc_var(net_profit, np_budget)
    
    bva_df = pd.DataFrame({
        t("Hạng mục"): [t("Doanh thu"), t("Giá vốn Hàng bán"), t("Lợi nhuận Gộp"), t("Chi phí HĐKD (SG&A)"), t("Lợi nhuận Ròng")],
        t("Thực tế"): [f"{rev_act/1e9:,.0f}", f"{cogs_act/1e9:,.0f}", f"{gp_act/1e9:,.0f}", f"{sga_act/1e9:,.0f}", f"{net_profit/1e9:,.0f}"],
        t("Ngân sách"): [f"{rev_budget/1e9:,.0f}", f"{cogs_budget/1e9:,.0f}", f"{gp_budget/1e9:,.0f}", f"{sga_budget/1e9:,.0f}", f"{np_budget/1e9:,.0f}"],
        t("Chênh lệch (Abs)"): [f"{v_rev/1e9:,.0f}", f"{v_cogs/1e9:,.0f}", f"{v_gp/1e9:,.0f}", f"{v_sga/1e9:,.0f}", f"{v_np/1e9:,.0f}"],
        "% BvA": [f"{p_rev:+.1f}%", f"{p_cogs:+.1f}%", f"{p_gp:+.1f}%", f"{p_sga:+.1f}%", f"{p_np:+.1f}%"],
        t("Đánh giá"): ["🟢" if f_rev else "🔴", "🟢" if f_cogs else "🔴", "🟢" if f_gp else "🔴", "🟢" if f_sga else "🔴", "🟢" if f_np else "🔴"]
    })
    
    st.table(bva_df.set_index(t("Hạng mục")))
    
    st.markdown(f"### {t('Giải thích chênh lệch (Waterfall Chart)')}")
    # Tính phần chênh lệch "Khác" (other_expenses variance) để waterfall cân bằng
    other_var = net_profit - (np_budget + v_rev - v_cogs - v_sga)
    
    wf_measures = ["absolute", "relative", "relative", "relative", "total"]
    wf_x = [t("Ngân sách (Lãi ròng)"), t("Vượt/hụt Doanh thu"), t("Tiết kiệm/Lạm Giá vốn"), t("Tiết kiệm/Lạm Chi phí HĐ"), t("Thực tế (Lãi ròng)")]
    wf_text = [f"{np_budget/1e9:,.0f}", f"{v_rev/1e9:,.0f}", f"{-v_cogs/1e9:,.0f}", f"{-v_sga/1e9:,.0f}", f"{net_profit/1e9:,.0f}"]
    wf_y = [np_budget/1e9, v_rev/1e9, -v_cogs/1e9, -v_sga/1e9, net_profit/1e9]
    
    # Chỉ thêm cột "Khác" nếu giá trị khác 0 đáng kể
    if abs(other_var/1e9) >= 1:
        wf_measures = ["absolute", "relative", "relative", "relative", "relative", "total"]
        wf_x = [t("Ngân sách (Lãi ròng)"), t("Vượt/hụt Doanh thu"), t("Tiết kiệm/Lạm Giá vốn"), t("Tiết kiệm/Lạm Chi phí HĐ"), t("Khác"), t("Thực tế (Lãi ròng)")]
        wf_text = [f"{np_budget/1e9:,.0f}", f"{v_rev/1e9:,.0f}", f"{-v_cogs/1e9:,.0f}", f"{-v_sga/1e9:,.0f}", f"{other_var/1e9:,.0f}", f"{net_profit/1e9:,.0f}"]
        wf_y = [np_budget/1e9, v_rev/1e9, -v_cogs/1e9, -v_sga/1e9, other_var/1e9, net_profit/1e9]
    
    fig_wf = go.Figure(go.Waterfall(
        name = "2023", orientation = "v",
        measure = wf_measures,
        x = wf_x,
        textposition = "outside",
        text = wf_text,
        y = wf_y,
        connector = {"line":{"color":"rgb(63, 63, 63)"}},
        decreasing = {"marker":{"color":"#E74C3C"}},
        increasing = {"marker":{"color":"#2ECC71"}},
        totals = {"marker":{"color":"#3498DB"}}
    ))
    fig_wf.update_layout(height=400, margin=dict(t=30, b=10, l=10, r=10), showlegend=False, plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_wf, use_container_width=True)

    # === STRATEGIC INSIGHTS BvA ===
    st.markdown("---")
    # Đếm số hạng mục Favorable / Unfavorable
    fav_count = sum([f_rev, f_cogs, f_gp, f_sga, f_np])
    unfav_count = 5 - fav_count
    
    # Xác định driver chính (biến gây ảnh hưởng lớn nhất)
    variances = {'Doanh thu': abs(v_rev), 'Giá vốn': abs(v_cogs), 'Chi phí SG&A': abs(v_sga)}
    biggest_driver = max(variances, key=variances.get)
    biggest_val = variances[biggest_driver]
    
    if st.session_state.get('lang', '🇻🇳 Tiếng Việt') == '🇬🇧 English':
        if f_np:
            bva_insight = f'''**Overall Assessment: ✅ FAVORABLE** — The company outperformed its budget with **{fav_count}/5** line items meeting or exceeding targets.

**Root Cause:** The largest variance driver is **{biggest_driver}** (±{biggest_val/1e9:,.0f} Bn VND). This suggests the management team has {'effectively controlled costs' if biggest_driver != 'Doanh thu' else 'strong commercial momentum'}.

**Recommendation for Leadership:** Capture this outperformance by allocating excess profit to: (1) R&D reserves, (2) Debt reduction, or (3) Shareholder returns.'''
        else:
            bva_insight = f'''**Overall Assessment: ⚠️ UNFAVORABLE** — The company missed its budget target with **{unfav_count}/5** line items underperforming.

**Root Cause:** The largest variance driver is **{biggest_driver}** (±{biggest_val/1e9:,.0f} Bn VND). {'Revenue shortfall indicates weakening demand or pricing pressure.' if biggest_driver == 'Doanh thu' else 'Cost overruns suggest supply chain inflation or operational inefficiency.'}

**Action Plan:** (1) Freeze discretionary spending, (2) Renegotiate supplier contracts, (3) Accelerate receivables collection to protect cash position.'''
    else:
        if f_np:
            bva_insight = f'''**Đánh giá chung: ✅ THUẬN LỢI (Favorable)** — Doanh nghiệp vượt Ngân sách với **{fav_count}/5** hạng mục đạt hoặc vượt chỉ tiêu.

**Nguyên nhân gốc rễ:** Biến số tác động lớn nhất là **{biggest_driver}** (±{biggest_val/1e9:,.0f} Tỷ VND). Điều này cho thấy ban điều hành {'đã kiểm soát chi phí hiệu quả' if biggest_driver != 'Doanh thu' else 'có động lực tăng trưởng thương mại mạnh mẽ'}.

**Khuyến nghị Ban lãnh đạo:** Tận dụng phần lợi nhuận vượt kế hoạch bằng cách phân bổ vào: (1) Quỹ R&D, (2) Trả nợ vay, hoặc (3) Cổ tức cho Cổ đông.'''
        else:
            bva_insight = f'''**Đánh giá chung: ⚠️ BẤT LỢI (Unfavorable)** — Doanh nghiệp hụt Ngân sách với **{unfav_count}/5** hạng mục không đạt chỉ tiêu.

**Nguyên nhân gốc rễ:** Biến số tác động lớn nhất là **{biggest_driver}** (±{biggest_val/1e9:,.0f} Tỷ VND). {'Hụt thu cho thấy sức cầu suy yếu hoặc áp lực giá bán.' if biggest_driver == 'Doanh thu' else 'Lạm chi phí cho thấy lạm phát chuỗi cung ứng hoặc vận hành kém hiệu quả.'}

**Kế hoạch hành động:** (1) Đóng băng chi tiêu tùy ý, (2) Tái đàm phán hợp đồng nhà cung cấp, (3) Đẩy nhanh thu hồi công nợ để bảo toàn dòng tiền.'''
    
    st.markdown(f'''
    <div style="background-color: {'#E8F8F5' if f_np else '#FDEDEC'}; border-left: 4px solid {'#1ABC9C' if f_np else '#E74C3C'}; padding: 15px; border-radius: 4px; margin-top: 10px;">
        <strong style="color: {'#117A65' if f_np else '#922B21'};">🤖 Nhận định từ Hệ thống Phân tích BvA (FP&A Insights):</strong><br><br>
        {bva_insight.replace(chr(10), '<br>')}
    </div>
    ''', unsafe_allow_html=True)

elif selected_module == "3. Cashflow Forecast":
    st.markdown(f'<div class="section-title">🌊 {t("3. Dự báo Dòng tiền (Cashflow Forecasting)")}</div>', unsafe_allow_html=True)
    st.markdown(f"### {t('Dự báo Dòng tiền & Thanh khoản')}")
    
    st.info(t('Áp dụng phương pháp Gián tiếp (Indirect Method) để dự phóng dòng tiền dựa trên Lợi nhuận kỳ vọng và Cấp vốn Lưu động.'))
    
    cf_c1, cf_c2, cf_c3 = st.columns(3)
    with cf_c1:
        capex_input = st.number_input(t("Ngân sách Đầu tư tài sản (CAPEX) - Tỷ VND"), min_value=0, max_value=50000, value=500, step=100) * 1e9
    with cf_c2:
        dso_input = st.number_input(t("Chu kỳ thu tiền (Days Sales Outstanding - DSO)"), min_value=0, max_value=360, value=45, step=5)
    with cf_c3:
        dpo_input = st.number_input(t("Chu kỳ thanh toán (Days Payable - DPO)"), min_value=0, max_value=360, value=30, step=5)
    
    sf_col1, sf_col2, sf_col3 = st.columns(3)
    with sf_col1:
        safety_stock_input = st.number_input(t("Ngưỡng Tiền mặt An toàn (Tỷ VND)"), min_value=0, max_value=100000, value=100, step=10) * 1e9
    
    cf_periods = [f"Q{i}" for i in range(1, 5)]
    baseline_cash = cash
    
    depr_forecast = float(get_val(bs_df, ['total assets', 'tổng cộng tài sản'])) * 0.05 / 4
    
    cash_balances = []
    fcf_list = []
    
    current_cash = baseline_cash
    for i in range(4):
        q_profit = (net_profit / 4) * (1 + 0.05 * i)
        wc_effect = (dpo_input - dso_input) * (rev / 360) / 4
        ocf = q_profit + depr_forecast + wc_effect
        fcf = ocf - (capex_input / 4)
        current_cash = current_cash + fcf
        
        fcf_list.append(fcf)
        cash_balances.append(current_cash)
        
    cf_fig = go.Figure()
    cf_colors = ['#E74C3C' if v<0 else '#1ABC9C' for v in fcf_list]
    cf_fig.add_trace(go.Bar(x=cf_periods, y=[v/1e9 for v in fcf_list], name=t("Dòng tiền Tự do (FCF)"), marker_color=cf_colors))
    cf_fig.add_trace(go.Scatter(x=cf_periods, y=[v/1e9 for v in cash_balances], mode='lines+markers+text', name=t("Số dư Tiền mặt Cuối kỳ"),
                                line=dict(color='#34495E', width=3), text=[f"{v/1e9:,.0f}T" for v in cash_balances], textposition="top center", yaxis="y2"))
    
    # Đường ngưỡng Safety Stock (nét đứt đỏ) trên trục y2
    cf_fig.add_trace(go.Scatter(
        x=cf_periods, y=[safety_stock_input/1e9]*4,
        mode='lines', name=f"Ngưỡng Safety Stock ({safety_stock_input/1e9:,.0f}T)",
        line=dict(color='#E74C3C', width=2, dash='dash'), yaxis="y2"
    ))
    
    # Đảm bảo trục y2 hiển thị cả Safety Stock line
    all_y2_vals = [v/1e9 for v in cash_balances] + [safety_stock_input/1e9]
    y2_min = min(all_y2_vals) * 0.9 if min(all_y2_vals) > 0 else min(all_y2_vals) * 1.1
    y2_max = max(all_y2_vals) * 1.15
    
    cf_fig.update_layout(
        height=400, margin=dict(t=40, b=10, l=10, r=10), plot_bgcolor='rgba(0,0,0,0)',
        yaxis2=dict(overlaying='y', side='right', showgrid=False, range=[y2_min, y2_max]),
        legend=dict(orientation="h", y=1.15, x=0.5, xanchor='center')
    )
    st.plotly_chart(cf_fig, use_container_width=True)
    
    # Summary Metrics
    sm1, sm2, sm3, sm4 = st.columns(4)
    sm1.metric(t("Tiền mặt (Cash)"), f"{baseline_cash/1e9:,.0f} T", "Đầu kỳ")
    sm2.metric(t("Số dư Tiền mặt Cuối kỳ"), f"{cash_balances[-1]/1e9:,.0f} T", f"{(cash_balances[-1]-baseline_cash)/1e9:+,.0f} T")
    sm3.metric(t("Dòng tiền Tự do (FCF)"), f"{sum(fcf_list)/1e9:,.0f} T", "Tổng 4 kỳ")
    sm4.metric(t("Ngưỡng Tiền mặt An toàn (Tỷ VND)"), f"{safety_stock_input/1e9:,.0f} T")
    
    st.markdown("---")
    min_cash = min(cash_balances)
    if min_cash < 0:
        st.error(t('Cảnh báo ĐỎ: Nguy cơ phá sản thanh khoản! Dòng tiền rơi xuống mức âm.'))
    elif min_cash < safety_stock_input:
        st.warning(t('Cảnh báo CAM: Quỹ tiền mặt đã chạm ngưỡng rủi ro (dưới mức Safety Stock định trước). Hãy rà soát lại kế hoạch vốn.'))
    else:
        st.success(t('An toàn: Quỹ tiền mặt đảm bảo khả năng thanh toán và duy trì trên mức Safety Stock.'))
    
    # === STRATEGIC INSIGHTS CASHFLOW ===
    cash_change = cash_balances[-1] - baseline_cash
    cash_change_pct = (cash_change / baseline_cash * 100) if baseline_cash > 0 else 0
    total_fcf = sum(fcf_list)
    cash_runway_months = (cash_balances[-1] / (abs(total_fcf/4))) if total_fcf != 0 else 999
    wc_gap = dso_input - dpo_input
    
    if st.session_state.get('lang', '🇻🇳 Tiếng Việt') == '🇬🇧 English':
        cf_insight = f'''**Cash Position Summary:**
- Starting Cash: **{baseline_cash/1e9:,.0f} Bn** → Ending Cash (Q4): **{cash_balances[-1]/1e9:,.0f} Bn** ({cash_change_pct:+.1f}%)
- Total FCF generated over 4 quarters: **{total_fcf/1e9:,.0f} Bn VND**
- Cash Runway: ~**{abs(cash_runway_months):.0f} quarters** of operating expenses at current burn rate

**Working Capital Efficiency:**
- Cash Conversion Gap (DSO - DPO) = **{wc_gap} days** {'⚠️ Cash is trapped in receivables longer than payables — unfavorable.' if wc_gap > 0 else '✅ Suppliers are financing your operations — favorable.'}

**CFO Recommendation:** {'Maintain current capital structure. Consider deploying excess cash into yield-generating instruments or strategic acquisitions.' if cash_change >= 0 else 'Reduce CAPEX or renegotiate payment terms to stabilize cash reserves. Consider revolving credit facility as liquidity backstop.'}'''
    else:
        cf_insight = f'''**Tổng quan Tình trạng Quỹ tiền:**
- Tiền mặt đầu kỳ: **{baseline_cash/1e9:,.0f} T** → Cuối Q4: **{cash_balances[-1]/1e9:,.0f} T** ({cash_change_pct:+.1f}%)
- Tổng Dòng tiền Tự do (FCF) sinh ra trong 4 quý: **{total_fcf/1e9:,.0f} Tỷ VND**
- Thời gian sống (Cash Runway): ~**{abs(cash_runway_months):.0f} quý** chi phí hoạt động ở mức hiện tại

**Hiệu quả Vốn Lưu động (Working Capital):**
- Khoảng cách Chuyển đổi Tiền (DSO - DPO) = **{wc_gap} ngày** {'⚠️ Tiền bị kẹt trong Công nợ phải thu lâu hơn Phải trả — bất lợi.' if wc_gap > 0 else '✅ Nhà cung cấp đang tài trợ cho hoạt động kinh doanh — thuận lợi.'}

**Khuyến nghị CFO:** {'Duy trì cấu trúc vốn hiện tại. Cân nhắc triển khai tiền dư thừa vào các công cụ sinh lãi hoặc M&A chiến lược.' if cash_change >= 0 else 'Giảm CAPEX hoặc tái đàm phán điều khoản thanh toán để ổn định dự trữ tiền mặt. Cân nhắc mở hạn mức tín dụng tuần hoàn (Revolving Credit) làm lưới an toàn thanh khoản.'}'''
    
    st.markdown(f'''
    <div style="background-color: {'#E8F8F5' if cash_change >= 0 else '#FDEDEC'}; border-left: 4px solid {'#1ABC9C' if cash_change >= 0 else '#E74C3C'}; padding: 15px; border-radius: 4px; margin-top: 10px;">
        <strong style="color: {'#117A65' if cash_change >= 0 else '#922B21'};">🤖 Nhận định từ Hệ thống Dự báo Dòng tiền (Treasury Insights):</strong><br><br>
        {cf_insight.replace(chr(10), '<br>')}
    </div>
    ''', unsafe_allow_html=True)

elif selected_module == "4. Financial Modeling":
    st.markdown(f'<div class="section-title">🔮 {t("2. Mô Hình Kịch Bản Chiến Lược (Cases)")}</div>', unsafe_allow_html=True)
    
    if 'rev_gr' not in st.session_state:
        st.session_state.rev_gr = 0.0
        st.session_state.cogs_ch = 0.0
        st.session_state.sga_ch = 0.0

    st.markdown(f"### {t('🎛️ Nạp Kịch Bản Nhanh (Scenario Presets)')}")
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    
    if btn_col1.button(t("🟢 Kịch bản Tích cực (Best Case)"), use_container_width=True):
        st.session_state.rev_gr = 20.0
        st.session_state.cogs_ch = -5.0
        st.session_state.sga_ch = -5.0
    if btn_col2.button("⚪ Kịch bản Cơ sở (Base Case)", use_container_width=True):
        st.session_state.rev_gr = 0.0
        st.session_state.cogs_ch = 0.0
        st.session_state.sga_ch = 0.0
    if btn_col3.button(t("🔴 Kịch bản Xấu (Worst Case)"), use_container_width=True):
        st.session_state.rev_gr = -20.0
        st.session_state.cogs_ch = 15.0
        st.session_state.sga_ch = 10.0

    st.markdown(f"### ⚙️ 1. {t('Thiết lập Tham số (Tùy chỉnh Thủ công)')}")
    c1, c2, c3 = st.columns(3)
    with c1:
        rev_growth = st.number_input(t("📈 Tăng trưởng Doanh thu (%)"), min_value=-1000.0, max_value=1000.0, key="rev_gr", step=1.0)
    with c2:
        cogs_change = st.number_input(t("📉 Biến động Giá Vốn (%)"), min_value=-1000.0, max_value=1000.0, key="cogs_ch", step=1.0)
    with c3:
        sga_change = st.number_input(t("🏢 Biến động Chi phí HĐ (%)"), min_value=-1000.0, max_value=1000.0, key="sga_ch", step=1.0)
        
    st.markdown("---")
    
    # Tính toán Scenario
    proj_rev = rev * (1 + rev_growth/100)
    proj_cogs = cogs * (1 + cogs_change/100)
    proj_gross = proj_rev - proj_cogs
    proj_sga = sga * (1 + sga_change/100)
    proj_profit = proj_gross - proj_sga - other_expenses
    
    st.markdown(f"### {t('📊 Chênh lệch Kịch Bản (Financial Impact)')}")
    sc_c1, sc_c2 = st.columns(2)
    with sc_c1:
        st.markdown(t("**Quá khứ (Thực tế năm nay)**"))
        st.write(f"- {t('Doanh thu')}: **{rev/1e9:,.0f} T**")
        st.write(f"- {t('Giá vốn')}: **{cogs/1e9:,.0f} T**")
        st.write(f"- {t('Lợi Nhuận Ròng')}: **{net_profit/1e9:,.0f} T**")
        
    with sc_c2:
        diff_profit = proj_profit - net_profit
        color = "#10B981" if diff_profit >= 0 else "#EF4444"
        arrow = "↑" if diff_profit >= 0 else "↓"
        st.markdown(t("**Tương lai (Dự phóng năm sau)**"))
        st.write(f"- {t('Doanh thu')}: **{proj_rev/1e9:,.0f} T**")
        st.write(f"- {t('Giá vốn')}: **{proj_cogs/1e9:,.0f} T**")
        st.write(f"- {t('Lợi Nhuận Ròng')}: <span style='color:{color}; font-weight:bold;'>{proj_profit/1e9:,.0f} T</span> ({arrow} {abs(diff_profit/1e9):,.0f} T)", unsafe_allow_html=True)

    st.markdown(t("### 🛡️ Chiến lược Giảm thiểu rủi ro (Mitigation Strategies)"))
    if diff_profit < 0:
        warning_msg = t("⚠️ CẢNH BÁO SUY THOÁI LỢI NHUẬN: Kịch bản rủi ro làm thất thoát {} T lợi nhuận.").format(f"{abs(diff_profit/1e9):,.0f}")
        st.warning(warning_msg)
        st.markdown(f"""
        {t('**Trigger Points & Kế hoạch hành động:**')}
        {t('- **Quản trị tỷ suất:** Rà soát lại rổ sản phẩm hiện tại, sản phẩm nào chỉ tạo doanh thu ảo nhưng không đóng góp Biên lợi nhuận thì mạnh tay cắt bỏ.')}
        {t('- **Quản trị chi phí:** Giải phóng nhân sự dôi dư (Freeze Hiring), cắt giảm ngân sách Marketing chưa ra chuyển đổi.')}
        {t('- **Tái đàm phán:** Khẩn cấp làm việc với chuỗi cung ứng để ép giá vốn (COGS) xuống mức an toàn.')}
        """)
    else:
        success_msg = t("✅ KỊCH BẢN TĂNG TRƯỞNG LÝ TƯỞNG: Lợi nhuận đột phá thêm {} T.").format(f"{diff_profit/1e9:,.0f}")
        st.success(success_msg)
        st.markdown(f"""
        {t('**Khuyến nghị Phân bổ Vốn (Capital Allocation):**')}
        {t('- Trích lập quỹ dự phòng cho chu kỳ sóng gió kế tiếp.')}
        {t('- Đẩy mạnh R&D (Phát triển sản phẩm) nhằm nới rộng Con hào kinh tế (Moat).')}
        {t('- Trả cổ tức tiền mặt để duy trì niềm tin Cổ đông.')}
        """)

    st.markdown("---")
    st.markdown(f"### 📑 {t('2. Các Bảng tính phụ trợ (Supporting Schedules)')}")
    st.write(t("Để các con số trong 3 báo cáo trên chính xác, bạn cần các bảng tính chi tiết bên dưới:"))
    
    # Xử lý Dynamic Data
    labels_4 = get_time_labels(is_df, 4)
    if not labels_4: labels_4 = ['T-3', 'T-2', 'T-1', 'T']
    
    def pad_s(series, length, default=0):
        return ([default]*(length - len(series)) + series)[-length:]

    fa_list = get_series(bs_df, ['fixed asset', 'tài sản cố định'], 4)
    fa_list = pad_s(fa_list, len(labels_4))
    if sum([abs(v) for v in fa_list]) > 0:
        with st.expander(f"📉 {t('Bảng khấu hao (Depreciation & Amortization)')}"):
            st.write(f"*{t('Tính toán giá trị tài sản hao mòn theo thời gian.')}*")
            dep_list = [-val * 0.1 for val in fa_list] # Ước tính hao mòn 10%
            end_fa = [fa + dep for fa, dep in zip(fa_list, dep_list)]
            
            depr_df = pd.DataFrame({
                t('Năm'): labels_4,
                t('Giá trị Tài sản đầu kỳ'): [f"{v/1e9:,.0f} T" for v in fa_list],
                t('Khấu hao trong kỳ'): [f"{v/1e9:,.0f} T" for v in dep_list],
                t('Giá trị Tài sản cuối kỳ'): [f"{v/1e9:,.0f} T" for v in end_fa]
            })
            st.dataframe(depr_df, hide_index=True, use_container_width=True)
        
    st_debt = get_series(bs_df, ['short-term borrow', 'short-term debt', 'vay và nợ ngắn', 'short-term loan', 'deposit', 'due to gov', 'valuable paper'], 4)
    lt_debt = get_series(bs_df, ['long-term borrow', 'long-term debt', 'vay và nợ dài', 'long-term loan', 'borrowings from'], 4)
    st_debt, lt_debt = pad_s(st_debt, len(labels_4)), pad_s(lt_debt, len(labels_4))
    tot_debt = [s + l for s, l in zip(st_debt, lt_debt)]
    ie_list = get_series(is_df, ['interest expense', 'chi phí lãi', 'similar expense'], 4)
    ie_list = pad_s(ie_list, len(labels_4))
    
    # Logic Nợ Đầu kỳ - Cuối kỳ
    begin_debt = [tot_debt[0]] + tot_debt[:-1]
    debt_change = [end - beg for beg, end in zip(begin_debt, tot_debt)]
    
    if sum([abs(v) for v in tot_debt]) > 0 or sum([abs(v) for v in ie_list]) > 0:
        with st.expander(f"💳 {t('Bảng tính nợ (Debt Schedule)')}"):
            st.write(f"*{t('Theo dõi số dư nợ gốc và lãi vay phải trả.')}*")
            debt_df = pd.DataFrame({
                t('Năm'): labels_4,
                t('Nợ đầu kỳ'): [f"{v/1e9:,.0f} T" for v in begin_debt],
                t('Lãi vay'): [f"{abs(v)/1e9:,.0f} T" for v in ie_list],
                t('Trả gốc / Vay thêm'): [f"{v/1e9:,.0f} T" for v in debt_change],
                t('Nợ cuối kỳ'): [f"{v/1e9:,.0f} T" for v in tot_debt]
            })
            st.dataframe(debt_df, hide_index=True, use_container_width=True)
        
    ar_list = get_series(bs_df, ['receivable', 'phải thu', 'loan', 'advances to customer'], 4)
    inv_list = get_series(bs_df, ['inventor', 'tồn kho'], 4)
    ap_list = get_series(bs_df, ['payable', 'phải trả', 'prepayment', 'supplier', 'deposit', 'due to'], 4)
    ar_list, inv_list, ap_list = pad_s(ar_list, len(labels_4)), pad_s(inv_list, len(labels_4)), pad_s(ap_list, len(labels_4))
    nwc_list = [r + i - p for r, i, p in zip(ar_list, inv_list, ap_list)]
    
    if sum([abs(v) for v in ar_list]) > 0 or sum([abs(v) for v in inv_list]) > 0 or sum([abs(v) for v in ap_list]) > 0:
        with st.expander(f"⚙️ {t('Bảng vốn lưu động (Working Capital Schedule)')}"):
            st.write(f"*{t('Quản lý các khoản phải thu, phải trả và hàng tồn kho.')}*")
            
            wc_dict = {t('Năm'): labels_4}
            if sum([abs(v) for v in ar_list]) > 0:
                wc_dict[t('Khoản phải thu (AR)')] = [f"{v/1e9:,.0f} T" for v in ar_list]
            if sum([abs(v) for v in inv_list]) > 0:
                wc_dict[t('Hàng tồn kho (INV)')] = [f"{v/1e9:,.0f} T" for v in inv_list]
            if sum([abs(v) for v in ap_list]) > 0:
                wc_dict[t('Khoản phải trả (AP)')] = [f"{v/1e9:,.0f} T" for v in ap_list]
                
            wc_dict[t('Vốn lưu động ròng')] = [f"{v/1e9:,.0f} T" for v in nwc_list]
            wc_df = pd.DataFrame(wc_dict)
            st.dataframe(wc_df, hide_index=True, use_container_width=True)

    st.markdown("---")
    st.markdown(f"### ⚖️ {t('3. Định giá và Phân tích kết quả (Valuation & Outputs)')}")
    st.write(t('Sau khi có dự báo, chúng ta cần biết doanh nghiệp "đáng giá" bao nhiêu.'))
    st.markdown(f"- {t('**DCF (Discounted Cash Flow)**: Phương pháp chiết khấu dòng tiền để tìm giá trị hiện tại của doanh nghiệp.')}")
    st.latex(r"PV = \sum_{t=1}^{n} \frac{CF_t}{(1+r)^t} + \frac{TV}{(1+r)^n}")
    st.markdown(f"- {t('**Các chỉ số tài chính**: Tính toán các tỷ số như ROE, ROA dự phóng.')}")
    
    val_c1, val_c2 = st.columns(2)
    with val_c1:
        r_rate = st.number_input(t('Tỷ suất chiết khấu (r - Discount Rate) %'), min_value=0.0, max_value=100.0, value=10.0, step=0.5) / 100
    with val_c2:
        g_rate = st.number_input(t('Tăng trưởng dài hạn (g - Terminal Growth) %'), min_value=-50.0, max_value=50.0, value=3.0, step=0.5) / 100
        
    try:
        cf_list = list(future_nps) if len(future_nps) > 0 else [proj_profit, proj_profit * 1.05, proj_profit * 1.10]
    except NameError:
        cf_list = [proj_profit, proj_profit * 1.05, proj_profit * 1.10]
        
    pv = 0
    for t_idx, cf in enumerate(cf_list):
        pv += cf / ((1 + r_rate) ** (t_idx + 1))
        
    terminal_value = (cf_list[-1] * (1 + g_rate)) / (r_rate - g_rate) if r_rate > g_rate else 0
    pv += terminal_value / ((1 + r_rate) ** len(cf_list))
    
    current_eq = get_val(bs_df, ['equity', "owner's equity", 'vốn chủ sở hữu', 'nguồn vốn chủ sở hữu', 'vốn và các quỹ', 'vốn csh'])
    current_ass = get_val(bs_df, ['total assets', 'tổng cộng tài sản', 'tổng tài sản'])
    
    is_negative_dcf = False
    raw_pv = pv
    if pv <= 0:
        is_negative_dcf = True
        pv = current_eq
        st.warning(t("⚠️ Cảnh báo Đốt tiền (Cash Burn): Dòng tiền dự phóng bị âm dẫn đến DCF vô nghĩa. Giá trị Nội tại đã được tự động chuyển sang Phương pháp Tài sản Ròng (NAV - dựa trên Vốn CSH)."))
        
    latex_str = r"PV = "
    for i, cf in enumerate(cf_list):
        latex_str += r"\frac{" + f"{cf/1e9:,.0f}" + r"}{(1 + " + f"{r_rate}" + r")^{" + str(i+1) + r"}} + "
    latex_str += r"\frac{" + f"{terminal_value/1e9:,.0f}" + r"}{(1 + " + f"{r_rate}" + r")^{" + str(len(cf_list)) + r"}}"
    
    if is_negative_dcf:
        latex_str += r" = " + f"{raw_pv/1e9:,.0f}" + r" < 0 \text{ (Red Flag)} \Rightarrow PV = \text{NAV} = " + f"{pv/1e9:,.0f}"
    else:
        latex_str += r" \approx " + f"{pv/1e9:,.0f}"
        
    st.latex(latex_str)
    
    if is_negative_dcf:
        market_cap = get_val(rt_df, ['market capital', 'market cap', 'mkt cap', 'vốn hóa'])
        pb_ratio = get_val(rt_df, ['p/b', 'price to book', 'pb'])
        
        st.markdown(f"> **💡 {t('Lưu ý chuẩn Institutional Grade')}**: {t('Mô hình đang định giá dựa trên tài sản do hiệu quả hoạt động (ROE/ROA) chưa đạt kỳ vọng. NAV theo lý thuyết = Giá trị thị trường Tài sản - Nợ phải trả, tuy nhiên nếu giá trị sổ sách sát với thực tế, việc dùng Vốn chủ sở hữu làm NAV là hoàn toàn hợp lý.')}")
        
        if market_cap > 0:
            nav_bn = pv / 1e9
            cheap_msg = t("rẻ hơn") if market_cap < nav_bn else t("đắt hơn")
            pb_str = f"**{pb_ratio:.2f}**" if pb_ratio > 0 else "N/A"
            st.markdown(f"> **📊 {t('Chỉ số P/B (Price-to-Book)')}**: {t('Vốn hóa thị trường hiện tại')} là **{market_cap:,.0f} T**, đang **{cheap_msg}** {t('so với Giá trị sổ sách (NAV)')} ({nav_bn:,.0f} T). {t('Tỷ lệ P/B')} = {pb_str}.")
            
    proj_roe = (proj_profit / current_eq) * 100 if current_eq > 0 else 0
    proj_roa = (proj_profit / current_ass) * 100 if current_ass > 0 else 0
    
    with st.expander(t("🔍 Xem chi tiết thông số đầu vào (Calculation Breakdown)")):
        st.write(f"- **{t('Dòng tiền Dự Kiến (CF1, CF2...)')}**: " + " | ".join([f"{cf/1e9:,.0f} T" for cf in cf_list]))
        st.write(f"- **{t('Giá trị Thanh lý (Terminal Value - TV)')}**: {terminal_value/1e9:,.0f} T")
        st.write(f"- **{t('Vốn Chủ Sở Hữu (Equity)')}**: {current_eq/1e9:,.0f} T")
        st.write(f"- **{t('Tổng Tài Sản (Total Assets)')}**: {current_ass/1e9:,.0f} T")
    
    v_col1, v_col2, v_col3 = st.columns(3)
    with v_col1:
        st.markdown(f"""
        <div class="met-card" style="text-align: center; border-left: 4px solid #8E44AD;">
            <div class="met-label">{t('Giá trị Nội tại (Intrinsic Value / PV)')}</div>
            <div class="met-val" style="color: #8E44AD; font-size: 28px;">{pv/1e9:,.0f} T</div>
        </div>
        """, unsafe_allow_html=True)
    with v_col2:
        st.markdown(f"""
        <div class="met-card" style="text-align: center;">
            <div class="met-label">{t('ROE Kỳ vọng')}</div>
            <div class="met-val {'red' if proj_roe<0 else 'teal'}" style="font-size: 28px;">{proj_roe:,.2f}%</div>
        </div>
        """, unsafe_allow_html=True)
    with v_col3:
        st.markdown(f"""
        <div class="met-card" style="text-align: center;">
            <div class="met-label">{t('ROA Kỳ vọng')}</div>
            <div class="met-val {'red' if proj_roa<0 else 'teal'}" style="font-size: 28px;">{proj_roa:,.2f}%</div>
        </div>
        """, unsafe_allow_html=True)

    st.info(f"💡 **{t('Strategic Insights (Gợi ý chiến lược):')}** {t('Giá trị Nội tại (Intrinsic Value) trả lời câu hỏi: Doanh nghiệp này thực sự đáng giá bao nhiêu tiền dựa trên khả năng sinh lời hoặc tài sản cốt lõi? Nếu Giá thị trường đang thấp hơn Giá trị Nội tại, đồng thời P/B < 1.0, đây thường là Vùng mua an toàn (Margin of Safety).')}")

    st.markdown("---")
    st.markdown(f"### 🌡️ {t('4. Phân tích Độ nhạy (Sensitivity Analysis)')}")
    st.write(t("Mô phỏng rủi ro đặc thù theo từng nhóm ngành khi 2 biến số vĩ mô/vi mô thay đổi đồng thời (Tác động lên Lợi nhuận Ròng)."))
    
    base_rev = proj_rev
    base_cogs = proj_cogs
    base_sga = proj_sga
    base_profit = proj_profit
    
    x_label = t("Tăng trưởng Doanh thu / Cầu (%)")
    y_label = t("Biến động Chi phí / Cung (%)")
    
    if global_ticker in ['VCB', 'TCB', 'MBB', 'ACB', 'STB', 'CTG', 'BID', 'VPB', 'HDB', 'VIB', 'SSB', 'SHB'] or is_bank:
        x_label = t("Tăng trưởng Tín dụng (%)")
        y_label = t("Biến động NIM (%)")
    elif global_ticker in ['VHM', 'VIC', 'VRE', 'BCM']:
        x_label = t("Tỷ lệ Hấp thụ Dự án (%)")
        y_label = t("Lãi suất Vay (%)")
    elif global_ticker in ['HPG', 'GAS', 'PLX', 'GVR', 'POW', 'DPM', 'DCM']:
        x_label = t("Giá bán Đầu ra (%)")
        y_label = t("Giá Nguyên liệu Đầu vào (%)")
    elif global_ticker in ['MWG', 'MSN', 'VNM', 'SAB', 'PNJ']:
        x_label = t("Tăng trưởng SSS/Sức mua (%)")
        y_label = t("Biến động Chi phí SG&A (%)")
    elif global_ticker in ['VJC', 'HVN']:
        x_label = t("Hệ số Lấp đầy (Load Factor) (%)")
        y_label = t("Giá Nhiên liệu (Jet A1) (%)")
    elif global_ticker in ['FPT', 'CMG']:
        x_label = t("Doanh thu Chuyển đổi số (%)")
        y_label = t("Chi phí Nhân sự IT (%)")

    st.markdown(f"**Trục X (Cột):** {x_label} | **Trục Y (Hàng):** {y_label}")
    
    legend_html = f"""
    <div style="display: flex; justify-content: center; align-items: center; gap: 15px; margin-bottom: 10px; font-size: 13px; color: #555;">
        <strong>{t('Chú giải màu sắc:')}</strong>
        <div style="display: flex; align-items: center; gap: 5px;"><span style="display: inline-block; width: 14px; height: 14px; background-color: #1ABC9C; border-radius: 3px;"></span> {t('Đột phá (>+10%)')}</div>
        <div style="display: flex; align-items: center; gap: 5px;"><span style="display: inline-block; width: 14px; height: 14px; background-color: #D4EFDF; border-radius: 3px;"></span> {t('Tăng trưởng')}</div>
        <div style="display: flex; align-items: center; gap: 5px;"><span style="display: inline-block; width: 14px; height: 14px; background-color: #FEF9E7; border: 2px solid #F39C12; border-radius: 3px; box-sizing: border-box;"></span> {t('Cơ sở (Base)')}</div>
        <div style="display: flex; align-items: center; gap: 5px;"><span style="display: inline-block; width: 14px; height: 14px; background-color: #F1948A; border-radius: 3px;"></span> {t('Suy giảm')}</div>
        <div style="display: flex; align-items: center; gap: 5px;"><span style="display: inline-block; width: 14px; height: 14px; background-color: #C0392B; border-radius: 3px;"></span> {t('Thua lỗ (<0)')}</div>
    </div>
    """
    st.markdown(legend_html, unsafe_allow_html=True)
    
    x_ranges = [-0.10, -0.05, 0.0, 0.05, 0.10]
    y_ranges = [-0.10, -0.05, 0.0, 0.05, 0.10]
    
    x_labels = [f"{x*100:+.0f}%" for x in x_ranges]
    y_labels = [f"{y*100:+.0f}%" for y in y_ranges]
    
    # 1. Determine Sector Logic robustly WITHOUT checking localized strings
    sector_type = "COMMODITY_DEFAULT"
    if global_ticker in ['VCB', 'TCB', 'MBB', 'ACB', 'STB', 'CTG', 'BID', 'VPB', 'HDB', 'VIB', 'SSB', 'SHB'] or is_bank:
        sector_type = "BANK"
    elif global_ticker in ['VHM', 'VIC', 'VRE', 'BCM']:
        sector_type = "REAL_ESTATE"
    elif global_ticker in ['MWG', 'MSN', 'VNM', 'SAB', 'PNJ', 'FPT', 'CMG']:
        sector_type = "SGA_DRIVEN"

    x_labels[0] = f"-10% ({t('Xấu nhất')})"
    x_labels[2] = f"+0% ({t('Nền')})"
    x_labels[-1] = f"+10% ({t('Tối ưu')})"
    
    if sector_type == "BANK": 
        y_labels[0] = f"-10% ({t('Xấu nhất')})"
        y_labels[2] = f"+0% ({t('Nền')})"
        y_labels[-1] = f"+10% ({t('Tối ưu')})"
    else: 
        y_labels[0] = f"-10% ({t('Tối ưu')})"
        y_labels[2] = f"+0% ({t('Nền')})"
        y_labels[-1] = f"+10% ({t('Xấu nhất')})"
        
    df_sens = pd.DataFrame(index=y_labels, columns=x_labels)
    
    for i, y_val in enumerate(y_ranges):
        for j, x_val in enumerate(x_ranges):
            sim_rev = base_rev * (1 + x_val)
            if sector_type == "BANK": 
                sim_profit = sim_rev * ( (base_profit / base_rev) + y_val ) if base_rev != 0 else base_profit * (1 + x_val + y_val)
            elif sector_type == "REAL_ESTATE":
                sim_cogs = base_cogs * (1 + x_val)
                sim_profit = sim_rev - sim_cogs - (base_sga * (1 + y_val)) - other_expenses
            elif sector_type == "SGA_DRIVEN":
                sim_profit = sim_rev - base_cogs - (base_sga * (1 + y_val)) - other_expenses
            else:
                sim_profit = sim_rev - (base_cogs * (1 + y_val)) - base_sga - other_expenses
            df_sens.iloc[i, j] = sim_profit / 1e9

    def color_cells(val):
        try:
            v_str = str(val).replace(' T', '').replace(',', '')
            v = float(v_str)
            bp_bn = base_profit / 1e9
            
            if bp_bn * 0.98 <= v <= bp_bn * 1.02: return 'background-color: #FEF9E7; color: #7D6608; border: 2px solid #F39C12; font-weight: bold;'
            elif v >= bp_bn * 1.10: return 'background-color: #1ABC9C; color: #FFFFFF;'
            elif v >= bp_bn * 1.02: return 'background-color: #D4EFDF; color: #186A3B;'
            elif v < 0: return 'background-color: #C0392B; color: #FFFFFF;'
            elif v <= bp_bn * 0.90: return 'background-color: #F1948A; color: #78281F;'
            else: return 'background-color: #FADBD8; color: #78281F;'
        except:
            return ''

    df_st = df_sens.astype(float).style
    if hasattr(df_st, 'map'):
        styled_df = df_st.map(color_cells).format("{:,.0f} T")
    else:
        styled_df = df_st.applymap(color_cells).format("{:,.0f} T")
        
    st.dataframe(styled_df, use_container_width=True)
    
    t_mat = 'Công cụ Quản trị Rủi ro (Risk Matrix) trả lời câu hỏi "Chuyện gì xảy ra nếu...?". Vùng màu đỏ đại diện cho các kịch bản đe dọa trực tiếp đến cấu trúc vốn. Hãy đặc biệt chú ý đến biến trục Y (Core driver), vì chỉ một thay đổi nhỏ cũng có thể khiến lợi nhuận bốc hơi nhanh chóng.'
    st.info(f"💡 **{t('Strategic Insights (Gợi ý chiến lược):')}** {t(t_mat)}")

elif selected_module == "5. Wealth Management":
    st.markdown(f'<div class="section-title">⚖️ {t("3. Portfolio Wealth Management")}</div>', unsafe_allow_html=True)
    
    st.markdown(f"### {t('🛒 Xây dựng Danh mục')}")
    selected_ports = st.multiselect(t("Chọn các mã gia nhập Danh mục của bạn:"), options=tickers, default=[global_ticker, "HPG"] if "HPG" in tickers else [global_ticker])
    
    if len(selected_ports) < 2:
        st.warning(t("Vui lòng chọn ít nhất 2 mã cổ phiếu để cấu trúc một danh mục chống rủi ro hệ thống."))
    else:
        st.markdown(t("**Phân bổ tỷ trọng vốn (Weights):**"))
        cols = st.columns(len(selected_ports))
        weights = []
        for i, tick in enumerate(selected_ports):
            key_name = f"weight_{tick}_{len(selected_ports)}"
            if key_name not in st.session_state:
                st.session_state[key_name] = 100.0 / len(selected_ports)
                
            with cols[i]:
                w = st.number_input(f"{t('Tỷ trọng')} {tick} (%)", min_value=0.0, max_value=100.0, key=key_name)
                weights.append(w)
        
        weights = np.array(weights) / 100
        
        if abs(sum(weights) - 1.0) > 0.01:
            st.error(t("Tổng tỷ trọng phải bằng 100%. Vui lòng điều chỉnh lại."))
        else:
            # Lấy dữ liệu giá
            price_data = {}
            for ticker_sym in selected_ports:
                td = load_local_data(ticker_sym)
                if td and not td.get('Price').empty:
                    df = td['Price'].copy()
                    df['time'] = pd.to_datetime(df['time'])
                    df.set_index('time', inplace=True)
                    price_data[ticker_sym] = df['close']
            
            if len(price_data) == len(selected_ports):
                import plotly.express as px
                prices = pd.DataFrame(price_data).dropna()
                returns = prices.pct_change().dropna()
                
                # Tính toán Modern Portfolio Theory
                mean_returns = returns.mean() * 252 # Annualized
                cov_matrix = returns.cov() * 252
                
                port_return = np.sum(mean_returns * weights)
                port_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
                sharpe_ratio = port_return / port_volatility if port_volatility > 0 else 0
                
                # --- MONTE CARLO MARKOWITZ ---
                num_portfolios = 5000
                results = np.zeros((3, num_portfolios))
                all_weights = np.zeros((num_portfolios, len(selected_ports)))
                
                for i in range(num_portfolios):
                    weights_rand = np.random.random(len(selected_ports))
                    weights_rand /= np.sum(weights_rand)
                    all_weights[i,:] = weights_rand
                    
                    p_rt = np.sum(mean_returns * weights_rand)
                    p_vol = np.sqrt(np.dot(weights_rand.T, np.dot(cov_matrix, weights_rand)))
                    
                    results[0,i] = p_rt
                    results[1,i] = p_vol
                    results[2,i] = p_rt / p_vol if p_vol > 0 else 0
                    
                # Nhận diện Optimal Portfolio
                max_sharpe_idx = np.argmax(results[2])
                opt_return = results[0, max_sharpe_idx]
                opt_volatility = results[1, max_sharpe_idx]
                opt_weights = all_weights[max_sharpe_idx]
                
                st.markdown(f"### {t('🎯 Tình trạng Danh mục (Current Portfolio Status)')}")
                m1, m2, m3 = st.columns(3)
                diff_return = port_return*100 - opt_return*100
                m1.metric(t("Lợi nhuận Kỳ vọng (Năm)"), f"{port_return*100:.1f}%", f"{diff_return:+.1f}% vs Max Sharpe" if abs(diff_return) > 0.1 else "")
                m2.metric(t("Mức độ Rủi ro (Volatility)"), f"{port_volatility*100:.1f}%")
                m3.metric(t("Sharpe Ratio"), f"{sharpe_ratio:.2f}")

                st.markdown("---")
                # CHARTS: Pie & Heatmap
                ch_col1, ch_col2 = st.columns(2)
                with ch_col1:
                    st.markdown(f"**{t('Tỷ trọng Hiện tại (Current Allocation)')}**")
                    fig_pie = go.Figure(data=[go.Pie(labels=selected_ports, values=weights, hole=.4, textinfo='label+percent')])
                    fig_pie.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=320, showlegend=False)
                    st.plotly_chart(fig_pie, use_container_width=True)

                with ch_col2:
                    st.markdown(f"**{t('Ma trận Tương quan Rủi ro (Correlation Heatmap)')}**")
                    corr_matrix = returns.corr().round(2)
                    fig_corr = px.imshow(corr_matrix, text_auto=True, color_continuous_scale="RdBu_r", aspect="auto")
                    fig_corr.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=320)
                    st.plotly_chart(fig_corr, use_container_width=True)
                    st.info(f"💡 **{t('Strategic Insights (Gợi ý chiến lược):')}**\n\n- **{t('Tương quan Dương (+1)')}**: {t('Hai mã di chuyển cùng chiều. Nếu bạn mua HPG và HSG, bạn không hề đa dạng hóa, bạn chỉ đang nhân đôi rủi ro.')}\n- **{t('Tương quan Bằng 0 (0)')}**: {t('Hai mã không có mối liên hệ nào. Trạng thái tốt để giảm rủi ro hệ thống.')}\n- **{t('Tương quan Âm (-1)')}**: {t('Hai mã di chuyển ngược chiều. Đây là chén thánh trong hedging. Khi mã này giảm, mã kia tăng để bù đắp lại.')}")

                st.markdown("---")
                st.markdown(f"### ☁️ {t('Đường cong Markowitz (Monte Carlo: 5000 Kịch bản)')}")
                fig_mk = go.Figure()
                # Random Portfolios
                fig_mk.add_trace(go.Scatter(x=results[1,:], y=results[0,:], mode='markers',
                                          marker=dict(color=results[2,:], colorscale='Viridis', showscale=True, size=5,
                                                      colorbar=dict(title="Sharpe")),
                                          name=t('Danh mục Ngẫu nhiên')))
                # Current Port
                fig_mk.add_trace(go.Scatter(x=[port_volatility], y=[port_return], mode='markers',
                                          marker=dict(color='#E74C3C', size=15, symbol='star', line=dict(width=2, color='white')),
                                          name=t('Danh mục của bạn')))
                # Max Sharpe
                fig_mk.add_trace(go.Scatter(x=[opt_volatility], y=[opt_return], mode='markers',
                                          marker=dict(color='#F39C12', size=15, symbol='diamond', line=dict(width=2, color='white')),
                                          name=t('Điểm Tối ưu (Max Sharpe)')))
                                      
                fig_mk.update_layout(
                    xaxis_title=t('Rủi ro - Volatility (Std. Deviation)'), 
                    yaxis_title=t('Lợi nhuận - Expected Return'), 
                    height=450, 
                    margin=dict(t=30, b=10, l=10, r=10),
                    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
                )
                st.plotly_chart(fig_mk, use_container_width=True)
                
                t_mark = 'Khoảng cách giữa Danh mục Hiện tại (Ngôi sao đỏ) và Điểm Tối ưu (Kim cương vàng) chính là phần lợi nhuận bạn đang bỏ quên trên bàn do phân bổ vốn chưa hợp lý. Hãy sử dụng Cố vấn Tái cơ cấu bên dưới để thu hồi phần lợi nhuận này.'
                st.info(f"💡 **{t('Strategic Insights (Gợi ý chiến lược):')}** {t(t_mark)}")
                
                st.markdown("---")
                st.markdown(f"### {t('🔄 Cố vấn Tái cơ cấu & Quản trị Rủi ro (Rebalancing)')}")
                
                c_rb1, c_rb2 = st.columns(2)
                with c_rb1:
                    st.write(f"**1. {t('Gợi ý Danh mục Tối ưu (Max Sharpe Ratio)')}**")
                    opt_df = pd.DataFrame({t('Mã CP'): selected_ports, t('Hiện tại'): weights*100, t('Tối ưu (Gợi ý)'): opt_weights*100})
                    opt_df[t('Hiện tại')] = opt_df[t('Hiện tại')].map("{:.1f}%".format)
                    opt_df[t('Tối ưu (Gợi ý)')] = opt_df[t('Tối ưu (Gợi ý)')].map("{:.1f}%".format)
                    st.table(opt_df.set_index(t('Mã CP')))
                    def apply_opt(w_arr, p_arr):
                        for c_idx, c_tick in enumerate(p_arr):
                            st.session_state[f"weight_{c_tick}_{len(p_arr)}"] = w_arr[c_idx] * 100
                            
                    st.button(t("🪄 Tự động Áp dụng Tỷ trọng Tối ưu"), on_click=apply_opt, args=(opt_weights, selected_ports))
                
                with c_rb2:
                    st.write(f"**2. {t('Tính toán Phí Chuyển đổi (Rebalancing Costs)')}**")
                    turnover = np.sum(np.abs(opt_weights - weights)) / 2 
                    trading_fee_tax = 0.0025 # 0.25% average
                    drag_cost = turnover * trading_fee_tax
                    extra_return = max(0, opt_return - port_return)
                    
                    if extra_return > drag_cost + 0.001: 
                        st.success(f"✔️ **{t('NÊN ĐẢO DANH MỤC!')}**\n\n{t('Lợi nhuận kỳ vọng tăng')} **+{extra_return*100:.2f}%**, {t('trong khi chi phí cơ cấu (Thuế+Phí) ước tính chỉ tốn')} **-{drag_cost*100:.3f}%** NAV.")
                    elif extra_return > 0.0001:
                        st.warning(f"⚠️ **{t('CÂN NHẮC KỸ!')}**\n\n{t('Biên lợi nhuận phụ trội')} (**+{extra_return*100:.2f}%**) {t('gần như bị ăn mòn hết bởi chi phí xào chẻ danh mục')} (**-{drag_cost*100:.3f}%** NAV). {t('Bạn nên Hold (Giữ nguyên).')}")
                    else:
                        st.info(f"💎 **{t('HOÀN HẢO!')}**\n\n{t('Danh mục của bạn hiện đã nằm ở mức hiệu quả cao nhất của đường chân trời Markowitz.')}")
                
                st.markdown("---")
                st.markdown(f"### {t('📉 Khảo nghiệm Sức chịu đựng (Stress Testing)')}")
                # Shock Events
                market_vol = 0.20 # Average VN-Index historically ~ 20% annualized vol
                beta_proxy = port_volatility / market_vol if market_vol > 0 else 1
                crash_2008 = -0.65 * beta_proxy # 2008 Crash -65%
                crash_2022 = -0.38 * beta_proxy # 2022 Crash -38%
                
                msg_stress = f"⚠️ **{t('Mô phỏng thảm họa Thiên nga đen (Black Swan):')}**\n\n"
                msg_stress += f"{t('Với độ nhạy rủi ro hệ thống (Beta Proxy) ước tính  ≈ ')} **{beta_proxy:.2f}**, "
                msg_stress += f"{t('thuật toán AI ước lượng Mức sụt giảm tối đa (Max Drawdown) mà bạn có thể phải gánh chịu là:')} \n\n"
                msg_stress += f"- {t('Khủng hoảng Vĩ mô / Bắt bớ (Kịch bản 2022):')} **{crash_2022*100:.1f}%** \n"
                msg_stress += f"- {t('Đại suy thoái Toàn cầu (Kịch bản 2008):')} **{crash_2008*100:.1f}%**"
                
                st.error(msg_stress)
                
            else:
                st.error(t("Không đủ dữ liệu giá đóng cửa Offline để tính toán cho một số mã đã chọn."))

elif selected_module == "6. About Me":
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1.5, 3.5], gap="large")
    
    with col1:
        st.markdown(f"### 📞 {t('Liên hệ')}")
        st.markdown(f"📧 **Email:** [hoanhkhoa1009@gmail.com](mailto:hoanhkhoa1009@gmail.com)")
        st.markdown(f"🌐 **LinkedIn:** [anh-khoa-3223912a0](https://www.linkedin.com/in/anh-khoa-3223912a0)")
    
    with col2:
        st.markdown(f"### 🧑‍💻 {t('Giới thiệu bản thân')}")
        st.markdown(f"#### **{t('Xin chào, tôi là Khoa.')}**")
        st.markdown(t('Chào mừng bạn đến với dự án cá nhân của tôi — một hệ thống được ấp ủ và phát triển từ niềm đam mê sâu sắc với thị trường tài chính Việt Nam.'))
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(t('Để tối ưu hóa quá trình xây dựng, tôi đã ứng dụng Google Antigravity. Nền tảng phát triển AI thế hệ mới này giúp tôi vượt qua những rào cản của việc viết code thủ công, từ đó dồn toàn bộ tâm trí vào việc định hình ý tưởng và hoàn thiện logic phân tích cốt lõi.'))
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(t('Nếu bạn ghé thăm trang web này từ CV của tôi, hy vọng hệ thống này sẽ là minh chứng rõ nét nhất: với tôi, kiến thức không chỉ nằm trên giấy tờ, mà phải được chuyển hóa thành năng lực thực thi và sản phẩm vận hành thực tế.'))
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"{t('Trân trọng,')}<br><b>Hồ Anh Khoa</b>", unsafe_allow_html=True)

