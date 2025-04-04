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
  'fn main() { println!("Hello, world!"); }',
  'vec![1, 2, 3].iter().sum::<i32>()',
  '"hello".chars().rev().collect::<String>()',
  'Some(42).unwrap_or_default()',
  'Option::<u8>::None.unwrap_or(0)',
  'Err::<(), _>("error").expect_err("must fail")',
  '#[derive(Debug, Clone, Copy)] struct Foo;',
  'async fn fetch() -> Result<(), Box<dyn Error>> { Ok(()) }',
  'std::collections::HashMap::<u32, u32>::new()',
  '(0..10).collect::<Vec<u32>>()',
  'futures::executor::block_on(async { 42 })',
  'serde_json::from_str::<Vec<u8>>("[]").unwrap()',
  'tokio::spawn(async { println!("async task"); })',
  'impl Default for MyType { fn default() -> Self { Self {} } }',
  'match Some(3) { Some(x) => x, None => 0 }',
  'Result::<(), &str>::Ok(()).unwrap()',
  'std::env::args().collect::<Vec<String>>()',
  'std::mem::replace(&mut val, new_val)',
  '"42".parse::<i32>().unwrap_or(0)',
  'my_vec.into_iter().map(|x| x + 1).collect::<Vec<_>>()',
  'Box::new([1, 2, 3])',
  'Rc::new("shared string".to_string())',
  'Mutex::new(Vec::<u8>::new())',
  'format!("The number is: {}", 42)',
  '"example".to_uppercase()',
  '" Rust ".trim().to_lowercase()',
  'Instant::now().elapsed().as_secs()',
  'std::thread::sleep(Duration::from_millis(10))',
  'u32::MAX.saturating_add(1)',
  'File::create("output.txt").unwrap()',
  'fs::read_to_string("input.txt").unwrap()',
  'IpAddr::from_str("127.0.0.1").unwrap()',
  '(0..).take(5).collect::<Vec<_>>()',
  '"rust,is,awesome".split(",").collect::<Vec<_>>()',
  '[0; 10].iter().enumerate().for_each(|(i, _)| println!("{}", i))',
  'Regex::new(r"\\d+").unwrap().is_match("123")',
  'chrono::Utc::now().to_rfc3339()',
  'url::Url::parse("https://rust-lang.org").unwrap()',
  'once_cell::sync::Lazy::new(|| 42)',
  '(1..=10).filter(|x| x % 2 == 0).count()',
  'str::repeat("rust", 3)',
  '"rust".chars().count()'
];

  function createMatrixChar() {
      const char = document.createElement('div');
      char.textContent = rustSnippets[Math.floor(Math.random() * rustSnippets.length)];
      char.style.position = 'fixed';
      char.style.color = 'var(--matrix-green)';
      char.style.fontSize = '10px'; 
      char.style.opacity = '0.1';
      char.style.left = (Math.random() * 100) + 'vw';
      char.style.top = '0vh';
      char.style.zIndex = '-1';
      char.style.textShadow = '0 0 3px rgba(0, 255, 65, 0.5)';
      document.body.appendChild(char);
      
      // Animate downward like in The Matrix
      let pos = 0;
      const speed = 0.01 + (Math.random() * 0.1); // Random speeds
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
