
// Basic JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    console.log('Page loaded successfully!');
    
    // Add any interactive functionality here
    const header = document.querySelector('header h1');
    if (header) {
        header.addEventListener('click', function() {
            alert('Welcome to my website!');
        });
    }
});
