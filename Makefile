GUI_FOLDER = ./pharmaship/gui
LOCALE_FOLDER = ${GUI_FOLDER}/locale
LOCALE_FOLDER_FR = ${LOCALE_FOLDER}/fr/LC_MESSAGES
LOCALE_FOLDER_EN = ${LOCALE_FOLDER}/fr/LC_MESSAGES

all:
	# Nothing

pot:
	xgettext --keyword=translatable -c -o ${LOCALE_FOLDER}/gui.pot ${GUI_FOLDER}/templates/*.glade
	xgettext --keyword=translatable -j -c -L Glade -o ${LOCALE_FOLDER}/gui.pot ${GUI_FOLDER}/templates/*.xml

	xgettext -f translatable_filelist -L Python -c -o ${LOCALE_FOLDER}/code.pot

	msgcat ${LOCALE_FOLDER}/gui.pot ${LOCALE_FOLDER}/code.pot > ${LOCALE_FOLDER}/com.devmaretique.pharmaship.pot
	msguniq -s -o ${LOCALE_FOLDER}/com.devmaretique.pharmaship.pot ${LOCALE_FOLDER}/com.devmaretique.pharmaship.pot

	rm ${LOCALE_FOLDER}/gui.pot
	rm ${LOCALE_FOLDER}/code.pot

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
	python manage.py compilemessages -l fr -l en
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

translatable:
	find pharmaship -type f \( -name '*.py' ! -iwholename "*/migrations/*" ! -iwholename "*/tests/*" \) -print > translatable_filelist;

icon:
	convert -background none ${GUI_FOLDER}/pharmaship_icon.svg -define icon:auto-resize bin/pharmaship.ico
	convert -background none -size 128x128 ${GUI_FOLDER}/pharmaship_icon.svg ${GUI_FOLDER}/templates/pharmaship_icon.png

gresource:
	glib-compile-resources --sourcedir=${GUI_FOLDER} --target=${GUI_FOLDER}/templates/resources.gresource ${GUI_FOLDER}/resources.gresource.xml

win64:
ifeq ($(OS),Windows_NT)     # is Windows_NT on XP, 2000, 7, Vista, 10...
	# Build the Windows packages with cx_Freeze
	..\venv4\bin\python setup.py build
	# Find and remove DLL duplicates
	./bin/jdupes.exe -r -S -j build/win64 > duplicates.json
	..\venv4\bin\python ./bin/deduplicate.py
	# Remove unecessary locale and dic files
	..\venv4\bin\python ./bin/remove_locale.py
else
	echo "Not on Windows. Aborting."
endif

win64_inst:
	makensis ./bin/installer.nsi
