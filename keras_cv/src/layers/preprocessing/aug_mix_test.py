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

try:
    import tensorflow as tf
except ImportError:
    raise ImportError(
        "To use  KerasCV, please install TensorFlow: `pip install tensorflow`. "
        "The TensorFlow package is required for data preprocessing with any backend."
    )

from keras_cv.src.layers import preprocessing
from keras_cv.src.tests.test_case import TestCase


class AugMixTest(TestCase):
    def test_return_shapes(self):
        layer = preprocessing.AugMix([0, 255])

        # RGB
        xs = tf.ones((2, 512, 512, 3))
        xs = layer(xs)
        ys_segmentation_masks = tf.ones((2, 512, 512, 3))
        ys_segmentation_masks = layer(ys_segmentation_masks)
        self.assertEqual(xs.shape, (2, 512, 512, 3))
        self.assertEqual(ys_segmentation_masks.shape, (2, 512, 512, 3))

        # greyscale
        xs = tf.ones((2, 512, 512, 1))
        xs = layer(xs)
        ys_segmentation_masks = tf.ones((2, 512, 512, 1))
        ys_segmentation_masks = layer(ys_segmentation_masks)
        self.assertEqual(xs.shape, (2, 512, 512, 1))
        self.assertEqual(ys_segmentation_masks.shape, (2, 512, 512, 1))

    def test_in_single_image_and_mask(self):
        layer = preprocessing.AugMix([0, 255])

        # RGB
        xs = tf.cast(
            tf.ones((512, 512, 3)),
            dtype=tf.float32,
        )

        xs = layer(xs)
        ys_segmentation_masks = tf.cast(
            tf.ones((512, 512, 3)),
            dtype=tf.float32,
        )

        ys_segmentation_masks = layer(ys_segmentation_masks)
        self.assertEqual(xs.shape, (512, 512, 3))
        self.assertEqual(ys_segmentation_masks.shape, (512, 512, 3))

        # greyscale
        xs = tf.cast(
            tf.ones((512, 512, 1)),
            dtype=tf.float32,
        )

        xs = layer(xs)
        ys_segmentation_masks = tf.cast(
            tf.ones((512, 512, 1)),
            dtype=tf.float32,
        )
        ys_segmentation_masks = layer(ys_segmentation_masks)
        self.assertEqual(xs.shape, (512, 512, 1))
        self.assertEqual(ys_segmentation_masks.shape, (512, 512, 1))

    def test_non_square_images_and_masks(self):
        layer = preprocessing.AugMix([0, 255])

        # RGB
        xs = tf.ones((2, 256, 512, 3))
        xs = layer(xs)
        ys_segmentation_masks = tf.ones((2, 256, 512, 3))
        ys_segmentation_masks = layer(ys_segmentation_masks)
        self.assertEqual(xs.shape, (2, 256, 512, 3))
        self.assertEqual(ys_segmentation_masks.shape, (2, 256, 512, 3))

        # greyscale
        xs = tf.ones((2, 256, 512, 1))
        xs = layer(xs)
        ys_segmentation_masks = tf.ones((2, 256, 512, 1))
        ys_segmentation_masks = layer(ys_segmentation_masks)
        self.assertEqual(xs.shape, (2, 256, 512, 1))
        self.assertEqual(ys_segmentation_masks.shape, (2, 256, 512, 1))

    def test_single_input_args(self):
        layer = preprocessing.AugMix([0, 255])

        # RGB
        xs = tf.ones((2, 512, 512, 3))
        xs = layer(xs)
        ys_segmentation_masks = tf.ones((2, 512, 512, 3))
        ys_segmentation_masks = layer(ys_segmentation_masks)
        self.assertEqual(xs.shape, (2, 512, 512, 3))
        self.assertEqual(ys_segmentation_masks.shape, (2, 512, 512, 3))

        # greyscale
        xs = tf.ones((2, 512, 512, 1))
        xs = layer(xs)
        ys_segmentation_masks = tf.ones((2, 512, 512, 1))
        ys_segmentation_masks = layer(ys_segmentation_masks)
        self.assertEqual(xs.shape, (2, 512, 512, 1))
        self.assertEqual(ys_segmentation_masks.shape, (2, 512, 512, 1))

    def test_many_augmentations(self):
        layer = preprocessing.AugMix([0, 255], chain_depth=[25, 26])

        # RGB
        xs = tf.ones((2, 512, 512, 3))
        xs = layer(xs)
        ys_segmentation_masks = tf.ones((2, 512, 512, 3))
        ys_segmentation_masks = layer(ys_segmentation_masks)
        self.assertEqual(xs.shape, (2, 512, 512, 3))
        self.assertEqual(ys_segmentation_masks.shape, (2, 512, 512, 3))

        # greyscale
        xs = tf.ones((2, 512, 512, 1))
        xs = layer(xs)
        ys_segmentation_masks = tf.ones((2, 512, 512, 1))
        ys_segmentation_masks = layer(ys_segmentation_masks)
        self.assertEqual(xs.shape, (2, 512, 512, 1))
        self.assertEqual(ys_segmentation_masks.shape, (2, 512, 512, 1))
