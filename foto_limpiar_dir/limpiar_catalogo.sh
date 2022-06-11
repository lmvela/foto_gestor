# Delete hidden files (starting with .)
find /media/cavehost_hdd/00_fotos/catalogo -type f -iname '.*' -exec rm -f {} \+

# Move files with no extension to papelera
find /media/cavehost_hdd/00_fotos/catalogo -type f ! -name '*.*' -exec mv -i {} /media/cavehost_hdd/00_fotos/descartar/papelera/ \;

# Move temp jpg~ to papelera
find /media/cavehost_hdd/00_fotos/catalogo -type f -name '*.jpg~' -exec mv -i {} /media/cavehost_hdd/00_fotos/descartar/papelera/ \;