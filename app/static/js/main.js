/**
 * Refresh the chart with the selected number of days
 */
function refreshChart() {
    const days = document.getElementById('dataDays').value;
    const url = days ? '/?days=' + days : '/';
    const btn = document.querySelector('.btn');
    btn.textContent = 'Loading...';
    btn.disabled = true;
    window.location.href = url;
}

/**
 * Check if the device is mobile
 * @returns {boolean} - True if the device is mobile, false otherwise
 */
function isMobile() {
    return window.innerWidth <= 768 || 'ontouchstart' in window;
}

/**
 * Drag and drop functionality for chart panning
 */
class ChartDragHandler {
    constructor() {
        this.isDragging = false;
        this.startPos = { x: 0, y: 0 };
        this.currentTransform = { x: 0, y: 0 };
        this.scale = 1;
        this.maxTranslate = 500;
        this.mobileSensitivity = 0.7;
        this.lastTapTime = 0;
        this.tapTimeout = null;
        this.initializeEventListeners();
    }
    
    /**
     * Initialize event listeners for the chart
     */
    initializeEventListeners() {
        const mainContent = document.getElementById('mainContent');
        const chartContainer = document.getElementById('chartContainer');
        
        if (!mainContent || !chartContainer) return;
        
        // Mouse events
        mainContent.addEventListener('mousedown', this.handleStart.bind(this));
        document.addEventListener('mousemove', this.handleMove.bind(this));
        document.addEventListener('mouseup', this.handleEnd.bind(this));
        
        // Touch events for mobile
        mainContent.addEventListener('touchstart', this.handleTouchStart.bind(this), { passive: false });
        document.addEventListener('touchmove', this.handleMove.bind(this), { passive: false });
        document.addEventListener('touchend', this.handleTouchEnd.bind(this));
        
        // Wheel event for zooming
        mainContent.addEventListener('wheel', this.handleWheel.bind(this), { passive: false });
        
        // Prevent context menu on right click
        mainContent.addEventListener('contextmenu', (e) => e.preventDefault());
    }
    
    /**
     * Get the position of the event
     * @param {Event} e - The event
     * @returns {Object} - The position of the event
     */
    getEventPos(e) {
        if (!e) return { x: 0, y: 0 };
        
        const rect = document.getElementById('mainContent').getBoundingClientRect();
        let clientX, clientY;
        
        if (e.touches && e.touches.length > 0) {
            clientX = e.touches[0].clientX;
            clientY = e.touches[0].clientY;
        } else if (e.changedTouches && e.changedTouches.length > 0) {
            clientX = e.changedTouches[0].clientX;
            clientY = e.changedTouches[0].clientY;
        } else {
            clientX = e.clientX || 0;
            clientY = e.clientY || 0;
        }
        
        return {
            x: clientX - rect.left,
            y: clientY - rect.top
        };
    }
    
    /**
     * Clamp a value between min and max
     * @param {number} value - The value to clamp
     * @param {number} min - The minimum value
     * @param {number} max - The maximum value
     * @returns {number} - The clamped value
     */
    clamp(value, min, max) {
        return Math.min(Math.max(value, min), max);
    }
    
    /**
     * Handle the start of the drag
     * @param {Event} e - The event
     */
    handleStart(e) {
        if (e.target.closest('.floating-panel')) return;
        
        this.isDragging = true;
        this.startPos = this.getEventPos(e);
        
        document.getElementById('mainContent').classList.add('dragging');
        e.preventDefault();
    }
    
    /**
     * Handle touch start with double-tap detection
     * @param {Event} e - The event
     */
    handleTouchStart(e) {
        if (e.target.closest('.floating-panel')) return;
        
        const currentTime = new Date().getTime();
        const timeDiff = currentTime - this.lastTapTime;
        
        if (timeDiff < 300 && timeDiff > 0) {
            this.resetTransform();
            e.preventDefault();
            return;
        }
        
        this.lastTapTime = currentTime;
        
        if (this.tapTimeout) {
            clearTimeout(this.tapTimeout);
        }
        
        this.tapTimeout = setTimeout(() => {
            this.handleStart(e);
        }, 300);
        
        e.preventDefault();
    }
    
