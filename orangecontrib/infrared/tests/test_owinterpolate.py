import numpy as np
import Orange
from Orange.widgets.tests.base import WidgetTest
from orangecontrib.infrared.widgets.owinterpolate import OWInterpolate
from orangecontrib.infrared.data import getx


class TestOWFiles(WidgetTest):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.collagen = Orange.data.Table("collagen.csv")
        cls.peach = Orange.data.Table("peach_juice.dpt")

    def setUp(self):
        self.widget = self.create_widget(OWInterpolate)

    def test_load_unload(self):
        # just to load the widget (it has no inputs)
        pass

    def test_autointerpolate(self):
        self.send_signal("Data", self.collagen)
        out = self.get_output("Interpolated data")
        np.testing.assert_equal(getx(self.collagen), getx(out))
        # no auto-interpolation
        non_interp = Orange.data.Table(self.collagen.domain, self.peach)
        self.assertTrue(np.isnan(non_interp.X).all())
        # auto-interpolation
        auto_interp = Orange.data.Table(out.domain, self.peach)
        self.assertFalse(np.isnan(auto_interp.X).all())
        np.testing.assert_equal(getx(self.collagen), getx(auto_interp))

    def test_interpolate_interval(self):
        self.widget.controls.input_radio.buttons[1].click()
        self.send_signal("Data", self.peach)
        out = self.get_output("Interpolated data")
        np.testing.assert_almost_equal(np.arange(499.53234, 4000.1161, 10), getx(out))
        self.widget.controls.dx.setText("0")
        self.widget.commit()
        self.assertTrue(self.widget.Error.dxzero.is_shown())
        self.widget.controls.dx.setText("0.001")
        self.widget.commit()
        self.assertTrue(self.widget.Error.too_many_points.is_shown())
        self.widget.controls.dx.setText("10")
        self.widget.commit()
        self.assertFalse(self.widget.Error.dxzero.is_shown())
        self.assertFalse(self.widget.Error.too_many_points.is_shown())
        self.widget.controls.xmin.setText("4000.1161")
        self.widget.controls.xmax.setText("499.53234")
        self.widget.commit()
        out2 = self.get_output("Interpolated data")
        np.testing.assert_almost_equal(getx(out2), getx(out))
        self.send_signal("Data", None)
        self.assertTrue(self.get_output("Interpolated data") is None)

    def test_interpolate_points(self):
        self.assertFalse(self.widget.Warning.reference_data_missing.is_shown())
        self.widget.controls.input_radio.buttons[2].click()
        self.assertTrue(self.widget.Warning.reference_data_missing.is_shown())
        self.send_signal("Data", self.peach)
        self.assertTrue(self.widget.Warning.reference_data_missing.is_shown())
        self.send_signal("Points", self.collagen)
        self.assertFalse(self.widget.Warning.reference_data_missing.is_shown())
        out = self.get_output("Interpolated data")
        np.testing.assert_equal(getx(self.collagen), getx(out))
        self.send_signal("Points", None)
        self.assertTrue(self.widget.Warning.reference_data_missing.is_shown())
