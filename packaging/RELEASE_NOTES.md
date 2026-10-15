## Descargar e instalar

| Sistema | Archivo | Cómo |
|---|---|---|
| **Windows 10/11** | **`Quadrafall-{VERSION}-Windows-Setup.exe`** | Ábrelo y sigue el asistente. No pide permisos de administrador. |
| **Linux** (cualquier distribución) | **`Quadrafall-{VERSION}-Linux-x86_64.AppImage`** | Dale permiso de ejecución y ábrelo (detalles abajo). |
| **Ubuntu / Debian / Mint** | **`quadrafall_{VERSION}_amd64.deb`** | Ábrelo con el instalador de software, o `sudo apt install ./quadrafall_{VERSION}_amd64.deb` |

<details>
<summary>Más detalles y otras descargas</summary>

- **Windows: aviso de SmartScreen.** El instalador no está firmado digitalmente, así que Windows
  puede mostrar «Windows protegió su PC». Pulsa **Más información → Ejecutar de todas formas**.
- **Windows sin instalar:** `Quadrafall-{VERSION}-Windows-Portable.zip`. Descomprímelo y abre
  `Quadrafall.exe`. Si creas un archivo vacío `portable.txt` junto al `.exe`, los ajustes se
  guardan en esa misma carpeta.
- **AppImage:** en el gestor de archivos, *Propiedades → Permisos → Permitir ejecutar como
  programa*, o en una terminal: `chmod +x Quadrafall-{VERSION}-Linux-x86_64.AppImage` y
  `./Quadrafall-{VERSION}-Linux-x86_64.AppImage`.
- **Linux sin instalar:** `Quadrafall-{VERSION}-Linux-x86_64.tar.gz`. Descomprímelo y ejecuta `Quadrafall/Quadrafall`.
- Las versiones de Linux necesitan una distribución de 2022 o posterior (glibc 2.35+, por ejemplo Ubuntu 22.04).

</details>

---

**English:** download the `Windows-Setup.exe` (Windows), the `.AppImage` (any Linux distribution) or
the `.deb` (Ubuntu/Debian). Quadrafall is free software (GPL-3.0-or-later).
