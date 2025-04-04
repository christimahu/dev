/**
 * Main JavaScript for Dev Environment Website with Matrix Theme
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
  
  // Matrix animation and effects
  initMatrixEffects();
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
        if (['overview', 'install', 'usage', 'commands'].includes(tabName)) {
          this.tab = tabName;
        }
      }
      
      // Listen for hash changes
      window.addEventListener('hashchange', () => {
        const newHash = window.location.hash;
        if (newHash) {
          const tabName = newHash.substring(1);
          if (['overview', 'install', 'usage', 'commands'].includes(tabName)) {
            this.tab = tabName;
          }
        }
      });
      
      // Scroll to top on page load
      window.scrollTo(0, 0);
      
      // Start typewriter effect for code blocks
      setTimeout(() => this.initTypewriterEffect(), 500);
    },
    
    // Change tab and update hash
    changeTab(tabName) {
      this.tab = tabName;
      this.mobileMenu = false;
      window.location.hash = tabName;
      window.scrollTo(0, 0);
      
      // Apply typing effect to newly visible code blocks
      setTimeout(() => this.initTypewriterEffect(), 300);
    },
    
    // Add typewriter effect to code blocks
    initTypewriterEffect() {
      const codeBlocks = document.querySelectorAll('.code-block:not(.typed)');
      
      codeBlocks.forEach(block => {
        if (!block.classList.contains('typed')) {
          block.classList.add('typed');
          
          const codeContent = block.innerHTML;
          block.innerHTML = '';
          
          // Create a typing container
          const typingContainer = document.createElement('div');
          typingContainer.classList.add('typing-container');
          block.appendChild(typingContainer);
          
          // Type out the code
          let i = 0;
          const typeCode = () => {
            if (i < codeContent.length) {
              typingContainer.innerHTML += codeContent.charAt(i);
              i++;
              setTimeout(typeCode, Math.random() * 10 + 5); // Random typing speed for effect
            }
          };
          
          // Only animate if the element is visible
          if (block.offsetParent !== null) {
            setTimeout(typeCode, 200);
          } else {
            // If not visible, just show the code without animation
            typingContainer.innerHTML = codeContent;
          }
        }
      });
    }
  }));
});

// Matrix effects initialization
function initMatrixEffects() {
  // Fix for iOS vh issues
  function setVH() {
    let vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', `${vh}px`);
  }
  
  window.addEventListener('resize', setVH);
  window.addEventListener('orientationchange', setVH);
  setVH();
  
  // Add occasional screen flicker effect
  const body = document.body;
  setInterval(() => {
    if (Math.random() > 0.9) {
      body.classList.add('flicker');
      setTimeout(() => {
        body.classList.remove('flicker');
      }, 150);
    }
  }, 10000);
  
  // Create some random matrix characters that float down occasionally
  const rustSnippets = [
    'let mut', 'fn main', 'struct', 'impl', 'enum', 'match', 'Option<T>', 
    'Result<T, E>', 'unwrap()', 'expect()', '#[derive]', 'Vec<T>', 'HashMap', 
    'async fn', 'await', '.collect()', '::new()', '->'
  ];
  
  function createMatrixChar() {
    // Only create if we pass the random check to keep characters sparse
    if (Math.random() > 0.9) {
      const char = document.createElement('div');
      // Use random Rust code snippets instead of 1s and 0s
      char.textContent = rustSnippets[Math.floor(Math.random() * rustSnippets.length)];
      char.style.position = 'fixed';
      char.style.color = 'var(--matrix-green)';
      char.style.fontSize = '6px'; // Very small font size
      char.style.opacity = '0.5';
      char.style.left = (Math.random() * 100) + 'vw';
      char.style.top = '0vh';
      char.style.zIndex = '-1';
      char.style.textShadow = '0 0 3px rgba(0, 255, 65, 0.5)';
      document.body.appendChild(char);
      
      // Animate downward like in The Matrix
      let pos = 0;
      const speed = 0.05 + (Math.random() * 0.1); // Random speeds
      const animate = () => {
        pos += speed;
        char.style.top = pos + 'vh';
        
        if (pos < 120) {
          requestAnimationFrame(animate);
        } else {
          char.remove();
        }
      };
      
      requestAnimationFrame(animate);
    }
  }
  
  // Create floating matrix characters occasionally
  setInterval(() => {
    // Create 0-3 characters at random positions
    const count = Math.floor(Math.random() * 4);
    for (let i = 0; i < count; i++) {
      createMatrixChar();
    }
  }, 500);
  
  // Add a subtle pulsing effect to the matrix background
  const matrixBg = document.querySelector('.matrix-bg');
  if (matrixBg) {
    // Add random subtle changes to opacity
    setInterval(() => {
      matrixBg.style.opacity = (0.05 + Math.random() * 0.04).toString();
    }, 2000);
  }
}

// Fix for Safari 100vh fix
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

// iOS-specific touch improvements
if (/iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream) {
  document.addEventListener('touchstart', function(){}, {passive: true});
}
