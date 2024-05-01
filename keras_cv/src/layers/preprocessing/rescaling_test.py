# Copyright 2022 The KerasCV Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import numpy as np
try:
    import tensorflow as tf
except ImportError:
    raise ImportError(
        "To use KerasCV, please install TensorFlow: `pip install tensorflow`. "
        "The TensorFlow package is required for data preprocessing with any backend."
    )

from keras_cv.src.backend import ops
from keras_cv.src.layers.preprocessing.rescaling import Rescaling
from keras_cv.src.tests.test_case import TestCase


class RescalingTest(TestCase):
    def test_rescaling_correctness_float(self):
        layer = Rescaling(scale=1.0 / 127.5, offset=-1.0)
        inputs = tf.random.uniform((2, 4, 5, 3))
        outputs = layer(inputs)
        self.assertAllClose(outputs, inputs * (1.0 / 127.5) - 1)

    def test_rescaling_correctness_int(self):
        layer = Rescaling(scale=1.0 / 127.5, offset=-1)
        inputs = tf.random.uniform((2, 4, 5, 3), 0, 100, dtype="int32")
        outputs = layer(inputs)
        outputs = ops.convert_to_numpy(outputs)
        self.assertEqual(outputs.dtype.name, "float32")
        self.assertAllClose(
            outputs, ops.convert_to_numpy(inputs) * (1.0 / 127.5) - 1
        )

    def test_config_with_custom_name(self):
        layer = Rescaling(0.5, name="rescaling")
        config = layer.get_config()
        layer_1 = Rescaling.from_config(config)
        self.assertEqual(layer_1.name, layer.name)

    def test_unbatched_image(self):
        layer = Rescaling(scale=1.0 / 127.5, offset=-1)
        inputs = tf.random.uniform((4, 5, 3))
        outputs = layer(inputs)
        self.assertAllClose(outputs, inputs * (1.0 / 127.5) - 1)

    def test_output_dtypes(self):
        inputs = np.array([[[1], [2]], [[3], [4]]], dtype="float64")
        layer = Rescaling(0.5)
        self.assertAllEqual(
            ops.convert_to_numpy(layer(inputs)).dtype.name, "float32"
        )
        layer = Rescaling(0.5, dtype="uint8")
        self.assertAllEqual(
            ops.convert_to_numpy(layer(inputs)).dtype.name, "uint8"
        )
