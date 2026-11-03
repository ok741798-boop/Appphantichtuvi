/* Trang Duyên Số Định Mệnh: tải phân tích, dựng các section và so sánh 2 lá số. */

const RING_RADIUS = 52;
const RING_LENGTH = 2 * Math.PI * RING_RADIUS;
const SCORE_GOOD_ABOVE = 75;
const SCORE_MID_MIN = 50;
const HARMONY_BARS = [
    { key: 'personality', label: 'Tính cách' },
    { key: 'ngu_hanh', label: 'Ngũ hành' },
    { key: 'goals', label: 'Mục tiêu' },
    { key: 'love', label: 'Tình cảm' },
];

/** Chọn màu điểm: đỏ dưới 50, vàng từ 50 đến 75, xanh trên 75. */
function scoreTone(score) {
    if (score > SCORE_GOOD_ABOVE) {
        return 'good';
    }
    return score >= SCORE_MID_MIN ? 'mid' : 'bad';
}

/** Dựng danh sách từ mảng chuỗi. */
function listHtml(items, className = '') {
    return `<ul class="d-list ${className}">${items.map((item) => `<li>${escapeHtml(item)}</li>`).join('')}</ul>`;
}

/** Dựng vòng tròn điểm. */
function ringHtml(score) {
    const offset = RING_LENGTH * (1 - score / 100);
    return `
        <div class="ring ring--${scoreTone(score)}" role="img" aria-label="${score} trên 100">
            <svg viewBox="0 0 120 120" aria-hidden="true">
                <circle class="ring__track" cx="60" cy="60" r="${RING_RADIUS}"></circle>
                <circle class="ring__value" cx="60" cy="60" r="${RING_RADIUS}"
                        stroke-dasharray="${RING_LENGTH}" stroke-dashoffset="${offset}"></circle>
            </svg>
            <span class="ring__label">${score}</span>
        </div>`;
}

/** Dựng các thanh chỉ số nhỏ. */
function barsHtml(bars, scores) {
    return bars.map(({ key, label }) => `
        <div class="bar bar--${scoreTone(scores[key])}">
            <div class="bar__head"><span>${label}</span><span>${scores[key]}</span></div>
            <div class="bar__track"><div class="bar__value" style="width: ${scores[key]}%"></div></div>
        </div>`).join('');
}

/** Dựng thẻ con trong phần chân dung. */
function traitCardHtml(icon, title, body) {
    return `
        <article class="trait-card">
            <h3><span aria-hidden="true">${icon}</span> ${title}</h3>
            ${body}
        </article>`;
}

/** Dựng hồ sơ tổng hợp về người ấy. Họ tên không suy ra được nên ghi rõ, không tự đặt tên. */
function dossierHtml(data) {
    const ages = data.meeting_ages;
    const best = ages.candidates[0];
    const rows = [
        ['Họ tên', `Lá số không cho biết. Tên gợi ý cho vui: ${ages.name_hints.join(', ')}`],
        ['Tuổi', `${ages.partner_age_from}-${ages.partner_age_to} tuổi âm khi gặp năm ${ages.meeting_year}, ${data.age_difference}`],
        ['Năm sinh hợp nhất', `${best.birth_year} (${best.can_chi}), ${best.ban_menh}`],
        ['Nghề nghiệp', `${data.partner_career.groups.join(', ')}. Thu nhập: ${data.partner_career.income}`],
        ['Gia đình', `${data.partner_family.wealth}. ${data.partner_family.parents}. ${data.partner_family.siblings}`],
        ['Quê quán', `${data.partner_family.hometown}, ${data.meeting_place.direction}`],
        ['Hoàn cảnh gặp', data.meeting_circumstance.join('; ')],
    ];
    const list = rows.map(([label, value]) => `<dt>${label}</dt><dd>${escapeHtml(value)}</dd>`).join('');
    return `
        <section class="d-card d-card--hero">
            <h2 class="d-card__title">🪪 Hồ sơ người ấy</h2>
            <p class="d-card__note">Tổng hợp xu hướng từ cung Phu Thê, không phải thông tin của một người có thật.</p>
            <dl class="dossier">${list}</dl>
        </section>`;
}

