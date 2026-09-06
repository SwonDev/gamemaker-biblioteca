# 11 · Vectores, matrices y ángulos en GML

> Referencia exhaustiva de **GameMaker LTS 2026** (IDE 2026.0.0.16 · Runtime 2026.0.0.23).

> Todas las firmas han sido verificadas contra el manual oficial LTS.

---

## El sistema de coordenadas de GameMaker

Antes de usar nada de esta página conviene tener claro el sistema de coordenadas,
porque **no es el habitual en matemáticas**:

- El eje **X** positivo apunta a la **derecha**.
- El eje **Y** positivo apunta hacia **abajo** (al revés que en el plano cartesiano clásico).
- El eje **Z** positivo apunta **hacia el observador** (fuera de la pantalla).
- Los ángulos crecen en sentido **antihorario** en pantalla, precisamente porque el eje Y
  está invertido.

```gml
// Mover 100 px en la dirección de la instancia
x += lengthdir_x(100, direction);
y += lengthdir_y(100, direction);

// Rotar suavemente hacia el ratón, sin saltos de 359° -> 0°
var _dir = point_direction(x, y, mouse_x, mouse_y);
image_angle += clamp(angle_difference(_dir, image_angle), -4, 4);
```

---

## Vectores: qué hay y qué no hay en 2026

GameMaker **no tiene un tipo de datos vectorial** dedicado. Las funciones de esta sección
trabajan con componentes sueltos (`x1, y1, x2, y2`) y las matrices se almacenan en
**arrays de 16 elementos en orden column-major**.

```gml
// Matriz 4x4 en orden column-major
matriz =
[
    1, 0, 0, 0,   // columna 1
    0, 1, 0, 0,   // columna 2
    0, 0, 1, 0,   // columna 3
    0, 0, 0, 1    // columna 4
];
```

Si necesitas álgebra vectorial más seria (normalizar, cruz, suma de vectores…), la
convención habitual es usar **structs** con `x` e `y` y escribirte las operaciones, o bien
apoyarte en las funciones de la familia `dot_product`.

---

## Trigonometría


### `sin(val)`

- **Devuelve:** Real
- **Qué hace:** Seno del ángulo `val`, expresado en **radianes**.
- **Ejemplo:**

```gml
val = sin(pi/2);
```

- **Notas:** Recuerda que `sin` trabaja en radianes. Si tienes grados, usa `dsin` o convierte antes con `degtorad`.

### `cos(val)`

- **Devuelve:** Real
- **Qué hace:** Coseno del ángulo `val`, expresado en **radianes**.
- **Ejemplo:**

```gml
val = cos(0);
```

- **Notas:** Recuerda que `cos` trabaja en radianes. Si tienes grados, usa `dcos` o convierte antes con `degtorad`.

### `tan(val)`

- **Devuelve:** Real
- **Qué hace:** Tangente del ángulo `val`, expresado en **radianes**.
- **Ejemplo:**

```gml
val = tan(pi);
```

- **Notas:** Recuerda que `tan` trabaja en radianes. Si tienes grados, usa `dtan` o convierte antes con `degtorad`.

### `dsin(val)`

- **Devuelve:** Real
- **Qué hace:** Seno del ángulo `val`, expresado en **grados**. Es la versión en grados de `sin`.
- **Ejemplo:**

```gml
val = dsin(90);
```

### `dcos(val)`

- **Devuelve:** Real
- **Qué hace:** Coseno del ángulo `val`, expresado en **grados**. Es la versión en grados de `cos`.
- **Ejemplo:**

```gml
val = dcos(45);
```

### `dtan(val)`

- **Devuelve:** Real
- **Qué hace:** Tangente del ángulo `val`, expresado en **grados**. Es la versión en grados de `tan`.
- **Ejemplo:**

```gml
val = dtan(45);
```

---

## Funciones inversas (arco)


### `arcsin(x)`

- **Devuelve:** Real
- **Qué hace:** Arco seno: devuelve el ángulo en **radianes** cuyo seno es `x`. El resultado está entre `-pi/2` y `pi/2`.
- **Ejemplo:**

