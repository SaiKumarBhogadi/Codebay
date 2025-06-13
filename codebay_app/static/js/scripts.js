// Toggle mobile search
    document.querySelector('.search-icon').addEventListener('click', function() {
      const mobileSearch = document.getElementById('mobileSearch');
      if (mobileSearch.classList.contains('collapse')) {
        mobileSearch.classList.remove('collapse');
      } else {
        mobileSearch.classList.add('collapse');
      }
    });


// Hero section
// Smooth scroll for CTAs
    document.querySelectorAll('.hero-cta a').forEach(anchor => {
      anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
          target.scrollIntoView({ behavior: 'smooth' });
        }
      });
    });


// Initialize Swiper
    const swiper = new Swiper('.swiper', {
      slidesPerView: 1,
      spaceBetween: 20,
      navigation: {
        nextEl: '.swiper-button-next',
        prevEl: '.swiper-button-prev',
      },
      breakpoints: {
        768: {
          slidesPerView: 2,
          spaceBetween: 20,
        },
        1200: {
          slidesPerView: 3,
          spaceBetween: 30,
        },
      },
    });