/** Dựng phần gia đình hai bên. */
function familiesHtml(data) {
    const column = (title, family) => `
        <div><h3>${title}</h3>${listHtml([family.wealth, family.parents, family.siblings])}</div>`;
    return `
        <section class="d-card">
            <h2 class="d-card__title">👨‍👩‍👧 Gia đình hai bên</h2>
            <p class="d-text d-text--lead">${escapeHtml(data.family_match.text)}</p>
            <div class="life-grid">
                ${column('Gia đình bạn', data.your_family)}
                ${column('Gia đình người ấy', data.partner_family)}
            </div>
        </section>`;
}

/** Dựng phần "Người ấy là ai?". */
function portraitHtml(data) {
    const { partner_appearance: look, partner_personality: mind, partner_career: job,
        partner_family: family } = data;
    const looks = [`Khuôn mặt: ${look.face}`, `Nước da: ${look.skin}`, `Vóc dáng: ${look.height}`,
        `Phong cách: ${look.style}`, ...look.features];
    const jobs = [`Nghề nghiệp: ${job.groups.join(', ')}`, `Thu nhập: ${job.income}`,
        `Tuổi tác: ${data.age_difference}`];
    const home = [family.wealth, family.siblings, family.parents, family.hometown];
    const stars = [...data.palace.chinh_tinh, ...data.palace.phu_tinh].join(', ') || 'Vô chính diệu';
    return `
        <section class="d-card d-card--hero">
            <h2 class="d-card__title">💑 Người ${escapeHtml(data.partner_term)} tương lai là ai?</h2>
            <p class="d-card__note">Cung Phu Thê tại ${escapeHtml(data.palace.position)}: ${escapeHtml(stars)}</p>
            <div class="trait-grid">
                ${traitCardHtml('✨', 'Ngoại hình', listHtml(looks))}
                ${traitCardHtml('💗', 'Tính cách', `${listHtml(mind.traits)}<p class="d-text">${escapeHtml(mind.summary)}.</p>`)}
                ${traitCardHtml('💼', 'Nghề nghiệp', listHtml(jobs))}
                ${traitCardHtml('🏡', 'Gia đình', listHtml(home))}
            </div>
        </section>`;
}

/** Dựng timeline gặp gỡ. */
function meetingHtml(data) {
    const rows = data.timeline.map((item) => `
        <li class="timeline-item${item.highlight ? ' timeline-item--highlight' : ''}">
            <div class="timeline-item__year">${item.year}</div>
            <div>
                <div class="timeline-item__meta">${escapeHtml(item.can_chi)} · ${item.age} tuổi âm</div>
                <p class="d-text">${escapeHtml(item.text)}</p>
            </div>
        </li>`).join('');
    return `
        <section class="d-card">
            <h2 class="d-card__title">🗓️ Khi nào gặp người ấy?</h2>
            <p class="d-text d-text--lead">${escapeHtml(data.meeting_time.text)}</p>
            <ol class="timeline-list">${rows}</ol>
        </section>`;
}

/** Dựng phần tuổi hai người lúc gặp và các năm sinh khả dĩ của người ấy. */
function agesHtml(data) {
    const ages = data.meeting_ages;
    const rows = ages.candidates.map((item, index) => `
        <tr${index === 0 ? ' class="age-table__best"' : ''}>
            <td>${item.birth_year}</td>
            <td>${escapeHtml(item.can_chi)}</td>
            <td>${escapeHtml(item.ban_menh)}</td>
            <td>${item.age_at_meeting} tuổi âm</td>
            <td>${escapeHtml(item.relation)}, ${escapeHtml(item.tuoi)}</td>
        </tr>`).join('');
    return `
        <section class="d-card">
            <h2 class="d-card__title">🎂 Hai người bao nhiêu tuổi khi gặp nhau?</h2>
            <p class="d-text d-text--lead">${escapeHtml(ages.text)}</p>
            <div class="age-pair">
                <div class="age-pair__item">
                    <span class="age-pair__label">Bạn</span>
                    <span class="age-pair__value">${ages.you_age}</span>
                    <span class="age-pair__note">tuổi âm, năm ${ages.meeting_year}</span>
                </div>
                <div class="age-pair__heart" aria-hidden="true">💕</div>
                <div class="age-pair__item">
                    <span class="age-pair__label">Người ấy</span>
                    <span class="age-pair__value">${ages.partner_age}</span>
                    <span class="age-pair__note">${escapeHtml(ages.gap_text)}</span>
                </div>
            </div>
            <h3 class="age-heading">Năm sinh khả dĩ của người ấy</h3>
            <div class="compare-table-wrap">
                <table class="compare-table">
                    <thead><tr><th scope="col">Năm sinh</th><th scope="col">Tuổi</th>
                        <th scope="col">Bản mệnh</th><th scope="col">Khi gặp</th>
                        <th scope="col">Với bạn</th></tr></thead>
                    <tbody>${rows}</tbody>
                </table>
            </div>
            <h3 class="age-heading">Tên người ấy</h3>
            <p class="d-text">Lá số không suy ra được tên thật của một người. Cho vui, tên mang hành
                ${escapeHtml(ages.name_element)} hợp với năm sinh đứng đầu có thể là:
                <strong>${ages.name_hints.map(escapeHtml).join(', ')}</strong>.</p>
        </section>`;
}

