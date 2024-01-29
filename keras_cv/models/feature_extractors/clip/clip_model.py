# Copyright 2023 The KerasCV Authors
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
from keras_cv.api_export import keras_cv_export
from keras_cv.backend import keras
from keras_cv.backend import ops
from keras_cv.models.feature_extractors.clip.clip_image_encoder import (
    CLIPImageEncoder,
)
from keras_cv.models.feature_extractors.clip.clip_image_encoder import (
    ResidualTransformerEncoder,
)

MODEL_CONFIGS = {
    "CLIP_B16": {
        "embed_dim": 512,
        "context_length": 77,
        "vocab_size": 49408,
        "transformer_width": 512,
        "transformer_heads": 8,
        "transformer_layers": 12,
        "vision_layers": 12,
        "vision_width": 768,
        "image_resolution": 224,
        "vision_patch_size": 16,
    },
}


@keras_cv_export(
    ["keras_cv.models.CLIP", "keras_cv.models.feature_extractors.CLIP"]
)
class CLIP(keras.Model):
    """
        CLIP implements the Contrastive Language-Image Pretraining (CLIP)
        architecture, which enables joint learning of visual and textual
        representations for various downstream tasks.

    Args:
        embed_dim (int): The dimensionality of the joint embedding space for
            images and texts.
        image_resolution (int): The resolution of the input images (both height
            and width).
        vision_layers (int): The number of layers in the vision (image) encoder.
            vision_width (int): The width of the hidden layers in the vision
            encoder.
        vision_patch_size (int): The size of each square patch in the input
            images.
        context_length (int): The maximum length of the contextualized text
            sequences.
        vocab_size (int): The size of the vocabulary for tokenization.
        transformer_width (int): The width of the hidden layers in the
            transformer-based text encoder.
        transformer_heads (int): The number of attention heads in the
            transformer-based text encoder.
        transformer_layers (int): The number of layers in the transformer-based
            text encoder.
    """

    def __init__(
        self,
        embed_dim,
        image_resolution,
        vision_layers,
        vision_width,
        vision_patch_size,
        context_length,
        vocab_size,
        transformer_width,
        transformer_heads,
        transformer_layers,
    ):
        super().__init__()

        self.context_length = context_length

        vision_heads = vision_width // 64
        self.visual = CLIPImageEncoder(
            input_resolution=image_resolution,
            patch_size=vision_patch_size,
            width=vision_width,
            layers=vision_layers,
            heads=vision_heads,
            output_dim=embed_dim,
            name="clip_encoder",
        )

        self.transformer = ResidualTransformerEncoder(
            width=transformer_width,
            layers=transformer_layers,
            heads=transformer_heads,
            attn_mask=self.build_attention_mask(),
            name="residual_transformer_encoder",
        )

        self.vocab_size = vocab_size
        self.token_embedding = keras.layers.Embedding(
            vocab_size,
            transformer_width,
            name="token_embedding",
        )
        self.positional_embedding = self.add_weight(
            shape=[self.context_length, transformer_width],
            name="positional_embedding",
        )
        self.ln_final = keras.layers.LayerNormalization(name="ln_final")

        self.text_projection = self.add_weight(
            shape=(transformer_width, embed_dim), name="text_projection"
        )
        self.logit_scale = keras.Variable(
            ops.ones([]) * ops.log(1 / 0.07), name="logit_scale"
        )
        self.image_embeddings = None
        self.text_embeddings = None

    def build_attention_mask(self):
        mask = ops.ones((self.context_length, self.context_length))
        # Zero out the lower diagonal
        mask = ops.triu(mask)
        return ops.cast(mask, "float32")

    def encode_images(self, image):
        return self.visual(image)

    def encode_text(self, text):
        x = self.token_embedding(text)  # [batch_size, n_ctx, d_model]
        x = x + self.positional_embedding
        x = self.transformer(x)
        x = self.ln_final(x)

        indices = ops.expand_dims(
            ops.cast(ops.argmax(text, axis=1), "int32"), axis=-1
        )
        selected_features = ops.take_along_axis(x, indices[:, :, None], axis=1)
        x = ops.matmul(selected_features, self.text_projection)
        x = ops.squeeze(x, axis=1)
        return x

    def call(self, image, text):
        self.image_embeddings = self.encode_images(image)
        self.text_embeddings = self.encode_text(text)
        normalize_image_features = keras.ops.sqrt(
            keras.ops.sum(
                keras.ops.power(self.image_embeddings, 2), keepdims=True
            )
        )
        normalize_text_features = keras.ops.sqrt(
            keras.ops.sum(
                keras.ops.power(self.text_embeddings, 2), keepdims=True
            )
        )
        self.image_embeddings = self.image_embeddings / normalize_image_features
        self.text_embeddings = self.text_embeddings / normalize_text_features

        logit_scale = ops.exp(self.logit_scale)
        logits_per_image = logit_scale * ops.matmul(
            self.image_embeddings,
            ops.transpose(self.text_embeddings),
        )
        logits_per_text = ops.transpose(logits_per_image)

        return logits_per_image, logits_per_text


def CLIP_B16():
    embed_dim = MODEL_CONFIGS["CLIP_B16"]["embed_dim"]
    context_length = MODEL_CONFIGS["CLIP_B16"]["context_length"]
    vocab_size = MODEL_CONFIGS["CLIP_B16"]["vocab_size"]
    transformer_width = MODEL_CONFIGS["CLIP_B16"]["transformer_width"]
    transformer_heads = MODEL_CONFIGS["CLIP_B16"]["transformer_heads"]
    transformer_layers = MODEL_CONFIGS["CLIP_B16"]["transformer_layers"]
    vision_layers = MODEL_CONFIGS["CLIP_B16"]["vision_layers"]
    vision_width = MODEL_CONFIGS["CLIP_B16"]["vision_width"]
    vision_patch_size = MODEL_CONFIGS["CLIP_B16"]["vision_patch_size"]
    image_resolution = MODEL_CONFIGS["CLIP_B16"]["image_resolution"]

    return CLIP(
        embed_dim,
        image_resolution,
        vision_layers,
        vision_width,
        vision_patch_size,
        context_length,
        vocab_size,
        transformer_width,
        transformer_heads,
        transformer_layers,
    )
