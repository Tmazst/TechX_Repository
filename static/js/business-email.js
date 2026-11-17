const emailForm = document.querySelector('[data-email-preview]');
if (emailForm) {
    const domainInput = emailForm.elements.namedItem('domain');
    const mailboxInput = emailForm.elements.namedItem('mailbox');
    const output = emailForm.querySelector('[data-email-address]');

    function renderEmailAddress() {
        const name = domainInput.value.trim().toLowerCase().replace(/\.$/, '');
        const mailbox = mailboxInput.value.trim().toLowerCase();
        const needsSuffix = emailForm.dataset.emailPreview === 'managed' && !name.endsWith('.eswtn.com');
        const domain = needsSuffix ? `${name}.eswtn.com` : name;
        output.hidden = !name || !mailbox;
        output.textContent = output.hidden ? '' : `${mailbox}@${domain}`;
    }

    emailForm.addEventListener('input', renderEmailAddress);
    renderEmailAddress();
}
