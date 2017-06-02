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
    organisation = draw(text(alphabet=printable))
    image_name = draw(text(alphabet=printable))
    tag = draw(text(alphabet=printable))
    return "{}/{}:{}".format(organisation, image_name, tag)
