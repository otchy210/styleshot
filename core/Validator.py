# -*- coding: utf-8 -*-

class Validator:
    def __init__(self, defs, labels):
        self.defs = defs
        self.labels = labels

    def validate(self, form):
        errors = {}
        for k, v in form.items():
            if k in self.defs:
                for f in self.defs[k]:
                    error = f(v, self.labels[k])
                    if error:
                        errors[k] = error
                        break
        return errors

    @staticmethod
    def required(value, label):
        if len(value) == 0:
            return u'{} は必須入力です。'.format(label)
        return None
