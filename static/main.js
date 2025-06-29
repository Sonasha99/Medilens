// Medical-themed interactive animations and effects

document.addEventListener('DOMContentLoaded', function() {
    // Navbar scroll effect
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // Mobile menu toggle
    const menuToggle = document.querySelector('.menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    
    if (menuToggle) {
        menuToggle.addEventListener('click', function() {
            menuToggle.classList.toggle('active');
            navLinks.classList.toggle('active');
        });
    }

    // Medical heartbeat effect for important elements
    const heartbeatElements = document.querySelectorAll('.heartbeat');
    heartbeatElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            this.style.animation = 'heartbeat 0.6s ease-in-out';
        });
        
        element.addEventListener('mouseleave', function() {
            this.style.animation = '';
        });
    });

    // Floating animation for medical icons
    const floatingElements = document.querySelectorAll('.floating-animation');
    floatingElements.forEach((element, index) => {
        element.style.animationDelay = `${index * 0.2}s`;
    });

    // Pulse effect for stethoscope icons
    const stethoscopes = document.querySelectorAll('.stethoscope');
    stethoscopes.forEach((stethoscope, index) => {
        stethoscope.addEventListener('click', function() {
            this.style.animation = 'stethoscopeBeat 0.5s ease-in-out';
            setTimeout(() => {
                this.style.animation = '';
            }, 500);
        });
    });

    // Doctor icon interaction
    const doctorIcons = document.querySelectorAll('.doctor-icon');
    doctorIcons.forEach(icon => {
        icon.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.3) rotate(5deg)';
            this.style.opacity = '0.3';
        });
        
        icon.addEventListener('mouseleave', function() {
            this.style.transform = '';
            this.style.opacity = '';
        });
    });

    // Medical-themed loading animation
    function createLoadingAnimation() {
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'medical-loading';
        loadingDiv.innerHTML = `
            <div class="loading-stethoscope">🩺</div>
            <div class="loading-text">Analyzing...</div>
        `;
        loadingDiv.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(37, 99, 235, 0.9);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 9999;
            color: white;
            font-size: 1.5rem;
            font-weight: bold;
        `;
        
        const stethoscope = loadingDiv.querySelector('.loading-stethoscope');
        stethoscope.style.cssText = `
            font-size: 4rem;
            animation: stethoscopeBeat 1s ease-in-out infinite;
            margin-bottom: 1rem;
        `;
        
        return loadingDiv;
    }

    // Add loading animation to forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const loading = createLoadingAnimation();
            document.body.appendChild(loading);
            
            // Remove loading after 2 seconds (or when form processing is done)
            setTimeout(() => {
                if (loading.parentNode) {
                    loading.parentNode.removeChild(loading);
                }
            }, 2000);
        });
    });

    // Medical-themed tooltips
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', function(e) {
            const tooltip = document.createElement('div');
            tooltip.className = 'medical-tooltip';
            tooltip.textContent = this.getAttribute('data-tooltip');
            tooltip.style.cssText = `
                position: absolute;
                background: var(--primary-color);
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 0.5rem;
                font-size: 0.875rem;
                z-index: 1000;
                pointer-events: none;
                transform: translateY(-100%);
                margin-top: -10px;
                box-shadow: var(--shadow-md);
            `;
            
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
            tooltip.style.top = rect.top + 'px';
            
            this.tooltip = tooltip;
        });
        
        element.addEventListener('mouseleave', function() {
            if (this.tooltip) {
                this.tooltip.remove();
                this.tooltip = null;
            }
        });
    });

    // Medical-themed scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'fadeInUp 0.6s ease-out forwards';
            }
        });
    }, observerOptions);

    // Observe elements for scroll animations
    const animatedElements = document.querySelectorAll('.feature-card, .stat-item, .testimonial-card');
    animatedElements.forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(30px)';
        observer.observe(element);
    });

    // Medical-themed cursor effect
    const cursor = document.createElement('div');
    cursor.className = 'medical-cursor';
    cursor.style.cssText = `
        position: fixed;
        width: 20px;
        height: 20px;
        background: var(--primary-color);
        border-radius: 50%;
        pointer-events: none;
        z-index: 9999;
        opacity: 0.7;
        transform: translate(-50%, -50%);
        transition: all 0.1s ease;
    `;
    document.body.appendChild(cursor);

    document.addEventListener('mousemove', function(e) {
        cursor.style.left = e.clientX + 'px';
        cursor.style.top = e.clientY + 'px';
    });

    // Hide cursor on mobile
    if ('ontouchstart' in window) {
        cursor.style.display = 'none';
    }

    // Medical-themed success/error notifications
    window.showMedicalNotification = function(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = `medical-notification ${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? 'var(--success-color)' : 'var(--error-color)'};
            color: white;
            padding: 1rem 2rem;
            border-radius: 0.5rem;
            box-shadow: var(--shadow-lg);
            z-index: 10000;
            transform: translateX(100%);
            transition: transform 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    };

    // Add medical-themed hover effects to buttons
    const buttons = document.querySelectorAll('button, .cta-button, .submit-button');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px) scale(1.02)';
            this.style.boxShadow = 'var(--shadow-xl)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = '';
            this.style.boxShadow = '';
        });
    });

    console.log('🩺 MediLens Medical Animations Loaded Successfully!');
}); 