GUI_FOLDER = ./pharmaship/gui
ASSETS_FOLDER = ${GUI_FOLDER}/assets
LOCALE_FOLDER = ${GUI_FOLDER}/locale
LOCALE_FOLDER_FR = ${LOCALE_FOLDER}/fr/LC_MESSAGES
LOCALE_FOLDER_EN = ${LOCALE_FOLDER}/fr/LC_MESSAGES

all:
	# Nothing

translatable:
	# Create Python translatable files list
	find pharmaship -type f \( -name '*.py' ! -iwholename "*/migrations/*" ! -iwholename "*/tests/*" \) -print > translatable_filelist;

pot: translatable
	# Get translations from UI files
	xgettext --keyword=translatable -c -o ${LOCALE_FOLDER}/gui.pot ${ASSETS_FOLDER}/ui/*.ui
	# Get translations from UI Menu files
	xgettext --keyword=translatable -j -c -L Glade -o ${LOCALE_FOLDER}/gui.pot ${ASSETS_FOLDER}/ui/menu/*.xml
	# Get translations from Python files
	xgettext -f translatable_filelist -L Python -c -o ${LOCALE_FOLDER}/code.pot

	# Concatenate POT files
	msgcat ${LOCALE_FOLDER}/gui.pot ${LOCALE_FOLDER}/code.pot > ${LOCALE_FOLDER}/com.devmaretique.pharmaship.pot
	msguniq -s -o ${LOCALE_FOLDER}/com.devmaretique.pharmaship.pot ${LOCALE_FOLDER}/com.devmaretique.pharmaship.pot

	# Delete unecessary POT files
	rm ${LOCALE_FOLDER}/gui.pot
	rm ${LOCALE_FOLDER}/code.pot

messages: messages-fr messages-en

messages-fr:
	# Create backup
	cp ${LOCALE_FOLDER_FR}/com.devmaretique.pharmaship.po ${LOCALE_FOLDER_FR}/com.devmaretique.pharmaship.po.bak

	# Parse files using Django makemessages customized command
	python manage.py make_messages --keep-pot -l fr

	# Merge the newly generated files
	msgcat ${LOCALE_FOLDER}/django.pot ${LOCALE_FOLDER}/com.devmaretique.pharmaship.pot > ${LOCALE_FOLDER_FR}/com.devmaretique.pharmaship.pot
	msguniq -s -o ${LOCALE_FOLDER_FR}/com.devmaretique.pharmaship.pot ${LOCALE_FOLDER_FR}/com.devmaretique.pharmaship.pot

	# Merge old translations
	cp ${LOCALE_FOLDER_FR}/com.devmaretique.pharmaship.pot ${LOCALE_FOLDER_FR}/com.devmaretique.pharmaship.po
	msgmerge -o ${LOCALE_FOLDER_FR}/com.devmaretique.pharmaship.po ${LOCALE_FOLDER_FR}/com.devmaretique.pharmaship.po.bak ${LOCALE_FOLDER_FR}/com.devmaretique.pharmaship.po

messages-en:
	# Create backup
	cp ${LOCALE_FOLDER_EN}/com.devmaretique.pharmaship.po ${LOCALE_FOLDER_EN}/com.devmaretique.pharmaship.po.bak

	# Parse files using Django makemessages customized command
	python manage.py make_messages --keep-pot -l en

	# Merge the newly generated files
	msgcat ${LOCALE_FOLDER}/django.pot ${LOCALE_FOLDER}/com.devmaretique.pharmaship.pot > ${LOCALE_FOLDER_EN}/com.devmaretique.pharmaship.pot
	msguniq -s -o ${LOCALE_FOLDER_EN}/com.devmaretique.pharmaship.pot ${LOCALE_FOLDER_EN}/com.devmaretique.pharmaship.pot

	# Merge old translations
	cp ${LOCALE_FOLDER_EN}/com.devmaretique.pharmaship.pot ${LOCALE_FOLDER_EN}/com.devmaretique.pharmaship.po
	msgmerge -o ${LOCALE_FOLDER_EN}/com.devmaretique.pharmaship.po ${LOCALE_FOLDER_EN}/com.devmaretique.pharmaship.po.bak ${LOCALE_FOLDER_EN}/com.devmaretique.pharmaship.po

mo:
	# Copy .po files for Django compatibility
	cp ${LOCALE_FOLDER_FR}/com.devmaretique.pharmaship.po ${LOCALE_FOLDER_FR}/django.po
	cp ${LOCALE_FOLDER_EN}/com.devmaretique.pharmaship.po ${LOCALE_FOLDER_EN}/django.po

	# Generate .mo files
ifeq ($(OS),Windows_NT)
	venv\bin\python manage.py compilemessages -l fr -l en
else
		python manage.py compilemessages -l fr -l en
endif

	msgfmt ${LOCALE_FOLDER_FR}/com.devmaretique.pharmaship.po
	msgfmt ${LOCALE_FOLDER_EN}/com.devmaretique.pharmaship.po

	# Copy .mo file for Django compatibility
	cp ${LOCALE_FOLDER_FR}/com.devmaretique.pharmaship.mo ${LOCALE_FOLDER_FR}/django.mo
	cp ${LOCALE_FOLDER_EN}/com.devmaretique.pharmaship.mo ${LOCALE_FOLDER_EN}/django.mo

clean:
	echo "Clean"
	rm -rf *.pyc
	rm -rf *.mo
	rm -rf *.pot
	rm -rf build/
	rm -rf appimage-builder-cache/
	rm translatable_filelist

icon:
	convert -background none ${ASSETS_FOLDER}/pharmaship_icon.svg -define icon:auto-resize bin/pharmaship.ico
	convert -background none -size 128x128 ${ASSETS_FOLDER}/pharmaship_icon.svg ${ASSETS_FOLDER}/pharmaship_icon.png
	convert -background white -size 150x57 ${ASSETS_FOLDER}/pharmaship_installer.svg bin/pharmaship_installer.bmp

gresource:
	glib-compile-resources --sourcedir=${ASSETS_FOLDER} --target=${GUI_FOLDER}/resources.gresource ${GUI_FOLDER}/resources.gresource.xml

win64_freeze:
ifeq ($(OS),Windows_NT)     # is Windows_NT on XP, 2000, 7, Vista, 10...
	# Build the Windows packages with cx_Freeze
	venv\bin\python setup_win.py build
else
	echo "Not on Windows. Aborting."
endif

win64_prepare:
ifeq ($(OS),Windows_NT)
	# Find and remove DLL duplicates
	./bin/jdupes.exe -r -S -j -o name -X onlyext:dll,DLL build/win64 > duplicates.json
	venv\bin\python ./bin/deduplicate.py
	# Remove unecessary locale and dic files
	venv\bin\python ./bin/remove_locale.py
else
	echo "Not on Windows. Aborting."
endif

win64_inst:
ifeq ($(OS),Windows_NT)
	makensis ./bin/installer.nsi
else
	echo "Not on Windows. Aborting."
endif

win64: win64_freeze win64_prepare win64_inst

patch_weasyprint:
# Patching Weasyprint for freezing
	patch -i bin/weasyprint.patch venv/lib/python3.8/site-packages/weasyprint/__init__.py

patch_cairosvg:
# Patching CairoSVG for freezing
	patch -i bin/cairosvg.patch venv/lib/python3.8/site-packages/cairosvg/__init__.py

doc_pdf:
	# Build the user and developer manuals in PDF. xelatex needed.
	sphinx-build -M latexpdf docs build/sphinx
	cp build/sphinx/latex/user_manual.pdf pharmaship/data/user_manual.pdf

build_appimage:
	# Create Linux AppImage
	appimage-builder --recipe appimage/AppImageBuilder.yml
