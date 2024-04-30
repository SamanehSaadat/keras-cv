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
        "To use  KerasCV, please install TensorFlow: `pip install tensorflow`. "
        "The TensorFlow package is required for data preprocessing with any backend."
    )

from keras_cv.src.layers import preprocessing
from keras_cv.src.tests.test_case import TestCase


class RandomJpegQualityTest(TestCase):
    def test_return_shapes(self):
        layer = preprocessing.RandomJpegQuality(factor=[0, 100])

        # RGB
        xs = np.ones((2, 512, 512, 3))
        xs = layer(xs)
        self.assertEqual(xs.shape, (2, 512, 512, 3))

        # greyscale
        xs = np.ones((2, 512, 512, 1))
        xs = layer(xs)
        self.assertEqual(xs.shape, (2, 512, 512, 1))

    def test_in_single_image(self):
        layer = preprocessing.RandomJpegQuality(factor=[0, 100])

        # RGB
        xs = tf.cast(
            np.ones((512, 512, 3)),
            dtype="float32",
        )

        xs = layer(xs)
        self.assertEqual(xs.shape, (512, 512, 3))

        # greyscale
        xs = tf.cast(
            np.ones((512, 512, 1)),
            dtype="float32",
        )

        xs = layer(xs)
        self.assertEqual(xs.shape, (512, 512, 1))

    def test_non_square_images(self):
        layer = preprocessing.RandomJpegQuality(factor=[0, 100])

        # RGB
        xs = np.ones((2, 256, 512, 3))
        xs = layer(xs)
        self.assertEqual(xs.shape, (2, 256, 512, 3))

        # greyscale
        xs = np.ones((2, 256, 512, 1))
        xs = layer(xs)
        self.assertEqual(xs.shape, (2, 256, 512, 1))
