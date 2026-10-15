# Quadrafall

Juego libre de bloques que caen, inspirado en **Quadrapassel** (GNOME) y en las reglas del
clásico de **NES**, con mejoras modernas opcionales: guardar pieza, varias piezas siguientes,
caída instantánea y pieza fantasma. Funciona en **Windows y Linux**.

> *Quadrafall* es un nombre provisional; se cambia en `src/quadrafall/__init__.py` (`APP_NAME`).

![Partida con el tema NES](docs/partida-nes.png)

## Características

- **Reglas del NES**: velocidades por nivel (48 → 1 fotogramas por fila), puntuación
  40/100/300/1200 × (nivel + 1), progresión de niveles, DAS 16/6, retardo de aparición
  variable, animación de borrado por columnas y estadísticas de piezas.
- **Mejoras modernas** (todas opcionales): guardar pieza, 0–5 piezas siguientes, caída
  instantánea, pieza fantasma, margen mínimo para fijar la pieza, rotación con ayudas o SRS
  y bolsa de 7.
- **Tres estilos predefinidos**: *NES clásico*, *NES+* (recomendado: como el NES, pero con al
  menos 1/3 s para colar la pieza en un hueco aunque bajes rápido) y *Moderno*. Cualquier
  ajuste se puede cambiar por separado.
- **Se pierde** cuando una pieza aparece sobre otra o cuando, al fijarse, algún bloque queda
  por encima del límite (por ejemplo, una I girada en el último momento).
- **Modos**: Maratón (A), 25 líneas (B) y Sprint de 40 líneas.
- **Filas prellenadas** con densidad configurable, como en Quadrapassel.
- **Personalización visual**: 8 temas (NES con colores por nivel, Clásico Tango, Neón,
  Portátil verde, Pastel, Minimalista claro y oscuro, y apto para daltonismo), 5 estilos de bloque,
  3 fuentes (píxel de terminal *VT323* por defecto, redondeada *Varela Round* y lisa),
  cuadrícula, animaciones, efecto CRT y vista previa en directo.
- **Controles reasignables**: dos teclas y un botón de mando por acción. Mandos con cruceta o palanca.
- **Sonido 8 bits generado por código** y música (*Korobeiniki*, canción popular de dominio público).
- **Récords** locales por modo, **español e inglés**, pantalla completa (F11) y modo portátil.

| | |
|---|---|
| ![Apariencia](docs/apariencia.png) | ![Tema Neón](docs/partida-neon.png) |
| ![Tema Minimalista](docs/partida-minimalista.png) | ![Tema Minimalista oscuro](docs/partida-minimalista-oscuro.png) |

## Controles por defecto

| Acción | Teclado | Alternativa | Mando |
|---|---|---|---|
| Mover | ← → | A D | Cruceta / palanca |
| Bajar | ↓ | S | Cruceta ↓ |
| Caída instantánea | Espacio | W | Cruceta ↑ |
| Girar a la derecha | X | ↑ | Botón 2 (B) |
| Girar a la izquierda | Z | Ctrl izq. | Botón 1 (A) |
| Guardar pieza | C | Mayús izq. | Botón 3 (X) |
| Pausa | Esc | P | Botón 8 (Start) |
| Pantalla completa | F11 / Alt+Intro | | |

## Jugar desde el código fuente

