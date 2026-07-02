<?php
declare(strict_types=1);

return [
    'ITTEMMALL_ORDER_STORE_PATH' => '/absolute/private/path/ittemmall-orders.json',
    'ITTEMMALL_TRACK_LOG_PATH' => '/absolute/private/path/ittemmall-track-events.jsonl',
    // Optional. Leave empty to derive from ITTEMMALL_ORDER_STORE_PATH at runtime.
    'ITTEMMALL_RATE_LIMIT_PATH' => '',
    'ITTEMMALL_TRACK_SALT' => 'replace-with-a-long-random-string',
    'ITTEMMALL_ADMIN_TOKEN' => 'replace-with-a-long-random-admin-token',
    'ITTEMMALL_SITE_BASE_URL' => 'https://ittemmall.com',
    'ITTEMMALL_NOTIFY_ENABLED' => '1',
    'ITTEMMALL_NOTIFY_EMAIL' => 'staysiaofficial@gmail.com',
    'ITTEMMALL_NOTIFY_FROM' => 'no-reply@ittemmall.com',
    'TOSS_PAYMENTS_MID' => 'issued-toss-mid',
    'TOSS_PAYMENTS_CLIENT_KEY' => 'issued-public-client-key',
    'TOSS_PAYMENTS_SECRET_KEY' => 'issued-server-only-secret-key',
    'TOSS_PAYMENTS_PAYMENT_WIDGET_VARIANT_KEY' => 'DEFAULT',
    'TOSS_PAYMENTS_APPROVE_ENABLED' => '0',
    'NAVER_PAY_CLIENT_ID' => 'issued-public-client-id',
    'NAVER_PAY_CHAIN_ID' => 'issued-chain-id',
    'NAVER_PAY_CLIENT_SECRET' => 'issued-server-only-client-secret',
    'NAVER_PAY_MODE' => 'development',
    // Optional. Leave empty unless Naver Pay gives you a merchant-specific approval URL.
    'NAVER_PAY_APPROVE_URL' => '',
    'NAVER_PAY_APPROVE_ENABLED' => '0',
    // Optional. Leave empty unless Naver Pay gives you a merchant-specific cancel URL.
    'NAVER_PAY_CANCEL_URL' => '',
    'NAVER_PAY_CANCEL_ENABLED' => '0',
];
