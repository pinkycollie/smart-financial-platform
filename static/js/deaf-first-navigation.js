/**
 * DEAF FIRST Navigation System
 * 
 * This script implements specialized navigation behaviors for the DEAF FIRST
 * digital framework, prioritizing clear visual feedback and accessibility
 * for deaf users.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Mobile navigation toggle
    const mobileNavToggle = document.getElementById('mobileNavToggle');
    const mobileSidebar = document.getElementById('mobileSidebar');
    const sidebarBackdrop = document.getElementById('sidebarBackdrop');
    const closeSidebar = document.getElementById('closeSidebar');
    
    if (mobileNavToggle && mobileSidebar && sidebarBackdrop) {
        // Open sidebar when toggle button is clicked
        mobileNavToggle.addEventListener('click', function() {
            mobileSidebar.classList.add('active');
            sidebarBackdrop.classList.add('active');
            document.body.style.overflow = 'hidden'; // Prevent scrolling
        });
        
        // Close sidebar when backdrop is clicked
        sidebarBackdrop.addEventListener('click', function() {
            mobileSidebar.classList.remove('active');
            sidebarBackdrop.classList.remove('active');
            document.body.style.overflow = ''; // Re-enable scrolling
        });
        
        // Close sidebar when close button is clicked
        if (closeSidebar) {
            closeSidebar.addEventListener('click', function() {
                mobileSidebar.classList.remove('active');
                sidebarBackdrop.classList.remove('active');
                document.body.style.overflow = ''; // Re-enable scrolling
            });
        }
    }
    
    // Horizontal scrolling navigation with visual indicators
    const scrollingNavContainer = document.querySelector('.scrolling-nav-container');
    if (scrollingNavContainer) {
        // Add scroll buttons for desktop
        const scrollLeftBtn = document.createElement('button');
        scrollLeftBtn.className = 'nav-scroll-btn nav-scroll-left';
        scrollLeftBtn.innerHTML = '<i class="fas fa-chevron-left"></i>';
        scrollLeftBtn.style.display = 'none'; // Hidden by default
        
        const scrollRightBtn = document.createElement('button');
        scrollRightBtn.className = 'nav-scroll-btn nav-scroll-right';
        scrollRightBtn.innerHTML = '<i class="fas fa-chevron-right"></i>';
        
        // Add buttons before and after the container
        scrollingNavContainer.parentNode.insertBefore(scrollLeftBtn, scrollingNavContainer);
        scrollingNavContainer.parentNode.insertBefore(scrollRightBtn, scrollingNavContainer.nextSibling);
        
        // Style the buttons with CSS
        const style = document.createElement('style');
        style.textContent = `
            .nav-scroll-btn {
                position: absolute;
                top: 50%;
                transform: translateY(-50%);
                width: 30px;
                height: 30px;
                border-radius: 50%;
                background-color: var(--deaf-first-blue);
                color: white;
                border: none;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                z-index: 10;
                transition: all 0.3s;
                opacity: 0.7;
            }
            
            .nav-scroll-btn:hover {
                opacity: 1;
                transform: translateY(-50%) scale(1.1);
            }
            
            .nav-scroll-left {
                left: 10px;
            }
            
            .nav-scroll-right {
                right: 10px;
            }
            
            @media (max-width: 768px) {
                .nav-scroll-btn {
                    display: none !important;
                }
            }
        `;
        document.head.appendChild(style);
        
        // Scroll functionality
        scrollLeftBtn.addEventListener('click', function() {
            scrollingNavContainer.scrollBy({
                left: -200,
                behavior: 'smooth'
            });
        });
        
        scrollRightBtn.addEventListener('click', function() {
            scrollingNavContainer.scrollBy({
                left: 200,
                behavior: 'smooth'
            });
        });
        
        // Show/hide scroll buttons based on scroll position
        scrollingNavContainer.addEventListener('scroll', function() {
            // Show left button only if scrolled
            scrollLeftBtn.style.display = scrollingNavContainer.scrollLeft > 0 ? 'flex' : 'none';
            
            // Show right button only if there's more to scroll
            const maxScrollLeft = scrollingNavContainer.scrollWidth - scrollingNavContainer.clientWidth;
            scrollRightBtn.style.display = scrollingNavContainer.scrollLeft < maxScrollLeft - 10 ? 'flex' : 'none';
        });
        
        // Initial check
        setTimeout(() => {
            const maxScrollLeft = scrollingNavContainer.scrollWidth - scrollingNavContainer.clientWidth;
            scrollRightBtn.style.display = maxScrollLeft > 10 ? 'flex' : 'none';
        }, 100);
    }
    
    // Add active state to current page in navigation
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link, .list-group-item');
    
    navLinks.forEach(link => {
        // Get the href attribute
        const href = link.getAttribute('href');
        
        // Check if this is the current page
        if (href === currentPath || 
            (currentPath.length > 1 && href !== '/' && currentPath.indexOf(href) === 0)) {
            link.classList.add('active');
            
            // If it's in a dropdown, also highlight the parent
            const dropdownToggle = link.closest('.dropdown').querySelector('.dropdown-toggle');
            if (dropdownToggle) {
                dropdownToggle.classList.add('active');
            }
            
            // If it's in the mobile accordion, expand it
            const accordionItem = link.closest('.accordion-collapse');
            if (accordionItem) {
                accordionItem.classList.add('show');
                const accordionButton = document.querySelector(`[data-bs-target="#${accordionItem.id}"]`);
                if (accordionButton) {
                    accordionButton.classList.remove('collapsed');
                    accordionButton.setAttribute('aria-expanded', 'true');
                }
            }
        }
    });
    
    // Visual feedback for focus events on all interactive elements
    document.querySelectorAll('a, button, input, select, textarea, [tabindex]:not([tabindex="-1"])').forEach(el => {
        el.addEventListener('focus', () => {
            // Add a faint visual pulse effect
            el.classList.add('deaf-first-pulse');
            
            // Remove it after animation completes
            setTimeout(() => {
                el.classList.remove('deaf-first-pulse');
            }, 1000);
        });
    });
    
    // Add ASL video buttons to headings when appropriate
    if (window.addAslVideoButtons) {
        addAslVideoButtons();
    }
});

/**
 * Add ASL video buttons to important content elements
 */
