import unittest
from should_dsl import should, should_not
from fluidity.machine import StateMachine, event
from fluidity.machine import InvalidTransition, InvalidConfiguration


class FluidityStateMachine(unittest.TestCase):

    def it_defines_states(self):
        class MyMachine(StateMachine):
            states = ['unread', 'read', 'closed']
            initial_state = 'read'
        machine = MyMachine()
        machine |should| have(3).states
        machine.states |should| include_all_of(['unread', 'read', 'closed'])

    def it_has_an_initial_state(self):
        class MyMachine(StateMachine):
            initial_state = 'closed'
            states = ['open', 'closed']
        machine = MyMachine()
        machine.initial_state |should| equal_to('closed')
        machine.current_state |should| equal_to('closed')


class FluidityConfigurationValidation(unittest.TestCase):

    def it_requires_at_least_two_states(self):
        class MyMachine(StateMachine):
            pass
        MyMachine |should| throw(InvalidConfiguration,
            message="There must be at least two states")
        class OtherMachine(StateMachine):
            states = ['open']
        OtherMachine |should| throw(InvalidConfiguration,
            message="There must be at least two states")

    def it_requires_an_initial_state(self):
        class MyMachine(StateMachine):
            states = ['open', 'closed']
        MyMachine |should| throw(InvalidConfiguration,
            message="There must exist an initial state")
        class AnotherMachine(StateMachine):
            states = ['open', 'closed']
            initial_state = None
        AnotherMachine |should| throw(InvalidConfiguration,
            message="There must exist an initial state")


class MyMachine(StateMachine):
     initial_state = 'created'
     states = ['created', 'waiting', 'processed']
     event('queue', from_='created', to='waiting')
     event('process', from_='waiting', to='processed')


class FluidityEvent(unittest.TestCase):

    def its_declaration_creates_a_method_with_its_name(self):
        machine = MyMachine()
        machine |should| respond_to('queue')
        machine |should| respond_to('process')

    def it_changes_machine_state(self):
        machine = MyMachine()
        machine.current_state |should| equal_to('created')
        machine.queue()
        machine.current_state |should| equal_to('waiting')
        machine.process()
        machine.current_state |should| equal_to('processed')

    def it_ensures_event_order(self):
        machine = MyMachine()
        machine.process |should| throw(InvalidTransition)
        machine.queue()
        machine.queue |should| throw(InvalidTransition)
        machine.process |should_not| throw(Exception)
