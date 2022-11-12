from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QThread, QObject, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QStatusTipEvent


def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix) :]
    return text


class WMSBase:
    def __init__(self):
        pass

    def ask_for_legend(self, wms, wmslayer):
        if hasattr(wms, "add_legend"):
            try:
                img = wms.fetch_legend(silent=True)
                if img is not None:
                    self._ask_for_legend(wms, wmslayer, img)
            except:
                pass

    def _ask_for_legend(self, wms, wmslayer, img=None):
        self._msg = QtWidgets.QMessageBox()
        self._msg.setIcon(QtWidgets.QMessageBox.Question)
        self._msg.setWindowTitle("Add a legend?")
        self._msg.setText(f"Do you want a legend for {wmslayer}?")
        self._msg.setWindowFlags(Qt.WindowStaysOnTopHint)
        self._msg.setStandardButtons(
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        self._msg.buttonClicked.connect(lambda: self._cb_add_legend(wms, img))
        self._msg.show()

    def _cb_add_legend(self, wms, img):
        if self._msg.standardButton(self._msg.clickedButton()) != self._msg.Yes:
            return

        if hasattr(wms, "add_legend"):
            try:
                wms.add_legend(img=img)
            except:
                pass


class WMS_GEBCO(WMSBase):
    layer_prefix = "GEBCO_"
    name = "GEBCO"

    def __init__(self, m=None):
        self.m = m
        self.wmslayers = [
            key
            for key in self.m.add_wms.GEBCO.add_layer.__dict__.keys()
            if not (key in ["m"] or key.startswith("_"))
        ]

    def do_add_layer(self, wmslayer, layer):
        wms = getattr(self.m.add_wms.GEBCO.add_layer, wmslayer)
        wms(layer=layer)
        self.ask_for_legend(wms, wmslayer)


class WMS_CAMS(WMSBase):
    layer_prefix = "CAMS_"
    name = "CAMS"

    def __init__(self, m=None):
        self.m = m
        self.wmslayers = [
            key
            for key in self.m.add_wms.CAMS.add_layer.__dict__.keys()
            if not (key in ["m"] or key.startswith("_"))
        ]

    def do_add_layer(self, wmslayer, layer):
        wms = getattr(self.m.add_wms.CAMS.add_layer, wmslayer)
        wms(layer=layer)
        self.ask_for_legend(wms, wmslayer)


class WMS_NASA_GIBS(WMSBase):
    layer_prefix = "NASA_GIBS_"
    name = "NASA_GIBS"

    def __init__(self, m=None):
        self.m = m

        if self.m.get_crs(3857) == m.crs_plot:
            self.usewms = self.m.add_wms.NASA_GIBS.EPSG_3857
        elif self.m.get_crs(3031) == m.crs_plot:
            self.usewms = self.m.add_wms.NASA_GIBS.EPSG_3031
        elif self.m.get_crs(3413) == m.crs_plot:
            self.usewms = self.m.add_wms.NASA_GIBS.EPSG_3413
        elif self.m.get_crs(4326) == m.crs_plot:
            self.usewms = self.m.add_wms.NASA_GIBS.EPSG_4326
        else:
            self.usewms = self.m.add_wms.NASA_GIBS.EPSG_3857

        self.wmslayers = [
            key
            for key in self.usewms.add_layer.__dict__.keys()
            if not (key in ["m"] or key.startswith("_"))
        ]

    def do_add_layer(self, wmslayer, layer):
        wms = getattr(self.usewms.add_layer, wmslayer)
        wms(layer=layer, transparent=True)
        self.ask_for_legend(wms, wmslayer)


class WMS_OSM(WMSBase):
    layer_prefix = "OSM_"
    name = "OpenStreetMap"

    def __init__(self, m=None):
        self.m = m
        self.wmslayers = [
            key
            for key in self.m.add_wms.OpenStreetMap.add_layer.__dict__.keys()
            if not (key in ["m"] or key.startswith("_"))
        ]

        self._terrestis = [
            "Terrestis__" + i
            for i in m.add_wms.OpenStreetMap.OSM_terrestis.add_layer.__dict__
        ]
        self._mundialis = [
            "Mundialis__" + i
            for i in m.add_wms.OpenStreetMap.OSM_mundialis.add_layer.__dict__
        ]
        self._OSM_landuse = [
            "OSM_landuse__" + i
            for i in m.add_wms.OpenStreetMap.OSM_landuse.add_layer.__dict__
        ]
        self._OSM_wms = [
            "OSM_wms__" + i for i in m.add_wms.OpenStreetMap.OSM_wms.add_layer.__dict__
        ]

        self.wmslayers += self._terrestis
        self.wmslayers += self._mundialis
        self.wmslayers += self._OSM_landuse
        self.wmslayers += self._OSM_wms

    def do_add_layer(self, wmslayer, layer):

        if wmslayer in self._OSM_wms:
            wms = getattr(
                self.m.add_wms.OpenStreetMap.OSM_wms.add_layer,
                remove_prefix(wmslayer, "OSM_wms__"),
            )
        elif wmslayer in self._OSM_landuse:
            wms = getattr(
                self.m.add_wms.OpenStreetMap.OSM_landuse.add_layer,
                remove_prefix(wmslayer, "OSM_landuse__"),
            )
        elif wmslayer in self._mundialis:
            wms = getattr(
                self.m.add_wms.OpenStreetMap.OSM_mundialis.add_layer,
                remove_prefix(wmslayer, "Mundialis__"),
            )
        elif wmslayer in self._terrestis:
            wms = getattr(
                self.m.add_wms.OpenStreetMap.OSM_terrestis.add_layer,
                remove_prefix(wmslayer, "Terrestis__"),
            )
        else:
            wms = getattr(self.m.add_wms.OpenStreetMap.add_layer, wmslayer)

        wms(layer=layer, transparent=True)
        self.ask_for_legend(wms, wmslayer)


class WMS_S2_cloudless(WMSBase):
    layer_prefix = "S2_"
    name = "S2 cloudless"

    def __init__(self, m=None):
        self.m = m
        wmslayers = sorted(self.m.add_wms.S2_cloudless.layers)

        if self.m.crs_plot == self.m.CRS.GOOGLE_MERCATOR:
            wmslayers = [i for i in wmslayers if i.endswith("3857")]
        else:
            wmslayers = [i for i in wmslayers if not i.endswith("3857")]

        self.wmslayers = wmslayers

    def do_add_layer(self, wmslayer, layer):
        wms = getattr(self.m.add_wms.S2_cloudless.add_layer, wmslayer)
        wms(layer=layer)
        self.ask_for_legend(wms, wmslayer)


class WMS_ESA_WorldCover(WMSBase):
    layer_prefix = ""
    name = "ESA WorldCover"

    def __init__(self, m=None):
        self.m = m
        self.wmslayers = [
            key
            for key in self.m.add_wms.ESA_WorldCover.layers
            if (key.startswith("WORLDCOVER") or key.startswith("COP"))
        ]

    def do_add_layer(self, wmslayer, layer):
        wms = getattr(self.m.add_wms.ESA_WorldCover.add_layer, wmslayer)
        wms(layer=layer)
        self.ask_for_legend(wms, wmslayer)


class WMS_S1GBM(WMSBase):
    layer_prefix = "S1GBM_"
    name = "S1GBM"

    def __init__(self, m=None):
        self.m = m
        self.wmslayers = ["vv", "vh"]

    def do_add_layer(self, wmslayer, layer):
        wms = getattr(self.m.add_wms.S1GBM.add_layer, wmslayer)
        wms(layer=layer)
        self.ask_for_legend(wms, wmslayer)


class WMS_ISRIC_SoilGrids(WMSBase):
    layer_prefix = "ISRIC_SoilGrids_"
    name = "ISRIC SoilGrids"

    def __init__(self, m=None):
        self.m = m

        subs = [i for i in m.add_wms.ISRIC_SoilGrids.__dir__() if not i.startswith("_")]

        self.wmslayers = []
        for l in subs:
            self.wmslayers.extend(
                [
                    key
                    for key in getattr(
                        self.m.add_wms.ISRIC_SoilGrids, l
                    ).add_layer.__dict__.keys()
                    if not (key in ["m"] or key.startswith("_"))
                ]
            )

    def do_add_layer(self, wmslayer, layer):

        sub = wmslayer.split("_", 1)[0]

        wms = getattr(getattr(self.m.add_wms.ISRIC_SoilGrids, sub).add_layer, wmslayer)
        wms(layer=layer)
        self.ask_for_legend(wms, wmslayer)


class WMS_DLR_basemaps(WMSBase):
    layer_prefix = "DLR_bm_"
    name = "DLR basemaps"

    def __init__(self, m=None):
        self.m = m
        self.wmslayers = self.m.add_wms.DLR_basemaps.layers

    def do_add_layer(self, wmslayer, layer):
        wms = getattr(self.m.add_wms.DLR_basemaps.add_layer, wmslayer)
        wms(layer=layer)
        self.ask_for_legend(wms, wmslayer)


# an event-filter to catch StatusTipFilter events
# (e.g. to avoid clearing the statusbar on mouse hoover over QMenu)
class StatusTipFilter(QObject):
    def eventFilter(self, watched, event):
        if isinstance(event, QStatusTipEvent):
            return True
        return super().eventFilter(watched, event)


class AddWMSMenuButton(QtWidgets.QPushButton):
    def __init__(self, *args, m=None, new_layer=False, show_layer=False, **kwargs):
        super().__init__(*args, **kwargs)

        self.m = m
        self._new_layer = new_layer
        self._show_layer = show_layer
        self.layer = None

        self.wms_dict = {
            "OpenStreetMap": WMS_OSM,
            "S2 Cloudless": WMS_S2_cloudless,
            "ESA WorldCover": WMS_ESA_WorldCover,
            "S1GBM": WMS_S1GBM,
            "GEBCO": WMS_GEBCO,
            "NASA GIBS": WMS_NASA_GIBS,
            "CAMS": WMS_CAMS,
            "ISRIC SoilGrids": WMS_ISRIC_SoilGrids,
            "DLR Basemaps": WMS_DLR_basemaps,
        }

        if self._new_layer:
            self.setText("Create new WebMap Layer")
        else:
            self.setText("Add WebMap Service")

        width = self.fontMetrics().boundingRect(self.text()).width()
        self.setFixedWidth(width + 30)

        self.feature_menu = QtWidgets.QMenu()
        self.feature_menu.setStyleSheet("QMenu { menu-scrollable: 1;}")
        self.feature_menu.aboutToShow.connect(self.populate_menu)

        self.setMenu(self.feature_menu)
        self.clicked.connect(self.show_menu)

        self._submenus = dict()

        # set event-filter to avoid showing tooltips on hovver over QMenu items
        self.installEventFilter(StatusTipFilter(self))

    def enterEvent(self, e):
        if self.window().showhelp is True:
            if self._new_layer:
                QtWidgets.QToolTip.showText(
                    e.globalPos(),
                    "<h3>New WebMap Layer</h3>"
                    "Create a new layer (<i>''[wms service]_[wms layer]''</i>) and add "
                    "the selected WebMap service to it."
                    "<p>"
                    "NOTE: The service is added to a new layer, <not> the "
                    "currently visible layer! (this is particularly useful to compare "
                    "existing layers to WebMap layers)",
                )
            else:
                QtWidgets.QToolTip.showText(
                    e.globalPos(),
                    "<h3>Add WebMap Service</h3>"
                    "Add the selected WebMap service to the "
                    "<b>currently selected layer-tab</b> "
                    "in the tab-bar below."
                    "<p>"
                    "NOTE: This is not necessarily the currently visible layer!",
                )

    @pyqtSlot()
    def show_menu(self):
        self.feature_menu.popup(self.mapToGlobal(self.menu_button.pos()))

    @pyqtSlot()
    def populate_menu(self):
        self.sub_menus = dict()
        for wmsname in self.wms_dict:
            self.sub_menus[wmsname] = self.feature_menu.addMenu(wmsname)
            self.sub_menus[wmsname].aboutToShow.connect(self.populate_submenu_thread)
        self.feature_menu.aboutToShow.disconnect()

    @pyqtSlot()
    def populate_submenu_thread(self):
        #

        class Worker(QObject):
            finished = pyqtSignal()
            progress = pyqtSignal(int)

            def __init__(self, *args, x=None, wmsname=None, **kwargs):
                super().__init__(*args, **kwargs)

                self.x = x
                self.wmsname = wmsname

            def run(self):
                self.x.fetch_submenu(wmsname=self.wmsname)
                self.finished.emit()

        if not isinstance(self.sender(), QtWidgets.QMenu):
            return

        wmsname = self.sender().title()

        if not hasattr(self, "threads"):
            self.threads = dict()
            self.workers = dict()

        if wmsname not in self.threads:
            thread = QThread()
            worker = Worker(x=self, wmsname=wmsname)
            worker.moveToThread(thread)
            thread.started.connect(worker.run)

            @pyqtSlot()
            def doit():
                self.populate_submenu(wmsname)

            thread.finished.connect(doit)
            worker.finished.connect(thread.quit)
            worker.finished.connect(worker.deleteLater)
            thread.finished.connect(thread.deleteLater)

            self.threads[wmsname] = thread
            self.workers[wmsname] = worker

            thread.start()

    def set_layer(self, layer):
        self.layer = layer

    def fetch_submenu(self, wmsname):
        # disconnect callbacks to avoid recursions
        self.sub_menus[wmsname].aboutToShow.disconnect()

        wmsclass = self.wms_dict[wmsname]
        wms = wmsclass(m=self.m)
        sub_features = wms.wmslayers
        self._submenus[wmsname] = sub_features

    def populate_submenu(self, wmsname=None):
        if wmsname not in self._submenus:
            print("No layers found for the WMS: {wmsname}")
            return
        else:
            wmsclass = self.wms_dict[wmsname]
            wms = wmsclass(m=self.m)
            sub_features = self._submenus[wmsname]

        try:
            for wmslayer in sub_features:
                action = self.sub_menus[wmsname].addAction(wmslayer)
                action.triggered.connect(self.menu_callback_factory(wms, wmslayer))
        except:
            print("There was a problem with the WMS: " + wmsname)

    def menu_callback_factory(self, wms, wmslayer):
        @pyqtSlot()
        def wms_cb():
            if self._new_layer:
                layer = wms.name + "_" + wmslayer
                # indicate creation of new layer in statusbar
                self.window().statusBar().showMessage(
                    f"New WebMap layer '{layer}' created!", 5000
                )

            else:
                layer = self.layer
                if layer.startswith("_") and "|" in layer:
                    self.window().statusBar().showMessage(
                        "Adding features to temporary multi-layers is not supported!",
                        5000,
                    )
                    return

            wms.do_add_layer(wmslayer, layer=layer)
            if self._show_layer:
                self.m.show_layer(layer)
            else:
                self.m.BM._do_on_layer_change(layer)
                if layer in self.m.BM._bg_layer.split("|"):
                    self.m.redraw()

        return wms_cb
