/* ============================================================================
   AIAY DASHBOARD - MAIN JAVASCRIPT
   ============================================================================ */

// Global Chart.js defaults configuration
if (typeof Chart !== 'undefined') {
    Chart.defaults.font.family = "'IBM Plex Sans Arabic', sans-serif";
    Chart.defaults.plugins.tooltip.rtl = true;
    Chart.defaults.plugins.legend.rtl = true;
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Format number with thousand separators
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

/**
 * Animate number counter
 */
function animateCounter(element, start, end, duration) {
    if (!element) return;

    const range = end - start;
    const increment = range / (duration / 16); // 60fps
    let current = start;

    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            element.textContent = formatNumber(Math.round(end));
            clearInterval(timer);
        } else {
            element.textContent = formatNumber(Math.round(current));
        }
    }, 16);
}

/**
 * Debounce function for search inputs
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer') || createToastContainer();

    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${type}`;
    toast.innerHTML = `
        <i class="fas fa-${getToastIcon(type)}"></i>
        <span>${message}</span>
    `;

    toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('show');
    }, 100);

    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toastContainer';
    container.style.cssText = 'position: fixed; top: 20px; left: 20px; z-index: 9999;';
    document.body.appendChild(container);
    return container;
}

function getToastIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || icons.info;
}

// ============================================================================
// SIDEBAR FUNCTIONALITY
// ============================================================================

class Sidebar {
    constructor() {
        this.sidebar = document.getElementById('sidebar');
        this.toggleBtn = document.getElementById('sidebarToggle');
        this.overlay = document.getElementById('sidebarOverlay');
        this.init();
    }

    init() {
        if (this.toggleBtn) {
            this.toggleBtn.addEventListener('click', () => this.toggle());
        }

        // Close sidebar when clicking overlay
        if (this.overlay) {
            this.overlay.addEventListener('click', () => this.close());
        }

        // Close sidebar on mobile when clicking outside
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 768) {
                if (!this.sidebar.contains(e.target) &&
                    !this.toggleBtn?.contains(e.target) &&
                    this.sidebar.classList.contains('active')) {
                    this.close();
                }
            }
        });

        // Handle window resize
        window.addEventListener('resize', debounce(() => {
            if (window.innerWidth > 768) {
                this.close();
            }
        }, 250));
    }

    toggle() {
        this.sidebar.classList.toggle('active');
        this.toggleBtn?.classList.toggle('active');
        this.overlay?.classList.toggle('active');
    }

    open() {
        this.sidebar.classList.add('active');
        this.toggleBtn?.classList.add('active');
        this.overlay?.classList.add('active');
    }

    close() {
        this.sidebar.classList.remove('active');
        this.toggleBtn?.classList.remove('active');
        this.overlay?.classList.remove('active');
    }
}

// ============================================================================
// CHART HELPERS
// ============================================================================

/**
 * Default Chart.js options for RTL support
 */
function getDefaultChartOptions(type = 'line') {
    return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'top',
                rtl: true,
                labels: {
                    font: {
                        family: 'IBM Plex Sans Arabic',
                        size: 12
                    },
                    padding: 15,
                    usePointStyle: true
                }
            },
            tooltip: {
                rtl: true,
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                titleFont: {
                    family: 'IBM Plex Sans Arabic',
                    size: 14
                },
                bodyFont: {
                    family: 'IBM Plex Sans Arabic',
                    size: 13
                },
                padding: 12,
                cornerRadius: 8,
                displayColors: true
            }
        },
        interaction: {
            mode: 'index',
            intersect: false
        }
    };
}

/**
 * Create gradient for chart backgrounds
 */
function createGradient(ctx, color1, color2) {
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, color1);
    gradient.addColorStop(1, color2);
    return gradient;
}

// ============================================================================
// TABLE ENHANCEMENTS
// ============================================================================

class DataTable {
    constructor(tableId, options = {}) {
        this.table = document.getElementById(tableId);
        this.options = {
            searchable: true,
            sortable: true,
            pagination: false,
            ...options
        };

        if (this.table) {
            this.init();
        }
    }

    init() {
        if (this.options.sortable) {
            this.initSorting();
        }

        if (this.options.searchable) {
            this.initSearch();
        }

        // Add row animations
        this.animateRows();
    }

