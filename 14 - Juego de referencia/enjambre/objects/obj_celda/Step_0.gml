if (global.congelado > 0) exit;
flote += 0.08;
y += sin(flote) * 0.35;
vida -= 1;
if (vida <= 0) instance_destroy();
image_index = (current_time div 110) mod 4;
// Parpadea al final: avisa antes de desaparecer en vez de esfumarse sin más.
image_alpha = (vida < 90 && (vida div 6) mod 2 == 0) ? 0.35 : 1;
