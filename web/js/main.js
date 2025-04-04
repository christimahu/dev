/**
 * Main JavaScript for Dev Environment Website
 */

document.addEventListener('DOMContentLoaded', function() {
  // Initialize code highlighting for code blocks
  if (typeof Prism !== 'undefined') {
    Prism.highlightAll();
  }
  
  // Add iOS-specific class if needed
  if (/iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream) {
    document.documentElement.classList.add('ios-device');
  }
});

// Alpine.js component for the app
document.addEventListener('alpine:init', () => {
  Alpine.data('devApp', () => ({
    tab: 'overview',
    mobileMenu: false,
    
    // Initialize from URL hash if present
    init() {
      // Check for hash in URL and set tab accordingly
      const hash = window.location.hash;
      if (hash) {
        const tabName = hash.substring(1); // Remove the # character
        if (['overview', 'features', 'install', 'usage', 'commands'].includes(tabName)) {
          this.tab = tabName;
        }
      }
      
      // Listen for hash changes
      window.addEventListener('hashchange', () => {
        const newHash = window.location.hash;
        if (newHash) {
          const tabName = newHash.substring(1);
          if (['overview', 'features', 'install', 'usage', 'commands'].includes(tabName)) {
            this.tab = tabName;
          }
        }
      });
      
      // Scroll to top on page load
      window.scrollTo(0, 0);
    },
    
    // Change tab and update hash
    changeTab(tabName) {
      this.tab = tabName;
      this.mobileMenu = false;
      window.location.hash = tabName;
      window.scrollTo(0, 0);
    }
  }));
});

// iOS-specific touch improvements
if (/iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream) {
  document.addEventListener('touchstart', function(){}, {passive: true});
}

// Fix for iOS vh issues
function setVH() {
  let vh = window.innerHeight * 0.01;
  document.documentElement.style.setProperty('--vh', `${vh}px`);
}

window.addEventListener('resize', setVH);
window.addEventListener('orientationchange', setVH);
setVH();

// Improve scrolling performance
let ticking = false;
window.addEventListener('scroll', function() {
  if (!ticking) {
    window.requestAnimationFrame(function() {
      ticking = false;
    });
    ticking = true;
  }
}, {passive: true});

// Add support for Safari 100vh fix
if (navigator.userAgent.indexOf('Safari') != -1 && 
    navigator.userAgent.indexOf('Chrome') == -1) {
  document.documentElement.classList.add('safari');
  
  const updateHeight = () => {
    document.documentElement.style.setProperty(
      '--real-vh', 
      `${window.innerHeight * 0.01}px`
    );
  };
  
  window.addEventListener('resize', updateHeight);
  updateHeight();
}
