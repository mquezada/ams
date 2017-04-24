---
author:
- MQ
bibliography:
- 'refs.bib'
title: Multimodal document model
---

Introduction
============

Definitions
-----------

#### Tweet

A [*tweet*]{} can be seen as a struct with the following fields:

-   [*text*]{}: the textual content of the tweet.

-   [*creation\_date*]{}: a timestamp when the tweet was published.

-   [*no\_retweets*]{}: the amount of times that tweet was shared or
    forwarded by other users.

-   [*no\_likes*]{}: the amount of times users “liked” the tweet.

-   [*user*]{}: an identifier of the user who published the tweet.

#### Summary

Given a set of tweets $E = \{t_1, t_2, \ldots, t_N\}$, called an [
*event*]{}, we want to select a subset $S \subseteq E$ of tweets, called
a [*summary*]{}. The summary must fulfill the following criteria:

-   [**Topical coverage**]{}: the tweets in $S$ must cover the same
    topics as $E$.

-   [**Redundancy**]{}: the content of tweets in $S$ must not be
    redundant with each other.

-   [**Importance**]{}: the tweets in $S$ must be the top $|S|$, with
    respect to $E$, according to a pre-defined ranking function,
    considering into account the previous two criteria. For example, if
    two tweets have the same value according to the ranking, but the two
    of them are equal in terms of content, then only one of them should
    be in $S$.

-   [**Human-manageable size**]{}: the size of $S$ must be of much less
    size than $E$, only if $E$ is large. [**(TODO: define what is
    “large” and how less is “less.”)**]{}

#### Replies and retweets

We denote by $\mathit{URL}(t) = \{u_1, u_2, \ldots, u_m\}$ the URLs
shared by the tweet $t$. $\mathit{URL}(t)$ is empty if $t$ does not
share any URL.

We also denote by $\mathit{replies}(t)$ the set of all tweets $t'$ such
that $t'$ is a [*reply*]{} of $t$, or $t'$ is a reply of another tweet
in $\mathit{replies}(t)$. The same applies to $\mathit{retweets}(t)$,
but by considering [*retweets*]{} instead of replies.

#### Document

We now define a [*document*]{} $d_u$ as a set of tweets, such that those
tweets share the same URL $u$, plus their replies and retweets, that is,

$$d_u = \{t\ :\ u \in \mathit{URL}(t) \lor \exists t'
(t \in \mathit{replies}(t') \lor t \in \mathit{retweets}(t')) \land
u \in \mathit{URL}(t')\}.$$

Note that a tweet $t$ can be a member of different documents, if $t$
shares more than one URL.

Methodology
-----------

We make use of the context of multiple tweets in order to arrange them
into topically similar groups. When a tweet shares an URL $u$, the
content of the tweet can be seen as a description (or [*anchor text*]{})
or a comment on the content of $u$. This also applies when a tweet is a
[*reply*]{} of another tweet: those two tweets (the reply and the
replied) are topically similar, because both of them refers to the same
subject of discussion. We use this context to group tweets into
documents.

Given an event $E$, let $U$ be the set of all the URLs shared across
tweets in $E$. The documents induced by $U$ are all the subsets of
tweets that share at least one URL, $D = \{d_u\ :\ u \in U\}$. Our goal
is to select representative tweets to create $S$, by using $D$ as a
proxy by grouping similar tweets into documents.

One main task is to compare documents. Two documents whose content is
topically similar should be similar according to the features of its
constituents. Note that the documents may have very different sizes, and
it is possible that two different documents are topically similar. This
makes comparing documents a difficult task.
