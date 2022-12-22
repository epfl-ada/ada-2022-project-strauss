#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import time
import math
from scipy.stats import spearmanr #to compute spearman correlation
from scipy.stats import pearsonr #to compute pearson correlation
from scipy.stats import kendalltau #to compute kendall tau correlation


# In[6]:


data_folder = '../Data/' # all my data is in one folder 
path_sources_final='sources_final.csv'
path_control_grp='sources_1.csv'
path_df1='df_1.csv'
path_df2='df_2.csv'

# color palette: 
ex_palette = sns.color_palette('deep')
palette=[ex_palette[0], 'darkorange', ex_palette[2], ex_palette[7]]


# In[7]:


#getting our necessary datasets
df_sources_final=pd.read_csv(data_folder + path_sources_final) #maps channel_id to extreme grp corresponding
df_1=pd.read_csv(data_folder + path_df1)
df_2=pd.read_csv(data_folder + path_df2)


# In[8]:


#combining the two dataframes from the two folders 
#(should do it right from the begining? I was afraid it would slow things to have a dataframe so big)
df=pd.concat([df_1, df_2],ignore_index=True)


# In[9]:


#extracting only necessary columns
df_sources=df_sources_final[["Category", "Id"]]
df_sources.rename(columns = {'Id':'channel_id'}, inplace = True)


# In[10]:


df_sources.head()


# In[11]:


#checking for NaN values
print("there are", len(df_sources[df_sources.isnull().any(axis=1)]), "Nan values")


# In[12]:


df.head()


# In[13]:


#checking for NaN values
print("there are", len(df[df.isnull().any(axis=1)]), "Nan values")


# In[14]:


#we have more channels in df than in df_sources but the difference is small


# In[15]:


df_final=df.merge(df_sources, how='left', on='channel_id')
df_final.head()


# In[16]:


#overwriting the category for the channels belonging to the control group
df_control_=pd.read_csv(data_folder + path_control_grp) #maps channel_id to extreme grp corresponding


# In[17]:


#list of channels belonging to control grp
list_control_=(df_control_[df_control_["Data Collection step"]=='control'].Id).tolist()


# In[18]:


df_final.loc[df_final["channel_id"].isin(list_control_), "Category"] = 'Control'


# In[19]:


#checking for NaN values
nb_Nan=len(df_final[df_final.isnull().any(axis=1)])
print("there are", nb_Nan, "Nan values which corresponds to", nb_Nan*100/len(df_final), "% of the dataframe")


# In[16]:


#dropping NaN values
df_final.dropna(inplace=True)
nb_Nan=len(df_final[df_final.isnull().any(axis=1)])
print("there are", nb_Nan, "Nan values which corresponds to", nb_Nan*100/len(df_final), "% of the dataframe")


# In[20]:


# correct the duplicated category
df_final.loc[df_final.Category == 'PUA ', 'Category'] = 'PUA'

#Notice None means "not associated to anything" and not "Nan" 
df_final.Category.value_counts()


# In[21]:


#MGTOW men going their own way, anti feminist misogynistic politic group

#MRA men's rights activist (again anti feminist)

#Incel a member of an online community of young men who consider themselves unable to attract women sexually, 
#typically associated with views that are hostile towards women and men who are sexually active:

#Pick up : online community sharing tips on how to pick up women


# In[22]:


# Some lists

# selection of channel categories
list_categories = ['Alt-lite', 'Alt-right', 'Intellectual Dark Web', 'Control']
# subcategories of toxicity
list_subcat_tox = ['severe_toxicity', 'obscene', 'identity_attack', 'insult', 'threat', 'sexual_explicit']
list_subcat_tox_titles = ['Severe toxicity', 'Obscene', 'Identity attack', 'Insult', 'Threat', 'Sexual explicit']
# all categories of toxicity
list_all_tox = ['toxicity'] + list_subcat_tox
list_all_tox_titles = ['Toxicity'] + list_subcat_tox_titles

#colors associated to each community
list_colors=['b','orange','g','r']
#alt-lite is |alt-right is |IDW is | Control is 


# ### Let's start our analysis

# Now that we have our dataframe and all the values we want we can start our analysis. 
# We're keeping only Alt-lite, Alt-right, Intellectual Dark Web channels and control channels. 

# In[25]:


#getting some basic information 
colors=[palette[3], palette[0], palette[2], palette[1]]
df_extreme=df_final.loc[df_final['Category'].isin(list_categories)]
""" fig = df_extreme.Category.value_counts().plot.pie(autopct='%.1f%%', colors=colors, title = "Number of videos per category")


# **Comments:** We see that we have a lot of data coming associated to the category 'Control'. This is good as it reduces the variance.

# In[21]:


colors=[palette[2], palette[1], palette[3], palette[0]]
ax = sns.boxplot(x="Category", y="toxicity", data=df_extreme, palette=colors)


# **Comments:** In my opinion we don't see much. 
# 
# We see that control's mean is the lowest which would mean that on average the comments made on videos belonging to Control are less toxic than the ones made on videos belonging to the other groups. But control has a large variance so it is though to compare Control to IDW and Alt-right. 
# 
# Alt-lit has the highest means and its interval \[Q_1, Q_2\] seems higher than the one for all other groups/categories.

# In[22]:


fig, axes = plt.subplots(3, 2, figsize=(14, 18))

fig.suptitle('Distribution of the toxic subcategory per category', fontsize='x-large')

k=0

for i in range(3):
    for j in range(2):
        sns.boxplot(ax=axes[i,j], x="Category", y=list_subcat_tox[k], data=df_extreme, palette=colors)
        k+=1


# **Comments:** For the subtoxicities 'threat', 'sexual_explicit', 'severe_toxicity' we don't seem as the inter-quartile interval is small.
# 
# For the subtoxicities:
# - identity_attack: Alt-right highest mean, highest inter-quartile interval
# - insult: Alt-lite highest mean, highest inter-quartile interval, although Control has a very large inter-quartile interval
# - obscene: Control has the smallest values, Alt-lite and IDW have highest values

# In[23]:


#same thing but with percentages (to be deleted?? discussion)

fig, ax = plt.subplots(2,2,figsize= (7,5), sharey = True, sharex = True) 

for i in range(4):
    sbplt = ax[i%2, math.floor(i/2)]
    df=df_extreme.loc[df_extreme['Category']==list_categories[i]]
    df_control=df_extreme.loc[df_extreme['Category']==list_categories[3]]
    sbplt.hist(df['toxicity'].values, bins = 50, color = palette[i], weights=np.ones(len(df['toxicity'])) / len(df['toxicity']), alpha=0.7, label=list_categories[i])
    sbplt.hist(df_control['toxicity'].values, bins = 50, color = palette[3], weights=np.ones(len(df_control['toxicity'])) / len(df_control['toxicity']), alpha=0.6, label='Control')
    sbplt.set_title(list_categories[i])
    sbplt.legend(loc='upper right')
    
fig.tight_layout()

fig.text(0.4,0, "toxicity level")
fig.text(0,0.6, "Percentage of videos", rotation = 90)


# **Comments:** They all have a right skewed distribution-> more low-toxicity score comments than high.
# 
# They all have a peak in 0 and then another one around
# - 0.25 for Alt-lite
# - 0.2 for IDW
# - 0.18 for Alt-right
# - 0.2 for Control 
# 
# By looking at the distribution, we see that a bigger proportion of videos are associated to higher toxicities in the extreme categories than in the control group.

# In[24]:


#define an histogram for the distribution 
fig, ax = plt.subplots(len(list_subcat_tox),3,figsize= (10,12), sharey = False, sharex = True) #chose sharey=False as we are interested 
#the distribution, not the exact values

for i in range (len(list_subcat_tox)):
    for j in range(3):
        sbplt = ax[i, j]
        df=df_extreme.loc[df_extreme['Category']==list_categories[j]]
        sbplt.hist(df[list_subcat_tox[i]].values, bins = 50, color = palette[j], weights=np.ones(len(df[list_subcat_tox[i]])) / len(df[list_subcat_tox[i]]), alpha=0.7, label=list_categories[j])
        sbplt.hist(df_control[list_subcat_tox[i]].values, bins = 50, color = palette[3], weights=np.ones(len(df_control[list_subcat_tox[i]])) / len(df_control[list_subcat_tox[i]]), alpha=0.6, label='Control')
        sbplt.set_title(list_categories[j]+' '+list_subcat_tox[i])
        sbplt.legend(loc='upper right')
    
fig.tight_layout()

fig.text(0.4,0, "Score per toxic subcategory")
fig.text(0,0.6, "Percentage of videos", rotation = 90)


# **Comments:** severe toxicity has values so small we don't see anything/is it even worth it to say something? 
# - they all are much more obscene than the control group
# - alt right and alt lite seem to have a little more identity attack
# - all have more insults than control
# - not so many threats, all the same
# - alt-lite has more sexual explicit (but note obvious)
# 

# ## Are toxicity scores and popularity correlated?

# Recall that we define the popularity of a video/channel by its number of views. 

# In[25]:


#define an histogram for the distribution 
fig, ax = plt.subplots(2,2,figsize= (7,4), sharey = False, sharex = False) #chose sharey=False and sharex=False 
#as we are interested the distribution, not the exact values

for i in range(4):
    sbplt = ax[i%2, math.floor(i/2)]
    ax[i%2, math.floor(i/2)].set_yscale('log')
    df=df_extreme.loc[df_extreme['Category']==list_categories[i]]
    sbplt.hist(df['view_count'].values, bins = 100, color = palette[i], weights=np.ones(len(df['view_count'])) / len(df['view_count']))
    sbplt.set_title(list_categories[i])
    
fig.tight_layout()

fig.text(0.4,0, "view_count")
fig.text(0,0.6, "percentage_videos", rotation = 90)


# **Comments:** We notice that the distribution is right-skewed. We take that in account when computing by creating the column "log_view_count", which is the log of the column "view_count". 

# In[26]:


df_extreme['log_view_count'] = np.log(df_extreme['view_count'])


# In[27]:


#for this part to work, in seaborn/distributions.py, function  _freedman_diaconis_bins(a) needs to be changed:
'''
def _freedman_diaconis_bins(a):
    '''Calculate number of hist bins using Freedman-Diaconis rule.'''
    # From https://stats.stackexchange.com/questions/798/
    a = np.asarray(a)
    if len(a) < 2:
        return 1
    iqr = np.subtract.reduce(np.nanpercentile(a, [75, 25]))
    h = 2 * iqr / (len(a) ** (1 / 3))
    # fall back to sqrt(a) bins if iqr is 0
    if h == 0:
        return int(np.sqrt(a.size))
    else:
        if np.ceil((a.max() - a.min()) / h) > 1e10:
                return 1e10
        else:
            return int(np.ceil((a.max() - a.min()) / h))
'''
#otherwise there is an issue with np.ceil((a.max() - a.min()) / h) being infinity, and not be changed to integers.

for i, category in enumerate(list_categories):
        df=df_extreme.loc[df_extreme['Category']==category]
        p = sns.jointplot(x='toxicity', y='log_view_count', data = df, kind='hex', color=palette[i],  joint_kws=dict(bins='log'))
        p.fig.suptitle(category)
        #p.ax_marg_x.remove()
        #p.ax_marg_y.remove()
        


# **Comments:** We see that the data is very polarized i.e. in all 4 cases there is a very large proportion of data in one spot. This could lead us to believe there is no correlation between toxicity and the view_count.

# In[28]:


#generalization to all subtoxicities

for j, subtoxicity in enumerate(list_subcat_tox):
    for i, category in enumerate(list_categories):
        df=df_extreme.loc[df_extreme['Category']==category]
        p = sns.jointplot(x=subtoxicity, y='log_view_count', data = df, kind='hex', color=palette[i],  joint_kws=dict(bins='log'))
        p.fig.suptitle(category)
        #p.ax_marg_x.remove()
        #p.ax_marg_y.remove()
        


# In[29]:


#Spearman's correlation, how well can the data be approcimated by a monotonic function
#Pearson's correlation, how well can the data be approximated by a linear function
#Kendall Tau'correlation, how well can the data be approximated in terms of "coherant pairs" (ex: a lot of data in the top right 
#a lot in the bottom left, and none elsewhere)

for i in list_categories:
    df=df_extreme.loc[df_extreme['Category']==i]
    print(i)
    rho_1, p_1=spearmanr(df['toxicity'], df['view_count'])
    print("spearman correlation coefficient is equal to", np.round(rho_1,3), "with an associated p-value of", np.round(p_1,3))
    rho_2, p_2=pearsonr(df['toxicity'], df['view_count'])
    print("pearson correlation coefficient is equal to", np.round(rho_2,3), "with an associated p-value of", np.round(p_2,3))
    rho_3, p_3=kendalltau(df['toxicity'], df['view_count'])
    print("kendall tau correlation coefficient is equal to", np.round(rho_3,3), "with an associated p-value of", np.round(p_3,3))


# **Comments:** We notice all p-values are less than 0.05 so we can reject the null hypothesis saying there is a 0 correlation. (Notice however that it doesn't exclude the case where the correlation found is very small, in this case we'll say there is a weak correlation)
# 
# - For Alt lite, spearman is the highest correlation coeficient (correlation following a monotonous fction) but it is little -> weak correlation
# - Alt-right spearman is the highest correlation coeficient (correlation following a monotonous fction) but it is little -> weak correlation
# - IDW spearman is the highest correlation coeficient (correlation following a monotonous fction) but it is little -> weak correlation
# - Control spearman is the highest correlation coeficient (correlation following a monotonous fction) but it is little -> weak correlation
# 
# They all have the same behaviour as the control group so we don't see any behaviour that could be caracteristic of extreme communities. 

# In[30]:


#generalizing to subtoxicities

for j, subtoxicity in enumerate(list_subcat_tox): 
    print('\033[1m'+subtoxicity+'\033[0m')
    for i in list_categories:
        df=df_extreme.loc[df_extreme['Category']==i]
        print('  '+i)
        rho_1, p_1=spearmanr(df[subtoxicity], df['view_count'])
        print("spearman correlation coefficient is equal to", np.round(rho_1,3), "with an associated p-value of", np.round(p_1,3))
        rho_2, p_2=pearsonr(df[subtoxicity], df['view_count'])
        print("pearson correlation coefficient is equal to", np.round(rho_2,3), "with an associated p-value of", np.round(p_2,3))
        rho_3, p_3=kendalltau(df[subtoxicity], df['view_count'])
        print("kendall tau correlation coefficient is equal to", np.round(rho_3,3), "with an associated p-value of", np.round(p_3,3))


# **Comments:** There is always **maximal** a difference of 0.2 points in correlation compared to the control group. So although some results are surprising (0.4 correlation between control group and sexual explicit comments or 0.34 correlation between control group and obscene comments) it is not a behaviour caracteristic of extreme communities. 
# 
# But on a general basis those or not strong correlations.

# ### Only the top 25
# view_count has a very skewed distribution, so the correlation that we get might be biased by the fact most videos have view_count 0. Therefore, we're studying the toxicity of the 25 most popular videos per community, where popularity is defined by its number of view_count

# In[31]:


#checking correlation and scatter plot only for top 25 videos per category

#define an histogram for the distribution 
fig, ax = plt.subplots(2,2,figsize= (14,8), sharey = False, sharex = True) #chose sharey=False as we are interested in
#the distribution, not the exact values

for i in range(4):
    sbplt = ax[i%2, math.floor(i/2)]
    df=df_extreme.loc[df_extreme['Category']==list_categories[i]]
    df=df.sort_values('view_count', ascending=False).head(25)
    sbplt.scatter(df['toxicity'], df['view_count'], s = 200, alpha=0.7, color = palette[i])
    sbplt.set_title(list_categories[i])
    
fig.tight_layout()

fig.text(0.4,0, "toxicity", fontsize='x-large')
fig.text(0,0.4, "view_count", rotation = 90, fontsize='x-large')


# **Comments:** For IDW we do see a linear relation, for control they all are in the same spot so it doesn't say much. The others there are datas a bit everywhere. 

# In[32]:


#checking correlation and scatter plot only for top 25 videos per category

#define an histogram for the distribution 

for j, subtoxicity in enumerate(list_subcat_tox): 
    fig, ax = plt.subplots(2,2,figsize= (14,8), sharey = False, sharex = True) #chose sharey=False as we are interested in
    #the distribution, not the exact values
    for i in range(4):
        sbplt = ax[i%2, math.floor(i/2)]
        df=df_extreme.loc[df_extreme['Category']==list_categories[i]]
        df=df.sort_values('view_count', ascending=False).head(25)
        sbplt.scatter(df[subtoxicity], df['view_count'], s = 200, alpha=0.7, color = palette[i])
        sbplt.set_title(list_categories[i])
    
    fig.tight_layout()

    fig.text(0.4,0, subtoxicity, fontsize='x-large')
    fig.text(0,0.4, "view_count", rotation = 90, fontsize='x-large')


# In[33]:


for i in list_categories:
    df=df_extreme.loc[df_extreme['Category']==i]
    df=df.sort_values('view_count', ascending=False).head(25)
    print(i)
    rho_1, p_1=spearmanr(df['toxicity'], df['view_count'])
    print("spearman correlation coefficient is equal to", np.round(rho_1,3), "with an associated p-value of", np.round(p_1,3))
    rho_2, p_2=pearsonr(df['toxicity'], df['view_count'])
    print("pearson correlation coefficient is equal to", np.round(rho_2,3), "with an associated p-value of", np.round(p_2,3))
    rho_3, p_3=kendalltau(df['toxicity'], df['view_count'])
    print("kendall tau correlation coefficient is equal to", np.round(rho_3,3), "with an associated p-value of", np.round(p_3,3))


# **Comments:** We have higher p-values, it comes from the fact we are working with less data. About the coefficient associated to p-values that are less than 0.05: 
# - Alt-right, pearson correlation of 0.403 (linear relation between the toxicity of the comments and the view_count, more popular Alt-right videos are associated to toxic comments) 
# - IDW spearman correlation of 0.548 same as before except data follow a monotonic function 
# 
# Although there is a correlation the correlation coeff rarely exceeds 0.5 

# In[34]:


for j, subtoxicity in enumerate(list_subcat_tox): 
    print('\033[1m'+subtoxicity+'\033[0m')
    for i in list_categories:
        df=df_extreme.loc[df_extreme['Category']==i]
        df=df.sort_values('view_count', ascending=False).head(25)
        print('  '+i)
        rho_1, p_1=spearmanr(df[subtoxicity], df['view_count'])
        print("spearman correlation coefficient is equal to", np.round(rho_1,3), "with an associated p-value of", np.round(p_1,3))
        rho_2, p_2=pearsonr(df[subtoxicity], df['view_count'])
        print("pearson correlation coefficient is equal to", np.round(rho_2,3), "with an associated p-value of", np.round(p_2,3))
        rho_3, p_3=kendalltau(df[subtoxicity], df['view_count'])
        print("kendall tau correlation coefficient is equal to", np.round(rho_3,3), "with an associated p-value of", np.round(p_3,3))


# **Comments:** (only about p-values less than 0.05)
# -IDW correlation 0.5 with sexual_explicit comments
# - Alt-right 0.7 with sexual_explicit comments
# - Alt-right and threat 0.4
# - 0.4 alt right and insult
# - 0.6 IDW and insult
# - 0.45 Alt right and insult
# - 0.5 IDW and obscene
# - 0.5 Alt right and obscene
# - 0.6 alt right and severe toxicity
# - 0.5 IDW and severe toxicity
# 
# Although there is a correlation the corr coeff rarely exceeds 0.5 but the trend is interesting 

# ## With channels instead of videos ! 

# In[35]:


#extracting channel_id and community it belongs to 
path_channel='rec_base.jsonl' #channel dataset
df_channel = pd.read_json(data_folder + path_channel, lines=True)


# In[36]:


list_view=[]
for i in range(len(df_channel)):
    s=df_channel.loc[i,"statistics"]['viewCount']
    list_view.append(float(s)) #in the dictionary it was stored as a string


# In[37]:


df_channel["channel_viewcount"]=list_view
df_channel=df_channel.drop(columns=["name", "edges", "description", "statistics"]) #only necessary columns


# In[38]:


#merge with the community data
df_channel_count=df_extreme[["channel_id", "Category", "toxicity", "severe_toxicity", 'obscene','identity_attack','insult','threat','sexual_explicit']].merge(df_channel, how='inner', on='channel_id')


# In[39]:


#group by everything and take the mean of the toxicity
df_channel_count=df_channel_count.groupby(by=["channel_id", "Category", "channel_viewcount"]).mean()
df_channel_count.reset_index(inplace=True)


# In[40]:


df_channel_count.head()


# In[41]:


#define an histogram for the distribution 
fig, ax = plt.subplots(2,2,figsize= (7,4), sharey = False, sharex = False) #chose sharey=False and sharex=False 
#as we are interested the distribution, not the exact values

for i in range(4):
    sbplt = ax[i%2, math.floor(i/2)]
    ax[i%2, math.floor(i/2)].set_yscale('log')
    df=df_channel_count.loc[df_channel_count['Category']==list_categories[i]]
    sbplt.hist(df['channel_viewcount'].values, bins = 100, color=palette[i], weights=np.ones(len(df['channel_viewcount'])) / len(df['channel_viewcount']))
    sbplt.set_title(list_categories[i])
    
fig.tight_layout()

fig.text(0.4,0, "view_count")
fig.text(0,0.5, "percentage_videos", rotation = 90)


# **Comments:** right skewed

# In[42]:


#define an histogram for the distribution 
fig, ax = plt.subplots(2,2,figsize= (14,8), sharey = False, sharex = True) #chose sharey=False as we are interested in
#the distribution, not the exact values

for i in range(4):
    sbplt = ax[i%2, math.floor(i/2)]
    ax[i%2, math.floor(i/2)].set_yscale('log') #plot the y axis in logarithm 
    df=df_channel_count.loc[df_channel_count['Category']==list_categories[i]]
    sbplt.scatter(df['toxicity'], df['channel_viewcount'], s = 100, alpha=1, color=palette[i])
    sbplt.set_title(list_categories[i])
    
fig.tight_layout()

fig.text(0.4,0, "toxicity", fontsize='x-large')
fig.text(0,0.4, "view_count", rotation = 90, fontsize='x-large')


# **Comments:** no obvisou correlation

# In[43]:


#define an histogram for the distribution 

for j, subtoxicity in enumerate(list_subcat_tox): 
    fig, ax = plt.subplots(2,2,figsize= (14,8), sharey = False, sharex = True) #chose sharey=False as we are interested in
    #the distribution, not the exact values

    for i in range(4):
        sbplt = ax[i%2, math.floor(i/2)]
        ax[i%2, math.floor(i/2)].set_yscale('log') #plot the y axis in logarithm 
        df=df_channel_count.loc[df_channel_count['Category']==list_categories[i]]
        sbplt.scatter(df[subtoxicity], df['channel_viewcount'], s = 50, alpha=1, color=palette[i])
        sbplt.set_title(list_categories[i])
    
    fig.tight_layout()

    fig.text(0.4,0, subtoxicity, fontsize='x-large')
    fig.text(0,0.4, "view_count", rotation = 90, fontsize='x-large')


# In[44]:


#Spearman's correlation, how well can the data be approcimated by a monotonic function
#Pearson's correlation, how well can the data be approximated by a linear function
#Kendall Tau'correlation, how well can the data be approximated in terms of "coherant pairs" (ex: a lot of data in the top right 
#a lot in the bottom left, and none elsewhere)

for i in list_categories:
    df=df_channel_count.loc[df_channel_count['Category']==i]
    print(i)
    rho_1, p_1=spearmanr(df['toxicity'], df['channel_viewcount'])
    print("spearman correlation coefficient is equal to", np.round(rho_1,3), "with an associated p-value of", np.round(p_1,3))
    rho_2, p_2=pearsonr(df['toxicity'], df['channel_viewcount'])
    print("pearson correlation coefficient is equal to", np.round(rho_2,3), "with an associated p-value of", np.round(p_2,3))
    rho_3, p_3=kendalltau(df['toxicity'], df['channel_viewcount'])
    print("kendall tau correlation coefficient is equal to", np.round(rho_3,3), "with an associated p-value of", np.round(p_3,3))


# **Comments:** everything similar to control group, nothing to say 

# In[45]:


#Spearman's correlation, how well can the data be approcimated by a monotonic function
#Pearson's correlation, how well can the data be approximated by a linear function
#Kendall Tau'correlation, how well can the data be approximated in terms of "coherant pairs" (ex: a lot of data in the top right 
#a lot in the bottom left, and none elsewhere)

for j, subtoxicity in enumerate(list_subcat_tox): 
    print('\033[1m'+subtoxicity+'\033[0m')
    for i in list_categories:
        df=df_channel_count.loc[df_channel_count['Category']==i]
        print('  '+i)
        rho_1, p_1=spearmanr(df['toxicity'], df['channel_viewcount'])
        print("spearman correlation coefficient is equal to", np.round(rho_1,3), "with an associated p-value of", np.round(p_1,3))
        rho_2, p_2=pearsonr(df['toxicity'], df['channel_viewcount'])
        print("pearson correlation coefficient is equal to", np.round(rho_2,3), "with an associated p-value of", np.round(p_2,3))
        rho_3, p_3=kendalltau(df['toxicity'], df['channel_viewcount'])
        print("kendall tau correlation coefficient is equal to", np.round(rho_3,3), "with an associated p-value of", np.round(p_3,3))


# **Comments:** Same, behavior similar as the control group, nothing much to say  """