```gml
val = arcsin(0);
```

### `arccos(x)`

- **Devuelve:** Real
- **Qué hace:** Arco coseno: devuelve el ángulo en **radianes** cuyo coseno es `x`. El resultado está entre `0` y `pi`.
- **Ejemplo:**

```gml
val = arccos(0);
```

### `arctan(x)`

- **Devuelve:** Real
- **Qué hace:** Arco tangente: devuelve el ángulo en **radianes** cuya tangente es `x`. El resultado está entre `-pi/2` y `pi/2`.
- **Ejemplo:**

```gml
val = arctan(0);
```

### `arctan2(y, x)`

- **Devuelve:** Real
- **Qué hace:** Arco tangente de `y / x` usando los **signos** de ambos para determinar el cuadrante correcto. Devuelve el ángulo en **radianes** entre `-pi` y `pi`. Es la función que usarás casi siempre para calcular direcciones.
- **Ejemplo:**

```gml
val = arctan2(1, 1);
```

- **Notas:** Cuidado con el orden de los argumentos: es `arctan2(y, x)`, no `(x, y)`. Es el orden estándar de C y del resto de lenguajes.

### `darcsin(x)`

- **Devuelve:** Real
- **Qué hace:** Arco seno en **grados**. Versión en grados de `arcsin`.
- **Ejemplo:**

```gml
val = darcsin(-1);
```

### `darccos(val)`

- **Devuelve:** Real
- **Qué hace:** Arco coseno en **grados**. Versión en grados de `arccos`.
- **Ejemplo:**

```gml
val = arccos(-1);
```

### `darctan(x)`

- **Devuelve:** Real
- **Qué hace:** Arco tangente en **grados**. Versión en grados de `arctan`.
- **Ejemplo:**

```gml
val = darctan(1);
```

### `darctan2(y, x)`

- **Devuelve:** Real
- **Qué hace:** Arco tangente de `y / x` con corrección de cuadrante, en **grados**. Es la más usada en juegos 2D porque `direction` e `image_angle` trabajan en grados.
- **Ejemplo:**

```gml
val = darctan2(1, 1);
```

- **Notas:** Igual que `arctan2` pero en grados, así que encaja directamente con `direction` e `image_angle`.

---

## Conversión de unidades angulares


### `degtorad(deg)`

- **Devuelve:** Real
- **Qué hace:** Convierte un ángulo de **grados a radianes**.
- **Ejemplo:**

```gml
val = degtorad(90);
```

### `radtodeg(rad)`

- **Devuelve:** Real
- **Qué hace:** Convierte un ángulo de **radianes a grados**.
- **Ejemplo:**

```gml
val = radtodeg(pi);
```

---

## Ángulos y dirección


### `point_direction(x1, y1, x2, y2)`

- **Devuelve:** Real
- **Qué hace:** Devuelve el ángulo en **grados** desde el punto `(x1, y1)` hasta el punto `(x2, y2)`. El `0` grados apunta a la derecha y el ángulo crece en sentido **antihorario** en el sistema de coordenadas de GameMaker.
- **Ejemplo:**

```gml
var _nearest = instance_nearest(x, y, obj_enemy);
var _ex = _nearest.x;
var _ey = _nearest.y;
with (instance_create_layer(x, y, "Bullets", obj_missile))
{
    direction = point_direction(x, y, _ex, _ey);
}
```

- **Notas:** Los grados en GameMaker crecen en sentido antihorario porque el eje Y apunta hacia abajo.

### `angle_difference(dest, src)`

- **Devuelve:** Real
- **Qué hace:** Devuelve la **diferencia más corta** entre dos ángulos (`dest - src`), normalizada al rango `-180`…`180` grados. Es la forma correcta de comparar o interpolar ángulos sin que el salto de 359° a 0° rompa el cálculo.
- **Ejemplo:**