Necesitas Python 3.10 o superior.

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -e .
.venv\Scripts\python -m quadrafall
```

**Linux:**

```sh
python3 -m venv .venv
.venv/bin/pip install -e .
.venv/bin/python -m quadrafall
```

Pruebas del motor: `pip install -e ".[dev]"` y después `python -m pytest`.

## Crear ejecutables para publicar

| Plataforma | Comando | Resultado |
|---|---|---|
| Windows | `powershell -ExecutionPolicy Bypass -File packaging\windows\build.ps1` | `dist\Quadrafall-<versión>-windows.zip` |
| Windows (instalador) | Compilar `packaging\windows\installer.iss` con [Inno Setup](https://jrsoftware.org/isinfo.php) tras el paso anterior | `dist\Quadrafall-<versión>-setup.exe` |
| Linux | `sh packaging/linux/build.sh` | `dist/Quadrafall-<versión>-linux-x86_64.tar.gz` |
| Linux (Flatpak) | Ver las instrucciones dentro de `packaging/linux/io.github.quadrafall.Quadrafall.yml` | Paquete para Flathub |

PyInstaller no compila de forma cruzada: el ejecutable de Windows se hace en Windows y el de
Linux en Linux. Si subes el proyecto a GitHub, el flujo `.github/workflows/build.yml` compila
ambos automáticamente y, al crear una etiqueta `v0.1.0`, publica una *release* con los dos archivos.

El identificador `io.github.quadrafall.Quadrafall` debe coincidir con tu cuenta u organización
de GitHub (`io.github.<usuario>.Quadrafall`) si quieres publicarlo en Flathub.

## Dónde se guardan los datos

| Sistema | Ajustes | Récords |
|---|---|---|
| Windows | `%APPDATA%\Quadrafall\settings.json` | `%APPDATA%\Quadrafall\scores.json` |
| Linux | `~/.config/quadrafall/settings.json` | `~/.local/share/quadrafall/scores.json` |
| Modo portátil | carpeta `data` junto al ejecutable | ídem |

Para el **modo portátil**, crea un archivo vacío `portable.txt` junto a `Quadrafall.exe`.

## Estructura del proyecto

```
src/quadrafall/
  engine/        Reglas del juego, sin pygame (pieces, randomizer, board, game)
  ui/            Dibujo, menús, entrada, temas y fuentes
  assets/fonts/  Fuentes incluidas (VT323 y Varela Round) con sus licencias OFL
  app.py         Ventana, bucle a 60 Hz y pila de escenas
  settings.py    Ajustes y estilos predefinidos (NES, NES+, Moderno)
  i18n.py        Textos en español e inglés
  audio.py       Efectos y música sintetizados
tests/           Pruebas del motor (pytest)
packaging/       PyInstaller, instalador de Windows, .desktop, AppStream y Flatpak
tools/           Generador del icono
```

- **Añadir un tema**: una entrada nueva en `THEMES` (`ui/themes.py`) y su nombre en `i18n.py` (`theme_<clave>`).
- **Añadir un idioma**: su código en `LANGUAGES` y una columna más en `STRINGS` (`i18n.py`).
- **Añadir un estilo de juego**: una entrada en `PRESETS` (`settings.py`).
- **Añadir una fuente**: el `.ttf` y su licencia en `assets/fonts`, una entrada en `FONTS`
  (`ui/font.py`) y su nombre en `i18n.py` (`font_<clave>`). Solo fuentes libres (p. ej. OFL).

## Licencia

Quadrafall es software libre bajo la licencia **GNU GPL versión 3 o posterior**
(`GPL-3.0-or-later`); consulta [LICENSE](LICENSE). Es compatible con la licencia de
Quadrapassel (GPL-2.0-or-later), aunque este proyecto es una reimplementación desde cero y
no incluye código ni recursos de Quadrapassel.

Todos los gráficos y sonidos se generan por código en este repositorio. La melodía
*Korobeiniki* es una canción popular rusa del siglo XIX de dominio público; el arreglo es propio.

Las fuentes [VT323](https://fonts.google.com/specimen/VT323) (© The VT323 Project Authors) y
[Varela Round](https://fonts.google.com/specimen/Varela+Round) (© The Varela Round Project Authors)
se distribuyen sin modificar bajo la licencia SIL Open Font License 1.1; sus textos están en
`src/quadrafall/assets/fonts/`.

Este proyecto no está afiliado a The Tetris Company ni a GNOME. «Tetris» es una marca
registrada de The Tetris Company; por eso el juego no usa ese nombre.
