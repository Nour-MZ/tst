(function() {
  "use strict";

  // Register GSAP plugins
  gsap.registerPlugin(ScrollTrigger);

  /**
   * Apply .scrolled class to the body as the page is scrolled down
   */
  function toggleScrolled() {
    const selectBody = document.querySelector('body');
    const selectHeader = document.querySelector('#header');
    if (!selectHeader.classList.contains('scroll-up-sticky') && !selectHeader.classList.contains('sticky-top') && !selectHeader.classList.contains('fixed-top')) return;
    window.scrollY > 100 ? selectBody.classList.add('scrolled') : selectBody.classList.remove('scrolled');
  }

  document.addEventListener('scroll', toggleScrolled);
  window.addEventListener('load', toggleScrolled);

  /**
   * Mobile nav toggle
   */
  const mobileNavToggleBtn = document.querySelector('.mobile-nav-toggle');

  function mobileNavToogle() {
    document.querySelector('body').classList.toggle('mobile-nav-active');
    mobileNavToggleBtn.classList.toggle('bi-list');
    mobileNavToggleBtn.classList.toggle('bi-x');
  }
  mobileNavToggleBtn.addEventListener('click', mobileNavToogle);

  /**
   * Hide mobile nav on same-page/hash links
   */
  document.querySelectorAll('#navmenu a').forEach(navmenu => {
    navmenu.addEventListener('click', () => {
      if (document.querySelector('.mobile-nav-active')) {
        mobileNavToogle();
      }
    });
  });

  /**
   * Toggle mobile nav dropdowns
   */
  document.querySelectorAll('.navmenu .toggle-dropdown').forEach(navmenu => {
    navmenu.addEventListener('click', function(e) {
      e.preventDefault();
      this.parentNode.classList.toggle('active');
      this.parentNode.nextElementSibling.classList.toggle('dropdown-active');
      e.stopImmediatePropagation();
    });
  });

  /**
   * Preloader
   */
  // const preloader = document.querySelector('#preloader');
  // if (preloader) {
  //   window.addEventListener('load', () => {
  //     // Animate out preloader before removing
  //     gsap.to(preloader, {
  //       opacity: 0,
  //       duration: 0.5,
  //       onComplete: () => preloader.remove()
  //     });
  //   });
  // }

  if (preloader) {
    window.addEventListener('load', () => {
      preloader.remove();
    });
  }
  /**
   * Scroll top button
   */
  let scrollTop = document.querySelector('.scroll-top');

  function toggleScrollTop() {
    if (scrollTop) {
      window.scrollY > 100 ? scrollTop.classList.add('active') : scrollTop.classList.remove('active');
    }
  }
  scrollTop.addEventListener('click', (e) => {
    e.preventDefault();
    gsap.to(window, {
      scrollTo: 0,
      duration: 1,
      ease: "power2.inOut"
    });
  });

  window.addEventListener('load', toggleScrollTop);
  document.addEventListener('scroll', toggleScrollTop);

  /**
   * GSAP Animations
   */
  function initAnimations() {
    // Hero section animation
    const heroTl = gsap.timeline();
    heroTl
      .from('.hero h1', {
        y: 80,
        opacity: 0,
        duration: 1.5,
        ease: "power3.out"
      })
      .from('.hero p', {
        y: 60,
        opacity: 0,
        duration: 1.35,
        ease: "power2.out"
      }, "-=0.6")
      .fromTo('.hero .btn-get-started', {
            y: 100,
            opacity: 0,
            rotationX: -15
          },
          {
            y: 0,
            opacity: 1,
            rotationX: 0,
            duration: 0.5,
            stagger: 0.2,
            ease: "power2.out"
          }, "-=0.4")
      .from('.hero-img', {
        x: 100,
        opacity: 0,
        duration: 1.5,
        ease: "power3.out"
      }, "-=0.2");

    // Section title animations
    gsap.utils.toArray('.section-title').forEach(section => {
      gsap.from(section, {
        scrollTrigger: {
          trigger: section,
          start: "top 80%",
          toggleActions: "play none none none"
        },
        y: 50,
        opacity: 0,
        delay: 0.5,
        duration: 1.5,
        ease: "power2.out"
      });
    });

    // About section animations
    gsap.from('.about .content', {
      scrollTrigger: {
        trigger: '.about',
        start: "top 70%",
        toggleActions: "play none none none"
      },
      x: -50,
      opacity: 0,
      duration: 1.7,
      delay: 0.5,
      ease: "power2.out"
    });

    gsap.from('.about .icon-box', {
      scrollTrigger: {
        trigger: '.about',
        start: "top 60%",
        toggleActions: "play none none none"
      },
      y: 50,
      opacity: 0,
      duration: 1.2,
      stagger: 0.2,
      ease: "power2.out"
    });

    gsap.fromTo('.service-item', 
      {
        y: 100,
        opacity: 0,
        rotationX: -15
      },
      {
        y: 0,
        opacity: 1,
        rotationX: 0,
        scrollTrigger: {
          trigger: '.services',
          start: "top 70%",
          toggleActions: "play none none none"
        },
        duration: 0.8,
        stagger: 0.2,
        ease: "power2.out"
      }
    );
    
    // Features section animations with fromTo
    gsap.fromTo('.features-item', 
      {
        y: 50,
        opacity: 0,
        scale: 0.9
      },
      {
        y: 0,
        opacity: 1,
        scale: 1,
        scrollTrigger: {
          trigger: '.features',
          start: "top 70%",
          toggleActions: "play none none none"
        },
        duration: 0.6,
        stagger: 0.2,
        ease: "power2.out"
      }
    );

    // Header animation on scroll
    const header = document.getElementById('header');
    ScrollTrigger.create({
      start: "top -100",
      end: "max",
      onUpdate: (self) => {
        if (self.direction === -1) {
          header.classList.add('sticky-visible');
        } else {
          header.classList.remove('sticky-visible');
        }
      }
    });
  }

  /**
   * Initiate glightbox
   */
 
 /* const glightbox = GLightbox({
    selector: '.glightbox'
  }); */

  /**
   * Initiate Pure Counter
   */
 // new PureCounter();

  /**
   * Init swiper sliders
   */
  function initSwiper() {
    document.querySelectorAll(".init-swiper").forEach(function(swiperElement) {
      let config = JSON.parse(
        swiperElement.querySelector(".swiper-config").innerHTML.trim()
      );

      if (swiperElement.classList.contains("swiper-tab")) {
        initSwiperWithCustomPagination(swiperElement, config);
      } else {
        new Swiper(swiperElement, config);
      }
    });
  }

  window.addEventListener("load", initSwiper);

  /**
   * Init isotope layout and filters
   */
  document.querySelectorAll('.isotope-layout').forEach(function(isotopeItem) {
    let layout = isotopeItem.getAttribute('data-layout') ?? 'masonry';
    let filter = isotopeItem.getAttribute('data-default-filter') ?? '*';
    let sort = isotopeItem.getAttribute('data-sort') ?? 'original-order';

    let initIsotope;
    imagesLoaded(isotopeItem.querySelector('.isotope-container'), function() {
      initIsotope = new Isotope(isotopeItem.querySelector('.isotope-container'), {
        itemSelector: '.isotope-item',
        layoutMode: layout,
        filter: filter,
        sortBy: sort
      });
    });

    isotopeItem.querySelectorAll('.isotope-filters li').forEach(function(filters) {
      filters.addEventListener('click', function() {
        isotopeItem.querySelector('.isotope-filters .filter-active').classList.remove('filter-active');
        this.classList.add('filter-active');
        initIsotope.arrange({
          filter: this.getAttribute('data-filter')
        });
        // Refresh ScrollTrigger after isotope layout changes
        ScrollTrigger.refresh();
      }, false);
    });
  });

  /**
   * Correct scrolling position upon page load for URLs containing hash links.
   */
  window.addEventListener('load', function(e) {
    if (window.location.hash) {
      if (document.querySelector(window.location.hash)) {
        setTimeout(() => {
          let section = document.querySelector(window.location.hash);
          let scrollMarginTop = getComputedStyle(section).scrollMarginTop;
          window.scrollTo({
            top: section.offsetTop - parseInt(scrollMarginTop),
            behavior: 'smooth'
          });
        }, 100);
      }
    }
  });

  /**
   * Navmenu Scrollspy
   */
  let navmenulinks = document.querySelectorAll('.navmenu a');

  function navmenuScrollspy() {
    navmenulinks.forEach(navmenulink => {
      if (!navmenulink.hash) return;
      let section = document.querySelector(navmenulink.hash);
      if (!section) return;
      let position = window.scrollY + 200;
      if (position >= section.offsetTop && position <= (section.offsetTop + section.offsetHeight)) {
        document.querySelectorAll('.navmenu a.active').forEach(link => link.classList.remove('active'));
        navmenulink.classList.add('active');
      } else {
        navmenulink.classList.remove('active');
      }
    })
  }
  window.addEventListener('load', navmenuScrollspy);
  document.addEventListener('scroll', navmenuScrollspy);

  // Initialize everything when DOM is loaded
  window.addEventListener('DOMContentLoaded', () => {
    initAnimations();
  });

})();