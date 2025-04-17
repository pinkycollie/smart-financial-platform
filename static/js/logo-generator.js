/**
 * DEAF FIRST Movement + MBTQ GROUP Logo Generator
 * 
 * This script generates a custom SVG logo that combines the MBTQ GROUP 
 * infinity triangle logo with DEAF FIRST movement styling and principles.
 * 
 * The logo design follows DEAF FIRST principles of high visual clarity,
 * strong contrast, and meaningful symbolism for deaf users.
 */

class LogoGenerator {
    constructor(options = {}) {
        // Default configuration
        this.config = {
            primaryColor: '#0055AA',      // DEAF FIRST blue
            accentColor: '#FFD700',       // DEAF FIRST gold/yellow
            textColor: '#FFFFFF',         // White text for contrast
            backgroundColor: '#212121',   // Dark background
            size: options.size || 80,     // Default size in pixels
            text: options.text || 'DEAF FIRST × MBTQ',
            animated: options.animated || false,
            container: options.container || null,
            displayText: options.displayText !== undefined ? options.displayText : true
        };
        
        // Container element where the logo will be rendered
        this.container = document.getElementById(this.config.container);
        if (!this.container && this.config.container) {
            console.error(`Container with ID "${this.config.container}" not found.`);
            return;
        }
    }
    
    /**
     * Generate the SVG markup for the logo
     * @returns {string} SVG markup
     */
    generateSVG() {
        const size = this.config.size;
        const halfSize = size / 2;
        const triangleSize = size * 0.6;
        const infinitySize = size * 0.3;
        
        // Create the SVG container
        let svg = `<svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}" xmlns="http://www.w3.org/2000/svg">`;
        
        // Add a circular background
        svg += `<circle cx="${halfSize}" cy="${halfSize}" r="${halfSize}" fill="${this.config.backgroundColor}" />`;
        
        // Add the triangle
        const triangleHeight = triangleSize * 0.866; // Height of equilateral triangle
        const triangleTop = halfSize - triangleHeight/2;
        const triangleLeft = halfSize - triangleSize/2;
        
        svg += `<polygon points="${halfSize},${triangleTop} ${triangleLeft + triangleSize},${triangleTop + triangleHeight} ${triangleLeft},${triangleTop + triangleHeight}" 
                 fill="none" stroke="${this.config.primaryColor}" stroke-width="2" />`;
        
        // Add the infinity symbol
        const infinityLeft = halfSize - infinitySize/2;
        const infinityTop = halfSize - infinitySize/4;
        
        svg += `<path d="M${infinityLeft},${infinityTop} 
                 C${infinityLeft - infinitySize/4},${infinityTop + infinitySize/4} ${infinityLeft - infinitySize/4},${infinityTop - infinitySize/4} ${infinityLeft},${infinityTop} 
                 C${infinityLeft + infinitySize/4},${infinityTop - infinitySize/4} ${infinityLeft + infinitySize/4},${infinityTop + infinitySize/4} ${infinityLeft},${infinityTop}" 
                 fill="none" stroke="${this.config.accentColor}" stroke-width="2" />`;
        
        // Add hand shapes for ASL if space allows
        if (size >= 100) {
            const handSize = size * 0.15;
            const handBottom = size * 0.85;
            
            // Simple hand shape (stylized)
            svg += `<path d="M${size*0.25},${handBottom} 
                     C${size*0.25},${handBottom-handSize} ${size*0.35},${handBottom-handSize} ${size*0.35},${handBottom-handSize*0.8}
                     C${size*0.35},${handBottom-handSize*0.6} ${size*0.45},${handBottom-handSize*0.6} ${size*0.45},${handBottom-handSize*0.8}
                     C${size*0.45},${handBottom-handSize*0.6} ${size*0.55},${handBottom-handSize*0.6} ${size*0.55},${handBottom-handSize*0.8}
                     C${size*0.55},${handBottom-handSize*0.6} ${size*0.65},${handBottom-handSize*0.6} ${size*0.65},${handBottom-handSize*0.8}
                     C${size*0.65},${handBottom-handSize*0.6} ${size*0.75},${handBottom-handSize*0.6} ${size*0.75},${handBottom-handSize*0.8}
                     L${size*0.75},${handBottom}" 
                     fill="none" stroke="${this.config.accentColor}" stroke-width="1.5" stroke-linecap="round" />`;
        }
        
        // Add animation elements if enabled
        if (this.config.animated) {
            svg += `<style>
                @keyframes pulse {
                    0% { opacity: 0.7; }
                    50% { opacity: 1; }
                    100% { opacity: 0.7; }
                }
                .pulse {
                    animation: pulse 2s infinite;
                }
            </style>`;
            
            // Add pulsing overlay
            svg += `<circle class="pulse" cx="${halfSize}" cy="${halfSize}" r="${halfSize*0.9}" 
                    fill="none" stroke="${this.config.primaryColor}" stroke-width="1" stroke-opacity="0.3" />`;
        }
        
        // Add text if enabled and specified
        if (this.config.displayText && this.config.text) {
            const fontSize = size * 0.12;
            const textY = size * 0.95;
            
            svg += `<text x="${halfSize}" y="${textY}" font-family="Arial, sans-serif" font-size="${fontSize}" 
                    font-weight="bold" fill="${this.config.textColor}" text-anchor="middle">${this.config.text}</text>`;
        }
        
        // Close the SVG tag
        svg += '</svg>';
        
        return svg;
    }
    
    /**
     * Render the logo to the specified container or return the SVG markup
     * @returns {string|void} SVG markup if no container specified
     */
    render() {
        const svg = this.generateSVG();
        
        if (this.container) {
            this.container.innerHTML = svg;
        } else {
            return svg;
        }
    }
    
    /**
     * Render the logo as a data URL for use in src attributes
     * @returns {string} Data URL containing the SVG
     */
    toDataURL() {
        const svg = this.generateSVG();
        return 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg);
    }
    
    /**
     * Utility method to generate logos with different configurations
     * @param {string} type The type of logo to generate: 'default', 'small', 'large', 'animated'
     * @param {string} containerId The ID of the container element
     * @returns {LogoGenerator} The logo generator instance
     */
    static create(type = 'default', containerId = null) {
        let options = {
            container: containerId
        };
        
        switch (type) {
            case 'small':
                options.size = 40;
                options.displayText = false;
                break;
            case 'large':
                options.size = 120;
                break;
            case 'animated':
                options.size = 80;
                options.animated = true;
                break;
            case 'navbar':
                options.size = 48;
                options.text = 'MBTQ';
                break;
            default:
                options.size = 80;
        }
        
        const generator = new LogoGenerator(options);
        if (containerId) {
            generator.render();
        }
        return generator;
    }
}

// Initialize logos when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize any logo containers on the page
    document.querySelectorAll('[data-logo-type]').forEach(container => {
        const type = container.dataset.logoType || 'default';
        LogoGenerator.create(type, container.id);
    });
    
    // Add logo to navbar if the element exists
    const navbarBrand = document.querySelector('.navbar-brand');
    if (navbarBrand) {
        // Create a logo container
        const logoContainer = document.createElement('div');
        logoContainer.className = 'me-2';
        logoContainer.style.width = '48px';
        logoContainer.style.height = '48px';
        
        // Generate the logo
        const logoSvg = LogoGenerator.create('navbar').generateSVG();
        logoContainer.innerHTML = logoSvg;
        
        // Insert at the beginning of navbar-brand
        navbarBrand.insertBefore(logoContainer, navbarBrand.firstChild);
    }
});