    initSorting() {
        const headers = this.table.querySelectorAll('th[data-sortable]');
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', () => this.sortTable(header));
        });
    }

    sortTable(header) {
        const column = header.cellIndex;
        const rows = Array.from(this.table.querySelectorAll('tbody tr'));
        const isAscending = header.classList.contains('sort-asc');

        rows.sort((a, b) => {
            const aValue = a.cells[column]?.textContent.trim() || '';
            const bValue = b.cells[column]?.textContent.trim() || '';

            if (isAscending) {
                return bValue.localeCompare(aValue, 'ar');
            } else {
                return aValue.localeCompare(bValue, 'ar');
            }
        });

        // Remove all sort classes
        this.table.querySelectorAll('th').forEach(th => {
            th.classList.remove('sort-asc', 'sort-desc');
        });

        // Add appropriate sort class
        header.classList.add(isAscending ? 'sort-desc' : 'sort-asc');

        // Reorder rows
        const tbody = this.table.querySelector('tbody');
        rows.forEach(row => tbody.appendChild(row));
    }

    initSearch() {
        const searchInput = document.getElementById(this.options.searchInputId || 'searchInput');
        if (!searchInput) return;

        searchInput.addEventListener('keyup', debounce((e) => {
            this.search(e.target.value);
        }, 300));
    }

    search(term) {
        const rows = this.table.querySelectorAll('tbody tr');
        const searchTerm = term.toLowerCase();

        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            if (text.includes(searchTerm)) {
                row.style.display = '';
                row.classList.add('fade-in');
            } else {
                row.style.display = 'none';
            }
        });
    }

    animateRows() {
        const rows = this.table.querySelectorAll('tbody tr');
        rows.forEach((row, index) => {
            row.style.animation = `fadeIn 0.3s ease-out ${index * 0.03}s both`;
        });
    }
}

// ============================================================================
// CARD ANIMATIONS
// ============================================================================

class CardAnimations {
    static init() {
        // Stat cards
        const statCards = document.querySelectorAll('.stat-card');
        statCards.forEach((card, index) => {
            card.style.animationDelay = `${index * 0.1}s`;

            // Hover effect
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-5px)';
            });

            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
            });
        });

        // Chart cards
        const chartCards = document.querySelectorAll('.chart-card');
        chartCards.forEach((card, index) => {
            card.style.animationDelay = `${(index + 2) * 0.1}s`;
        });

        // Table cards
        const tableCards = document.querySelectorAll('.table-card');
        tableCards.forEach((card, index) => {
            card.style.animationDelay = `${(index + 3) * 0.1}s`;
        });
    }
}

// ============================================================================
// SCROLL ANIMATIONS
// ============================================================================

class ScrollAnimations {
    constructor() {
        this.observer = new IntersectionObserver(
            (entries) => this.handleIntersection(entries),
            {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            }
        );

        this.init();
    }

    init() {
        const elements = document.querySelectorAll('[data-animate]');
        elements.forEach(el => this.observer.observe(el));
    }

    handleIntersection(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const animation = entry.target.dataset.animate || 'fadeIn';
                entry.target.classList.add(animation);
                this.observer.unobserve(entry.target);
            }
        });
    }
}

// ============================================================================
// FORM ENHANCEMENTS
// ============================================================================

class FormEnhancements {
    static init() {
        // Add floating label effect
        const formControls = document.querySelectorAll('.form-control');
        formControls.forEach(control => {
            control.addEventListener('focus', function() {
                this.parentElement?.classList.add('focused');
            });

            control.addEventListener('blur', function() {
                if (!this.value) {
                    this.parentElement?.classList.remove('focused');
                }
            });
        });

        // Form validation
        const forms = document.querySelectorAll('form[data-validate]');
        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                if (!form.checkValidity()) {
                    e.preventDefault();
                    e.stopPropagation();
                }
                form.classList.add('was-validated');
            });
        });
    }
}

// ============================================================================
// LOADING STATES
// ============================================================================

class LoadingManager {
    static show(element) {
        if (!element) return;

        const spinner = document.createElement('div');
        spinner.className = 'loading-overlay';
        spinner.innerHTML = '<div class="loading-spinner"></div>';
        element.style.position = 'relative';
        element.appendChild(spinner);
    }

    static hide(element) {
        if (!element) return;

        const overlay = element.querySelector('.loading-overlay');
        if (overlay) {
            overlay.remove();
        }
    }
}

// ============================================================================
// THEME MANAGER (Optional)
// ============================================================================

class ThemeManager {
    constructor() {
        this.currentTheme = localStorage.getItem('theme') || 'light';
        this.init();
    }

    init() {
        this.applyTheme(this.currentTheme);

        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggle());
        }
    }

    toggle() {
        this.currentTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.applyTheme(this.currentTheme);
        localStorage.setItem('theme', this.currentTheme);
    }

    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
    }
}

