
-- Documents for an event
select @event := 'libya_hotel';

select distinct d.*
from document d
join document_tweet dt on d.id = dt.document_id
join tweet t on dt.tweet_id = t.tweet_id
join event_id e on e.event_id = t.event_id_id
where e.title = @event and d.total_tweets > 1;


-- Tweets of a document
select @doc_id := 1;

select distinct t.tweet_id, t.retweet_of_id, t.in_reply_to_status_id, t.text, u.expanded_clean, u.title
from tweet t
join document_tweet dt on dt.tweet_id = t.tweet_id
join tweet_url tu on tu.tweet_id = t.tweet_id
join url u on u.id = tu.url_id
join event_id e on e.event_id = t.event_id_id
where e.title = @event and dt.document_id = @doc_id;


-- Tweet
select @tweet_id := 560027386171764736;

select t.text, u.expanded_clean, t.retweet_of_id, t.in_reply_to_status_id
from tweet t
join tweet_url tu on t.tweet_id = tu.tweet_id
join url u on u.id = tu.url_id
where t.tweet_id = @tweet_id;


-- Tweets by URL
select @expanded := 'http://www.bbc.co.uk/news/world-africa-31001094';

select t.text, u.expanded_clean
from tweet t
join tweet_url tu on t.tweet_id = tu.tweet_id
join url u on tu.url_id = u.id
where u.expanded_clean = @expanded;


-- cluster
select
@method := 'minibatch_kmeans',
@distance := 'euclidean',
@n_clusters := 3,
@label := 0;

select d.tweet_id, dc.label, d.url, u.expanded_clean, d.total_tweets, d.total_rts, d.total_favs, d.total_replies
from document d
join document_cluster dc on d.id = dc.document_id
join cluster c on c.id = dc.cluster_id
join tweet_url tu on d.tweet_id = tu.tweet_id
join url u on tu.url_id = u.id
where c.method = @method and c.distance = @distance and c.n_clusters = @n_clusters and dc.label = @label;


-- view -- cluster kmeans euclidean
create view __kmeans_libya as
select d.tweet_id, c.n_clusters, dc.label, d.url, u.expanded_clean, d.total_tweets, d.total_rts, d.total_favs, d.total_replies
from document d
left join document_cluster dc on d.id = dc.document_id
left join cluster c on c.id = dc.cluster_id
left join tweet_url tu on d.tweet_id = tu.tweet_id
left join url u on tu.url_id = u.id
where c.method = 'minibatch_kmeans' and c.distance = 'euclidean'
union
select d.tweet_id, c.n_clusters, dc.label, d.url, u.expanded_clean, d.total_tweets, d.total_rts, d.total_favs, d.total_replies
from document d
right join document_cluster dc on d.id = dc.document_id
right join cluster c on c.id = dc.cluster_id
right join tweet_url tu on d.tweet_id = tu.tweet_id
right join url u on tu.url_id = u.id
where c.method = 'minibatch_kmeans' and c.distance = 'euclidean';