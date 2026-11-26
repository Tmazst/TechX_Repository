<?php

$config['product_name'] = 'TechX Webmail';
$config['use_https'] = true;
$config['trusted_host_patterns'] = ['webmail.eswtn.com'];
$config['enable_installer'] = false;
$config['enable_spellcheck'] = false;
$config['x_frame_options'] = 'deny';
$config['identities_level'] = 3;
$config['login_autocomplete'] = 1;
$config['login_username_filter'] = 'email';

$tls = ['verify_peer' => true, 'verify_peer_name' => true];
$config['imap_conn_options'] = ['ssl' => $tls];
$config['smtp_conn_options'] = ['ssl' => $tls];
$config['imap_timeout'] = 15;
$config['smtp_timeout'] = 15;
