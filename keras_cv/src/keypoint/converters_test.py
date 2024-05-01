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

import itertools

import numpy as np
try:
    import tensorflow as tf
except ImportError:
    raise ImportError(
        "To use KerasCV, please install TensorFlow: `pip install tensorflow`. "
        "The TensorFlow package is required for data preprocessing with any backend."
    )
from absl.testing import parameterized

from keras_cv.src import keypoint
from keras_cv.src.tests.test_case import TestCase

xy_keypoints = np.array(
    [[[10, 20], [110, 120], [210, 220]], [[20, 30], [120, 130], [220, 230]]],
    dtype="float32",
)
rel_xy_keypoints = np.array(
    [
        [[0.01, 0.04], [0.11, 0.24], [0.21, 0.44]],
        [[0.02, 0.06], [0.12, 0.26], [0.22, 0.46]],
    ],
    dtype="float32",
)

images = np.ones([2, 500, 1000, 3])

keypoints = {
    "xy": xy_keypoints,
    "rel_xy": rel_xy_keypoints,
}

test_cases = [
    (f"{source}_{target}", source, target)
    for (source, target) in itertools.permutations(keypoints.keys(), 2)
] + [("xy_xy", "xy", "xy")]


class ConvertersTestCase(TestCase):
    @parameterized.named_parameters(*test_cases)
    def test_converters(self, source, target):
        source_keypoints = keypoints[source]
        target_keypoints = keypoints[target]
        self.assertAllClose(
            keypoint.convert_format(
                source_keypoints, source=source, target=target, images=images
            ),
            target_keypoints,
        )

    @parameterized.named_parameters(*test_cases)
    def test_converters_unbatched(self, source, target):
        source_keypoints = keypoints[source][0]
        target_keypoints = keypoints[target][0]

        self.assertAllClose(
            keypoint.convert_format(
                source_keypoints, source=source, target=target, images=images[0]
            ),
            target_keypoints,
        )

    @parameterized.named_parameters(*test_cases)
    def test_converters_ragged_groups(self, source, target):
        source_keypoints = keypoints[source]
        target_keypoints = keypoints[target]

        def create_ragged_group(ins):
            res = []
            for b, groups in zip(ins, [[1, 2], [0, 3]]):
                res.append(tf.RaggedTensor.from_row_lengths(b, groups))
            return tf.stack(res, axis=0)

        source_keypoints = create_ragged_group(source_keypoints)
        target_keypoints = create_ragged_group(target_keypoints)

        self.assertAllClose(
            keypoint.convert_format(
                source_keypoints, source=source, target=target, images=images
            ),
            target_keypoints,
        )

    @parameterized.named_parameters(*test_cases)
    def test_converters_with_metadata(self, source, target):
        source_keypoints = keypoints[source]
        target_keypoints = keypoints[target]

        def add_metadata(ins):
            return tf.concat([ins, np.ones([2, 3, 5])], axis=-1)

        source_keypoints = add_metadata(source_keypoints)
        target_keypoints = add_metadata(target_keypoints)

        self.assertAllClose(
            keypoint.convert_format(
                source_keypoints, source=source, target=target, images=images
            ),
            target_keypoints,
        )

    def test_raise_errors_when_missing_shape(self):
        with self.assertRaises(ValueError) as e:
            keypoint.convert_format(
                keypoints["xy"], source="xy", target="rel_xy"
            )

        self.assertEqual(
            str(e.exception),
            "convert_format() must receive `images` when transforming "
            "between relative and absolute formats. convert_format() "
            "received source=`xy`, target=`rel_xy`, but images=None",
        )

    @parameterized.named_parameters(
        (
            "keypoint_rank",
            np.ones([2, 3, 4, 2, 1]),
            None,
            "Expected keypoints rank to be in [2, 4], got "
            "len(keypoints.shape)=5.",
        ),
        (
            "images_rank",
            np.ones([4, 2]),
            np.ones([35, 35]),
            "Expected images rank to be 3 or 4, got len(images.shape)=2.",
        ),
        (
            "batch_mismatch",
            np.ones([2, 4, 2]),
            np.ones([35, 35, 3]),
            "convert_format() expects both `keypoints` and `images` to be "
            "batched or both unbatched. Received len(keypoints.shape)=3, "
            "len(images.shape)=3. Expected either len(keypoints.shape)=2 and "
            "len(images.shape)=3, or len(keypoints.shape)>=3 and "
            "len(images.shape)=4.",
        ),
    )
    def test_input_format_exception(self, keypoints, images, expected):
        with self.assertRaises(ValueError) as e:
            keypoint.convert_format(
                keypoints, source="xy", target="rel_xy", images=images
            )
        self.assertEqual(str(e.exception), expected)
