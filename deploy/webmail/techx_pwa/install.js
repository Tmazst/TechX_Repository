(() => {
    const installLinks = document.querySelectorAll('.techx-webmail-install');
    const help = document.getElementById('techx-webmail-install-help');
    const storageKey = 'techx-webmail-install-intro';
    const removeInstallLinks = () => installLinks.forEach((link) => link.remove());
    const rememberIntro = () => {
        try {
            localStorage.setItem(storageKey, '1');
        } catch {
            // The dialog can still be used when browser storage is unavailable.
        }
    };

    const launchMarker = new URLSearchParams(window.location.search).get('_techx_app') === '1';
    const appMode = window.matchMedia('(display-mode: standalone), (display-mode: minimal-ui), (display-mode: window-controls-overlay)');
    const appWindowKey = 'techx-webmail-app-window';
    let appWindow = launchMarker || appMode.matches || navigator.standalone;
    try {
        // Preserve app context as Roundcube moves to URLs without the launch marker.
        appWindow = appWindow || sessionStorage.getItem(appWindowKey) === '1';
        if (appWindow) {
            sessionStorage.setItem(appWindowKey, '1');
        }
    } catch {
        // The current URL and display mode still identify the installed app.
    }

    if (appWindow) {
        rememberIntro();
        removeInstallLinks();
        return;
    }

    if (typeof help?.showModal !== 'function') {
        return;
    }

    const action = document.getElementById('techx-webmail-install-action');
    const installButton = document.getElementById('techx-webmail-install-now');
    const closeButton = help.querySelector('[type="submit"]');
    const loginForm = document.getElementById('login-form');
    const agent = navigator.userAgent;
    const appleMobile = /iPad|iPhone|iPod/.test(agent) ||
        (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
    let installPrompt;
    let seen = false;
    let signInStarted = false;
    let installed = false;

    const manualAction = () => {
        if (appleMobile) {
            return 'In Safari, tap Share → Add to Home Screen. Turn on Open as Web App if shown, then tap Add.';
        }
        if (/Android/.test(agent)) {
            return 'Open the browser menu and tap Install app or Add to Home screen.';
        }
        if (/Edg\//.test(agent)) {
            return 'Open Edge’s menu → More tools → Apps → Install this site as an app.';
        }
        if (/Chrome|Chromium/.test(agent)) {
            return 'Open Chrome’s menu → Cast, save, and share → Install page as app.';
        }
        if (/Macintosh.*Version\/.*Safari\//.test(agent)) {
            return 'In Safari, choose File → Add to Dock.';
        }
        return 'Open your browser’s menu and look for its option to install this page as an app.';
    };

    const updateDialog = () => {
        const nativeAvailable = Boolean(installPrompt);
        action.textContent = nativeAvailable
            ? 'Open your inbox from your home screen or desktop in one tap.'
            : manualAction();
        installButton.hidden = !nativeAvailable;
        closeButton.textContent = nativeAvailable ? 'Not now' : 'Got it';
    };

    const showDialog = () => {
        updateDialog();
        if (!help.open) {
            help.showModal();
        }
        seen = true;
        rememberIntro();
    };

    try {
        seen = localStorage.getItem(storageKey) === '1';
    } catch {
        // Fall back to tracking the prompt for this page.
    }

    const offerOnSignIn = () => {
        if (loginForm) {
            window.setTimeout(() => {
                if (!seen && !signInStarted && !installed && document.visibilityState === 'visible') {
                    showDialog();
                }
            }, 4000);
        }
    };

    for (const eventName of ['input', 'submit']) {
        loginForm?.addEventListener(eventName, () => { signInStarted = true; }, { once: true });
    }

    window.addEventListener('beforeinstallprompt', (event) => {
        event.preventDefault();
        installPrompt = event;
        if (help.open) {
            updateDialog();
        }
        offerOnSignIn();
    });

    if (appleMobile) {
        offerOnSignIn();
    }

    window.addEventListener('appinstalled', () => {
        installed = true;
        rememberIntro();
        removeInstallLinks();
        if (help.open) {
            help.close();
        }
    }, { once: true });

    for (const link of installLinks) {
        link.addEventListener('click', (event) => {
            event.preventDefault();
            showDialog();
        });
    }

    installButton.addEventListener('click', async () => {
        if (!installPrompt) {
            return;
        }
        const prompt = installPrompt;
        installPrompt = undefined;
        help.close();
        try {
            await prompt.prompt();
        } catch {
            if (!installed) {
                showDialog();
            }
        }
    });
})();