/** Dựng phần địa điểm và hoàn cảnh gặp. */
function placeHtml(data) {
    return `
        <section class="d-card">
            <h2 class="d-card__title">📍 Gặp ở đâu?</h2>
            <p class="d-text d-text--lead">${escapeHtml(data.meeting_place.text)}</p>
            <p class="d-text">Hoàn cảnh dễ gặp:</p>
            ${listHtml(data.meeting_circumstance)}
        </section>`;
}

/** Dựng phần điểm hòa hợp. */
function harmonyHtml(data) {
    return `
        <section class="d-card">
            <h2 class="d-card__title">💯 Điểm hòa hợp</h2>
            <div class="harmony">
                ${ringHtml(data.harmony.overall)}
                <div class="harmony__bars">${barsHtml(HARMONY_BARS, data.harmony)}</div>
            </div>
            <p class="d-text">${escapeHtml(data.fate.text)}</p>
            <p class="d-text">${escapeHtml(data.marriage_age.text)}</p>
        </section>`;
}

/** Dựng phần cuộc sống hôn nhân. */
function lifeHtml(data) {
    const { marriage_life: life, marriage_stability: stability, children } = data;
    return `
        <section class="d-card">
            <h2 class="d-card__title">🏠 Cuộc sống hôn nhân</h2>
            <p class="d-text d-text--lead">${escapeHtml(stability.level)}: ${escapeHtml(stability.text)}</p>
            <div class="life-grid">
                <div><h3>✅ Điểm tích cực</h3>${listHtml(life.positives)}</div>
                <div><h3>⚠️ Điểm cần lưu ý</h3>${listHtml(life.cautions)}</div>
            </div>
            <p class="d-text">${escapeHtml(life.decision)}. ${escapeHtml(life.finance)}.</p>
            <p class="d-text">${escapeHtml(children.text)}</p>
        </section>`;
}

/** Dựng các mốc tương lai. */
function futureHtml(data) {
    const items = data.future_timeline.map((item) => `
        <li class="milestone">
            <span class="milestone__icon" aria-hidden="true">${item.icon}</span>
            <span class="milestone__year">${item.year}</span>
            <strong>${escapeHtml(item.title)}</strong>
            <span class="milestone__text">${escapeHtml(item.text)}</span>
        </li>`).join('');
    return `
        <section class="d-card">
            <h2 class="d-card__title">🌸 Các mốc tương lai</h2>
            <ol class="milestones">${items}</ol>
        </section>`;
}

/** Dựng phần cảnh báo và lời khuyên. */
function adviceHtml(data) {
    const warnings = data.warnings.length
        ? listHtml(data.warnings.map((item) => item.text))
        : '<p class="d-text">Chưa thấy năm nào cần lưu ý đặc biệt trong 10 năm tới.</p>';
    return `
        <section class="d-card">
            <h2 class="d-card__title">💡 Lưu ý và lời khuyên</h2>
            <div class="life-grid">
                <div><h3>Năm cần lưu ý</h3>${warnings}</div>
                <div><h3>Lời khuyên</h3>${listHtml(data.advice)}</div>
            </div>
        </section>`;
}

