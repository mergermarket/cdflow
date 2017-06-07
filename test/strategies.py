from os import path
from string import printable, ascii_letters, digits

from hypothesis.strategies import composite, lists, text


VALID_ALPHABET = ascii_letters + digits + '-._'


@composite
def filepath(draw):
    parts = draw(lists(
        elements=text(alphabet=(ascii_letters+digits)), min_size=1
    ))
    return path.join(*parts)


@composite
def image_id(draw):
    organisation = draw(text(alphabet=printable, min_size=1))
    image_name = draw(text(alphabet=printable, min_size=1))
    tag = draw(text(alphabet=printable))
    args = [organisation, image_name]
    if tag:
        args[-1] = ':{}'.format(tag)
    return '{}/{}'.format(*args)
