from django import template

from blocks.puzzles import puzzles_block_context

register = template.Library()


@register.inclusion_tag("blocks/puzzles_block.html")
def puzzles_block():
    """The GroundUp Puzzles block. See blocks/puzzles.py."""
    return puzzles_block_context()
