document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-input');
    const resultsContainer = document.getElementById('results-container');
    
    const debounce = (func, delay) => {
        let inDebounce;
        return function() {
            const context = this;
            const args = arguments;
            clearTimeout(inDebounce);
            inDebounce = setTimeout(() => func.apply(context, args), delay);
        };
    };
    
    const fetchResults = async (query) => {
        if (query.length < 2) {
            resultsContainer.innerHTML = '';
            return;
        }
        
        try {
            const response = await fetch(`/api/contacts/?search=${encodeURIComponent(query)}`);
            const data = await response.json();
            renderResults(data);
        } catch (error) {
            console.error('Search error:', error);
        }
    };
    
    const renderResults = (contacts) => {
        if (contacts.length === 0) {
            resultsContainer.innerHTML = '<div class="alert alert-info">No results found</div>';
            return;
        }
        
        let html = '<div class="list-group">';
        contacts.forEach(contact => {
            html += `
                <div class="list-group-item">
                    <h5>${contact.first_name} ${contact.last_name}</h5>
                    <p>${contact.email} | ${contact.phone_number}</p>
                    <small>${contact.address}</small>
                </div>
            `;
        });
        html += '</div>';
        
        resultsContainer.innerHTML = html;
    };
    
    searchInput.addEventListener('input', debounce(function() {
        fetchResults(this.value);
    }, 300));
});
