/* Dựng tab Hiện tại: đại vận, tiểu hạn và 4 khía cạnh của năm nay. */

const ASPECTS = [
    { key: 'career', title: 'Sự nghiệp', icon: '💼' },
    { key: 'wealth', title: 'Tài lộc', icon: '💰' },
    { key: 'love', title: 'Tình cảm', icon: '❤️' },
    { key: 'health', title: 'Sức khỏe', icon: '🩺' },
];

/** Dựng thẻ đại vận hoặc tiểu hạn. */
function periodCardHtml(title, cung, meta, rating) {
    const stars = rating === null ? '' : ratingStars(rating);
    return `
        <article class="card period-card">
            <h2>${escapeHtml(title)}</h2>
            <div class="period-card__value">${escapeHtml(cung)}</div>
            <p class="period-card__meta">${escapeHtml(meta)}</p>
            ${stars}
        </article>`;
}

/** Dựng thẻ một khía cạnh. */
function aspectCardHtml(aspect, data) {
    return `
        <article class="card aspect-card">
            <div class="aspect-card__head">
                <span class="aspect-card__icon" aria-hidden="true">${aspect.icon}</span>
                <h2 class="aspect-card__title">${aspect.title}</h2>
                ${ratingStars(data.aspect_ratings[aspect.key])}
            </div>
            <p class="aspect-card__text">${escapeHtml(data[aspect.key])}</p>
        </article>`;
}

/** Dựng toàn bộ tab Hiện tại vào phần tử container. */
function renderAnalysis(data, container) {
    const { dai_van: daiVan, tieu_han: tieuHan } = data;
    const daiVanMeta = daiVan.position
        ? `Cung ${daiVan.position}, tuổi ${daiVan.age_range}`
        : `Tuổi ${daiVan.age_range}`;
    container.innerHTML = `
        <div class="analysis">
            <div class="period-grid">
                ${periodCardHtml('Đại vận hiện tại', daiVan.cung, daiVanMeta, daiVan.rating)}
                ${periodCardHtml(`Tiểu hạn năm ${data.year}`, tieuHan.cung,
                    `Cung ${tieuHan.position}, ${data.can_chi}, ${data.age} tuổi âm`, tieuHan.rating)}
            </div>
            <article class="card analysis__summary">
                <h2>Tổng quan năm ${data.year}</h2>
                ${ratingStars(data.overall_rating)}
                <p>${escapeHtml(data.summary)}</p>
            </article>
            <div class="aspect-grid">
                ${ASPECTS.map((aspect) => aspectCardHtml(aspect, data)).join('')}
            </div>
        </div>`;
}
