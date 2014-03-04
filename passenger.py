# -*- coding: utf-8 -*-


class Passenger:
    def __init__(self,
                 first_name,
                 last_name,
                 age,
                 is_male=True,
                 document_type=None,
                 document_number=None,
                 document_expires=None):
        self.first_name = first_name
        self.last_name = last_name
        self.age = age
        self.is_male = is_male
        self.document_type = document_type
        self.document_number = document_number
        self.document_expires = document_expires
