<?php
/**
 * SÁM digital · envío del formulario de contacto (/contacto/).
 *
 * Recibe un POST (FormData) de assets/js/pages.js, valida, filtra spam y envía el mensaje por correo.
 * Responde siempre JSON: {"ok":true} o {"ok":false,"error":"..."}; si falla, la página ofrece WhatsApp como respaldo.
 *
 * Antispam: campo trampa oculto (sitio_web), tiempo mínimo desde que se abrió la página (t, en ms),
 * mismo origen y máximo de envíos por hora y por IP.
 */
declare(strict_types=1);

// Destino codificado en base64 solo para que el repositorio público no exponga el correo a los rastreadores.
const TO_B64 = 'c2FtZGlnaXRhbG1hcmtAZ21haWwuY29t';
const FROM = 'info@samdigital.com.co';       // buzón del dominio: mejora la entrega frente al spam
const ALLOWED_HOST = '/(^|\.)samdigital\.com\.co$/i';
const MIN_MS = 2000;                          // una persona tarda más que esto en llenar el formulario
const MAX_MS = 86400000;                      // 24 h
const MAX_PER_HOUR = 5;

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
header('X-Content-Type-Options: nosniff');

function reply(int $code, array $data): void
{
    http_response_code($code);
    echo json_encode($data, JSON_UNESCAPED_UNICODE);
    exit;
}

function fail(int $code, string $msg): void
{
    reply($code, ['ok' => false, 'error' => $msg]);
}

/** Texto limpio: sin caracteres de control, sin saltos de línea (salvo $multi) y con largo máximo. */
function clean($v, int $max, bool $multi = false): string
{
    $s = is_string($v) ? str_replace("\0", '', $v) : '';
    if ($multi) {
        $s = preg_replace('/[^\P{C}\n]+/u', '', str_replace("\r\n", "\n", $s));
    } else {
        $s = preg_replace('/[\p{C}\s]+/u', ' ', $s);
    }
    $s = trim((string) $s);
    return function_exists('mb_substr') ? mb_substr($s, 0, $max) : substr($s, 0, $max);
}

/** Cabecera con acentos (RFC 2047). */
function enc(string $s): string
{
    if (function_exists('mb_encode_mimeheader')) {
        return mb_encode_mimeheader($s, 'UTF-8', 'B', "\r\n");
    }
    return '=?UTF-8?B?' . base64_encode($s) . '?=';
}

function too_many(string $ip): bool
{
    $file = rtrim(sys_get_temp_dir(), '/\\') . '/samdigital_form_' . md5($ip) . '.json';
    $now = time();
    $hits = [];
    if (is_file($file)) {
        $old = json_decode((string) @file_get_contents($file), true);
        if (is_array($old)) {
            foreach ($old as $t) {
                if (is_int($t) && $t > $now - 3600) {
                    $hits[] = $t;
                }
            }
        }
    }
    if (count($hits) >= MAX_PER_HOUR) {
        return true;
    }
    $hits[] = $now;
    @file_put_contents($file, json_encode($hits), LOCK_EX);
    return false;
}

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    header('Allow: POST');
    fail(405, 'Método no permitido.');
}

// Solo desde el propio sitio
$from = $_SERVER['HTTP_ORIGIN'] ?? ($_SERVER['HTTP_REFERER'] ?? '');
if ($from !== '') {
    $host = parse_url($from, PHP_URL_HOST);
    if (!is_string($host) || !preg_match(ALLOWED_HOST, $host)) {
        fail(403, 'Origen no permitido.');
    }
}

// Campo trampa: los bots lo llenan; se les responde "ok" sin enviar nada
if (clean($_POST['sitio_web'] ?? '', 200) !== '') {
    reply(200, ['ok' => true]);
}

$ms = (int) ($_POST['t'] ?? 0);
if ($ms < MIN_MS || $ms > MAX_MS) {
    fail(400, 'Espera un momento e inténtalo de nuevo.');
}

$nombre = clean($_POST['nombre'] ?? '', 120);
$email = clean($_POST['email'] ?? '', 254);
$tel = clean($_POST['telefono'] ?? '', 30);
$empresa = clean($_POST['empresa'] ?? '', 120);
$mensaje = clean($_POST['mensaje'] ?? '', 3000, true);

if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    fail(400, 'Escribe un correo electrónico válido.');
}
if (!preg_match('/^[0-9+()\s.\-]{7,30}$/', $tel) || preg_match_all('/\d/', $tel) < 7) {
    fail(400, 'Escribe un teléfono válido.');
}
if (empty($_POST['acepto'])) {
    fail(400, 'Debes aceptar el Aviso Legal y la Política de Privacidad.');
}

$ip = (string) ($_SERVER['REMOTE_ADDR'] ?? 'desconocida');
if (too_many($ip)) {
    fail(429, 'Has enviado varios mensajes seguidos. Inténtalo más tarde.');
}

$corto = function_exists('mb_substr') ? mb_substr($nombre, 0, 40) : substr($nombre, 0, 40);
$asunto = enc('Nuevo mensaje desde samdigital.com.co' . ($corto !== '' ? ' · ' . $corto : ''));
$cuerpo = "Nuevo mensaje desde el formulario de contacto de samdigital.com.co\n\n"
    . 'Nombre:   ' . ($nombre !== '' ? $nombre : '(sin nombre)') . "\n"
    . 'Correo:   ' . $email . "\n"
    . 'Teléfono: ' . $tel . "\n"
    . 'Empresa:  ' . ($empresa !== '' ? $empresa : '(no indicada)') . "\n\n"
    . "Mensaje:\n" . ($mensaje !== '' ? $mensaje : '(sin mensaje)') . "\n\n"
    . "--\n"
    . 'Enviado el ' . date('Y-m-d H:i:s') . ' (hora del servidor) · IP ' . $ip . "\n"
    . "Puedes responder directamente a este correo: va al visitante.\n";

$cabeceras = implode("\r\n", [
    'From: ' . enc('SÁM digital') . ' <' . FROM . '>',
    'Reply-To: ' . $email,
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=UTF-8',
    'Content-Transfer-Encoding: 8bit',
    'X-Mailer: samdigital-contact-form',
]);

$to = base64_decode(TO_B64);
$ok = @mail($to, $asunto, $cuerpo, $cabeceras, '-f' . FROM);
if (!$ok) {
    $ok = @mail($to, $asunto, $cuerpo, $cabeceras);   // algunos servidores no admiten el parámetro -f
}
if (!$ok) {
    error_log('samdigital contact form: mail() falló');
    fail(500, 'No pudimos enviar tu mensaje en este momento.');
}

reply(200, ['ok' => true]);
