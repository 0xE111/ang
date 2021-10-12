from sqlalchemy.types import TypeDecorator, String


class ChoiceType(TypeDecorator):

    impl = String

    def __init__(self, choices, **kw):
        self.choices = dict(choices)
        self.reverse_choices = {v: k for v, k in self.choices.items()}
        super().__init__(**kw)

    def process_bind_param(self, value, dialect):
        return self.reverse_choices[value]

    def process_result_value(self, value, dialect):
        return self.choices[value]
