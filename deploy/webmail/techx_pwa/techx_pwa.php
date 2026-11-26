<?php

class techx_pwa extends rcube_plugin
{
    public $noajax = true;
    public $noframe = true;

    public function init()
    {
        $this->add_hook('render_page', [$this, 'add_install_metadata']);
    }

    public function add_install_metadata(array $page): array
    {
        $webmail = rcmail::get_instance();
        $assets = '/static.php/plugins/techx_pwa/';

        $webmail->output->add_header('<link rel="manifest" href="' . $assets . 'manifest.json">');
        $webmail->output->add_header('<link rel="apple-touch-icon" href="' . $assets . 'icon-192.png">');
        $webmail->output->add_header('<meta name="theme-color" content="#294393">');

        if ($page['template'] === 'login') {
            $webmail->output->add_header('<script defer src="' . $assets . 'install.js"></script>');
        }

        return $page;
    }
}
