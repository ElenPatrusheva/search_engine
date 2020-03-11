
from wtforms import Form, StringField #, SelectField
class QueryForm(Form):
    
    '''
    choices = [('Artist', 'Artist'),
               ('Album', 'Album'),
               ('Publisher', 'Publisher')]
    select = SelectField('Search for music:', choices=choices)
    '''
    search = StringField('')