# ## Analysis of toxicity level through time

# In[46]:


# change the format of the upload date, and add a column of month created
df_extreme.upload_date = pd.to_datetime(df_extreme.upload_date, format='%Y%m%d')
df_extreme["month_created"] = df_extreme.upload_date.apply(lambda x: pd.to_datetime(x.strftime('%Y-%m')))

# all categories have data until April 2019. Therefore we consider only the data until then:
df_final_cat = df_extreme[df_extreme.upload_date < pd.to_datetime("2019-05")]


""" # ## Number of comments per month
# We see in the first graph below that the data is quite noisy before 2014. Then, we show that there is more content to study from 2014, which explains why the data is not stable before. Therefore, we will only study the toxicity level from 2014 until April 2019.

# In[47]:


fig, axs = plt.subplots(1, 1, figsize=(10,3))

for i, category in enumerate(list_categories):
    sns.lineplot(x="month_created", y="toxicity", data=df_final_cat[df_final_cat['Category'] == category],
            label=category, color=palette[i])
axs.set_ylabel("Toxicity")
axs.set_xlabel("Month")


# Notice that a 95% CI is plotted.

# In[48]:


#plot number of commented videos per month per category: 
fig, axs = plt.subplots(1,1, figsize=(7,7), sharex=True)

for i, category in enumerate(list_categories):
        df_final_cat.loc[df_final_cat['Category'] == category, 'month_created'].value_counts().plot(kind = 'line', ax=axs, logy=True, color=palette[i])

axs.axhline(y=40, linestyle = '--', color='b')
axs.set_ylabel("Nbr of videos")
axs.set_xlabel("Date")
axs.set_title("Number of comments per channel-category over time")
axs.legend(list_categories + ['nbr videos = 40'])

 """
