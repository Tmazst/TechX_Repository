(() => {
    const installLinks = document.querySelectorAll('.techx-webmail-install');
    const help = document.getElementById('techx-webmail-install-help');
    const removeInstallLinks = () => installLinks.forEach((link) => link.remove());

    if (window.matchMedia('(display-mode: standalone)').matches || navigator.standalone) {
        removeInstallLinks();
        return;
    }

    let installPrompt;
    window.addEventListener('beforeinstallprompt', (event) => {
        event.preventDefault();
        installPrompt = event;
    });

    window.addEventListener('appinstalled', removeInstallLinks, { once: true });

    for (const link of installLinks) {
        link.addEventListener('click', async (event) => {
            if (!installPrompt && typeof help?.showModal !== 'function') {
                return;
            }

            event.preventDefault();
            if (installPrompt) {
                const prompt = installPrompt;
                installPrompt = undefined;
                try {
                    await prompt.prompt();
                    return;
                } catch {
                    // An expired browser prompt can still fall back to the install steps.
                }
            }

            if (typeof help?.showModal === 'function') {
                if (!help.open) {
                    help.showModal();
                }
            } else {
                window.location.assign(link.href);
            }
        });
    }
})();
