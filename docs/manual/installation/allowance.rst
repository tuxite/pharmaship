Configure your allowances
=========================

.. image:: ./pics/allowancemanager.png
   :width: 600px
   :align: center
   :alt: Allowance Manager Button

In any software window, open *Configuration Menu* then *Allowance Manager*.

.. image:: ./pics/allowancemanagerinfo.png
   :width: 600px
   :align: center
   :alt: Allowance Manager Info

This configuration window is split in two columns, on the left, the top part shows allowance loaded for your vessel
when the bottom part shows import button to update allowance you have to use.

Allowances
++++++++++

You should have allowances packets in your possession, if not you may download some from `Pharmaship/Allowance <https://www.dsm.com/pharmaship/allowances>`_.
These files look like *A_type_version.tar.asc*, where *type* can be *GSMU* for instance, and *version* is the revision number.

.. note:: These files are encrypted, using GnuPG public and private keys for signature validation from authors of packets. This is to ensure origin of data, and prove its integrity.

Active column allows you to (de)activate any allowance you want, in order to check for example quantity and dotation of an other specific allowance.

Vessel pharmacy
+++++++++++++++

On the column, you will be able to (de)activate Laboratory and/or Telemedical equipment depending if your vessel is equipped, or not.
Then you need to specify how many first aid kit(s) and rescue bag(s) you have, they may be stow outside of vessel's pharmacy.
They usually are.

Finally, set-up the warning delay for pharmacy check. This is interval between when you need to order new medicines
in order to receive them before the old ones were expired.

.. warning:: Sailing with expired medicines is prohibited.

But don't throw expired medicines until you receive the good
one, it may save life ! Expired medicines have to be kept outside of good medicines, with a placard : "expired medicines, do not used".
In fact, it could be used on Maritime Medical Consultation Center Doctor advice only.
