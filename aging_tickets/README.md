#
# Scripts for getting aging tickets lists
#

## Notebook and python script for getting aging tickets
  - service_now_tidying.ipynb
  - service_now_tidying.py

## Instructions
```
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

```

## Example output

  - aging_tickets_2023_10_30__orphaned.csv
  - aging_tickets_2023_10_30__summary.csv
  - aging_tickets_2023_10_30_ageod.csv
  - aging_tickets_2023_10_30_cnh.csv
  - aging_tickets_2023_10_30_erbmi1.csv
  - aging_tickets_2023_10_30_imstof.csv
  - aging_tickets_2023_10_30_jcuff.csv
  - aging_tickets_2023_10_30_lgardner.csv
  - aging_tickets_2023_10_30_m_ludwig.csv
  - aging_tickets_2023_10_30_milechin.csv
  - aging_tickets_2023_10_30_phsi.csv
  - aging_tickets_2023_10_30_rhellen.csv
  - aging_tickets_2023_10_30_s_b.csv
  - aging_tickets_2023_10_30_shaohao.csv
  - aging_tickets_2023_10_30_yani.csv

