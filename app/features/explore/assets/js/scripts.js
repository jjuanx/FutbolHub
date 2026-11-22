// The whole file is inert outside /explore: the asset registry serves it on
// every page, so each entry point checks for the search form first.
function on_explore_page() {
    return document.getElementById('filters') !== null;
}

const URL_TEXT_FILTER_IDS = [
    'query',
    'tags',
    'author',
    'date_from',
    'date_to',
    'competition',
    'season',
    'country',
    'team',
    'min_matches',
    'max_matches',
    'min_teams',
    'max_teams',
];

function syncFiltersToUrl(criteria) {
    if (typeof window === 'undefined' || !window.history || !window.history.replaceState) {
        return;
    }
    const params = new URLSearchParams();
    URL_TEXT_FILTER_IDS.forEach(key => {
        if (key === 'tags') {
            const tagsVal = Array.isArray(criteria.tags) ? criteria.tags.join(',') : (criteria.tags || '');
            if (tagsVal.trim() !== '') {
                params.set('tags', tagsVal.trim());
            }
            return;
        }
        const val = criteria[key];
        if (val !== undefined && val !== null && String(val).trim() !== '') {
            params.set(key, String(val).trim());
        }
    });

    if (criteria.publication_type && criteria.publication_type !== 'any') {
        params.set('publication_type', criteria.publication_type);
    }
    if (criteria.sorting && criteria.sorting !== 'newest') {
        params.set('sorting', criteria.sorting);
    }

    const qs = params.toString();
    const newUrl = qs ? `${window.location.pathname}?${qs}` : window.location.pathname;
    window.history.replaceState(null, '', newUrl);
}

