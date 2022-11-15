import io
import warnings

import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
from PIL import Image
from stability_sdk import client

import config

stability_api = client.StabilityInference(
    key=config.stability_key,
    verbose=True,
)


def generate(prompt: str, seed: int = None, steps: int = None):
    # the object returned is a python generator
    answers = stability_api.generate(
        prompt=prompt,
        seed=seed,  # if provided, specifying a random seed makes results deterministic
        steps=steps,  # defaults to 50 if not specified
    )

    # iterating over the generator produces the api response
    for resp in answers:
        for artifact in resp.artifacts:
            if artifact.finish_reason == generation.FILTER:
                warnings.warn(
                    "Your request activated the API's safety filters and could not be processed."
                    "Please modify the prompt and try again.")
                raise Exception('bad prompt')
            if artifact.type == generation.ARTIFACT_IMAGE:
                img = Image.open(io.BytesIO(artifact.binary))
                return img
