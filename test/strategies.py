from os import path
from string import ascii_letters, digits, printable

from hypothesis.strategies import composite, lists, text

VALID_ALPHABET = ascii_letters + digits + '-._'


@composite
def s3_bucket_and_key(draw):
    bucket = draw(text(
        alphabet=VALID_ALPHABET,
        min_size=3,
        max_size=5,
    ))
    key_parts = draw(lists(
        elements=text(
            alphabet=VALID_ALPHABET,
            min_size=1,
            max_size=3,
        ),
        min_size=1,
        max_size=3,
    ))
    key = '/'.join(key_parts)
    return bucket, key


@composite
def filepath(draw):
    parts = draw(lists(
        elements=text(
            alphabet=(ascii_letters + digits),
            min_size=1,
            max_size=3,
        ),
        min_size=1,
        max_size=3,
    ))
    return path.join(*parts)


@composite
def image_id(draw):
    organisation = draw(text(
        alphabet=printable,
        min_size=1,
        max_size=3,
    ))
    image_name = draw(text(
        alphabet=printable,
        min_size=1,
        max_size=3,
    ))
    tag = draw(text(
        alphabet=printable,
        max_size=5,
    ))
    args = [organisation, image_name]
    if tag:
        args[-1] = ':{}'.format(tag)
    return '{}/{}'.format(*args)
