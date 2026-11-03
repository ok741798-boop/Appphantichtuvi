/* Tiện ích dùng chung, logic trang chủ và khởi động trang kết quả. */

const STORAGE_KEYS = { chartId: 'tuvi_chart_id', birthInfo: 'tuvi_birth_info' };
const TOAST_DURATION_MS = 4500;
const MIN_BIRTH_DATE = '1900-01-01';
const LATE_TY_HOUR = 23;
const LIVE_SERVER_PORT = '5500';
// Mở thẳng file HTML hoặc qua Live Server thì trang không do Flask phục vụ, phải gọi API theo địa chỉ đầy đủ.
const OPENED_WITHOUT_FLASK = window.location.protocol === 'file:' || window.location.port === LIVE_SERVER_PORT;
const API_BASE = OPENED_WITHOUT_FLASK ? 'http://127.0.0.1:5057/api' : '/api';
const SERVER_CHECK_MS = 3000;
// Bản đăng trên GitHub Pages chạy Python ngay trong trình duyệt, xem pyodide-bridge.js.
const BROWSER_PYTHON = window.tuviPython;
const BROWSER_PYTHON_ERROR = 'Không tải được bộ tính lá số. Hãy kiểm tra kết nối mạng rồi tải lại trang.';
const SERVER_DOWN_MESSAGE = 'Chưa kết nối được máy chủ. Hãy bấm đúp file run.bat trong thư mục tuvi-analyzer '
    + 'và giữ cửa sổ đó mở. Trang sẽ tự kết nối lại.';

// ==================== Tiện ích chung ====================

/** Escape chuỗi trước khi chèn vào innerHTML. */
function escapeHtml(value) {
    const element = document.createElement('div');
    element.textContent = String(value ?? '');
    return element.innerHTML;
}

