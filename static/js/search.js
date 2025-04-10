document.addEventListener('DOMContentLoaded', function() {
    // Initialize elements
    const searchInput = document.getElementById('search-input');
    const resultsContainer = document.getElementById('results-container');
    const statusFilter = document.getElementById('status-filter');
    const clientStatusFilter = document.getElementById('client-status-filter');
    
    // Debounce function to limit API calls
    const debounce = (func, delay) => {
        let inDebounce;
        return function() {
            const context = this;
            const args = arguments;
            clearTimeout(inDebounce);
            inDebounce = setTimeout(() => func.apply(context, args), delay);
        };
    };

    // Fetch results from API
    const fetchResults = async (query) => {
        if (query.length < 2 && !statusFilter.value && !clientStatusFilter.value) {
            resultsContainer.innerHTML = '';
            return;
        }

        try {
            // Build query parameters
            const params = new URLSearchParams();
            if (query) params.append('search', query);
            if (statusFilter.value) params.append('file_status', statusFilter.value);
            if (clientStatusFilter.value) params.append('client_status', clientStatusFilter.value);

            const response = await fetch(`/api/contacts/?${params.toString()}`);
            const data = await response.json();
            renderResults(data.results || data);
        } catch (error) {
            console.error('Search error:', error);
            resultsContainer.innerHTML = `
                <div class="alert alert-danger">
                    Error loading results. Please try again.
                </div>
            `;
        }
    };

    // Render results to the page
    const renderResults = (contacts) => {
        if (!contacts || contacts.length === 0) {
            resultsContainer.innerHTML = `
                <div class="alert alert-info">
                    No contacts found matching your criteria.
                </div>
            `;
            return;
        }

        let html = '<div class="list-group">';
        
        contacts.forEach(contact => {
            // Determine badge classes based on status
            const fileStatusClass = contact.file_status === 'OPEN' ? 
                'status-open' : 'status-closed';
            const clientStatusClass = contact.client_status === 'ALIVE' ? 
                'client-alive' : 'client-deceased';
            
            html += `
                <div class="list-group-item contact-card">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h5 class="mb-1">
                                ${contact.first_name} 
                                ${contact.middle_name ? contact.middle_name + ' ' : ''}
                                ${contact.last_name}
                                <span class="badge ${fileStatusClass} status-badge ms-2">
                                    ${contact.file_status}
                                </span>
                                <span class="badge ${clientStatusClass} status-badge">
                                    ${contact.client_status}
                                </span>
                            </h5>
                            <p class="mb-1">
                                <strong>File #:</strong> ${contact.file_number} | 
                                <a href="mailto:${contact.email}">${contact.email}</a> | 
                                ${contact.phone_number}
                            </p>
                            ${contact.company ? `<p class="mb-1"><strong>Company:</strong> ${contact.company}</p>` : ''}
                            <small class="text-muted">${contact.address}</small>
                        </div>
                        <div>
                            <a href="/${contact.id}/edit/" class="btn btn-sm btn-outline-primary">
                                <i class="bi bi-pencil"></i>
                            </a>
                        </div>
                    </div>
                </div>
            `;
        });

        html += '</div>';
        resultsContainer.innerHTML = html;
    };

    // Event listeners with debouncing
    searchInput.addEventListener('input', debounce(function() {
        fetchResults(this.value);
    }, 300));

    statusFilter.addEventListener('change', () => {
        fetchResults(searchInput.value);
    });

    clientStatusFilter.addEventListener('change', () => {
        fetchResults(searchInput.value);
    });

    // Initial load (optional - load some contacts on page load)
    fetchResults('');
});