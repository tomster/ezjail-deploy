from ezjaildeploy.stages import Step, Stage, step


class CustomStep(Step):

    def command(self, level=None):
        print "{0} at level {1}".format(self.name, level)


class DummyStage(Stage):

    foo = CustomStep(level=2)

    @step
    def mike(self):
        print "hi, i'm mike!"

    @step
    def bob(self):
        print "hi, i'm bob!"


class PackStuff(Step):

    def command(self, toothbrush=False):
        if toothbrush:
            print "I'm packing a tooth brush"


class TakeTrip(Stage):

    @step
    def book_flight(self):
        print "fly"

    pack_bags = PackStuff(toothbrush=True)

    @step
    def feed_cat(self):
        print "I'll be back soon, kitty!"


def test_steps_assembly():
    stage = DummyStage()
    assert [step.name for step in stage.steps] == ['foo', 'mike', 'bob']


def test_steps_execution():
    stage = DummyStage()
    stage()


def test_stage_assembly():

