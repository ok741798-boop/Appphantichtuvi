/* Dựng bảng lá số 12 cung và tooltip ý nghĩa sao. */

// Vị trí trên lưới 4x4 theo Địa Chi, thứ tự Tý -> Hợi: [hàng, cột], đếm từ 1.
const PALACE_GRID = [
    [4, 3], [4, 2], [4, 1], [3, 1], [2, 1], [1, 1],
    [1, 2], [1, 3], [1, 4], [2, 4], [3, 4], [4, 4],
];
const TOOLTIP_GAP_PX = 10;

/** Dựng nút một sao, kèm nhãn Hóa nếu sao đó được hóa. */
function starHtml(name, kind, tuHoa) {
    const hoa = tuHoa.find((item) => item.star === name);
    const hoaLabel = hoa
        ? `<button class="star star--hoa" type="button" data-star="${escapeHtml(hoa.hoa)}">${escapeHtml(hoa.hoa.replace('Hóa ', ''))}</button>`
        : '';
    return `<span><button class="star star--${kind}" type="button" data-star="${escapeHtml(name)}">${escapeHtml(name)}</button>${hoaLabel}</span>`;
}

/** Dựng HTML một cung. */
function palaceHtml(palace, isMenh) {
    const [row, column] = PALACE_GRID[palace.position_index];
    const mainStars = palace.chinh_tinh.map((name) => starHtml(name, 'main', palace.tu_hoa)).join('');
    const minorStars = palace.phu_tinh.map((name) => starHtml(name, 'minor', palace.tu_hoa)).join('');
    const marks = [
        palace.is_than ? '<span class="mark">Thân</span>' : '',
        palace.tuan ? '<span class="mark mark--block">Tuần</span>' : '',
        palace.triet ? '<span class="mark mark--block">Triệt</span>' : '',
    ].join('');
    return `
        <article class="palace${isMenh ? ' palace--menh' : ''}" style="--grid-row: ${row}; --grid-column: ${column}">
            <div class="palace__head">
                <span class="palace__name">${escapeHtml(palace.name)}</span>
                <span class="palace__branch">${escapeHtml(palace.can)} ${escapeHtml(palace.position)}</span>
            </div>
            <div class="palace__stars palace__stars--main">
                ${mainStars || '<span class="palace__empty">Vô chính diệu</span>'}
            </div>
            <div class="palace__stars palace__stars--minor">${minorStars}</div>
            <div class="palace__foot">
                <span>${escapeHtml(palace.trang_sinh)}</span>
                <span class="palace__marks">${marks}</span>
                <span>Đại vận ${escapeHtml(palace.dai_van_age)}</span>
            </div>
        </article>`;
}

/** Dựng ô trung tâm của lá số. */
function centerHtml(chart) {
    const rows = [
        ['Âm dương', chart.am_duong],
        ['Bản mệnh', chart.ban_menh],
        ['Cục', chart.cuc.name],
        ['Mệnh chủ', chart.menh_chu],
        ['Thân chủ', chart.than_chu],
        ['Thân cư', chart.than_cu],
        ['Đại vận', chart.chieu_dai_van],
    ];
    const list = rows
        .map(([label, value]) => `<dt>${escapeHtml(label)}</dt><dd>${escapeHtml(value)}</dd>`)
        .join('');
    return `
        <div class="chart-center">
            <div class="chart-center__symbol" aria-hidden="true">☯</div>
            <h2 class="chart-center__title">${escapeHtml(chart.info.full_name)}</h2>
            <dl class="chart-center__list">${list}</dl>
        </div>`;
}

/** Hiện tooltip của một sao cạnh phần tử được trỏ tới, không tràn khỏi màn hình. */
function showStarTooltip(target, starInfo) {
    const tooltip = document.getElementById('star-tooltip');
    const name = target.dataset.star;
    const info = starInfo[name];
    if (!info) {
        return;
    }
    const meta = [info.ngu_hanh && `Hành ${info.ngu_hanh}`, info.rating && `Điểm ${info.rating}/10`]
        .filter(Boolean)
        .join(' · ');
    tooltip.innerHTML = `
        <div class="star-tooltip__name">${escapeHtml(name)}</div>
        ${meta ? `<div class="star-tooltip__meta">${escapeHtml(meta)}</div>` : ''}
        <div>${escapeHtml(info.y_nghia)}</div>`;
    tooltip.hidden = false;

    const anchor = target.getBoundingClientRect();
    const box = tooltip.getBoundingClientRect();
    const left = Math.min(Math.max(TOOLTIP_GAP_PX, anchor.left),
        window.innerWidth - box.width - TOOLTIP_GAP_PX);
    const below = anchor.bottom + TOOLTIP_GAP_PX;
    const top = below + box.height > window.innerHeight
        ? anchor.top - box.height - TOOLTIP_GAP_PX
        : below;
    tooltip.style.left = `${left}px`;
    tooltip.style.top = `${top}px`;
}

/** Ẩn tooltip. */
function hideStarTooltip() {
    document.getElementById('star-tooltip').hidden = true;
}

/** Gán sự kiện tooltip cho toàn bộ sao bằng một listener trên bảng. */
function bindStarTooltip(grid, starInfo) {
    const show = (event) => {
        const star = event.target.closest('.star');
        if (star) {
            showStarTooltip(star, starInfo);
        }
    };
    grid.addEventListener('mouseover', show);
    grid.addEventListener('focusin', show);
    grid.addEventListener('mouseout', hideStarTooltip);
    grid.addEventListener('focusout', hideStarTooltip);
    window.addEventListener('scroll', hideStarTooltip, { passive: true });
}

/** Dựng bảng lá số vào phần tử container. */
function renderChart(chart, container) {
    const palaces = chart.cung.map((palace) => palaceHtml(palace, palace.name === 'Mệnh')).join('');
    container.innerHTML = `
        <div class="chart-scroll">
            <div class="chart-grid">${centerHtml(chart)}${palaces}</div>
        </div>
        <p class="chart-legend">Trỏ chuột, chạm hoặc Tab vào tên sao để xem ý nghĩa.</p>`;
    bindStarTooltip(container.querySelector('.chart-grid'), chart.star_info);
}