# From 2014, we have at least 40 comments per category per month (see horizontal line). We presume it is enough to make analysis on the overall toxicity of the comments. Therefore, from now on we will consider data from January 2014 until April 2019.

# In[49]:


df_after2014 = df_final_cat[df_final_cat.upload_date >= pd.to_datetime("2014-01")]


# ## Analysis: each category of toxicity
# In the period defined before, we compare the toxicity levels in between each channel-category.

# In[50]:
#confidence interval
def bootstrap_CI(data, nbr_draws): #the bootstrap function gave by in the lab session solution
    means = np.zeros(nbr_draws)
    data = np.array(data)
    for n in range(nbr_draws):
        indices = np.random.randint(0, len(data), len(data))
        data_tmp = data[indices]
        means[n] = np.nanmean(data_tmp)
    return [np.nanpercentile(means, 2.5),np.nanpercentile(means, 97.5)]

# prints the categories of toxicity over time. 
# takes about 45 sec to run
from plotly.tools import mpl_to_plotly
import plotly.graph_objects as go
import plotly.offline as poff 
import plotly.express as px
from dash import Dash, html, dcc
from base64 import b64encode
import io

app = Dash(__name__)
df_avg_month = df_after2014.groupby(['month_created', 'Category']).mean()

""" fig = px.line(df_avg_month, x=df_avg_month.index.get_level_values('month_created'),
     y='toxicity', color=df_avg_month.index.get_level_values('Category'))
fig.write_html("test.html")
fig.show() """