/** Hiện thông báo ở góc phải màn hình. type: info, success hoặc error. */
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast--${type}`;
    toast.textContent = message;
    container.append(toast);
    setTimeout(() => toast.remove(), TOAST_DURATION_MS);
}

/** Gọi API JSON; lỗi mạng hoặc lỗi HTTP đều ném Error có thông điệp tiếng Việt. */
async function apiRequest(path, options = {}) {
    let response;
    try {
        response = await (BROWSER_PYTHON
            ? BROWSER_PYTHON.fetch(path, options)
            : fetch(`${API_BASE}${path}`, options));
    } catch {
        throw new Error(BROWSER_PYTHON ? BROWSER_PYTHON_ERROR : SERVER_DOWN_MESSAGE);
    }
    if (response.ok) {
        return response;
    }
    const body = await response.json().catch(() => ({}));
    const error = new Error(body.error || 'Máy chủ gặp lỗi, vui lòng thử lại.');
    error.status = response.status;
    throw error;
}

/** Hỏi server TuVi còn chạy không, không ném lỗi. Server khác chiếm cùng cổng thì coi như chưa chạy. */
async function isServerOnline() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        return response.ok && (await response.json()).app === 'tuvi-analyzer';
    } catch {
        return false;
    }
}

/** Server tắt thì hiện băng hướng dẫn và hỏi lại định kỳ; có lại thì ẩn băng. */
async function watchServer() {
    // Không có server riêng thì không cần báo; lỗi tải Pyodide hiện qua thông báo của từng request.
    if (BROWSER_PYTHON || await isServerOnline()) {
        return;
    }
    const banner = document.createElement('div');
    banner.className = 'server-banner';
    banner.setAttribute('role', 'alert');
    banner.textContent = SERVER_DOWN_MESSAGE;
    document.body.prepend(banner);
    const timer = setInterval(async () => {
        if (!await isServerOnline()) {
            return;
        }
        clearInterval(timer);
        banner.remove();
        showToast('Đã kết nối máy chủ.', 'success');
        // Trang kết quả cần tải lại dữ liệu; trang chủ giữ nguyên để không mất thông tin đã nhập.
        if (!document.getElementById('birth-form') || document.getElementById('destiny-form')) {
            window.location.reload();
        }
    }, SERVER_CHECK_MS);
}

/** Gửi POST với body JSON và trả về JSON kết quả. */
async function apiPost(path, body) {
    const response = await apiRequest(path, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
    });
    return response.json();
}

/** Đọc localStorage; trình duyệt chặn lưu trữ thì trả về null. */
function readStorage(key) {
    try {
        return localStorage.getItem(key);
    } catch {
        return null;
    }
}

/** Ghi localStorage; lỗi thì bỏ qua vì chỉ làm mất khả năng khôi phục khi refresh. */
function writeStorage(key, value) {
    try {
        localStorage.setItem(key, value);
    } catch {
        showToast('Trình duyệt không cho lưu dữ liệu, tải lại trang có thể mất lá số.');
    }
}

/** Lưu lá số vừa lập để tải lại trang vẫn còn. */
function saveChartReference(chart) {
    writeStorage(STORAGE_KEYS.chartId, chart.chart_id);
    writeStorage(STORAGE_KEYS.birthInfo, JSON.stringify(chart.info));
}

/** Đổi điểm thang 10 sang số sao 1-5. */
function toFiveStars(rating) {
    return Math.min(5, Math.max(1, Math.round(rating / 2)));
}

/** Dựng HTML dãy 5 sao từ điểm thang 10. */
function ratingStars(rating) {
    const stars = toFiveStars(rating);
    return `<span class="rating" role="img" aria-label="${stars} trên 5 sao">`
        + `${'★'.repeat(stars)}${'☆'.repeat(5 - stars)}</span>`;
}

// ==================== Trang chủ ====================

/** Lấy ngày hôm nay theo giờ máy, định dạng YYYY-MM-DD. */
function todayIso() {
    const now = new Date();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    return `${now.getFullYear()}-${month}-${day}`;
}

/** Hiện hoặc xóa lỗi của một trường trong form. */
function setFieldError(inputId, message) {
    document.getElementById(`${inputId}-error`).textContent = message;
    document.getElementById(inputId)?.setAttribute('aria-invalid', message ? 'true' : 'false');
}

/** Kiểm tra form; trả về dữ liệu gửi API, hoặc null nếu có lỗi. */
function readBirthForm(form) {
    const data = new FormData(form);
    const fullName = data.get('full_name').trim();
    const gender = data.get('gender');
    const birthDate = data.get('birth_date');
    const hour = data.get('hour');
    const dateValid = birthDate >= MIN_BIRTH_DATE && birthDate <= todayIso();

    setFieldError('full-name', fullName ? '' : 'Vui lòng nhập họ tên.');
    setFieldError('gender', gender ? '' : 'Vui lòng chọn giới tính.');
    setFieldError('birth-date', dateValid ? '' : 'Ngày sinh phải từ 01/01/1900 đến hôm nay.');
    setFieldError('birth-hour', hour ? '' : 'Vui lòng chọn giờ sinh.');
    if (!fullName || !gender || !dateValid || !hour) {
        return null;
    }

    const [year, month, day] = birthDate.split('-').map(Number);
    const lateTy = hour === '0' && document.getElementById('late-ty').checked;
    return {
        full_name: fullName,
        gender,
        year,
        month,
        day,
        hour: lateTy ? LATE_TY_HOUR : Number(hour),
        birth_place: data.get('birth_place').trim(),
    };
}

/** Gán sự kiện cho form nhập thông tin sinh. */
function initHomePage(form) {
    const hourSelect = document.getElementById('birth-hour');
    const lateTyField = document.getElementById('late-ty-field');
    const overlay = document.getElementById('loading-overlay');
    document.getElementById('birth-date').max = todayIso();

    hourSelect.addEventListener('change', () => {
        lateTyField.hidden = hourSelect.value !== '0';
    });

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const payload = readBirthForm(form);
        if (!payload) {
            showToast('Vui lòng kiểm tra lại thông tin.', 'error');
            return;
        }
        overlay.hidden = false;
        try {
            saveChartReference(await apiPost('/chart/build', payload));
            window.location.href = form.dataset.next || 'result.html';
        } catch (error) {
            overlay.hidden = true;
            showToast(error.message, 'error');
        }
    });
}

// ==================== Trang kết quả ====================

/** Tải lá số đã lưu; server khởi động lại thì lập lại từ thông tin sinh đã lưu. */
async function loadChart(chartId) {
    try {
        const response = await apiRequest(`/chart/${encodeURIComponent(chartId)}`);
        return await response.json();
    } catch (error) {
        const birthInfo = readStorage(STORAGE_KEYS.birthInfo);
        if (error.status !== 404 || !birthInfo) {
            throw error;
        }
        const chart = await apiPost('/chart/build', JSON.parse(birthInfo));
        saveChartReference(chart);
        return chart;
    }
}

/** Hiện dòng thông tin người xem phía trên các tab. */
function renderProfile(chart) {
    const { info, lunar, can_chi: canChi } = chart;
    const leap = lunar.is_leap ? ' nhuận' : '';
    const pad = (value) => String(value).padStart(2, '0');
    const place = info.birth_place ? ` · ${escapeHtml(info.birth_place)}` : '';
    document.getElementById('profile').innerHTML = `
        <h1 class="profile__name">${escapeHtml(info.full_name)}</h1>
        <p class="profile__meta">${escapeHtml(info.gender)} · Dương lịch
            ${pad(info.day)}/${pad(info.month)}/${info.year} · giờ ${escapeHtml(chart.gio_sinh)}${place}</p>
        <p class="profile__meta">Âm lịch ${lunar.lunar_day}/${lunar.lunar_month}${leap}/${lunar.lunar_year} ·
            Năm ${escapeHtml(canChi.year)} · Tháng ${escapeHtml(canChi.month)} ·
            Ngày ${escapeHtml(canChi.day)} · Giờ ${escapeHtml(canChi.hour)}</p>`;
}

/** Hiện spinner trong một tab. */
function showPanelLoading(panel, message) {
    panel.innerHTML = `<div class="panel-status"><div class="spinner" role="status"></div>
        <p>${escapeHtml(message)}</p></div>`;
}

/** Hiện lỗi trong một tab, kèm nút thử lại nếu có. */
function showPanelError(panel, message, retry) {
    panel.innerHTML = `<div class="panel-status"><p>${escapeHtml(message)}</p></div>`;
    if (retry) {
        const button = document.createElement('button');
        button.className = 'btn btn--ghost';
        button.type = 'button';
        button.textContent = 'Thử lại';
        button.addEventListener('click', retry);
        panel.querySelector('.panel-status').append(button);
    }
}

/** Tạo hàm nạp dữ liệu một lần cho tab; lỗi thì cho phép thử lại. */
function createTabLoader(panel, loadingMessage, load) {
    let loaded = false;
    const run = async () => {
        if (loaded) {
            return;
        }
        loaded = true;
        showPanelLoading(panel, loadingMessage);
        try {
            await load();
        } catch (error) {
            loaded = false;
            showToast(error.message, 'error');
            // 404: server đã khởi động lại, tải lại trang để lập lại lá số.
            showPanelError(panel, error.message, error.status === 404 ? () => window.location.reload() : run);
        }
    };
    return run;
}

/** Gán sự kiện chuyển tab. */
function initTabs(loaders) {
    const buttons = document.querySelectorAll('.tabs__button');
    buttons.forEach((button) => {
        button.addEventListener('click', () => {
            buttons.forEach((other) => {
                const active = other === button;
                other.classList.toggle('tabs__button--active', active);
                other.setAttribute('aria-selected', String(active));
                document.getElementById(`panel-${other.dataset.tab}`).hidden = !active;
            });
            loaders[button.dataset.tab]?.();
        });
    });
}

/** Tải PDF từ server và lưu về máy. */
async function exportPdf(chart, button) {
    button.disabled = true;
    try {
        const response = await apiRequest(`/chart/${encodeURIComponent(chart.chart_id)}/pdf`);
        const url = URL.createObjectURL(await response.blob());
        const link = document.createElement('a');
        link.href = url;
        link.download = `la-so-tu-vi-${chart.info.year}.pdf`;
        link.click();
        URL.revokeObjectURL(url);
        showToast('Đã xuất file PDF.', 'success');
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        button.disabled = false;
    }
}

/** Khởi động trang kết quả. */
async function initResultPage() {
    const chartPanel = document.getElementById('panel-chart');
    const currentPanel = document.getElementById('panel-current');
    const futurePanel = document.getElementById('panel-future');
    const chartId = readStorage(STORAGE_KEYS.chartId);

    if (!chartId) {
        showPanelError(chartPanel, 'Bạn chưa có lá số. Hãy quay lại trang chủ để lập lá số.');
        return;
    }

    let chart;
    try {
        chart = await loadChart(chartId);
    } catch (error) {
        showToast(error.message, 'error');
        showPanelError(chartPanel, error.message, initResultPage);
        return;
    }

    renderProfile(chart);
    renderChart(chart, chartPanel);
    initForecastModal();

    initTabs({
        current: createTabLoader(currentPanel, 'Đang luận giải vận hạn năm nay...', async () => {
            renderAnalysis(await apiPost('/analysis/current', { chart_id: chart.chart_id }), currentPanel);
        }),
        future: createTabLoader(futurePanel, 'Đang tính vận hạn 10 năm tới...', async () => {
            const { forecast } = await apiPost('/analysis/forecast', { chart_id: chart.chart_id });
            renderForecast(forecast, futurePanel);
        }),
    });

    const pdfButton = document.getElementById('export-pdf');
    pdfButton.disabled = false;
    pdfButton.addEventListener('click', () => exportPdf(chart, pdfButton));
}

document.addEventListener('DOMContentLoaded', () => {
    watchServer();
    const form = document.getElementById('birth-form');
    if (form) {
        initHomePage(form);
    } else if (document.getElementById('result-page')) {
        initResultPage();
    }
});
