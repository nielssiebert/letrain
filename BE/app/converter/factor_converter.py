from ..model.factor import Factor


class FactorConverter:
    pass
    
    def to_dict(self, factor):
        return {
            'id': factor.id,
            'name': factor.name,
            'factor': factor.factor,
            'triggers': [trigger.id for trigger in factor.triggers]
        }

    @staticmethod
    def from_dict(data):
        return Factor(**data)