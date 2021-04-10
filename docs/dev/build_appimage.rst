Create an AppImage
==================

To create an AppImage file, you need:
  * ``appimage-builder`` (https://github.com/AppImageCrafters/appimage-builder)
  * ``appimagetool`` (https://appimage.github.io/appimagetool/)


In the Python environment::

  pipenv run appimage-builder --recipe appimage/AppImageBuilder.yml

If needed::

  appimagetool -n --runtime-file appimage-builder-cache/runtime-x86_64 --updateinformation "gh-releases-zsync|tuxite|pharmaship|latest|Pharmaship-*x86_64.AppImage.zsync" ./appimage/AppDir ./Pharmaship-x86_64.AppImage
