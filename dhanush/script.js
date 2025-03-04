document.addEventListener('DOMContentLoaded', function() {
    const navLinks = document.querySelectorAll('header nav a');

    navLinks.forEach(link => {
        link.addEventListener('click', function(event) {
            event.preventDefault(); // Prevent default anchor behavior

            const pageName = this.textContent.toLowerCase().replace(' ', '-'); // Get link text and format for filename
            let fileName = pageName + '.html'; // Default filename

            // Specific file names for certain links
            if (pageName === 'home') {
                fileName = 'index.html'; // Or whatever your home page is named.
            } else if (pageName === 'time-table') {
                fileName = 'ss.html';
            } else if (pageName === 'schedules') {
                fileName = 'schedules.html';
            } else if (pageName === 'education') {
                fileName = 'education.html';
            } else if (pageName === 'experience') {
                fileName = 'experience.html';
            } else if (pageName === 'contact') {
                fileName = 'contact.html';
            }

            // Redirect to the corresponding HTML file
            window.location.href = fileName;
        });
    });
});