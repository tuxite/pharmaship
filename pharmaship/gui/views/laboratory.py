# -*- coding: utf-8 -*-
import gi
gi.require_version("Gtk", "3.0")  # noqa: E402
from gi.repository import Gtk

from django.utils.translation import gettext as _

from pluralizer import Pluralizer

from pharmaship.core.utils import log, query_count_all

from pharmaship.inventory import models
from pharmaship.inventory import forms
from pharmaship.inventory.parsers.laboratory import parser

from pharmaship.gui import utils, widgets
from pharmaship.gui.utils import first_lower, get_date_mask


NC_TEXT_TEMPLATE = "<span foreground='darkred' weight='bold' style='normal'>{0} {1}</span>"


class View:
    def __init__(self, window, chosen=None):
        self.window = window
        self.params = window.params
        self.builder = window.builder
        # For recording the open equipments in the grid
        self.toggled = False

        self.chosen = None
        self.row_widget_num = None
        if isinstance(chosen, int):
            self.chosen = chosen

    def refresh_grid(self):
        # Get present scroll position
        position = self.scrolled.get_vadjustment().get_value()

        # The Gtk.ScrolledWindow adds automatically a Gtk.Viewport for Gtk.grid
        # Destroy all viewport children
        viewport = self.scrolled.get_children()[0]
        for child in viewport.get_children():
            child.destroy()

        toggle_row_num = None
        if self.toggled:
            toggle_row_num = self.toggled[0] - 1

        # Reset toggled value
        self.toggled = False
        self.chosen = None
        self.row_widget_num = None

        # Re-create the Grid and attach it to the viewport
        grid = self.create_grid(toggle_row_num)

        viewport.add(grid)
        viewport.show_all()
        viewport.get_vadjustment().set_value(position)

    def create_grid(self, toggle_row_num=None):
        grid = Gtk.Grid()

        # Header
        label = Gtk.Label(_("Name"), xalign=0)
        label.set_hexpand(True)
        label.get_style_context().add_class("header-cell")
        grid.attach(label, 0, 0, 1, 1)
        label = Gtk.Label(_("Remarks"), xalign=0)
        label.set_hexpand(True)
        label.get_style_context().add_class("header-cell")
        grid.attach(label, 1, 0, 1, 1)
        label = Gtk.Label(_("Packaging"), xalign=0)
        label.set_hexpand(True)
        label.get_style_context().add_class("header-cell")
        grid.attach(label, 2, 0, 1, 1)
        label = Gtk.Label(_("Location"), xalign=0)
        label.get_style_context().add_class("header-cell")
        grid.attach(label, 3, 0, 1, 1)
        label = Gtk.Label(_("Expiry"), xalign=0.5)
        label.get_style_context().add_class("header-cell")
        grid.attach(label, 4, 0, 1, 1)
        label = Gtk.Label(_("Quantity"), xalign=0.5)
        label.get_style_context().add_class("header-cell")
        grid.attach(label, 5, 0, 1, 1)

        label = Gtk.Label("", xalign=0)
        label.get_style_context().add_class("header-cell")
        # Size request because by default the colum content is "hidden"
        label.set_size_request(125, -1)
        grid.attach(label, 6, 0, 1, 1)

        data = parser(self.params)

        i = 0
        toggle_equipment = None

        for equipment in data:
            i += 1

            # If toggle_row_num is defined, record first the equipment then, when
            # all construction is done, call toggle_article function.
            if toggle_row_num and toggle_row_num == i:
                toggle_equipment = equipment
            if self.chosen and self.chosen == equipment["id"]:
                toggle_equipment = equipment
                toggle_row_num = i
                self.row_widget_num = i

            label = Gtk.Label(equipment["name"], xalign=0)
            label.set_line_wrap(True)
            label.set_lines(1)
            label.set_line_wrap_mode(2)
            label.get_style_context().add_class("item-cell")
            evbox = widgets.EventBox(equipment, self.toggle_article, 7, i)
            evbox.add(label)
            grid.attach(evbox, 0, i, 1, 1)

            label = Gtk.Label(equipment["remark"], xalign=0)
            label.set_line_wrap(True)
            label.set_lines(1)
            label.set_line_wrap_mode(2)
            label.get_style_context().add_class("item-cell")
            label.get_style_context().add_class("article-remark")
            evbox = widgets.EventBox(equipment, self.toggle_article, 7, i)
            evbox.add(label)
            grid.attach(evbox, 1, i, 1, 1)

            label = Gtk.Label(equipment["packaging"], xalign=0)
            label.get_style_context().add_class("item-cell")
            label.set_line_wrap(True)
            label.set_lines(1)
            label.set_line_wrap_mode(2)
            evbox = widgets.EventBox(equipment, self.toggle_article, 7, i)
            evbox.add(label)
            grid.attach(evbox, 2, i, 1, 1)

            # Get list of locations
            locations_len = len(equipment["locations"])
            if locations_len == 0:
                locations_display = ""
            elif locations_len >= 1:
                equipment["locations"].sort()
                locations_display = equipment["locations"][0]
            if locations_len > 1:
                locations_display += ", ..."

            label = Gtk.Label(locations_display, xalign=0)
            label.set_line_wrap(True)
            label.set_lines(1)
            label.set_line_wrap_mode(2)
            label.get_style_context().add_class("item-cell")
            evbox = widgets.EventBox(equipment, self.toggle_article, 7, i)
            evbox.add(label)
            grid.attach(evbox, 3, i, 1, 1)

            # Get first expiry date
            date_display = ""
            if len(equipment["exp_dates"]) > 0 and None not in equipment["exp_dates"]:
                date_display = min(equipment["exp_dates"]).strftime("%Y-%m-%d")

            label = Gtk.Label(date_display, xalign=0.5)
            label.get_style_context().add_class("item-cell")
            label.get_style_context().add_class("text-mono")
            if equipment["has_date_expired"]:
                label.get_style_context().add_class("article-expired")
            elif equipment["has_date_warning"]:
                label.get_style_context().add_class("article-warning")

            evbox = widgets.EventBox(equipment, self.toggle_article, 7, i)
            evbox.add(label)
            grid.attach(evbox, 4, i, 1, 1)

            label = Gtk.Label(xalign=0.5)
            label.set_markup("{0}<small>/{1}</small>".format(equipment["quantity"], equipment["required_quantity"]))
            label.get_style_context().add_class("item-cell")
            label.get_style_context().add_class("text-mono")
            # Set style according to quantity
            utils.quantity_set_style(label, equipment)

            evbox = widgets.EventBox(equipment, self.toggle_article, 7, i)
            evbox.add(label)
            grid.attach(evbox, 5, i, 1, 1)

            # Set tooltip to give information on allowances requirements
            tooltip_text = []
            for item in equipment["allowance"]:
                tooltip_text.append("<b>{0}</b> ({1})".format(item["name"], item["quantity"]))
            label.set_tooltip_markup("\n".join(tooltip_text))

            if equipment["picture"]:
                # Button box for actions
                linked_btn = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                linked_btn.get_style_context().add_class("linked")
                linked_btn.get_style_context().add_class("equipment-item-buttons")
                evbox = widgets.EventBox(equipment, self.toggle_article, 7, i)
                evbox.add(linked_btn)
                grid.attach(evbox, 6, i, 1, 1)

                # Picture
                picture = equipment["picture"]
                btn_picture = widgets.ButtonWithImage("image-x-generic-symbolic", tooltip="View picture", connect=utils.picture_frame, data=picture)
                linked_btn.pack_end(btn_picture, False, True, 0)
            else:
                label = Gtk.Label("", xalign=0.5)
                label.get_style_context().add_class("item-cell")
                evbox = widgets.EventBox(equipment, self.toggle_article, 7, i)
                evbox.add(label)
                grid.attach(evbox, 6, i, 1, 1)

        # Toggle if active
        if toggle_row_num and toggle_equipment:
            self.toggle_article(source=None, grid=grid, equipment=toggle_equipment, row_num=toggle_row_num)

        query_count_all()

        return grid

    def create_main_layout(self):
        # Create content
        self.scrolled = Gtk.ScrolledWindow()
        self.scrolled.props.hscrollbar_policy = Gtk.PolicyType.NEVER
        # No overlay of the scrollbar
        self.scrolled.props.overlay_scrolling = False
        self.window.layout.pack_start(self.scrolled, True, True, 0)

        grid = self.create_grid()

        viewport = Gtk.Viewport()
        viewport.add(grid)

        self.scrolled.add(viewport)

        vadjust = viewport.get_vadjustment()
        grid.set_focus_vadjustment(vadjust)

        self.window.layout.show_all()

        # Change Gtk Alignment if a widget is selected
        if self.row_widget_num:
            self.scrolled.connect("draw", utils.set_focus, self.row_widget_num)

    def dialog_use(self, source, article):
        pluralizer = Pluralizer()

        builder = Gtk.Builder.new_from_file(utils.get_template("article_use.glade"))
        dialog = builder.get_object("dialog")
        dialog.set_title(_("Use an article"))

        # Get packing
        quantity = article["quantity"]
        form = first_lower(article["equipment"]["packaging"])

        if article["packing"]:
            quantity /= article["packing"]["content"]
            form = article["packing"]["name"]

        # Set the current values
        name = builder.get_object("name")
        name.set_text("{0} ({1})".format(article["name"], article["exp_date"]))

        remaining = builder.get_object("remaining")
        remaining.set_value(quantity)

        remaining_adjustment = builder.get_object("remaining_adjustment")
        remaining_adjustment.set_lower(0)
        remaining_adjustment.set_upper(quantity)

        quantity_adjustment = builder.get_object("quantity_adjustment")
        quantity_adjustment.set_lower(0)
        quantity_adjustment.set_upper(quantity)

        label = builder.get_object("consumed_packing")
        label.set_text(pluralizer.pluralize(form, 0))

        label = builder.get_object("remaining_packing")
        label.set_text(pluralizer.pluralize(form, quantity))

        builder.connect_signals({
            "on-response": (self.response_use, dialog, article, builder),
            "on-cancel": (utils.dialog_destroy, dialog),
            "quantity-changed": (utils.item_quantity_changed, builder)
        })

        dialog.set_transient_for(self.window)
        dialog.run()

        dialog.destroy()

    def dialog_modify(self, source, article):
        pluralizer = Pluralizer()

        builder = Gtk.Builder.new_from_file(utils.get_template("article_add.glade"))
        dialog = builder.get_object("dialog")
        dialog.set_title(_("Modify an article"))

        label = builder.get_object("equipment")
        label.set_text(article["equipment"]["name"])

        btn_add = builder.get_object("btn_response")
        btn_add.set_label(_("Modify the article"))

        location_combo = builder.get_object("location")
        utils.location_combo(
            combo=location_combo,
            locations=self.params.locations,
            active=article["location"]["id"]
            )

        # Set the current values
        name = builder.get_object("name")
        name.set_text(article["name"])

        exp_date = builder.get_object("exp_date_raw")
        exp_date = utils.grid_replace(exp_date, widgets.EntryMasked(
            mask=get_date_mask(self.params.setting),
            activate_cb=(self.response_modify, dialog, article, builder)
            ))

        builder.expose_object("exp_date", exp_date)
        if article["exp_date"]:
            date_display = article["exp_date"].strftime("%Y-%m-%d")
            exp_date.get_buffer().set_text(date_display, len(date_display))

        if article["remark"]:
            remark = builder.get_object("remark")
            remark.set_text(article["remark"])

        if article["nc_packaging"]:
            nc_packaging = builder.get_object("nc_packaging")
            nc_packaging.set_text(article["nc_packaging"])
            nc_expander = builder.get_object("nc_expander")
            nc_expander.set_expanded(True)

        # Packing set-up
        active = None
        content = 1
        if article["packing"]:
            active = article["packing"]["id"]
            content = article["packing"]["content"]

        packing_quantity = article["quantity"]/content

        packing_combo = builder.get_object("packing_combo")
        utils.packing_combo(
            combo=packing_combo,
            default=first_lower(article["equipment"]["packaging"]),
            active=active,
            num=packing_quantity
            )

        packing_content = builder.get_object("packing_content")
        packing_content.set_value(content)

        quantity = builder.get_object("quantity")
        quantity.set_value(packing_quantity)

        label = builder.get_object("packing_form")
        label.set_text(
            pluralizer.pluralize(
                first_lower(article["equipment"]["packaging"]),
                packing_quantity
                )
            )

        utils.toggle_packing(packing_combo, builder)

        # Connect signals
        builder.connect_signals({
            "on-response": (self.response_modify, dialog, article, builder),
            "on-cancel": (utils.dialog_destroy, dialog),
            "on-packing-change": (utils.toggle_packing, builder),
            "on-quantity-change": (
                utils.update_packing_combo,
                builder,
                article["equipment"]["packaging"],
                ),
            "on-content-change": (utils.update_packing_form, builder),
        })

        dialog.set_transient_for(self.window)
        dialog.run()

        dialog.destroy()

    def dialog_delete(self, source, article):
        builder = Gtk.Builder.new_from_file(utils.get_template("article_delete.glade"))
        dialog = builder.get_object("dialog")

        # Set the current values
        name = builder.get_object("name")
        name.set_text("{0} ({1}) - quantity: {2}".format(article["name"], article["exp_date"], article["quantity"]))

        # Delete reason combo box
        reason_combo = builder.get_object("reason")

        utils.reason_combo(reason_combo, expired=article["expired"])

        # Connect signals
        builder.connect_signals({
            "on-response": (self.response_delete, dialog, article, builder),
            "on-cancel": (utils.dialog_destroy, dialog),
        })

        dialog.set_transient_for(self.window)
        dialog.run()

        dialog.destroy()

    def dialog_add(self, source, equipment):
        builder = Gtk.Builder.new_from_file(utils.get_template("article_add.glade"))
        dialog = builder.get_object("dialog")

        label = builder.get_object("equipment")
        label.set_text("{0} ({1})".format(equipment["name"], equipment["packaging"]))

        btn_add = builder.get_object("btn_response")
        btn_add.set_label(_("Add the article"))

        # Check if equipment has previous locations to input the latest one as
        # default to ease the input
        active_location = None
        equipment_obj = models.Equipment.objects.get(id=equipment["id"])
        try:
            latest_article = equipment_obj.articles.latest("exp_date")
        except models.Article.DoesNotExist:
            latest_article = None

        if latest_article:
            active_location = latest_article.location.id
            active_packing_name = latest_article.packing_name
            active_packing_content = latest_article.packing_content

        location_combo = builder.get_object("location")
        utils.location_combo(
            combo=location_combo,
            locations=self.params.locations,
            active=active_location
            )

        # Packing set-up
        pluralizer = Pluralizer()

        label = builder.get_object("packing_form")
        label.set_text(
            pluralizer.pluralize(
                first_lower(equipment["packaging"]),
                active_packing_content
                )
            )

        packing_combo = builder.get_object("packing_combo")
        utils.packing_combo(
            combo=packing_combo,
            default=equipment["packaging"],
            active=active_packing_name
            )

        packing_content = builder.get_object("packing_content")
        packing_content.set_value(active_packing_content)

        utils.toggle_packing(packing_combo, builder)

        # By default name = equipment name
        name = builder.get_object("name")
        name.set_text(equipment["name"])

        # Expiration date widget custom
        exp_date = builder.get_object("exp_date_raw")
        exp_date = utils.grid_replace(exp_date, widgets.EntryMasked(
            mask=get_date_mask(self.params.setting),
            activate_cb=(self.response_add, dialog, equipment, builder)
            ))
        builder.expose_object("exp_date", exp_date)

        # Connect signals
        builder.connect_signals({
            "on-response": (self.response_add, dialog, equipment, builder),
            "on-cancel": (utils.dialog_destroy, dialog),
            "on-packing-change": (utils.toggle_packing, builder),
            "on-quantity-change": (
                utils.update_packing_combo,
                builder,
                equipment["packaging"],
                ),
            "on-content-change": (utils.update_packing_form, builder),
        })

        query_count_all()

        dialog.set_transient_for(self.window)
        dialog.run()

        dialog.destroy()

    def response_add(self, source, dialog, equipment, builder):
        fields = {
            "entry": [
                "name",
                "exp_date",
                "nc_packaging",
                "remark"
            ],
            "combobox": [
                "location",
                "packing_combo"
            ],
            "spinbutton": [
                "quantity",
                "packing_content"
            ],
            "textview": []
        }

        data = {
            "parent_id": equipment["id"],
            "perishable": equipment["perishable"]
        }

        cleaned_data = utils.get_form_data(forms.AddArticleForm, builder, fields, data)
        if cleaned_data is None:
            return

        packing_content = cleaned_data['packing_content']
        if cleaned_data['packing_combo_id'] >= 20:
            packing_content = int(cleaned_data['packing_combo_id']/10)

        # Add the article
        article = models.Article.objects.create(
            name=cleaned_data['name'],
            exp_date=cleaned_data['exp_date'],
            location_id=cleaned_data['location_id'],
            nc_packaging=cleaned_data['nc_packaging'],
            parent_id=cleaned_data['parent_id'],
            remark=cleaned_data['remark'],
            packing_name=cleaned_data['packing_combo_id'],
            packing_content=packing_content
            )
        # Add the quantity
        quantity = cleaned_data["quantity"]
        if cleaned_data['packing_combo_id'] > 0:
            quantity *= packing_content

        # Add the quantity
        models.QtyTransaction.objects.create(
            transaction_type=1,
            value=quantity,
            content_object=article
            )

        query_count_all()

        # At the end only
        dialog.destroy()
        # Refresh the list!
        self.refresh_grid()

    def response_modify(self, source, dialog, article, builder):
        fields = {
            "entry": [
                "name",
                "exp_date",
                "nc_packaging",
                "remark"
            ],
            "combobox": [
                "location",
                "packing_combo"
            ],
            "spinbutton": [
                "quantity",
                "packing_content"
            ],
            "textview": []
        }

        cleaned_data = utils.get_form_data(forms.ModifyArticleForm, builder, fields)
        if cleaned_data is None:
            return

        # Add the article
        article_obj = models.Article.objects.get(id=article['id'])
        article_obj.name = cleaned_data['name']
        article_obj.exp_date = cleaned_data['exp_date']
        article_obj.location_id = cleaned_data['location_id']
        article_obj.remark = cleaned_data['remark']

        article_obj.packing_name = cleaned_data['packing_combo_id']
        article_obj.packing_content = cleaned_data['packing_content']
        if cleaned_data['packing_combo_id'] >= 20:
            article_obj.packing_content = int(cleaned_data['packing_combo_id']/10)

        article_obj.nc_packaging = cleaned_data['nc_packaging']

        article_obj.save()

        quantity = cleaned_data["quantity"]

        if cleaned_data['packing_combo_id'] >= 20:
            quantity *= int(cleaned_data['packing_combo_id']/10)
        elif cleaned_data['packing_combo_id'] > 0:
            quantity *= cleaned_data['packing_content']

        if quantity != article['quantity']:
            # Add the quantity (transaction type STOCK COUNT)
            models.QtyTransaction.objects.create(
                transaction_type=8,
                value=quantity,
                content_object=article_obj
                )

        query_count_all()

        # At the end only
        dialog.destroy()
        # Refresh the list!
        self.refresh_grid()

    def response_delete(self, source, dialog, article, builder):
        invalid = False
        # Get response
        reason_combo = builder.get_object("reason")
        reason = utils.get_combo_value(reason_combo)

        if reason is None:
            reason_combo.get_style_context().add_class("error-combobox")
            invalid = True

        if invalid:
            return

        # Get the object
        article_obj = models.Article.objects.get(id=article['id'])

        # Reason is Other (error during input ?)
        if reason == 9:
            article_obj.delete()

        # Reason is Perished - it is one way to declare as perished, other way
        # is to "use" the article
        if reason == 4:
            article_obj.used = True
            article_obj.save()

            models.QtyTransaction.objects.create(
                transaction_type=4,
                value=0,
                content_object=article_obj
            )

        query_count_all()

        # At the end only
        dialog.destroy()
        # Refresh the list!
        self.refresh_grid()

    def response_use(self, source, dialog, article, builder):
        # Get response
        quantity_obj = builder.get_object("quantity")
        quantity = quantity_obj.get_value()

        if quantity < 0:
            return False

        if quantity == 0:
            # Nothing to do
            dialog.destroy()
            return

        # Get the object
        article_obj = models.Article.objects.get(id=article['id'])

        # Adapt the quantity to the paking if any
        if article_obj.packing_name > 0:
            quantity *= article_obj.packing_content

        if article["quantity"] == quantity:
            article_obj.used = True
            article_obj.save()

        models.QtyTransaction.objects.create(
            transaction_type=2,
            value=quantity,
            content_object=article_obj
        )

        query_count_all()

        # At the end only
        dialog.destroy()
        # Refresh the list!
        self.refresh_grid()

    def toggle_article(self, source, grid, equipment, row_num):
        # If already toggled, destroy the toggled part
        if self.toggled and self.toggled[0] > 0:
            # Remove the active-row CSS class of the parent item
            utils.grid_row_class(grid, self.toggled[0] - 1, 7, False)

            for i in range(self.toggled[1] - self.toggled[0] + 1):
                grid.remove_row(self.toggled[0])
            # No need to recreate the widget, we just want to hide
            if row_num + 1 == self.toggled[0]:
                self.toggled = False
                return True

        # Add the active-row CSS class
        utils.grid_row_class(grid, row_num, 7)

        # Need to create the content
        new_row = row_num + 1
        grid.insert_row(new_row)

        # Header row
        label = Gtk.Label("Commercial Name", xalign=0)
        label.set_hexpand(True)
        label.get_style_context().add_class("article-header-cell")
        grid.attach(label, 0, 0 + new_row, 1, 1)

        label = Gtk.Label("Remarks", xalign=0)
        label.get_style_context().add_class("article-header-cell")
        grid.attach(label, 1, 0 + new_row, 2, 1)

        label = Gtk.Label("Location", xalign=0)
        label.get_style_context().add_class("article-header-cell")
        grid.attach(label, 3, 0 + new_row, 1, 1)

        label = Gtk.Label("Expiry", xalign=0.5)
        label.get_style_context().add_class("article-header-cell")
        grid.attach(label, 4, 0 + new_row, 1, 1)

        label = Gtk.Label("Quantity", xalign=0.5)
        label.get_style_context().add_class("article-header-cell")
        grid.attach(label, 5, 0 + new_row, 1, 1)

        label = Gtk.Label("Actions", xalign=1)
        label.get_style_context().add_class("article-header-cell")
        grid.attach(label, 6, 0 + new_row, 1, 1)

        # Get related articles
        articles = equipment["articles"]

        i = new_row
        for article in articles:
            i += 1
            grid.insert_row(i)

            label = Gtk.Label(article["name"], xalign=0)
            label.set_hexpand(True)
            label.get_style_context().add_class("article-item-cell-name")
            label.get_style_context().add_class("article-item-cell")
            grid.attach(label, 0, i, 1, 1)

            # Remark field (mainly used for non-compliance)
            remark_text = []

            if article["nc_packaging"]:
                remark_text.append(NC_TEXT_TEMPLATE.format(_("Non-compliant packaging:"), article["nc_packaging"]))
            if article["remark"]:
                remark_text.append(article["remark"])

            label = Gtk.Label(xalign=0)
            label.set_markup("\n".join(remark_text))
            label.get_style_context().add_class("article-item-cell")
            label.get_style_context().add_class("article-remark")

            grid.attach(label, 1, i, 2, 1)

            label = Gtk.Label(xalign=0)
            label.get_style_context().add_class("article-item-cell")
            sequence = article["location"]["sequence"]
            if len(sequence) > 1:
                parents = " > ".join(sequence[:-1])
                location_display = "<span foreground=\"#555\">{0} > </span>{1}".format(parents, sequence[-1])
            else:
                location_display = sequence[0]

            label.set_markup(location_display)
            label.set_line_wrap(True)
            label.set_lines(1)
            label.set_line_wrap_mode(2)
            grid.attach(label, 3, i, 1, 1)

            if article["exp_date"]:
                label = Gtk.Label(article["exp_date"].strftime("%Y-%m-%d"), xalign=0.5)
                label.get_style_context().add_class("text-mono")
            else:
                label = Gtk.Label()
            label.get_style_context().add_class("article-item-cell")

            # If expiry is soon or due, affect corresponding style
            if article["expired"]:
                label.get_style_context().add_class("article-expired")
            elif article["warning"]:
                label.get_style_context().add_class("article-warning")
            grid.attach(label, 4, i, 1, 1)

            label = Gtk.Label(article["quantity"], xalign=0.5)
            label.get_style_context().add_class("article-item-cell")
            label.get_style_context().add_class("text-mono")
            grid.attach(label, 5, i, 1, 1)

            # Button box for actions
            linked_btn = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            linked_btn.get_style_context().add_class("linked")
            linked_btn.get_style_context().add_class("article-item-buttons")
            # linked_btn.set_halign(Gtk.Align.END)
            grid.attach(linked_btn, 6, i, 1, 1)

            # Use
            if equipment["consumable"]:
                btn_use = widgets.ButtonWithImage("edit-redo-symbolic", tooltip="Use", connect=self.dialog_use, data=article)
                linked_btn.pack_end(btn_use, False, True, 0)
            # Modify
            btn_modify = widgets.ButtonWithImage("document-edit-symbolic", tooltip="Modify", connect=self.dialog_modify, data=article)
            linked_btn.pack_end(btn_modify, False, True, 0)
            # Delete
            btn_delete = widgets.ButtonWithImage("edit-delete-symbolic", tooltip="Delete", connect=self.dialog_delete, data=article)
            btn_delete.get_style_context().add_class("article-btn-delete")
            linked_btn.pack_end(btn_delete, False, True, 0)

        i += 1
        grid.insert_row(i)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        button = Gtk.Button()
        label = Gtk.Label("Add an article", xalign=0)
        button.add(label)
        button.set_relief(Gtk.ReliefStyle.NONE)
        button.get_style_context().add_class("article-btn-add")
        button.connect("clicked", self.dialog_add, equipment)
        box.add(button)
        box.get_style_context().add_class("article-item-cell-add")
        grid.attach(box, 0, i, 1, 1)

        # Empty row for styling purpose
        label = Gtk.Label("")
        label.get_style_context().add_class("article-item-cell-add")
        grid.attach(label, 1, i, 6, 1)

        grid.show_all()
        self.toggled = (new_row, i)
        # log.info("Size %s, %s", linked_btn.get_preferred_size().minimum_size.width, linked_btn.get_preferred_size().natural_size.width)
        query_count_all()
