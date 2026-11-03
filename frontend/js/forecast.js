/* Dựng tab Tương lai: timeline 10 năm và modal chi tiết từng năm. */

// Điểm đúng bằng 7 cũng tính là tốt, trùng với ngưỡng trong forecast.py.
const GOOD_YEAR_MIN = 7;
const BAD_YEAR_BELOW = 4;

/** Chọn màu thẻ năm theo điểm. */
function yearTone(rating) {
    if (rating >= GOOD_YEAR_MIN) {
        return 'good';
    }
    return rating < BAD_YEAR_BELOW ? 'bad' : 'mid';
}

/** Dựng một thẻ năm. */
function yearCardHtml(item, index) {
    return `
        <button class="year-card year-card--${yearTone(item.rating)}" type="button" data-index="${index}">
            <span class="year-card__year">${item.year}</span>
            <span class="year-card__can-chi">${escapeHtml(item.can_chi)}</span>
            ${ratingStars(item.rating)}
            <span class="year-card__summary">${escapeHtml(item.short_summary)}</span>
            <span class="year-card__verdict">${escapeHtml(item.verdict)}</span>
        </button>`;
}

/** Mở modal chi tiết của một năm. */
function openYearModal(item) {
    const aspects = ASPECTS.map((aspect) => `
        <section class="year-modal__aspect">
            <div class="year-modal__aspect-head">
                <h3><span aria-hidden="true">${aspect.icon}</span> ${aspect.title}</h3>
                ${ratingStars(item.aspect_ratings[aspect.key])}
            </div>
            <p class="year-modal__text">${escapeHtml(item[aspect.key])}</p>
        </section>`).join('');
    document.getElementById('year-modal-body').innerHTML = `
        <h2 class="year-modal__title" id="year-modal-title">Năm ${item.year}</h2>
        <p class="year-modal__meta">${escapeHtml(item.can_chi)} · ${item.age} tuổi âm ·
            ${item.rating}/10 · ${escapeHtml(item.verdict)}</p>
        <p class="year-modal__text">${escapeHtml(item.summary)}</p>
        ${aspects}`;
    document.getElementById('year-modal').showModal();
}

/** Gán sự kiện đóng modal: nút đóng, phím Esc (mặc định của dialog) và bấm ra ngoài. */
function initForecastModal() {
    const modal = document.getElementById('year-modal');
    document.getElementById('year-modal-close').addEventListener('click', () => modal.close());
    modal.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.close();
        }
    });
}

/** Dựng timeline 10 năm vào phần tử container. */
function renderForecast(items, container) {
    container.innerHTML = `
        <p class="timeline-intro">Bấm vào từng năm để xem chi tiết 4 khía cạnh.</p>
        <div class="timeline">${items.map(yearCardHtml).join('')}</div>`;
    container.querySelector('.timeline').addEventListener('click', (event) => {
        const card = event.target.closest('.year-card');
        if (card) {
            openYearModal(items[Number(card.dataset.index)]);
        }
    });
}