function restoreFiltersFromUrl() {
    const urlParams = new URLSearchParams(window.location.search);

    URL_TEXT_FILTER_IDS.forEach(id => {
        const el = document.getElementById(id);
        if (!el) return;
        if (id === 'tags') {
            const allTags = urlParams.getAll('tags');
            if (allTags.length > 0) {
                el.value = allTags.join(', ');
            }
            return;
        }
        const paramVal = urlParams.get(id);
        if (paramVal !== null) {
            el.value = paramVal;
        }
    });

    const pubType = urlParams.get('publication_type');
    const pubSelect = document.getElementById('publication_type');
    if (pubType && pubSelect) {
        pubSelect.value = pubType;
    }

    const sortingParam = urlParams.get('sorting');
    if (sortingParam) {
        const sortingRadios = document.querySelectorAll('[name="sorting"]');
        sortingRadios.forEach(radio => {
            radio.checked = radio.value === sortingParam;
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (!on_explore_page()) return;
    send_query();
});

function send_query() {

    console.log("send query...")

    document.getElementById('results').innerHTML = '';
    document.getElementById("results_not_found").style.display = "none";
    console.log("hide not found icon");

    const filters = document.querySelectorAll('#filters input, #filters select, #filters [type="radio"]');

    // Sequencing guard: each new query supersedes the previous one, so the
    // in-flight request is aborted before a new one starts. Only the latest
    // response can repaint the result list.
    let inFlightController = null;

    filters.forEach(filter => {
        // Selects and radios do not fire "input" on every browser (Chrome only
        // fires "change" for a programmatic option click), so both events run
        // the search. When a control fires both, the abort guard collapses
        // them into a single repaint.
        ['input', 'change'].forEach(eventType => filter.addEventListener(eventType, () => {
            const csrfToken = document.getElementById('csrf_token').value;
            const getVal = (id) => {
                const el = document.getElementById(id);
                return el ? el.value : '';
            };
            const rawTags = getVal('tags');
            const tagsList = rawTags
                ? rawTags.split(',').map(t => t.trim()).filter(Boolean)
                : [];

            const searchCriteria = {
                csrf_token: csrfToken,
                query: document.querySelector('#query').value,
                publication_type: document.querySelector('#publication_type').value,
                sorting: document.querySelector('[name="sorting"]:checked').value,
                tags: tagsList,
                author: getVal('author'),
                date_from: getVal('date_from'),
                date_to: getVal('date_to'),
                competition: getVal('competition'),
                season: getVal('season'),
                country: getVal('country'),
                team: getVal('team'),
                min_matches: getVal('min_matches'),
                max_matches: getVal('max_matches'),
                min_teams: getVal('min_teams'),
                max_teams: getVal('max_teams'),
            };

            syncFiltersToUrl(searchCriteria);

            if (inFlightController !== null) {
                inFlightController.abort();
            }
            inFlightController = new AbortController();

            fetch('/explore', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(searchCriteria),
                signal: inFlightController.signal,
            })
                .then(response => response.json())
                .then(data => {

                    console.log(data);
                    document.getElementById('results').innerHTML = '';

                    // results counter
                    const resultCount = data.length;
                    const resultText = resultCount === 1 ? 'dataset' : 'datasets';
                    document.getElementById('results_number').textContent = `${resultCount} ${resultText} found`;

                    if (resultCount === 0) {
                        console.log("show not found icon");
                        document.getElementById("results_not_found").style.display = "block";
                    } else {
                        document.getElementById("results_not_found").style.display = "none";
                    }


                    data.forEach(dataset => {
                        let card = document.createElement('div');
                        card.className = 'col-12';
                        card.innerHTML = `
                            <div class="card">
                                <div class="card-body">
                                    <div class="d-flex align-items-center justify-content-between">
                                        <h3><a href="${dataset.url}">${dataset.title}</a></h3>
                                        <div>
                                            <span class="badge bg-primary" style="cursor: pointer;" onclick="set_publication_type_as_query('${dataset.publication_type}')">${dataset.publication_type}</span>
                                        </div>
                                    </div>
                                    <p class="text-secondary">${formatDate(dataset.created_at)}</p>

                                    <div class="row mb-2">

                                        <div class="col-md-4 col-12">
                                            <span class=" text-secondary">
                                                Description
                                            </span>
                                        </div>
                                        <div class="col-md-8 col-12">
                                            <p class="card-text">${dataset.description}</p>
                                        </div>

                                    </div>

                                    <div class="row mb-2">

                                        <div class="col-md-4 col-12">
                                            <span class=" text-secondary">
                                                Authors
                                            </span>
                                        </div>
                                        <div class="col-md-8 col-12">
                                            ${dataset.authors.map(author => `
                                                <p class="p-0 m-0">${author.name}${author.affiliation ? ` (${author.affiliation})` : ''}${author.orcid ? ` (${author.orcid})` : ''}</p>
                                            `).join('')}
                                        </div>

                                    </div>

                                    <div class="row mb-2">

                                        <div class="col-md-4 col-12">
                                            <span class=" text-secondary">
                                                Tags
                                            </span>
                                        </div>
                                        <div class="col-md-8 col-12">
                                            ${dataset.tags.map(tag => `<span class="badge bg-primary me-1" style="cursor: pointer;" onclick="set_tag_as_query('${tag}')">${tag}</span>`).join('')}
                                        </div>

                                    </div>

                                    <div class="row">

                                        <div class="col-md-4 col-12">

                                        </div>
                                        <div class="col-md-8 col-12">
                                            <a href="${dataset.url}" class="btn btn-outline-primary btn-sm" id="search" style="border-radius: 5px;">
                                                View dataset
                                            </a>
                                            <a href="/dataset/download/${dataset.id}" class="btn btn-outline-primary btn-sm" id="search" style="border-radius: 5px;">
                                                Download (${dataset.total_size_in_human_format})
                                            </a>
                                        </div>


                                    </div>

                                </div>
                            </div>
                        `;

                        document.getElementById('results').appendChild(card);
                    });
                })
                .catch(error => {
                    // Aborted requests are superseded queries, not failures.
                    if (error.name !== 'AbortError') {
                        throw error;
                    }
                });
        }));
    });
}

function formatDate(dateString) {
    const options = {day: 'numeric', month: 'long', year: 'numeric', hour: 'numeric', minute: 'numeric'};
    const date = new Date(dateString);
    return date.toLocaleString('en-US', options);
}

function set_tag_as_query(tagName) {
    const cleanTag = tagName.trim();
    const tagsInput = document.getElementById('tags');
    if (tagsInput) {
        const currentTags = tagsInput.value
            .split(',')
            .map(t => t.trim())
            .filter(Boolean);
        if (!currentTags.includes(cleanTag)) {
            currentTags.push(cleanTag);
        }
        tagsInput.value = currentTags.join(', ');
        tagsInput.dispatchEvent(new Event('input', {bubbles: true}));
        return;
    }
    const queryInput = document.getElementById('query');
    queryInput.value = cleanTag;
    queryInput.dispatchEvent(new Event('input', {bubbles: true}));
}

function set_publication_type_as_query(publicationType) {
    const publicationTypeSelect = document.getElementById('publication_type');
    for (let i = 0; i < publicationTypeSelect.options.length; i++) {
        if (publicationTypeSelect.options[i].text === publicationType.trim()) {
            // Set the value of the select to the value of the matching option
            publicationTypeSelect.value = publicationTypeSelect.options[i].value;
            break;
        }
    }
    publicationTypeSelect.dispatchEvent(new Event('input', {bubbles: true}));
}

// Guarded: the asset registry serves every feature's script on every page, so
// this file also loads where the explore form does not exist.
if (document.getElementById('clear-filters')) {
    document.getElementById('clear-filters').addEventListener('click', clearFilters);
}

function clearFilters() {
    URL_TEXT_FILTER_IDS.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = "";
    });

    const publicationTypeSelect = document.querySelector('#publication_type');
    if (publicationTypeSelect) publicationTypeSelect.value = "any";

    const sortingOptions = document.querySelectorAll('[name="sorting"]');
    sortingOptions.forEach(option => {
        option.checked = option.value === "newest";
    });

    const queryInput = document.querySelector('#query');
    queryInput.dispatchEvent(new Event('input', {bubbles: true}));
}

document.addEventListener('DOMContentLoaded', () => {
    if (!on_explore_page()) return;

    restoreFiltersFromUrl();

    const queryInput = document.getElementById('query');
    queryInput.dispatchEvent(new Event('input', {bubbles: true}));
});