```gml
var _dir = point_direction(x, y, mouse_x, mouse_y);
var _diff = angle_difference(_dir, image_angle);
image_angle += _diff * 0.1;
```

- **Notas:** Imprescindible para rotar suavemente hacia un objetivo: `image_angle += clamp(angle_difference(dir, image_angle), -5, 5);`

---

## Distancia


### `point_distance(x1, y1, x2, y2)`

- **Devuelve:** Real
- **Qué hace:** Devuelve la distancia euclidiana entre los puntos `(x1, y1)` y `(x2, y2)`.
- **Ejemplo:**

```gml
var _nearest= instance_nearest(x, y, obj_enemy);
if (_nearest != noone)
{
    if (point_distance(x, y, _nearest.x, _nearest.y) < 200)
    {
        instance_create_layer(x, y, "Bullets", obj_missile);
    }
}
```

### `point_distance_3d(x1, y1, z1, x2, y2, z2)`

- **Devuelve:** Real
- **Qué hace:** Devuelve la distancia euclidiana en 3D entre los puntos `(x1, y1, z1)` y `(x2, y2, z2)`.
- **Ejemplo:**

```gml
var _nearest= instance_nearest(x, y, obj_enemy);
if (_nearest != noone)
{
    if (point_distance_3d(x, y, z, _nearest.x, _nearest.y, _nearest.z) < 200)
    {
        instance_create_layer(x, y, "Bullets", obj_missile);
    }
}
```

### `distance_to_object(obj)`

- **Devuelve:** Real
- **Qué hace:** Devuelve la distancia desde el borde de la máscara de colisión de la instancia actual hasta el borde de la máscara del objeto indicado, o `100000` si no hay colisión. Debe llamarse desde dentro de una instancia.
- **Ejemplo:**

```gml
if (distance_to_object(obj_player) < range)
{
    can_shoot = true;
}
```

- **Notas:** Devuelve `100000` cuando no hay colisión, no `-1`. Comprueba ese centinela antes de usar el valor.

### `distance_to_point(x, y)`

- **Devuelve:** Real
- **Qué hace:** Devuelve la distancia desde el borde de la máscara de colisión de la instancia actual hasta el punto `(x, y)`. Devuelve `0` si el punto está dentro de la máscara. Debe llamarse desde dentro de una instancia.
- **Ejemplo:**

```gml
if (distance_to_point(obj_player.x, obj_player.y) < range)
{
    can_shoot = true;
}
```

- **Notas:** Usa la máscara de colión de la instancia, no su origen, así que el resultado depende del sprite asignado.

---

## Descomposición de vectores


### `lengthdir_x(len, dir)`

- **Devuelve:** Real
- **Qué hace:** Devuelve el **componente horizontal** de un vector de longitud `len` y dirección `dir` (en grados). Combinada con `lengthdir_y` es la forma canónica de mover algo hacia una dirección.
- **Ejemplo:**

```gml
var _xx = x + lengthdir_x(64, image_angle);
var _yy = y + lengthdir_y(64, image_angle);
instance_create_layer(_xx, _yy, "Bullets", obj_bullet);
```

### `lengthdir_y(len, dir)`

- **Devuelve:** Real
- **Qué hace:** Devuelve el **componente vertical** de un vector de longitud `len` y dirección `dir` (en grados). Recuerda que en GameMaker el eje Y crece **hacia abajo**.
- **Ejemplo:**

```gml
var _xx = x + lengthdir_x(64, image_angle);
var _yy = y + lengthdir_y(64, image_angle);
instance_create_layer(_xx, _yy, "Bullets", obj_bullet);
```

- **Notas:** En GameMaker el eje Y apunta hacia abajo, así que `lengthdir_y(len, 90)` devuelve un valor **negativo**.

---

## Producto escalar (dot product)


### `dot_product(x1, y1, x2, y2)`

- **Devuelve:** Real
- **Qué hace:** Producto escalar de dos vectores 2D. El resultado es `|a| * |b| * cos(ángulo)`. Si ambos vectores están normalizados, equivale al coseno del ángulo que los separa: `1` si apuntan igual, `0` si son perpendiculares, `-1` si son opuestos.
- **Ejemplo:**

