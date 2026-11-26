<?php

class techx_pwa extends rcube_plugin
{
    public $noajax = true;
    public $noframe = true;
    private $has_install_link = false;

    public function init()
    {
        $this->add_hook('template_container', [$this, 'add_install_link']);
        $this->add_hook('render_page', [$this, 'add_install_metadata']);
    }

    public function add_install_link(array $container): array
    {
        $style = match ($container['name']) {
            'loginfooter' => 'btn btn-link btn-sm d-block mx-auto',
            'taskbar' => 'download',
            default => null,
        };

        if ($style !== null) {
            $this->has_install_link = true;
            $container['content'] .= '<a class="techx-webmail-install ' . $style
                . '" href="https://techx.eswtn.com/webmail#install-webmail"'
                . ' title="Install Webmail" aria-label="Install Webmail">'
                . '<span class="inner">Install Webmail</span></a>';
        }

        return $container;
    }

    public function add_install_metadata(array $page): array
    {
        $webmail = rcmail::get_instance();
        $assets = '/static.php/plugins/techx_pwa/';

        $webmail->output->add_header('<link rel="manifest" href="' . $assets . 'manifest.json">');
        $webmail->output->add_header('<link rel="apple-touch-icon" href="' . $assets . 'icon-192.png">');
        $webmail->output->add_header('<meta name="theme-color" content="#294393">');

        if ($this->has_install_link) {
            $webmail->output->add_header('<link rel="stylesheet" href="' . $assets . 'install.css">');
            $webmail->output->add_header('<script defer src="' . $assets . 'install.js?v=2"></script>');
            $webmail->output->add_footer(<<<'HTML'
<dialog id="techx-webmail-install-help" aria-labelledby="techx-webmail-install-heading">
    <h2 id="techx-webmail-install-heading">Install Webmail</h2>
    <p>Add TechX Webmail to your desktop or home screen from this page.</p>
    <ul>
        <li><strong>Edge on Windows</strong> · More tools → Apps → Install this site as an app.</li>
        <li><strong>Chrome on a computer</strong> · Cast, save, and share → Install page as app.</li>
        <li><strong>Chrome on Android</strong> · Install and create shortcut → Install. Some versions show Add to Home screen.</li>
        <li><strong>Safari on iPhone</strong> · Share → Add to Home Screen → Add. Turn on Open as Web App if shown.</li>
    </ul>
    <form method="dialog">
        <button type="submit" class="btn btn-primary">Close</button>
    </form>
</dialog>
HTML
            );
        }

        return $page;
    }
}
