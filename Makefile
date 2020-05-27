
pot:
	xgettext --keyword=translatable -c -o pharmaship/gui/locale/gui.pot pharmaship/gui/templates/*.glade
	xgettext --keyword=translatable -j -c -L Glade -o pharmaship/gui/locale/gui.pot pharmaship/gui/templates/*.xml

	xgettext -f translatable_filelist -L Python -c -o pharmaship/gui/locale/code.pot

	msgcat pharmaship/gui/locale/gui.pot pharmaship/gui/locale/code.pot > pharmaship/gui/locale/com.devmaretique.pharmaship.pot
	msguniq -s -o pharmaship/gui/locale/com.devmaretique.pharmaship.pot pharmaship/gui/locale/com.devmaretique.pharmaship.pot

	rm pharmaship/gui/locale/gui.pot
	rm pharmaship/gui/locale/code.pot

messages-fr:
	python manage.py makemessages -i "venv*" -i "bin*" -i "build*" -l fr

	cp pharmaship/gui/locale/fr/LC_MESSAGES/com.devmaretique.pharmaship.po pharmaship/gui/locale/fr/LC_MESSAGES/com.devmaretique.pharmaship.po.bak
	msgcat pharmaship/gui/locale/fr/LC_MESSAGES/django.po pharmaship/gui/locale/fr/LC_MESSAGES/com.devmaretique.pharmaship.po.bak pharmaship/gui/locale/com.devmaretique.pharmaship.pot > pharmaship/gui/locale/fr/LC_MESSAGES/com.devmaretique.pharmaship.po
	msguniq -s -o pharmaship/gui/locale/fr/LC_MESSAGES/com.devmaretique.pharmaship.po pharmaship/gui/locale/fr/LC_MESSAGES/com.devmaretique.pharmaship.po

messages-en:
	python manage.py makemessages -i "venv*" -i "bin*" -i "build*" -l en

	cp pharmaship/gui/locale/en/LC_MESSAGES/com.devmaretique.pharmaship.po pharmaship/gui/locale/en/LC_MESSAGES/com.devmaretique.pharmaship.po.bak
	msgcat pharmaship/gui/locale/en/LC_MESSAGES/django.po pharmaship/gui/locale/en/LC_MESSAGES/com.devmaretique.pharmaship.po.bak pharmaship/gui/locale/com.devmaretique.pharmaship.pot > pharmaship/gui/locale/en/LC_MESSAGES/com.devmaretique.pharmaship.po
	msguniq -s -o pharmaship/gui/locale/en/LC_MESSAGES/com.devmaretique.pharmaship.po pharmaship/gui/locale/en/LC_MESSAGES/com.devmaretique.pharmaship.po

mo:
	python manage.py compilemessages -l fr -l en

	msgfmt pharmaship/gui/locale/fr/LC_MESSAGES/com.devmaretique.pharmaship.po
	msgfmt pharmaship/gui/locale/en/LC_MESSAGES/com.devmaretique.pharmaship.po
	# Copy .mo file for Django compatibility
	cp pharmaship/gui/locale/fr/LC_MESSAGES/com.devmaretique.pharmaship.mo pharmaship/gui/locale/fr/LC_MESSAGES/django.mo
	cp pharmaship/gui/locale/en/LC_MESSAGES/com.devmaretique.pharmaship.mo pharmaship/gui/locale/en/LC_MESSAGES/django.mo

clean:
	echo "Clean"
	rm -rf *.pyc
	rm -rf *.mo
	rm -rf build/

translatable:
	find pharmaship -type f \( -name '*.py' ! -iwholename "*/migrations/*" \) -print > translatable_filelist;

icon:
	convert -background none pharmaship/gui/pharmaship_icon.svg -define icon:auto-resize bin/pharmaship.ico
	convert -background none -size 128x128 pharmaship/gui/pharmaship_icon.svg pharmaship/gui/templates/pharmaship_icon.png

gresource:
	glib-compile-resources --sourcedir=pharmaship/gui --target=pharmaship/gui/templates/resources.gresource pharmaship/gui/resources.gresource.xml

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
