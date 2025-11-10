document.addEventListener('DOMContentLoaded', function() {
    // Check if user is logged in
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = '/static/login.html';
        return;
    }

    // Display user email
    const userEmail = localStorage.getItem('user_email');
    document.getElementById('user-email').textContent = userEmail;

    // Logout functionality
    document.getElementById('logout-btn').addEventListener('click', function() {
        localStorage.removeItem('token');
        localStorage.removeItem('user_email');
        window.location.href = '/static/login.html';
    });

    // Query functionality
    document.getElementById('query-btn').addEventListener('click', async function() {
        const queryInput = document.getElementById('query-input').value;
        const resultsContainer = document.getElementById('query-results');
        
        if (!queryInput.trim()) {
            resultsContainer.innerHTML = '<p>Please enter a query.</p>';
            return;
        }
        
        resultsContainer.innerHTML = '<p>Loading results...</p>';
        
        try {
            const response = await fetch('/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    query: queryInput
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Display results
                let resultsHtml = '';
                
                if (data.data && data.data.length > 0) {
                    resultsHtml = '<table border="1" cellpadding="10" style="border-collapse: collapse; width: 100%;">';
                    
                    // Table header
                    resultsHtml += '<thead><tr>';
                    const headers = Object.keys(data.data[0]);
                    headers.forEach(header => {
                        resultsHtml += `<th>${header}</th>`;
                    });
                    resultsHtml += '</tr></thead>';
                    
                    // Table body
                    resultsHtml += '<tbody>';
                    data.data.forEach(row => {
                        resultsHtml += '<tr>';
                        headers.forEach(header => {
                            resultsHtml += `<td>${row[header]}</td>`;
                        });
                        resultsHtml += '</tr>';
                    });
                    resultsHtml += '</tbody></table>';
                } else {
                    resultsHtml = '<p>No results found.</p>';
                }
                
                // Display SQL query
                resultsHtml += `<div style="margin-top: 20px;">
                    <h3>SQL Query:</h3>
                    <pre style="background-color: #f5f5f5; padding: 10px; border-radius: 5px;">${data.sql}</pre>
                </div>`;
                
                resultsContainer.innerHTML = resultsHtml;
            } else {
                resultsContainer.innerHTML = `<p>Error: ${data.detail || 'Failed to execute query.'}</p>`;
            }
        } catch (error) {
            console.error('Error:', error);
            resultsContainer.innerHTML = '<p>An error occurred. Please try again later.</p>';
        }
    });
});
