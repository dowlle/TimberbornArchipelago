from test.bases import WorldTestBase
from .. import TimberbornWorld


class TimberbornTestBase(WorldTestBase):
    game = "Timberborn"
    world: TimberbornWorld
