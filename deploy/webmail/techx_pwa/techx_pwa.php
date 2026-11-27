<?php

class techx_pwa extends rcube_plugin
{
    public $noajax = true;
    public $noframe = true;
    private $has_install_link = false;

    public function init()
    {
        $this->add_hook('ready', [$this, 'open_inbox_from_root']);
        $this->add_hook('template_container', [$this, 'add_install_link']);
        $this->add_hook('render_page', [$this, 'add_install_metadata']);
    }

    public function open_inbox_from_root(array $request): array
    {
        // Roundcube runs the ready hook after validating the mailbox session.
        // Older app icons still open the bare root.
        if ($request['task'] === 'mail' && $request['action'] === ''
            && ($_SERVER['REQUEST_METHOD'] ?? '') === 'GET'
            && ($_SERVER['REQUEST_URI'] ?? '') === '/') {
            rcmail::get_instance()->output->redirect(['_task' => 'mail', '_mbox' => 'INBOX'], 0);
        }

        return $request;
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

        $webmail->output->add_header('<link rel="manifest" href="' . $assets . 'manifest.json?v=2">');
        $webmail->output->add_header('<link rel="apple-touch-icon" href="' . $assets . 'icon-192.png">');
        $webmail->output->add_header('<meta name="theme-color" content="#294393">');

        if ($this->has_install_link) {
            $webmail->output->add_header('<link rel="stylesheet" href="' . $assets . 'install.css?v=4">');
            $webmail->output->add_header('<script defer src="' . $assets . 'install.js?v=4"></script>');
            $webmail->output->add_footer(<<<'HTML'
<dialog id="techx-webmail-install-help" aria-labelledby="techx-webmail-install-heading" aria-describedby="techx-webmail-install-action">
    <img src="/static.php/plugins/techx_pwa/icon-192.png" width="64" height="64" alt="">
    <h2 id="techx-webmail-install-heading">Install TechX Webmail</h2>
    <p id="techx-webmail-install-action"></p>
    <form method="dialog" class="techx-install-actions">
        <button type="submit" class="btn btn-secondary" autofocus>Got it</button>
        <button type="button" class="btn btn-primary" id="techx-webmail-install-now" hidden>Install</button>
    </form>
</dialog>
HTML
            );
        }

        return $page;
    }
}
