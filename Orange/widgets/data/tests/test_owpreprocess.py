# Test methods with long descriptive names can omit docstrings
# pylint: disable=missing-docstring
import numpy as np

from Orange.data import Table
from Orange.preprocess import (
    Randomize, Scale, Discretize, Continuize, Impute, ProjectPCA, ProjectCUR
)
from Orange.preprocess import discretize, impute, fss, score
from Orange.widgets.data import owpreprocess
from Orange.widgets.data.owpreprocess import OWPreprocess
from Orange.widgets.tests.base import WidgetTest


class TestOWPreprocess(WidgetTest):
    def setUp(self):
        self.widget = self.create_widget(OWPreprocess)
        self.zoo = Table("zoo")

    def test_randomize(self):
        saved = {"preprocessors": [("orange.preprocess.randomize",
                                    {"rand_type": Randomize.RandomizeClasses,
                                     "rand_seed": 1})]}
        model = self.widget.load(saved)
        self.widget.set_model(model)
        self.send_signal("Data", self.zoo)
        output = self.get_output("Preprocessed Data")
        np.random.seed(1)
        np.random.shuffle(self.zoo.Y)
        np.testing.assert_array_equal(self.zoo.X, output.X)
        np.testing.assert_array_equal(self.zoo.Y, output.Y)
        np.testing.assert_array_equal(self.zoo.metas, output.metas)

    def test_normalize(self):
        data = Table("iris")
        saved = {"preprocessors": [("orange.preprocess.scale",
                                    {"center": Scale.CenteringType.Mean,
                                     "scale": Scale.ScalingType.Std})]}
        model = self.widget.load(saved)
        self.widget.set_model(model)
        self.send_signal("Data", data)
        output = self.get_output("Preprocessed Data")

        np.testing.assert_allclose(output.X.mean(0), 0, atol=1e-7)
        np.testing.assert_allclose(output.X.std(0), 1, atol=1e-7)


# Test for editors
class TestDiscretizeEditor(WidgetTest):
    def test_editor(self):
        widget = owpreprocess.DiscretizeEditor()
        self.assertEqual(widget.parameters(),
                         {"method": owpreprocess.DiscretizeEditor.EqualFreq,
                          "n": 4})
        p = widget.createinstance(widget.parameters())
        self.assertIsInstance(p, Discretize)
        self.assertIsInstance(p.method, discretize.EqualFreq)
        widget.setParameters(
            {"method": owpreprocess.DiscretizeEditor.EntropyMDL}
        )
        p = widget.createinstance(widget.parameters())
        self.assertIsInstance(p, Discretize)
        self.assertIsInstance(p.method, discretize.EntropyMDL)

        widget.setParameters(
            {"method": owpreprocess.DiscretizeEditor.EqualWidth,
             "n": 10}
        )
        p = widget.createinstance(widget.parameters())
        self.assertIsInstance(p, Discretize)
        self.assertIsInstance(p.method, discretize.EqualWidth)
        self.assertEqual(p.method.n, 10)


class TestContinuizeEditor(WidgetTest):
    def test_editor(self):
        widget = owpreprocess.ContinuizeEditor()
        self.assertEqual(widget.parameters(),
                         {"multinomial_treatment": Continuize.Indicators})

        p = widget.createinstance(widget.parameters())
        self.assertIsInstance(p, Continuize)
        self.assertEqual(p.multinomial_treatment, Continuize.Indicators)

        widget.setParameters(
            {"multinomial_treatment": Continuize.FrequentAsBase})
        p = widget.createinstance(widget.parameters())
        self.assertIsInstance(p, Continuize)
        self.assertEqual(p.multinomial_treatment, Continuize.FrequentAsBase)


class TestImputeEditor(WidgetTest):
    def test_editor(self):
        widget = owpreprocess.ImputeEditor()
        self.assertEqual(widget.parameters(),
                         {"method": owpreprocess.ImputeEditor.Average})
        widget.setParameters(
            {"method": owpreprocess.ImputeEditor.Average}
        )
        p = widget.createinstance(widget.parameters())
        self.assertIsInstance(p, Impute)
        self.assertIsInstance(p.method, impute.Average)


class TestFeatureSelectEditor(WidgetTest):
    def test_editor(self):
        widget = owpreprocess.FeatureSelectEditor()
        p = widget.createinstance(widget.parameters())
        self.assertIsInstance(p, fss.SelectBestFeatures)
        self.assertEqual(p.method, score.InfoGain)
        self.assertEqual(p.k, 10)


class TestRandomFeatureSelectEditor(WidgetTest):
    def test_editor(self):
        widget = owpreprocess.RandomFeatureSelectEditor()
        p = widget.createinstance(widget.parameters())
        self.assertIsInstance(p, fss.SelectRandomFeatures)
        self.assertEqual(p.k, 10)

        widget.setParameters(
            {"strategy": owpreprocess.RandomFeatureSelectEditor.Percentage,
             "p": 25})
        p = widget.createinstance(widget.parameters())
        self.assertIsInstance(p, fss.SelectRandomFeatures)
        self.assertEqual(p.k, 0.25)


class TestRandomizeEditor(WidgetTest):
    def test_editor(self):
        widget = owpreprocess.Randomize()
        p = widget.createinstance(widget.parameters())
        self.assertIsInstance(p, Randomize)
        self.assertEqual(p.rand_type, Randomize.RandomizeClasses)

        widget.setParameters({"rand_type": Randomize.RandomizeAttributes})
        p = widget.createinstance(widget.parameters())
        self.assertIsInstance(p, Randomize)
        self.assertEqual(p.rand_type, Randomize.RandomizeAttributes)


class TestPCAEditor(WidgetTest):
    def test_editor(self):
        widget = owpreprocess.PCA()
        self.assertEqual(widget.parameters(),
                         {"n_components": 10})
        p = widget.createinstance(widget.parameters())
        self.assertIsInstance(p, ProjectPCA)
        self.assertEqual(p.n_components, 10)

        widget.setParameters({"n_components": 5})
        p = widget.createinstance(widget.parameters())
        self.assertIsInstance(p, ProjectPCA)
        self.assertEqual(p.n_components, 5)


class TestCUREditor(WidgetTest):
    def test_editor(self):
        widget = owpreprocess.CUR()
        self.assertEqual(widget.parameters(),
                         {"rank": 10, "max_error": 1})
        p = widget.createinstance(widget.parameters())
        self.assertIsInstance(p, ProjectCUR)
        self.assertEqual(p.rank, 10)
        self.assertEqual(p.max_error, 1)

        widget.setParameters({"rank": 5, "max_error": 0.5})
        p = widget.createinstance(widget.parameters())
        self.assertIsInstance(p, ProjectCUR)
        self.assertEqual(p.rank, 5)
        self.assertEqual(p.max_error, 0.5)