```gml
var _x1, _y1, _x2, _y2;
_x1 = lengthdir_x(1, image_angle);
_y1 = lengthdir_y(1, image_angle);
_x2 = obj_player.x - x;
_y2 = obj_player.y - y;
if (dot_product(_x1, _y1, _x2, _y2) > 0)
{
    seen = true;
}
else
{
    seen = false;
}
```

### `dot_product_3d(x1, y1, z1, x2, y2, z2)`

- **Devuelve:** Real
- **Qué hace:** Producto escalar de dos vectores 3D construidos a partir de los puntos `(x1, y1, z1)` y `(x2, y2, z2)`.
- **Ejemplo:**

```gml
var _x1, _y1, _z1, _x2, _y2, _z2;
_x1 = 0;
_y1 = 1;
_z1 = 0;
_x2 = obj_player.x - x;
_y2 = obj_player.y - y;
_z2 = obj_player.z - z;
if (dot_product_3d(_x1, _y1, _z1, _x2, _y2, _z2) > 0)
{
    above = true;
}
else
{
    above = false;
}
```

### `dot_product_normalised(x1, y1, x2, y2)`

- **Devuelve:** Real
- **Qué hace:** Producto escalar de dos vectores 2D **normalizados internamente**. Devuelve directamente el coseno del ángulo entre ambos, en el rango `-1`…`1`, sin que tengas que normalizarlos tú.
- **Ejemplo:**

```gml
var _x1 = lengthdir_x(1, image_angle);
var _y1 = lengthdir_y(1, image_angle);
var _x2 = obj_player.x - x;
var _y2 = obj_player.y - y;
if (dot_product_normalised(_x1, _y1, _x2, _y2) > 0)
{
    seen = true;
}
else
{
    seen = false;
}
```

- **Notas:** Al normalizar internamente, pierdes la información de longitud: solo obtienes el ángulo relativo.

### `dot_product_3d_normalised(x1, y1, z1, x2, y2, z2)`

- **Devuelve:** Real
- **Qué hace:** Producto escalar de dos vectores 3D **normalizados internamente**. Devuelve el coseno del ángulo entre ambos en el rango `-1`…`1`.
- **Ejemplo:**

```gml
var _x1 = 0;
var _y1 = 1;
var _z1 = 0;
var _x2 = obj_player.x - x;
var _y2 = obj_player.y - y;
var _z2 = obj_player.z - z;
if (dot_product_3d_normalised(_x1, _y1, _z1, _x2, _y2, _z2) > 0)
{
    above = true;
}
else
{
    above = false;
}
```

---

## Matrices

Una **matriz** es una colección de números dispuesta en filas y columnas.
En GameMaker se usan sobre todo para transformar lo que se dibuja: pasar cada vértice
del espacio local al espacio de mundo, de ahí al de la cámara y finalmente a la pantalla.

```
Transformar por matrix_world -> Transformar por matrix_view -> Transformar por matrix_projection
```

> **Nota:** las matrices **no** tienen su propio tipo de datos: son arrays de 16 elementos
> almacenados en orden **column-major**.

### Transformaciones jerárquicas con la pila

La pila de matrices permite encadenar transformaciones de forma elegante, lo que resulta
ideal para animación esquelética o para estructuras padre-hijo:

```gml
matrix_stack_clear();
var _m = matrix_build(x, y, 0, 0, 0, direction, 1, 1, 1);
matrix_stack_push(_m);
matrix_set(matrix_world, matrix_stack_top());
draw_sprite(sprite_index, 0, 0, 0);
matrix_stack_pop();
matrix_set(matrix_world, matrix_build_identity());
```


### Matrices internas de dibujo


### `matrix_get(type, [result_matrix])`

- **Devuelve:** Matrix (array de 16 elementos)
- **Qué hace:** Devuelve una copia de una de las matrices internas que GameMaker usa para dibujar (`matrix_world`, `matrix_view` o `matrix_projection`).
- **Ejemplo:**

