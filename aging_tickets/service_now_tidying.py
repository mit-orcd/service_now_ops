#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#
# - Instructions
#
# 1. Use URL below in a browser to download all fields for all tickets into a CSV
#
#    https://mit.service-now.com/x_mits2_sloanfcs_case_list.do?sysparm_query=assignment_groupDYNAMIC106bd930db925010893e10c913961927&CSV&sysparm_default_export_fields=all
#
#    ( tip from https://www.servicenowelite.com/blog/2020/9/29/ten-methods-to-find-sysid )
#
# 2. Rename downloaded .csv as snow_all_tickets_YYYY_MM_DD.csv
#.    - where YYYY is year, MM is month number and DD is day of month number.
#
# 3. Run this notebook 
#
# 4. Share aging ticket details and summary info with ids in question
#    - program prints summary table of
#       Kerberos Id    |   Number of Aging Tickets
#    - program writes several .csv files
#       1 x aging_tickets_YYYY_MM_DD__summary.csv  
#       1 x aging_tickets_YYYY_MM_DD__orphaned.csv
#       N x aging_tickets_YYYY_MM_DD_KERBEROSID.csv
#        where KERBEROSID is kerberos id of ORCD team members
#


import pandas as pd
pd.options.mode.chained_assignment = None
import wordcloud
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt     


# In[ ]:


# Get some things set up

# Read in current SNOW export and sort by ticket number
# - default to current date, uncomment and edit direct setting for different date
csv_date_string=dt.datetime.now().strftime('%Y_%m_%d')
# csv_date_string="2023_10_30"
#
csv_name="snow_all_tickets_"+csv_date_string+".csv"
sdf=pd.read_csv(csv_name,encoding = "ISO-8859-1")
sdf.sort_values('number',axis=0,ascending=False,inplace=True)

# Filter to all active tickets
active_issues=sdf[sdf['active']==True]

# Make list of ORCD team
# Note - everyone has two "ids" they can appear as in servicenow
#  1. a kerberos id e.g. "cnh", "milechin" etc..
#  2. an assignee id e.g. "Christopher N Hill", "Lauren Milechin"
# Code makes list of these for ORCD team and mapping between the two
#
assignee_to_kerb_dict={
                       'Scott Blomquist'      : 's_b',
                       'Shaohao Chen'         : 'shaohao',
                       'James Cuff'           : 'jcuff',
                       'Adam Drucker'         : 'ageod',
                       'Christopher Ehnstrom' : 'imstof',
                       'Michel Erb'           : 'erbmi1',
                       'Yani Garcia'          : 'yani',
                       'Larry Gardner'        : 'lgardner',
                       'Renee Hellenbrecht'   : 'rhellen',
                       'Christopher N Hill'   : 'cnh',
                       'Paul Hsi'             : 'phsi',
                       'Morgan Ludwig'        : 'm_ludwig',
                       'Lauren E Milechin'    : 'milechin',
                      }
kerb_to_assignee_dict = {v: k for k, v in assignee_to_kerb_dict.items()}
ot=pd.DataFrame.from_dict({'assigned':assignee_to_kerb_dict.keys(),'kerberos':assignee_to_kerb_dict.values()})


# In[ ]:


# Create some handy functions

def get_old_by_assignee(older_than_days=14,assigned_to_id='Christopher N Hill',df=None,tag_processed=True ):
    #
    # Get assigned to certain id and older than a certain date from not processed already
    #
    fdf=df[(df['orcd_processed']==False) & (df['update_days_old']>older_than_days) & (df['assigned_to']==assigned_to_id) ]
    if tag_processed:
        df.loc[fdf.index,'orcd_processed']=True
    return(fdf)

def get_old_by_updated(older_than_days=14,updated_by_id='cnh',df=None,tag_processed=True ):
    #
    # Get updated by certain id and older than a certain date from not processed already
    #
    fdf=df[(df['orcd_processed']==False) & (df['update_days_old']>older_than_days) & (df['sys_updated_by']==updated_by_id) ]
    if tag_processed:
        df.loc[fdf.index,'orcd_processed']=True
    return(fdf)

