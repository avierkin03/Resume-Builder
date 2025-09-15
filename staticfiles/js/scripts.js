console.log('scripts.js loaded successfully');

let currentPage = 1;

function loadTemplates(page) {
    console.log('loadTemplates called with page:', page);
    const templateList = document.getElementById('template-list');
    if (!templateList) {
        console.error('Element #template-list not found');
        return;
    }
    templateList.innerHTML = '<p id="loading-message">Завантаження шаблонів...</p>';

    if (!window.TEMPLATE_AJAX_URL) {
        console.error('TEMPLATE_AJAX_URL is not defined');
        templateList.innerHTML = '<p>Помилка: URL для AJAX не визначено.</p>';
        return;
    }

    console.log('Fetching templates from:', window.TEMPLATE_AJAX_URL + '?page=' + page);
    fetch(window.TEMPLATE_AJAX_URL + '?page=' + page)
        .then(response => {
            console.log('Fetch response status:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Received data:', data);
            templateList.innerHTML = '';

            if (!data.templates || data.templates.length === 0) {
                console.log('No templates found');
                templateList.innerHTML = '<p>Шаблони поки недоступні.</p>';
                document.getElementById('prev-page').disabled = true;
                document.getElementById('next-page').disabled = true;
                return;
            }

            data.templates.forEach(template => {
                let templateCard = `
                    <div class="col-md-4 mb-3">
                        <div class="card">
                            <div class="card-body">
                                <h5 class="card-title">${template.name}</h5>
                                ${template.image ? `<img src="${template.image}" class="d-block w-100 mb-2" alt="${template.name}">` : ''}
                                <p class="card-text">${template.description ? template.description.substring(0, 100) + '...' : 'Без опису'}</p>
                                <a href="/resume/create/?template_id=${template.id}" class="btn btn-primary">Спробувати</a>
                            </div>
                        </div>
                    </div>
                `;
                templateList.innerHTML += templateCard;
            });

            const prevPage = document.getElementById('prev-page');
            const nextPage = document.getElementById('next-page');
            if (prevPage && nextPage) {
                prevPage.disabled = !data.has_previous;
                prevPage.href = data.has_previous ? '#' : '';
                nextPage.disabled = !data.has_next;
                nextPage.href = data.has_next ? '#' : '';
            } else {
                console.error('Pagination buttons not found');
            }
            currentPage = page;
        })
        .catch(error => {
            console.error('Error loading templates:', error);
            templateList.innerHTML = '<p>Помилка завантаження шаблонів.</p>';
        });
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing template loading');
    if (!window.TEMPLATE_AJAX_URL) {
        console.error('TEMPLATE_AJAX_URL is not defined');
        document.getElementById('template-list').innerHTML = '<p>Помилка: URL для AJAX не визначено.</p>';
        return;
    }
    loadTemplates(1);

    const prevPage = document.getElementById('prev-page');
    const nextPage = document.getElementById('next-page');
    if (!prevPage || !nextPage) {
        console.error('Pagination buttons not found');
        return;
    }

    prevPage.addEventListener('click', function(e) {
        e.preventDefault();
        if (!this.disabled) {
            console.log('Previous page clicked');
            loadTemplates(currentPage - 1);
        }
    });

    nextPage.addEventListener('click', function(e) {
        e.preventDefault();
        if (!this.disabled) {
            console.log('Next page clicked');
            loadTemplates(currentPage + 1);
        }
    });
});