```gml
v_array = matrix_get(matrix_view);
```

- **Notas:** Las matrices son arrays de 16 elementos en orden **column-major**: los 4 primeros son la columna 1, los siguientes la columna 2, y así sucesivamente.

### `matrix_set(type, matrix)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Establece una de las matrices internas de dibujo (`matrix_world`, `matrix_view` o `matrix_projection`) a partir de un array de 16 elementos.
- **Ejemplo:**

*Draw Event*


```gml
var _world_matrix = matrix_build(x, y, 0, 0, 0, image_angle, 1, 1, 1);
matrix_set(matrix_world, _world_matrix);
draw_sprite(sprite_index, 0, 0, 0);
matrix_set(matrix_world, matrix_build_identity());
```

---

### Álgebra de matrices


### `matrix_multiply(matrix1, matrix2, [result_matrix])`

- **Devuelve:** Matrix (array de 16 elementos)
- **Qué hace:** Multiplica dos matrices y devuelve la matriz resultante. **El orden importa**: no es lo mismo `A * B` que `B * A`. Para concatenar transformaciones, multiplica en el orden inverso al que quieres que se apliquen.
- **Ejemplo:**

*Ejemplo 1: uso básico*


```gml
var _v_matrix = matrix_get(matrix_view);
var _new_matrix = matrix_multiply(_v_matrix, my_matrix);
matrix_set(matrix_view, _new_matrix);
```

*Ejemplo 2: usar una matriz existente para guardar el resultado*


*Create Event*


```gml
mat_result = matrix_build_identity();

mat_one = matrix_build(0, 0, 10, 0, 0, 90, 1, 1, 1);
mat_two = matrix_build(10, 0, 4, 30, 45, 0, 1, 1, 1);
```

*Step Event*


```gml
mat_one[12] = 100 + lengthdir_x(100, current_time/100);
matrix_multiply(mat_one, mat_two, mat_result);
```

*Ejemplo 3: dibujar un rectángulo relativo a un círculo*


*Draw Event*


```gml
var _mat_child_local = matrix_build(100, 100, 0, 0, 0, current_time/2, 1, 1, 1);
var _mat_parent_global = matrix_build(x, y, 0, 0, 0, current_time/12 + dsin(current_time/4) * 30, 1, 1, 1);
var _mat_child_global = matrix_multiply(_mat_child_local, _mat_parent_global);

matrix_set(matrix_world, _mat_parent_global);
draw_circle_color(0, 0, 100, c_blue, c_blue, false);
matrix_set(matrix_world, _mat_child_global);
draw_rectangle_color(-10, -10, 10, 10, c_red, c_red, c_red, c_red, false);
matrix_set(matrix_world, matrix_build_identity());
```

- **Notas:** Para aplicar «primero escala, luego rota, y por último traslada», multiplica en orden inverso: traslación × rotación × escala.

### `matrix_inverse(matrix, [result_matrix])`