def get_old_by_created(older_than_days=14,created_by_id='cnh',df=None,tag_processed=True ):
    #
    # Get created by certain id and older than a certain date from not processed already
    #
    fdf=df[(df['orcd_processed']==False) & (df['update_days_old']>older_than_days) & (df['sys_created_by']==created_by_id) ]
    if tag_processed:
        df.loc[fdf.index,'orcd_processed']=True
    return(fdf)

def prep_active_summary(df=None):
    # Prepare summary data frame to process
    # - select a subset of full SNOW fields
    # - add extra columns
    #    o True/False processed flag for filtering in stages
    #    o updated_days_old field for filtering on
    #    o URL that can be used to access ticket directly
    
    # - get subset
    pdf=df[[
            'opened_at',
            'requester',
            'sys_created_by',
            'short_description',
            'sys_updated_by',
            'sys_updated_on',
            'sys_created_on',
            'assigned_to',
            'state',
            'number',
            'sys_id',
            'category_ref',
            'service_ref'
          ]]
    
    # - add processed flag
    pdf.insert(0, "orcd_processed", False)
    
    # - time in days since updated
    pdf.insert(1, "update_days_old", -1)
    for i in pdf.index:
        update_days_old=(pd.to_datetime(dt.datetime.now())-pd.to_datetime(df['sys_updated_on'][i])).days
        pdf.loc[i,'update_days_old']=update_days_old
 
    # - full url to ticket
    url_prefix='https://mit.service-now.com/nav_to.do?uri=%2Fx_mits2_sloanfcs_case.do%3Fsys_id%3D'
    pdf.insert(1, "url", "")
    for i in pdf.index:
        url=url_prefix + df['sys_id'][i]
        pdf.loc[i,'url']=url
    
    return(pdf)


# In[ ]:


#
# Filter for aging tickets - order is important!
#

# Get subset of fields
active_summary=prep_active_summary(df=active_issues)
# Set cutoff for older than time in days
older_than_days=14

# - create empty DataFrame for each id
t_to_check=dict()
for id in ot.kerberos:
    t_to_check[id]=pd.DataFrame()

# - search all for "assigned to" by id and older than cutoff
for id in ot.assigned:
    kid=assignee_to_kerb_dict[id]
    cdf=get_old_by_assignee(older_than_days=older_than_days,assigned_to_id=id,df=active_summary,tag_processed=True)
    t_to_check[kid]=pd.concat([t_to_check[kid],cdf])

# - search remaining for "updated by" by id and older than cutoff
for id in ot.kerberos:
    cdf=get_old_by_updated(older_than_days=older_than_days,updated_by_id=id,df=active_summary,tag_processed=True)
    t_to_check[id]=pd.concat([t_to_check[id],cdf])
    
# - search remaining for "created by" by id and older than cutoff
for id in ot.kerberos:
    cdf=get_old_by_created(older_than_days=older_than_days,created_by_id=id,df=active_summary,tag_processed=True)
    t_to_check[id]=pd.concat([t_to_check[id],cdf])
    
for id in ot.kerberos:
    t_to_check[id].sort_values('opened_at', ascending=False,inplace=True)
    
# Now deal with "orphaned" tickets i.e. ones where nobody in ORCD team has been assigned, has updated or created.
old_orphaned_tickets=active_summary[(active_summary['orcd_processed']==False) & (active_summary['update_days_old']>older_than_days)]
csv_name="aging_tickets_"+csv_date_string+"__"+"orphaned"+".csv"
old_orphaned_tickets.to_csv(csv_name)
    
summarydf=pd.DataFrame(columns=['Kerberos Id','Number Aging Tickets'])
for id in ot.sort_values('kerberos').kerberos:
    nr=t_to_check[id].shape[0] 
    csv_name="aging_tickets_"+csv_date_string+"_"+id+".csv"
    t_to_check[id].to_csv(csv_name)
    new_row=pd.DataFrame.from_dict({'Kerberos Id':[id],'Number Aging Tickets':[nr]})
    summarydf=pd.concat([summarydf,new_row],ignore_index=True)
    
summarydf.to_csv("aging_tickets_"+csv_date_string+"__summary.csv")
summarydf


# In[ ]:


# Make a workd cloud for fun
text = ' '.join(sdf['short_description'].values )


# In[ ]:


wc=wordcloud.WordCloud().generate(text)


# In[ ]:


plt.figure(figsize=(40, 30))
plt.imshow(wc)
plt.axis("off");

