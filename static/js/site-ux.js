(() => {
    const menuButton = document.querySelector('.nav-toggle');
    const menu = document.querySelector('.nav-links');
    const services = document.querySelector('.nav-dropdown');
    const servicesButton = document.querySelector('.nav-dropdown__toggle');

    const closeServices = () => {
        if (!services || !servicesButton) return;
        services.classList.remove('is-open');
        servicesButton.setAttribute('aria-expanded', 'false');
    };

    if (menuButton && menu) {
        menuButton.addEventListener('click', () => {
            const open = menu.classList.toggle('is-open');
            menuButton.setAttribute('aria-expanded', String(open));
            if (!open) closeServices();
        });
        menu.querySelectorAll('a').forEach((link) => link.addEventListener('click', () => {
            menu.classList.remove('is-open');
            menuButton.setAttribute('aria-expanded', 'false');
            closeServices();
        }));
    }

    if (services && servicesButton) {
        servicesButton.addEventListener('click', () => {
            const open = services.classList.toggle('is-open');
            servicesButton.setAttribute('aria-expanded', String(open));
        });
        document.addEventListener('click', (event) => {
            if (!services.contains(event.target)) closeServices();
        });
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') {
                closeServices();
                servicesButton.focus();
            }
        });
    }

    const facebookSection = document.querySelector('[data-facebook-portfolio]');
    if (!facebookSection) return;

    let facebookStarted = false;
    const loadFacebook = () => {
        if (facebookStarted || document.getElementById('facebook-jssdk')) return;
        facebookStarted = true;
        const script = document.createElement('script');
        script.id = 'facebook-jssdk';
        script.async = true;
        script.defer = true;
        script.crossOrigin = 'anonymous';
        script.src = 'https://connect.facebook.net/en_US/sdk.js#xfbml=1&version=v25.0&appId=427392679808082';
        document.body.appendChild(script);
    };

    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            if (entries.some((entry) => entry.isIntersecting)) {
                loadFacebook();
                observer.disconnect();
            }
        }, { rootMargin: '350px 0px' });
        observer.observe(facebookSection);
    } else {
        loadFacebook();
    }

    const moreButton = facebookSection.querySelector('.facebook-work-more');
    const grid = facebookSection.querySelector('.facebook-work-grid');
    if (moreButton && grid) {
        moreButton.addEventListener('click', () => {
            grid.classList.add('is-expanded');
            moreButton.setAttribute('aria-expanded', 'true');
            grid.querySelectorAll('.fb-post-deferred').forEach((post) => {
                post.classList.replace('fb-post-deferred', 'fb-post');
            });
            loadFacebook();
            if (window.FB && window.FB.XFBML) window.FB.XFBML.parse(grid);
        });
    }
})();