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
 * Drag and drop functionality for chart panning
 */
class ChartDragHandler {
    constructor() {
        this.isDragging = false;
        this.startPos = { x: 0, y: 0 };
        this.currentTransform = { x: 0, y: 0 };
        this.scale = 1;
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
        mainContent.addEventListener('touchstart', this.handleStart.bind(this), { passive: false });
        document.addEventListener('touchmove', this.handleMove.bind(this), { passive: false });
        document.addEventListener('touchend', this.handleEnd.bind(this));
        
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
        const clientX = e.clientX || (e.touches && e.touches[0] && e.touches[0].clientX) || 0;
        const clientY = e.clientY || (e.touches && e.touches[0] && e.touches[0].clientY) || 0;
        
        return {
            x: clientX - rect.left,
            y: clientY - rect.top
        };
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
     * Handle the move of the drag
     * @param {Event} e - The event
     */
    handleMove(e) {
        if (!this.isDragging) return;
        
        const currentPos = this.getEventPos(e);
        const deltaX = currentPos.x - this.startPos.x;
        const deltaY = currentPos.y - this.startPos.y;
        
        const newTransformX = this.currentTransform.x + deltaX;
        const newTransformY = this.currentTransform.y + deltaY;
        
        this.applyTransform(newTransformX, newTransformY, this.scale);
        e.preventDefault();
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
            const deltaX = currentPos.x - this.startPos.x;
            const deltaY = currentPos.y - this.startPos.y;
            
            this.currentTransform.x += deltaX;
            this.currentTransform.y += deltaY;
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
        
        this.currentTransform.x = newTransformX;
        this.currentTransform.y = newTransformY;
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
        if (!this.isMobile()) {
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
            if (this.isMobile() && this.activeMobilePanel) {
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
    
    /**
     * Check if the device is mobile
     * @returns {boolean} - True if the device is mobile, false otherwise
     */
    isMobile() {
        return window.innerWidth <= 768;
    }
}

/**
 * Toggle the mobile panel
 * @param {string} panelId - The id of the panel
 */
function toggleMobilePanel(panelId) {
    if (!window.panelManager || !window.panelManager.isMobile()) return;
    
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
    if (!window.panelManager || !window.panelManager.isMobile()) return;
    
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
    if (!window.panelManager || !window.panelManager.isMobile()) return;
    
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
        if (e.key === 'Escape' && window.panelManager && window.panelManager.isMobile()) {
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
        if (!window.panelManager.isMobile()) {
            closeAllMobilePanels();
        }
    });
}); 