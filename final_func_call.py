import all_func
from all_func import *
from datetime import datetime

def final_df():


    # Calling 4 functions
    # print("__________________________START OF SCRAPPING APEC DATA_______________________________")
    # print(datetime.now())    
    # scap_apec()
    # print("__________________________END OF SCRAPPING APEC DATA_______________________________")


    # print("______________START OF SCRAPPING WELCOME TO THE JUNGLE  DATA________________________")
    # print(datetime.now())
    # scrape_wttj()
    # print("______________END OF SCRAPPING WELCOME TO THE JUNGLE  DATA________________________")





    # print("______________START OF SCRAPPING LINKEDIN  DATA________________________")
    # print(datetime.now())
    # linkedin()
    # print("______________END OF SCRAPPING LINKEDIN  DATA________________________")



    # print("______________ START SCRAPPING HELLO WORK DATA________________________")
    # print(datetime.now())
    # hellowork1()
    # print("______________END OF SCRAPPING HELLO WORK DATA________________________")



    # Recupération de datasets
    # chemin = '/Users/margaryta/Desktop/WILD/Python/P3job_platform/'
    chemin=''

    print("______________START OF MERGING JOB DATASETS ________________________")
    print(datetime.now())
    
    apec_jobs = pd.read_csv(chemin+'apec_jobs.csv')
    jungle_jobs = pd.read_csv(chemin+'jungle_jobs.csv')
    hello_jobs = pd.read_csv(chemin+'hello_jobs.csv')
    linkedIn_jobs = pd.read_csv(chemin+'linkedin_jobs.csv')

    print("apec_jobs : ", apec_jobs.shape)
    print("jungle_jobs : ", jungle_jobs.shape )
    print("hello_jobs : " , hello_jobs.shape)
    print("linkedIn_jobs : ", linkedIn_jobs.shape )

    jobs_final = pd.concat([jungle_jobs, hello_jobs, linkedIn_jobs, apec_jobs], ignore_index=True)

    jobs_final.dropna(subset='city',inplace = True)
    jobs_final['city'] = jobs_final['city'].apply(lambda x: str(x.upper()))

    jobs_final.dropna(subset='company_name',inplace = True)
    jobs_final['company_name'] = jobs_final['company_name'].apply(lambda x: str(x.upper()))

    jobs_final.dropna(subset='job_title',inplace = True)
    jobs_final['job_title']=jobs_final['job_title'].apply(lambda x: str(x.capitalize()))
    jobs_final.drop_duplicates(subset=['job_title', 'city', 'company_name'], keep='first')

    jobs_final['zip_code'][jobs_final['zip_code'].isna()] = 0
    jobs_final['zip_code'] = jobs_final['zip_code'].apply(lambda x : int(x))
    
    
    print("")
    print("jobs_final : ", jobs_final.shape)
       
    jobs_final.to_csv('jobs_final.csv')

    print("______________________END OF A FINAL JOB DATASET________________________")
    print(datetime.now())

    print("______________START OF MERGING COMPANIES DATASETS ________________________")

    apec_companies = pd.read_csv(chemin+'apec_companies.csv')
    jungle_companies = pd.read_csv(chemin+'jungle_companies.csv')
    hello_companies = pd.read_csv(chemin+'hello_companies.csv')
    linkedIn_companies = pd.read_csv(chemin+'linkedin_companies.csv')

    print("apec_companies : ", apec_companies.shape)
    print("jungle_companies : ", jungle_companies.shape )
    print("hello_companies : " , hello_companies.shape)
    print("linkedIn_companies : ", linkedIn_companies.shape )


    companies_final = pd.concat([apec_companies, jungle_companies, hello_companies, linkedIn_companies], ignore_index=True)
    companies_final.drop_duplicates(subset='company_name'.lower(), keep='first')

    print("")
    print("companies_final : ", companies_final.shape )

    companies_final.to_csv('companies_final.csv')

    print("______________________END OF A FINAL COMPANIES DATASET________________________")
    print(datetime.now())
    return

import schedule
import time

# schedule.every().day.at("02:00").do(final_df)
print(datetime.now())
final_df()