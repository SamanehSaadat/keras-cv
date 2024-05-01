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

import pytest
try:
    import tensorflow as tf
except ImportError:
    raise ImportError(
        "To use KerasCV, please install TensorFlow: `pip install tensorflow`. "
        "The TensorFlow package is required for data preprocessing with any backend."
    )

from keras_cv.src import version_check


@pytest.fixture(autouse=True)
def cleanup_tf_version():
    actual_tf_version = tf.__version__
    # Tests will be run after yield
    yield

    # Cleanup
    tf.__version__ = actual_tf_version


def test_check_tf_version_error():
    tf.__version__ = "2.10.0"

    with pytest.raises(
        RuntimeError,
        match="Tensorflow package version needs to be at least 2.11.0",
    ):
        version_check.check_tf_version()


def test_check_tf_version_passes_rc2():
    # should pass
    tf.__version__ = "2.13.1rc2"
    version_check.check_tf_version()


def test_check_tf_version_passes_nightly():
    # should pass
    tf.__version__ = "2.14.0-dev20230119"
    version_check.check_tf_version()