    /**
     * Handle the move of the drag
     * @param {Event} e - The event
     */
    handleMove(e) {
        if (!this.isDragging) return;
        
        const currentPos = this.getEventPos(e);
        let deltaX = currentPos.x - this.startPos.x;
        let deltaY = currentPos.y - this.startPos.y;
        
        if (isMobile()) {
            deltaX *= this.mobileSensitivity;
            deltaY *= this.mobileSensitivity;
        }
        
        const newTransformX = this.clamp(
            this.currentTransform.x + deltaX,
            -this.maxTranslate,
            this.maxTranslate
        );
        const newTransformY = this.clamp(
            this.currentTransform.y + deltaY,
            -this.maxTranslate,
            this.maxTranslate
        );
        
        this.applyTransform(newTransformX, newTransformY, this.scale);
        e.preventDefault();
    }
    
    /**
     * Handle touch end
     * @param {Event} e - The event
     */
    handleTouchEnd(e) {
        if (this.tapTimeout && !this.isDragging) {
            clearTimeout(this.tapTimeout);
            this.tapTimeout = null;
        }
        
        this.handleEnd(e);
    }
    
    /**
     * Handle the end of the drag
     * @param {Event} e - The event
     */
    handleEnd(e) {
        if (!this.isDragging) return;
        
        this.isDragging = false;
        
        if (e) {
            const currentPos = this.getEventPos(e);
            let deltaX = currentPos.x - this.startPos.x;
            let deltaY = currentPos.y - this.startPos.y;
            
            if (isMobile()) {
                deltaX *= this.mobileSensitivity;
                deltaY *= this.mobileSensitivity;
            }
            
            this.currentTransform.x = this.clamp(
                this.currentTransform.x + deltaX,
                -this.maxTranslate,
                this.maxTranslate
            );
            this.currentTransform.y = this.clamp(
                this.currentTransform.y + deltaY,
                -this.maxTranslate,
                this.maxTranslate
            );
        }
        
        document.getElementById('mainContent').classList.remove('dragging');
    }
    
    /**
     * Handle the wheel event for zooming
     * @param {Event} e - The event
     */
    handleWheel(e) {
        e.preventDefault();
        
        const delta = e.deltaY > 0 ? 0.9 : 1.1;
        const newScale = Math.max(0.5, Math.min(3, this.scale * delta));
        
        const rect = document.getElementById('mainContent').getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;
        
        const deltaScale = newScale / this.scale;
        const newTransformX = mouseX - (mouseX - this.currentTransform.x) * deltaScale;
        const newTransformY = mouseY - (mouseY - this.currentTransform.y) * deltaScale;
        
        this.currentTransform.x = this.clamp(newTransformX, -this.maxTranslate, this.maxTranslate);
        this.currentTransform.y = this.clamp(newTransformY, -this.maxTranslate, this.maxTranslate);
        this.scale = newScale;
        
        this.applyTransform(this.currentTransform.x, this.currentTransform.y, this.scale);
    }
    
    /**
     * Apply the transform to the chart
     * @param {number} x - The x position
     * @param {number} y - The y position
     * @param {number} scale - The scale
     */
    applyTransform(x, y, scale) {
        const chartContainer = document.getElementById('chartContainer');
        if (chartContainer) {
            chartContainer.style.transform = `translate(${x}px, ${y}px) scale(${scale})`;
        }
    }
    
    /**
     * Reset the transform to the default position
     */
    resetTransform() {
        this.currentTransform = { x: 0, y: 0 };
        this.scale = 1;
        this.applyTransform(0, 0, 1);
    }
}

/**
 * Panel management
 */
class PanelManager {
    constructor() {
        this.activeMobilePanel = null;
        this.initializePanels();
    }
    
    /**
     * Initialize the panels
     */
    initializePanels() {        
        if (!isMobile()) {
            this.makePanelsDraggable();
        } else {
            this.initializeMobileBehavior();
        }
    }

    /**
     * Initialize the mobile behavior
     */
    initializeMobileBehavior() {
        this.updateMobileNavStates();
        
        document.addEventListener('click', (e) => {
            if (isMobile() && this.activeMobilePanel) {
                const panel = document.getElementById(this.activeMobilePanel);
                const navItems = document.querySelectorAll('.nav-item');
                
                if (panel && !panel.contains(e.target) && 
                    ![...navItems].some(item => item.contains(e.target))) {
                    closeAllMobilePanels();
                }
            }
        });
    }
    
