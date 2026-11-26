window.addEventListener('beforeinstallprompt', (event) => {
    const loginFooter = document.getElementById('login-footer');
    if (!loginFooter) {
        return;
    }

    event.preventDefault();

    const installButton = document.createElement('button');
    installButton.type = 'button';
    installButton.className = 'btn btn-link btn-sm d-block mx-auto';
    installButton.textContent = 'Install Webmail';
    installButton.addEventListener('click', async () => {
        installButton.disabled = true;
        try {
            await event.prompt();
        } catch {
            // The browser menu remains available if the prompt has expired.
        } finally {
            installButton.remove();
        }
    }, { once: true });

    loginFooter.append(installButton);
    window.addEventListener('appinstalled', () => installButton.remove(), { once: true });
}, { once: true });