// ============================================================================
// INITIALIZE ON DOM READY
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    // Initialize sidebar
    if (document.getElementById('sidebar')) {
        new Sidebar();
    }

    // Initialize card animations
    CardAnimations.init();

    // Initialize scroll animations
    if (window.IntersectionObserver) {
        new ScrollAnimations();
    }

    // Initialize form enhancements
    FormEnhancements.init();

    // Animate counters
    const counters = document.querySelectorAll('.stat-value');
    counters.forEach(counter => {
        const target = parseInt(counter.textContent.replace(/,/g, '')) || 0;
        animateCounter(counter, 0, target, 1000);
    });

    // Add smooth scroll behavior
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;

            const target = document.querySelector(targetId);
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add copy to clipboard functionality
    document.querySelectorAll('[data-copy]').forEach(element => {
        element.addEventListener('click', function() {
            const text = this.dataset.copy || this.textContent;
            navigator.clipboard.writeText(text).then(() => {
                showToast('تم النسخ إلى الحافظة', 'success');
            });
        });
    });

    // Handle external links
    document.querySelectorAll('a[target="_blank"]').forEach(link => {
        link.setAttribute('rel', 'noopener noreferrer');
    });

    // Add loading state to buttons
    document.querySelectorAll('button[type="submit"]').forEach(button => {
        button.addEventListener('click', function() {
            if (this.form?.checkValidity()) {
                this.disabled = true;
                const originalText = this.innerHTML;
                this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> جاري المعالجة...';

                setTimeout(() => {
                    this.disabled = false;
                    this.innerHTML = originalText;
                }, 5000);
            }
        });
    });

    console.log('✅ Dashboard initialized successfully');
});

// ============================================================================
// TOAST NOTIFICATIONS
// ============================================================================

/**
 * Initialize Bootstrap toasts and auto-hide them
 */
function initializeToasts() {
    const toastElements = document.querySelectorAll('.toast');

    toastElements.forEach((toastElement, index) => {
        const toast = new bootstrap.Toast(toastElement, {
            autohide: true,
            delay: 5000 // 5 seconds
        });

        // Stagger the display if multiple toasts
        setTimeout(() => {
            toast.show();
        }, index * 200);

        // Auto-hide with animation
        toastElement.addEventListener('hidden.bs.toast', function() {
            this.remove();
        });
    });
}

// Initialize toasts when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeToasts);
} else {
    initializeToasts();
}

/**
 * Programmatically create and show a toast
 */
function showToast(message, type = 'info') {
    const toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) return;

    const typeColors = {
        success: 'var(--bs-success)',
        error: 'var(--bs-danger)',
        danger: 'var(--bs-danger)',
        warning: 'var(--bs-warning)',
        info: 'var(--bs-info)',
        primary: 'var(--bs-primary)'
    };

    const typeIcons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        danger: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle',
        primary: 'fa-bell'
    };

    const toastHtml = `
        <div class="toast align-items-center text-white border-0 show" role="alert" aria-live="assertive" aria-atomic="true"
             style="background-color: ${typeColors[type] || typeColors.info};">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas ${typeIcons[type] || typeIcons.info} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;

    toastContainer.insertAdjacentHTML('beforeend', toastHtml);

    const newToast = toastContainer.lastElementChild;
    const toast = new bootstrap.Toast(newToast, {
        autohide: true,
        delay: 5000
    });

    toast.show();

    newToast.addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
}

// ============================================================================
// PAGE LOADER
// ============================================================================

/**
 * Page Loader Controller
 */
const PageLoader = {
    loader: null,
    startTime: null,

    init() {
        this.loader = document.getElementById('pageLoader');
        this.startTime = Date.now();

        // Show loader immediately on page load
        this.show();

        // Hide loader when page is fully loaded
        window.addEventListener('load', () => {
            this.hide();
        });
    },

    show() {
        if (this.loader) {
            this.loader.classList.remove('hidden');
            this.loader.classList.add('show');
        }
    },

    hide() {
        if (this.loader) {
            // Ensure loader shows for at least 1 second
            const elapsedTime = Date.now() - this.startTime;
            const minimumDisplayTime = 1000; // 1 second
            const remainingTime = Math.max(0, minimumDisplayTime - elapsedTime);

            setTimeout(() => {
                this.loader.classList.remove('show');
                this.loader.classList.add('hidden');
            }, remainingTime + 300);
        }
    }
};

// Initialize page loader immediately
PageLoader.init();// ============================================================================
// EXPORT FOR GLOBAL USE
// ============================================================================

window.DashboardUtils = {
    formatNumber,
    animateCounter,
    debounce,
    showToast,
    PageLoader,
    LoadingManager,
    getDefaultChartOptions,
    createGradient
};

