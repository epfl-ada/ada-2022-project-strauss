# Youtube’s Toxic Rabitholes

## Abstract

As reported by the [New York Times Magazine](https://www.nytimes.com/2017/08/03/magazine/for-the-new-far-right-youtube-has-become-the-new-talk-radio.html) in 2017, YouTube has become "the new Conservative talk radio" for the far right. Moreover, in 2019, [Kevin Roose depicted](https://www.nytimes.com/interactive/2019/06/08/technology/youtube-radical.html) "countless" stories of young men, looking for direction or distraction on YouTube, ending up "seduced by a community of far-right creators". The existence of a radicalization pipeline on Youtube was strongly suggested by the study [“Auditing Radicalization Pathways on Youtube”, by Ribeiro et al. (2020)](https://dlab.epfl.ch/people/west/pub/HortaRibeiro-Ottoni-West-Almeida-Meira_FAT-20.pdf). In particular, intersections of commenting users across different communities were inspected, as well as users migration. From there, we would like to enlarge the scope of this research by studying the toxicity of the comments and the co-commenting activities in far right channel videos. Doing so, we would like to see if these channels generate more toxic behavior and isolate users. Finally, this project could help find suitable solutions in order to reduce toxicity and attenuate far-right radicalization.

## Research questions
#### Toxicity
- How toxic are the Alt-lite, Intellectual Dark Web (I.D.W) and Alt-right communities, compared to the control group Media?
- How does toxicity level evolve through time among these communities?
- Are toxicity scores and popularity correlated?
#### Clusters
- How toxic are the found clusters?
- [TO BE FILLED]
    
## Proposed additional datasets 
We will base the list of far-right ideology channels on the study [“Auditing Radicalization Pathways on Youtube”, made in 2020 by Ribeiro et al](https://dlab.epfl.ch/people/west/pub/HortaRibeiro-Ottoni-West-Almeida-Meira_FAT-20.pdf). Moreover, we will use from their [data](https://drive.google.com/drive/folders/10r7nMK0-LAIfZws_jk2IpNdsWcrm-oOg?usp=share_link):
- The **vd folder**: datasets with a description of the videos (their `channel_id`, `uploaded date`…) 
- The **cm folder**: datasets about the comments on each video ( `id`, `author`, `author_link`, `authorThumb`, `text`, `likes`, `time`, `edited`, `timestamp`, `hasReplies`).

## Methods
### Toxicity
To deal with the comments’ dataset size (20.6 Go), we can use a cluster. We ‘ll also keep only the strictly necessary data from it (out of all the features we’ll only keep the `text`). If using a cluster does not work, we can use the Monte Carlo method.   

[Detoxify](https://github.com/unitaryai/detoxify) is a machine learning model which rates on a scale from 0 to 1 (0 not at all, 1 very much) a comment to detect if it is toxic or not and to detect if it fits into these subcategories of toxicity: `severe_toxicity`, `obscene`, `identity_attack`, `insult`, `threat`, `sexual_explicit`. A comment is rated 1 in toxicity if it is a very ‘hateful, aggressive, or disrespectful that is very likely to make you leave a discussion or give up on sharing your perspective’. For our analysis, we will keep the toxic category and all of the subcategories as they are independently defined. We’ll store them in a dataframe where the first column is the name of the video and the other columns correspond to the category's score output by detoxify.

<p align="center">
 <img src="./Figures/table_toxicity.jpg"" alt="Table toxicity" width=500"/>
</p>

We’ll denote the `toxic_score_array` of a comment, its array output by detoxify through all categories.

We will compute the average of each category in the `toxic_score_array` over the comments for each of the videos. This allows us to generalize the term `toxic_score_array` to *videos*. Since `toxicity` is the main feature, that the other ones are subfeatures, and also that they are defined independently from each other, we choose to study them independently. The `toxic_score_array` of a *channel* contains the averages of the categories over all comments of its videos. 

Having these results in hand, we will use them to compare the toxicity of each of the extreme communities (Alt-right, Alt-light, IDW) and of the control group (Media). 

We’ll check how the `toxic_score_array` of the videos is distributed per community (are a few videos very toxic but the majority doesn’t care or is every video somewhat toxic?). We’ll also investigate how the `toxic_score_array` evolves with regard to the popularity of a channel or video. We’ll define the popularity of a channel and of a video by its number of views (the more views, the more popular).
Finally we’ll do an analysis over time. We will study the evolutions of the averages (and the distribution) in the `toxic_score_array` of the videos/channels over time. To study this development over time, we’ll group our videos per month based on the upload date.

### Clusters
[TO BE FILLED]


## Proposed timeline
- 22 Nov 2022: 
    - Toxicity: Format the data 
    - Cluster: Generate a complete graph
- 02 Dec 2022: 
    - **Homework 2**
- 06 Dec 2022: 
    - Toxicity: parallelize the ML process and store the data in a table
    - Cluster: computing betweenness centrality
- 08 Dec 2022:
    - Toxicity: study the distribution of the table
    - Cluster: implement and compute min-cut on channels of interest
- 13 Dec 2022: 
    - Compute how toxic are the clusters
- 15 Dec 2022: 
    - Complete implementations and visualizations
- 20 Dec 2022: 
    - Complete datastory
- 23 Dec 2022: 
    - **Project milestone P3**

## Organization within the team
Armelle & Anya: toxicity  
Bartul & Ariane: cluster