/** Dựng kết quả so sánh 2 lá số. */
function compareHtml(data) {
    const rows = data.rows.map((row) => `
        <tr><th scope="row">${escapeHtml(row.label)}</th><td>${escapeHtml(row.you)}</td>
            <td>${escapeHtml(row.partner)}</td></tr>`).join('');
    const bars = [
        { key: 'ngu_hanh', label: 'Ngũ hành' },
        { key: 'personality', label: 'Tính cách' },
        { key: 'goals', label: 'Mục tiêu' },
    ];
    return `
        <div class="harmony compare-result">
            ${ringHtml(data.overall)}
            <div class="harmony__bars">${barsHtml(bars, data.scores)}</div>
        </div>
        <div class="compare-table-wrap">
            <table class="compare-table">
                <thead><tr><th scope="col"></th><th scope="col">Bạn</th>
                    <th scope="col">${escapeHtml(data.partner_name)}</th></tr></thead>
                <tbody>${rows}</tbody>
            </table>
        </div>
        <p class="d-text">${escapeHtml(data.ngu_hanh_text)} ${escapeHtml(data.tuoi_text)}</p>
        <p class="d-text">Gia đình hai bên: ${escapeHtml(data.family_text)}</p>
        <div class="life-grid">
            <div><h3>⚠️ Xung đột tiềm ẩn</h3>${listHtml(data.warnings)}</div>
            <div><h3>💡 Lời khuyên</h3>${listHtml(data.advice)}</div>
        </div>`;
}

/** Gán sự kiện form so sánh 2 lá số. */
function initCompare(chartId) {
    const form = document.getElementById('compare-form');
    const hourSelect = document.getElementById('compare-hour');
    const button = document.getElementById('compare-submit');
    hourSelect.innerHTML = document.getElementById('birth-hour').innerHTML;
    document.getElementById('compare-date').max = todayIso();

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const [year, month, day] = document.getElementById('compare-date').value.split('-').map(Number);
        const partner = {
            full_name: document.getElementById('compare-name').value.trim(),
            gender: document.getElementById('compare-gender').value,
            year,
            month,
            day,
            hour: Number(hourSelect.value),
        };
        button.disabled = true;
        try {
            const data = await apiPost('/marriage/compare', { chart_id: chartId, partner });
            document.getElementById('compare-result').innerHTML = compareHtml(data);
        } catch (error) {
            showToast(error.message, 'error');
        } finally {
            button.disabled = false;
        }
    });
}

/** Hiện lỗi thay cho spinner, kèm nút thử lại. */
function showDestinyError(message, retry) {
    const status = document.getElementById('destiny-status');
    status.hidden = false;
    status.innerHTML = `<p>${escapeHtml(message)}</p>`;
    if (retry) {
        const button = document.createElement('button');
        button.className = 'btn btn--ghost';
        button.type = 'button';
        button.textContent = 'Thử lại';
        button.addEventListener('click', retry);
        status.append(button);
    }
}

/** Khởi động trang: chưa có lá số thì hiện form, có rồi thì tải phân tích. */
async function initMarriagePage() {
    const status = document.getElementById('destiny-status');
    const chartId = readStorage(STORAGE_KEYS.chartId);
    if (!chartId) {
        status.hidden = true;
        document.getElementById('destiny-form').hidden = false;
        return;
    }
    try {
        const chart = await loadChart(chartId);
        const data = await apiPost('/marriage/analyze', { chart_id: chart.chart_id });
        const result = document.getElementById('destiny-result');
        result.innerHTML = [dossierHtml, portraitHtml, meetingHtml, agesHtml, placeHtml, familiesHtml,
            harmonyHtml, lifeHtml, futureHtml, adviceHtml].map((render) => render(data)).join('');
        result.hidden = false;
        status.hidden = true;
        document.getElementById('compare-section').hidden = false;
        initCompare(chart.chart_id);
    } catch (error) {
        // 403: chưa đủ tuổi, thử lại cũng không đổi kết quả.
        showDestinyError(error.message, error.status === 403 ? null : initMarriagePage);
    }
}

document.addEventListener('DOMContentLoaded', initMarriagePage);