function addAslVideoButtons() {
    // Only add to important headings and content areas
    const importantElements = document.querySelectorAll('h1, h2, .key-content');
    
    importantElements.forEach(element => {
        // Check if this element already has an ASL button
        if (!element.querySelector('.asl-button')) {
            // Create ASL button
            const aslButton = document.createElement('button');
            aslButton.className = 'asl-button ms-2';
            aslButton.innerHTML = '<i class="fas fa-hands asl-icon"></i> ASL';
            aslButton.setAttribute('type', 'button');
            aslButton.setAttribute('data-content-id', element.id || generateId(element));
            
            // If element is a heading, append button
            if (element.tagName.match(/^H[1-6]$/)) {
                element.appendChild(aslButton);
            } 
            // Otherwise insert before the element
            else {
                element.parentNode.insertBefore(aslButton, element);
            }
            
            // Add click event
            aslButton.addEventListener('click', function() {
                showAslVideo(this.getAttribute('data-content-id'));
            });
        }
    });
}

/**
 * Generate a unique ID for an element
 */
function generateId(element) {
    // Generate a random ID if none exists
    const id = 'content-' + Math.random().toString(36).substr(2, 9);
    element.id = id;
    return id;
}

/**
 * Show ASL video for specific content
 */
function showAslVideo(contentId) {
    // This would connect to a video service in production
    // For now, show a placeholder message
    alert('ASL video for this content will be available soon. (Content ID: ' + contentId + ')');
}