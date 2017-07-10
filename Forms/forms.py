from wtforms import Form, validators, SelectField, BooleanField


class SelectionForm(Form):
    event = SelectField(u'Evento', id='events_1', coerce=str, validators=[validators.required(),validators.DataRequired()],
                        choices=[('',''),('43911', 'Libia Hotel'), (
                            '13472', 'Jucio Oscar Pistorius'), ('91', 'Microsoft buys Nokia')])
    clustering = SelectField(u'Clustering', id='events_2', coerce=str, validators=[validators.DataRequired()],
                             choices=[])
    n_clusters = SelectField(u'Número de Clusters', id='events_3', coerce=str, validators=[validators.DataRequired()],
                             choices=[])
    order = SelectField(u'Ordenamiento', id='events_4', coerce=str, validators=[validators.required(), validators.DataRequired()],
                        choices=[('total_tweets', 'Total Tweets'), ('total_rts', 'Total Retweets'), ('total_favs', 'Total Favs'), ('total_replies', 'Total Replies')])
    sort = BooleanField(u'Ordenar Topicos', id='sort',default=False)