- **Devuelve:** Matrix (or undefined in case a new matrix is returned and the matrix doesn't have an inverse)
- **Qué hace:** Devuelve la **matriz inversa** de la matriz dada. Al multiplicar una matriz por su inversa se obtiene la matriz identidad, lo que permite «deshacer» las transformaciones aplicadas. No todas las matrices tienen inversa.
- **Ejemplo:**

```gml
transform = matrix_build(x, y, 0, 90, 0, direction, 1, 1, 1);
transform_inverse = matrix_inverse(transform);

transform_product = matrix_multiply(transform, transform_inverse);

show_debug_message(transform);
show_debug_message(transform_inverse);
show_debug_message(transform_product);
```

- **Notas:** Si la matriz no tiene inversa (determinante cero), el resultado es indefinido. Comprueba antes si no estás seguro.

### `matrix_transform_vertex(matrix, x, y, z, [w], [result_array])`

- **Devuelve:** Array (3 elements (x, y and z are passed) or 4 elements (x, y, z and w are passed))
- **Qué hace:** Transforma un vértice `(x, y, z)` por la matriz dada y devuelve un array con las coordenadas transformadas. Es la forma de calcular dónde acaba un punto tras aplicar una transformación.
- **Ejemplo:**

```gml
t_matrix = matrix_build(0, 0, 0, 0, 90, 0, 1, 2, 1);
new_xyz = matrix_transform_vertex(t_matrix, x, y, z);
```

---

### Construcción de matrices


### `matrix_build(x, y, z, xrotation, yrotation, zrotation, xscale, yscale, zscale, [result_matrix])`

- **Devuelve:** Matrix (array de 16 elementos)
- **Qué hace:** Construye una **matriz de transformación** combinando traslación `(x, y, z)`, rotación en los tres ejes (en grados, orden YXZ) y escalado `(xscale, yscale, zscale)`. Es la función base para transformar lo que dibujas.
- **Ejemplo:**

*Ejemplo 1: uso básico*


```gml
t_matrix = matrix_build(x, y, 0, 0, 90, 0, 1, 2, 1);
```

*Ejemplo 2: reutilizar una matrix existente*


*Create Event*


```gml
mat_world = matrix_build_identity();
```

*Step Event*


```gml
matrix_build(x, y, 0, 0, 0, direction, 1, 1, 1, mat_world);
```

- **Notas:** Las rotaciones se aplican en orden **YXZ**. Si necesitas otro orden, multiplica varias matrices a mano.

### `matrix_build_identity()`

- **Devuelve:** Matrix (array de 16 elementos)
- **Qué hace:** Devuelve la **matriz identidad**: el equivalente matricial del 1. Multiplicar cualquier matriz por ella no produce ningún cambio.
- **Ejemplo:**

```gml
i_matrix = matrix_build_identity();
```

### `matrix_build_lookat(xfrom, yfrom, zfrom, xto, yto, zto, xup, yup, zup, [result_matrix])`

- **Devuelve:** Matrix (array de 16 elementos)
- **Qué hace:** Construye una **matriz de vista** (cámara) a partir de la posición del observador, el punto al que mira y el vector «arriba». Es la cámara de un entorno 3D.
- **Ejemplo:**

```gml
viewmat = matrix_build_lookat(640, 240, -10, 640, 240, 0, 0, 1, 0);
projmat = matrix_build_projection_ortho(640, 480, 1.0, 32000.0);
camera_set_view_mat(view_camera[0], viewmat);
camera_set_proj_mat(view_camera[0], projmat);
```

### `matrix_build_projection_ortho(width, height, znear, zfar, [result_matrix])`

- **Devuelve:** Matrix (array de 16 elementos)
- **Qué hace:** Construye una matriz de **proyección ortográfica** con el ancho, alto, plano cercano y plano lejano indicados. Sin perspectiva: los objetos no se encogen con la distancia.
- **Ejemplo:**

```gml
viewmat = matrix_build_lookat(640, 240, -10, 640, 240, 0, 0, 1, 0);
projmat = matrix_build_projection_ortho(640, 480, 1.0, 32000.0);
camera_set_view_mat(view_camera[0], viewmat);
camera_set_proj_mat(view_camera[0], projmat);
```

### `matrix_build_projection_perspective(width, height, znear, zfar, [result_matrix])`

- **Devuelve:** Matrix (array de 16 elementos)
- **Qué hace:** Construye una matriz de **proyección en perspectiva** a partir del campo de visión (FOV), la relación de aspecto y los planos cercano y lejano.
- **Ejemplo:**

```gml
var _projmat = matrix_build_projection_perspective(640, 480, 640.0, 32000.0);
camera_set_proj_mat(view_camera[0], _projmat);
```

### `matrix_build_projection_perspective_fov(fov_y, aspect, znear, zfar, [result_matrix])`

- **Devuelve:** Matrix (array de 16 elementos)
- **Qué hace:** Construye una matriz de **proyección en perspectiva** calculando el FOV a partir del ángulo vertical y la relación de aspecto. Es la recomendada cuando trabajas con la ventana o el puerto de vista.
- **Ejemplo:**

```gml
var _projmat = matrix_build_projection_perspective_fov(60, 320/240, 1.0, 32000.0);
camera_set_proj_mat(view_camera[0], _projmat);
```

- **Notas:** Usa un FOV **negativo** con una relación de aspecto positiva para que coincida con el sistema de coordenadas de GameMaker.

---

### Pila de matrices


### `matrix_stack_is_empty()`

- **Devuelve:** Booleano
- **Qué hace:** Indica si la pila de matrices está vacía.
- **Ejemplo:**

```gml
if (!matrix_stack_is_empty())
{
    matrix_stack_clear();
}
```

### `matrix_stack_clear()`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Vacía por completo la pila de matrices.
- **Ejemplo:**

```gml
if (!matrix_stack_is_empty())
{
    matrix_stack_clear();
}
```

### `matrix_stack_set(matrix)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Reemplaza la matriz situada en la **cima** de la pila por otra, multiplicándola por la matriz que había debajo.
- **Ejemplo:**

```gml
var _matrix = matrix_build(x, y, 0, 0, 0, 0, 1, 1, 1);
matrix_stack_set(_matrix);
```

### `matrix_stack_push(matrix)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Apila una matriz. En realidad **multiplica** la matriz que está en la cima por la que le pasas y apila el resultado, lo que permite concatenar transformaciones jerárquicas de forma cómoda.
- **Ejemplo:**

```gml
var _m1 = matrix_build(66, 145, 0, 0, 0, 0, 1, 1, 1);
var _m2 = matrix_build(0, 0, 0, 0, 0, image_angle * 6, 1, 1, 1);
matrix_stack_push(_m1);
matrix_stack_push(_m2);
matrix_set(matrix_world, matrix_stack_top());
draw_sprite(spr_tyre, 0, 0, 0);
matrix_stack_pop();
matrix_stack_pop();
```

- **Notas:** La pila admite como máximo **50** elementos. Saca siempre todo lo que apiles o desbordarás la pila.

### `matrix_stack_pop()`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Saca la matriz de la cima de la pila y la devuelve. De este modo se «deshace» la última transformación añadida.
- **Ejemplo:**

```gml
var _m1 = matrix_build(66, 145, 0, 0, 0, 0, 1, 1, 1);
var _m2 = matrix_build(0, 0, 0, 0, 0, image_angle * 6, 1, 1, 1) ;
matrix_stack_push(_m1);
matrix_stack_push(_m2);
matrix_set(matrix_world, matrix_stack_top());
draw_sprite(spr_tyre, 0, 0, 0);
matrix_stack_pop();
matrix_stack_pop();
```

### `matrix_stack_top()`

- **Devuelve:** Matrix (array de 16 elementos)
- **Qué hace:** Devuelve una copia de la matriz que está en la cima de la pila, sin sacarla.
- **Ejemplo:**

```gml
var _m1 = matrix_build(66, 145, 0, 0, 0, 0, 1, 1, 1);
var _m2 = matrix_build(0, 0, 0, 0, 0, image_angle * 6, 1, 1, 1) ;
matrix_stack_push(_m1);
matrix_stack_push(_m2);
matrix_set(matrix_world, matrix_stack_top());
draw_sprite(tyre, 0, 0, 0);
matrix_stack_pop();
matrix_stack_pop();
```

---

## Fuentes

- [GML Code Reference — GameMaker LTS 2026](https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/GML_Reference.htm)
- [Matrix Functions (LTS)](https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Maths_And_Numbers/Matrix_Functions/Matrix_Functions.htm)
- [Angles And Distance (LTS)](https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Maths_And_Numbers/Angles_And_Distance/Angles_And_Distance.htm)
- Verificación de cada firma con `gm-cli manual read "<función>"` y contra el manual LTS (IDE 2026.0.0.16 / Runtime 2026.0.0.23).