traces=[]
fig = go.Figure()
subcat = 'toxicity'
category = 'Alt-lite'
#for index, subcat in enumerate(list_all_tox):
#for i, category in enumerate(list_categories):
df_category = df_after2014[df_after2014.Category == category]
low, high = bootstrap_CI(df_category.groupby(['month_created'])[subcat])  
fig.add_traces(go.Scatter(x=df_avg_month.index.get_level_values('month_created'), 
                    y=df_avg_month[df_avg_month.index.get_level_values('Category') == category][subcat],
                    mode = 'lines+markers'))#, color=palette[i]))

fig.write_html("test2.html")
fig.show()

""" 
# For each category of toxicity, we observe different behaviours. 
# * Toxicity: alt-lite has become more toxic than other categories.
# * Severe toxicity: (SMALL SCALE!) since the results are very small, we can conclude that none of the channel-category are severly toxic.
# * Obscene: all channel categories became higher than media, the control group.
# * Identity attack: Alt-right on the top, then alt-lite. Then IDW has approximately the same score as the control group.
# * Insult: Alt-lite is above control group.
# * Threat: (SMALL SCALE!) However pick for alt-right in 2016.
# * Sexual Explicit: (SMALL SCALE!) right wing is above control group. 

# ## Analysis: each channel-category
# Now, we compare the behaviours of the toxicity features within each channel-category.

# In[51]:


fig, axs = plt.subplots(4,1, figsize=(9,12), sharex=True, sharey=True)

for i, category in enumerate(list_categories):
    for j, subcat in enumerate(list_all_tox):
        sns.lineplot(x="month_created", y=subcat, data=df_after2014[df_after2014['Category'] == category],
            label=list_all_tox_titles[j], ax = axs[i])
    axs[i].set_ylabel(list_categories[i])
    axs[i].set_xlabel("Date")
    sns.move_legend(axs[i], "upper left", bbox_to_anchor=(1, 1))


# Overall the 4 channel-categories, the three main subcategories of toxicity that are signifcant are toxicity, insult and obscene.
# * Alt-lite: we see a small increase of the three main subcategories mentioned above, until 2018, where a drop is observed. The values might have dropped because of the #Metoo movement, starting in 2017 as a way to draw attention on the magnitude against sexual abuse and harassment. Then the values are quite stable.
# * Alt-right: a steep increase is observed mid 2016 in toxicity, insult, obscene. It coincides with the election of Donald Trump in the U.S. Indeed, June 2015, he announced that he would be a candidate in the U.S presidential election of 2016. In November 2016, he won the election. Also youtube didn't moderate the comments, following the Russian interference in the 2016 U.S. elections. We also see a pick in the first quarter of 2018. 
# * IDW: rather constant.
# * Control: a very light increase of toxicity and insult since 2014. A decrease of obscene from 2018.

# ## Study of the top 25 videos per month per channel-category
# For each month and each channel category, we select the 25 videos with the most views and analyze their toxicity.

# In[52]:


# create the dataframe:
df_top25 = pd.DataFrame()
# create a list of all months we considered: 
list_dates = df_after2014.month_created.unique()

for i, category in enumerate(list_categories):
    df_category=df_after2014.loc[df_after2014['Category'] == category]
    for j, date in enumerate(list_dates):
        df = df_category.loc[df_category['month_created'] == date]
        if i==0 and j==0:
            df_top25 = df.sort_values('view_count', ascending=False).head(25)
        else:
            df_top25 = pd.concat([df_top25, df.sort_values('view_count', ascending=False).head(25)])
            
df_top25.head()


# In[53]:


# prints the categories of toxicity over time. We compare them with the mean obtained over all videos of the month.

fig, axs = plt.subplots(7,1, figsize=(12,16), sharex=True)

for index, subcat in enumerate(list_all_tox):
    for j, category in enumerate(list_categories):
        sns.lineplot(x="month_created", y=subcat, data=df_top25[df_top25['Category'] == category],
            label=category + " (top 25)", ax = axs[index], color = palette[j])
        sns.lineplot(x="month_created", y=subcat, data=df_after2014[df_after2014['Category'] == category],
            label=category, ax = axs[index], color = palette[j], linestyle='--', errorbar=None, linewidth = 1)
    axs[index].set_ylabel(list_all_tox_titles[index])
    axs[index].set_xlabel("Date")
    sns.move_legend(axs[index], "upper left", bbox_to_anchor=(1, 1))


# Looking at each subcategory of toxicity, the top 25 videos have usually the same or a noticeably higher mean than the overall mean of their corresponding category. This is most detectable in the Alt-lite community. However, the reverse happens in the control group: the most viewed videos are usually less toxic than the mean of all the videos. 
# From there, we observe a really different behavior between the control group and the right wing categories.
# 

# In[54]:


# prints the subcategories of toxicity per channel-category
# takes about 1 min
fig, axs = plt.subplots(4,1, figsize=(9,15), sharex=True, sharey=True)

for i, category in enumerate(list_categories):
    for j, subcat in enumerate(list_all_tox):
        sns.lineplot(x="month_created", y=subcat, data=df_top25[df_top25['Category'] == category],
            label=list_all_tox_titles[j] + " (top 25)", ax = axs[i], color = ex_palette[j])
        sns.lineplot(x="month_created", y=subcat, data=df_after2014[df_after2014['Category'] == category],
            label=list_all_tox_titles[j], ax = axs[i], color = ex_palette[j], linestyle='--', linewidth = 1)
    axs[i].set_ylabel(list_categories[i])
    axs[i].set_xlabel("Date")
    sns.move_legend(axs[i], "upper left", bbox_to_anchor=(1, 1))


# In the right wing channels, the most popular videos have a higher mean of toxicity than the rest of the videos of the category. This phenomena is not observed in the control group. On the contrary, we can observe since mid 2015 that the top 25 videos contain less toxic comments than the mean over all videos of the control category.
 """