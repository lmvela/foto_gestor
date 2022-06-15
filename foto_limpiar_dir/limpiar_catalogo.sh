# For files in Catalogue

# Delete hidden files (starting with .)
echo Moviendo ficheros ocultos a la papelera
find /media/cavehost_hdd/00_fotos/catalogo -type f -iname '.*' -exec mv -f {} /media/cavehost_hdd/00_fotos/descartar/papelera/ \;
read -p "Press any key to resume ..."

# Move files with no extension to papelera
echo Moviendo ficheros sin extension a la papelera
find /media/cavehost_hdd/00_fotos/catalogo -type f ! -name '*.*' -exec mv -i {} /media/cavehost_hdd/00_fotos/descartar/papelera/ \;
read -p "Press any key to resume ..."

# Move temp jpg~ to papelera
echo Moviendo jpg~ a la papelera
find /media/cavehost_hdd/00_fotos/catalogo -type f -name '*.jpg~' -exec mv -i {} /media/cavehost_hdd/00_fotos/descartar/papelera/ \;
read -p "Press any key to resume ..."