    /**
     * Update the mobile nav states
     */
    updateMobileNavStates() {
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.classList.remove('active');
        });
        
        if (this.activeMobilePanel) {
            const activeNavItem = this.getNavItemForPanel(this.activeMobilePanel);
            if (activeNavItem) {
                activeNavItem.classList.add('active');
            }
        }
    }
    
    /**
     * Get the nav item for the panel
     * @param {string} panelId - The id of the panel
     * @returns {Element} - The nav item
     */
    getNavItemForPanel(panelId) {
        const navItems = document.querySelectorAll('.nav-item');
        return [...navItems].find(item => {
            const onclick = item.getAttribute('onclick');
            return onclick && onclick.includes(panelId);
        });
    }
    
    /**
     * Make the panels draggable
     */
    makePanelsDraggable() {
        const panels = document.querySelectorAll('.floating-panel');
        
        panels.forEach(panel => {
            const header = panel.querySelector('.panel-header');
            if (header) {
                header.style.cursor = 'move';
                this.makeDraggable(panel, header);
            }
        });
    }
    
    /**
     * Make the panel draggable
     * @param {Element} panel - The panel
     * @param {Element} handle - The handle
     */
    makeDraggable(panel, handle) {
        let isDragging = false;
        let startPos = { x: 0, y: 0 };
        let panelPos = { x: 0, y: 0 };
        
        handle.addEventListener('mousedown', (e) => {
            isDragging = true;
            startPos = { x: e.clientX, y: e.clientY };
            
            const rect = panel.getBoundingClientRect();
            panelPos = { x: rect.left, y: rect.top };
            
            panel.style.position = 'fixed';
            panel.style.zIndex = '1000';
            
            e.preventDefault();
        });
        
        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            
            const deltaX = e.clientX - startPos.x;
            const deltaY = e.clientY - startPos.y;
            
            panel.style.left = (panelPos.x + deltaX) + 'px';
            panel.style.top = (panelPos.y + deltaY) + 'px';
            panel.style.right = 'auto';
            panel.style.bottom = 'auto';
        });
        
        document.addEventListener('mouseup', () => {
            if (isDragging) {
                isDragging = false;
                panel.style.zIndex = '500';
            }
        });
    }
}

/**
 * Toggle the mobile panel
 * @param {string} panelId - The id of the panel
 */
function toggleMobilePanel(panelId) {
    if (!window.panelManager || !isMobile()) return;
    
    const panel = document.getElementById(panelId);
    const overlay = document.getElementById('mobileOverlay');
    
    if (!panel || !overlay) return;
    
    if (window.panelManager.activeMobilePanel === panelId) {
        closeAllMobilePanels();
        return;
    }
    
    closeAllMobilePanels();
    
    panel.classList.add('mobile-active');
    overlay.classList.add('active');
    window.panelManager.activeMobilePanel = panelId;
    window.panelManager.updateMobileNavStates();
    
    document.body.style.overflow = 'hidden';
}

/**
 * Close the mobile panel
 * @param {string} panelId - The id of the panel
 */
function closeMobilePanel(panelId) {
    if (!window.panelManager || !isMobile()) return;
    
    const panel = document.getElementById(panelId);
    if (!panel) return;
    
    panel.classList.remove('mobile-active');
    
    if (window.panelManager.activeMobilePanel === panelId) {
        window.panelManager.activeMobilePanel = null;
        window.panelManager.updateMobileNavStates();
        
        const overlay = document.getElementById('mobileOverlay');
        if (overlay) {
            overlay.classList.remove('active');
        }
        
        document.body.style.overflow = '';
    }
}

/**
 * Close all mobile panels
 */
function closeAllMobilePanels() {
    if (!window.panelManager || !isMobile()) return;
    
    const panels = document.querySelectorAll('.floating-panel');
    const overlay = document.getElementById('mobileOverlay');
    
    panels.forEach(panel => {
        panel.classList.remove('mobile-active');
    });
    
    if (overlay) {
        overlay.classList.remove('active');
    }
    
    window.panelManager.activeMobilePanel = null;
    window.panelManager.updateMobileNavStates();
    
    document.body.style.overflow = '';
}

/**
 * Initialize the keyboard shortcuts
 */
function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        if (e.key === ' ' && window.chartDragHandler) {
            e.preventDefault();
            window.chartDragHandler.resetTransform();
        }
        if (e.key === 'Escape' && window.panelManager && isMobile()) {
            closeAllMobilePanels();
        }
    });
}

/**
 * Initialize everything when DOM is loaded
 */
document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const days = urlParams.get('days');
    if (days) {
        const daysSelect = document.getElementById('dataDays');
        if (daysSelect) {
            daysSelect.value = days;
        }
    }
    
    window.chartDragHandler = new ChartDragHandler();
    
    window.panelManager = new PanelManager();
    
    initializeKeyboardShortcuts();
    
    window.addEventListener('resize', () => {
        if (!isMobile()) {
            closeAllMobilePanels();
        }
    });
}); 