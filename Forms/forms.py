from wtforms import Form, validators, SelectField


class SelectionForm(Form):
    event = SelectField(u'Evento', id='events_1', coerce=str, validators=[validators.required(),validators.DataRequired()],
                        choices=[('',''),('libya_hotel', 'Libia Hotel'), (
                            'oscar_pistorius', 'Jucio Oscar Pistorius'), ('microsoft_nokia', 'Microsoft buys Nokia')])
    clustering = SelectField(u'Clustering', id='events_2', coerce=str, validators=[validators.DataRequired()],
                             choices=[])
    n_clusters = SelectField(u'Número de Clusters', id='events_3', coerce=str, validators=[validators.DataRequired()],
                             choices=[])
    order = SelectField(u'Ordenamiento', id='events_4', coerce=int, validators=[validators.required(), validators.DataRequired()],
                        choices=[(2, 'Total Tweets'), (3, 'Total Retweets'), (4, 'Total Favs'), (5, 'Total Replies')])
