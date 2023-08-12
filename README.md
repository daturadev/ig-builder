# InstaForm

InstaForm is designed to provide a passive way to grow successful Instagram accounts for wholesale or personal use.
The concept consists of consistent, niche postings with popular hashtags.
This is hypothesized to gain followers over time. The account is then used/sold along with its credentials.
At this point, the buyer/user has the option to customize the page (already equipped with a high and faithful following)
to his/her liking.

This program aims to use a set of API's to provide automated caption generation
using the current trending hashtags on Instagram. These hashtags are then formed into a
complete post using Pexel's API to fetch relevant photos in combination using a provided keyword.

## Installation

To install necessary requirements:

```
 python3 -m pip install -r requirements.txt
```

## Usage

InstaForm is intended to be ran persistently on a virtual server. Twice per day, at a set time, InstaForm will post a
feed.

To run InstaForm:

```
 python3 main.py -type -keyword -instagramApiKey -pexelsApiKey -userID
```
