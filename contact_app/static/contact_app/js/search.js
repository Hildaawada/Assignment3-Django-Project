document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('search-form');
    const spinner = document.getElementById('loading-spinner');
    const results = document.getElementById('search-results');

    form.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent the default form submission

        // Show the loading spinner
        spinner.style.display = 'block';

        // Get the search query
        const query = form.querySelector('input[name="query"]').value;

        // Perform the search using Fetch API
        fetch(`${form.action}?query=${encodeURIComponent(query)}`)
            .then(response => response.text())
            .then(data => {
                // Hide the loading spinner
                spinner.style.display = 'none';

                // Display the search results
                results.innerHTML = data;
            })
            .catch(error => {
                console.error('Error:', error);
                // Hide the loading spinner even if there's an error
                spinner.style.display = 'none';
            });
    });
});
