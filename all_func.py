import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
from datetime import timedelta
import json
from datetime import date
from pprint import pprint
import time
import requests
import numpy as np
from html.parser import HTMLParser
from bs4 import BeautifulSoup
import re
import warnings
warnings.filterwarnings("ignore")



#___________________APEC________________________
def scap_apec():

    try:
        driver = webdriver.Chrome()
    except:
        driver = webdriver.Chrome(ChromeDriverManager(version="114.0.5735.90").install())

    time.sleep(3)

    driver.get(
        'https://www.apec.fr/candidat/recherche-emploi.html/emploi?motsCles=data&typesConvention=143684&typesConvention=143685&typesConvention=143686&typesConvention=143687')

    time.sleep(3)
    accept_cookies = driver.find_element(By.ID, "onetrust-accept-btn-handler")
    driver.execute_script("arguments[0].click();", accept_cookies);

    offres = []

    for i in range(0, 50):
        time.sleep(5)
        driver.get(
            'https://www.apec.fr/candidat/recherche-emploi.html/emploi?motsCles=data&typesConvention=143684&typesConvention=143685&typesConvention=143686&typesConvention=143687&page=' + str(
                i))
        offres_webscrapped = driver.find_elements(By.XPATH, '//div[@class="container-result"]/div/a')
        for offre in offres_webscrapped:
            time.sleep(0.5)
            offres.append(offre.get_attribute('href'))

    driver.quit()

    list_id = []
    for x in range(len(offres)):
        id = offres[x].split("?")[0].split("/")[-1]
        list_id.append(id)

    list_lien = []
    for x in range(len(list_id)):
        lien = "https://www.apec.fr/cms/webservices/offre/public?numeroOffre=" + list_id[x]
        list_lien.append(lien)

    # adresse offre à apliquer sur la colonne 'lieux' :
    def adresse_1(add):
        try:
            lieu = str(add)
            i = re.findall("\w+ \d+ - \d+", lieu)
            return i[0]
        except:
            return (add)

    def adresse_2(add):
        try:
            lieu = str(add)
            i = re.findall("[a-zA-Z]+ - \d+", lieu)
            return i[0]
        except:
            return (add)

    # pour tier les savoir etre et savoir faire à apliquer sur la colonne 'competences' :

    def savoir_faire(comp):
        savoir_faire = []
        try:
            for x in range(len(comp)):
                type = comp[x]['type']
                libelle = comp[x]['libelle']
                if type == "SAVOIR_FAIRE":
                    savoir_faire.append(libelle)
            return savoir_faire
        except:
            return "non renseigné"

    def savoir_etre(comp):
        savoir_etre = []
        try:
            for x in range(len(comp)):
                type = comp[x]['type']
                libelle = comp[x]['libelle']
                if type == "SAVOIR_ETRE":
                    savoir_etre.append(libelle)
            return savoir_etre
        except:
            return "non renseigné"

    api = []
    for x in range(len(list_lien)):
        try:
            link = list_lien[x]
            r = requests.get(link)
            r.text
            data = json.loads(r.text)
            api.append(data)
        except:
            pass

    df_apec = pd.DataFrame(api)

    df_apec = df_apec[['numeroOffre', 'enseigne', 'intitule', 'lieux', 'salaireTexte', 'idNomTypeContrat', 'texteHtml',
                       'texteHtmlEntreprise', 'texteHtmlProfil', 'logoEtablissement', 'datePremierePublication',
                       'competences']]

    df_apec.drop_duplicates(subset='numeroOffre', keep='first', inplace=True)

    df_apec['lieux'] = df_apec['lieux'].apply(adresse_1)
    df_apec['lieux'] = df_apec['lieux'].apply(adresse_2)

    df_apec['lieux'] = df_apec['lieux'].apply(lambda x: str(x))

    df_apec = df_apec[~df_apec['lieux'].str.contains(':')]

    df_apec['dept'] = df_apec['lieux'].apply(lambda x: x.split(" - ")[1])
    df_apec['lieux'] = df_apec['lieux'].apply(lambda x: x.split(" - ")[0])

    df_apec['savoir_faire'] = df_apec['competences'].apply(savoir_faire)
    df_apec['savoir_etre'] = df_apec['competences'].apply(savoir_etre)

    df_apec.drop(columns='competences', inplace=True)

    try:
        df_apec.drop(columns='Unnamed: 0', inplace=True)
    except:
        pass

    # pour avoir le logo de l'entreprise :
    try:
        for ind, val in enumerate(df_apec['logoEtablissement']):
            df_apec['logoEtablissement'][ind] = 'https://www.apec.fr/files/live/mounts/images' + val
    except:
        pass

    df_apec = df_apec.reset_index(drop=True)

    df_apec['idNomTypeContrat'] = df_apec['idNomTypeContrat'].replace(101888, "CDI")
    df_apec['idNomTypeContrat'] = df_apec['idNomTypeContrat'].replace(101887, "CDD")
    df_apec['idNomTypeContrat'] = df_apec['idNomTypeContrat'].replace(597137, "Alternance - Contrat d'apprentissage")
    df_apec['idNomTypeContrat'] = df_apec['idNomTypeContrat'].replace(597138,
                                                                      "Alternance - Contrat de professionnalisation")
    df_apec['idNomTypeContrat'] = df_apec['idNomTypeContrat'].replace(597139, "Alternance - Contrat d'apprentissage")
    df_apec['idNomTypeContrat'] = df_apec['idNomTypeContrat'].replace(597141, "intérim")
    df_apec['idNomTypeContrat'] = df_apec['idNomTypeContrat'].replace(101889, "intérim")

    df_apec['datePremierePublication'] = df_apec['datePremierePublication'].apply(lambda x: x.replace("+0000", ""))
    df_apec['datePremierePublication'] = df_apec['datePremierePublication'].apply(
        lambda x: datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%f"))
    df_apec['datePremierePublication'] = df_apec['datePremierePublication'].apply(
        lambda x: datetime.strftime(x, "%Y-%m-%d"))
    df_apec['datePremierePublication'] = df_apec['datePremierePublication'].apply(
        lambda x: datetime.strptime(x, "%Y-%m-%d"))

    df_apec.rename(columns={'numeroOffre': 'id', 'intitule': 'job_title', 'enseigne': 'company_name', 'lieux': 'city',
                            'dept': 'zip_code', 'idNomTypeContrat': 'contract_type', 'salaireTexte': 'salary',
                            'texteHtml': 'job_description', 'texteHtmlProfil': 'profile_description',
                            'texteHtmlEntreprise': 'company_description', 'logoEtablissement': 'logo',
                            'datePremierePublication': 'date_creation', 'savoir_faire': 'hard_skills',
                            'savoir_etre': 'soft_skills'}, inplace=True)

    df_apec = df_apec[
        df_apec['job_title'].str.contains('Data') | df_apec['job_title'].str.contains('Analyst') | df_apec[
            'job_title'].str.contains('Données')]

    df_apec = df_apec.reset_index(drop=True)

    df_apec.insert(14, 'link', value="", allow_duplicates=False)

    for ind, val in enumerate(df_apec['id']):
        for offre in offres:
            if str(val) in offre:
                df_apec['link'][ind] = offre
            else:
                pass

    df_apec_ent = df_apec[['company_name', 'company_description', 'logo']]
    df_apec.drop(columns=['company_description', 'logo'], inplace=True)
    df_apec_ent.drop_duplicates(subset='company_name', keep='first', inplace=True)
    df_apec_ent = df_apec_ent.reset_index(drop=True)

    for x, val in enumerate(df_apec['hard_skills']):
        df_apec['hard_skills'][x] = ', '.join(val)

    for x, val in enumerate(df_apec['soft_skills']):
        df_apec['soft_skills'][x] = ', '.join(val)

    def html_str(x):
        class HTMLFilter(HTMLParser):
            text = ""

            def handle_data(self, data):
                self.text += data

        f = HTMLFilter()
        f.feed(x)
        return f.text

    df_apec_ent['company_description'] = df_apec_ent['company_description'].apply(html_str)
    df_apec['job_description'] = df_apec['job_description'].apply(html_str)
    df_apec['profile_description'] = df_apec['profile_description'].apply(html_str)

    df_apec_ent['company_description'] = df_apec_ent['company_description'].apply(lambda x: re.sub("\n", " ", x))
    df_apec['job_description'] = df_apec['job_description'].apply(lambda x: re.sub("\n", " ", x))
    df_apec['profile_description'] = df_apec['profile_description'].apply(lambda x: re.sub("\n", " ", x))
    df_apec_ent['company_description'] = df_apec_ent['company_description'].apply(lambda x: re.sub("\xa0", "", x))
    df_apec['job_description'] = df_apec['job_description'].apply(lambda x: re.sub("\xa0", "", x))
    df_apec['profile_description'] = df_apec['profile_description'].apply(lambda x: re.sub("\xa0", "", x))
    df_apec_ent['company_description'] = df_apec_ent['company_description'].apply(lambda x: re.sub("\t", "", x))
    df_apec['job_description'] = df_apec['job_description'].apply(lambda x: re.sub("\t", "", x))
    df_apec['profile_description'] = df_apec['profile_description'].apply(lambda x: re.sub("\t", "", x))

    df_apec.insert(13, 'update', value=date.today(), allow_duplicates=False)

    df_apec.to_csv("apec_jobs.csv", index=False)

    df_apec_ent.to_csv("apec_companies.csv", index=False)

    return


#__________________________________WELCOME TO THE JUNGLE______________________________________________

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import requests
import numpy as np
from html.parser import HTMLParser
import re
import datetime
from datetime import datetime
import all_func
from all_func import *

def scrap_job_urls():

    try:
        driver = webdriver.Chrome()
    except:
        driver = webdriver.Chrome(ChromeDriverManager(version="114.0.5735.90").install())

    time.sleep(3)
    
    url_page = 'https://www.welcometothejungle.com/fr/jobs?refinementList%5Boffices.country_code%5D%5B%5D=FR&refinementList%5Bcontract_type%5D%5B%5D=full_time&refinementList%5Bcontract_type%5D%5B%5D=apprenticeship&refinementList%5Bcontract_type%5D%5B%5D=internship&refinementList%5Bcontract_type%5D%5B%5D=temporary&query=data&page=1'
    driver.get(url_page)
    time.sleep(5)

    # Accepter les cookies
    try:
        accept_cookies = driver.find_element(By.ID, "axeptio_btn_acceptAll")
        driver.execute_script("arguments[0].click();", accept_cookies)
        time.sleep(3)
    except Exception as e:
        print("Pas de bouton de cookies trouvé ou erreur :", e)

    # Fermer le questionnaire de satisfaction
    try:
        close_button = driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/div/div/div[2]/div/ul/div/div/button')
        driver.execute_script("arguments[0].click();", close_button)
        print("Le bouton de fermeture a été cliqué.")
    except Exception as e:
        print(f"Erreur lors de la fermeture du bouton : {e}")

    time.sleep(5)

    # Trouver le nombre total de pages
    pagination = driver.find_elements(By.XPATH, '//*[@id="app"]/div[1]/div/div/div[2]/div/div[2]/nav//a')
    num_pages = int(pagination[-2].text)
    print(f"Nombre total de pages : {num_pages}")

    # Collecte des URLs des annonces
    job_urls = []
    for page_num in range(1, num_pages + 1):
        page_url = f"https://www.welcometothejungle.com/fr/jobs?refinementList%5Boffices.country_code%5D%5B%5D=FR&refinementList%5Bcontract_type%5D%5B%5D=full_time&refinementList%5Bcontract_type%5D%5B%5D=apprenticeship&refinementList%5Bcontract_type%5D%5B%5D=internship&refinementList%5Bcontract_type%5D%5B%5D=temporary&query=data&page={page_num}"
        driver.get(page_url)
        time.sleep(10)

        for i in range(1, 31):
            try:
                job_element = driver.find_element(By.XPATH,
                                                  f'//*[@id="app"]/div[1]/div/div/div[2]/div/ul/li[{i}]/div/div/a')
                job_url = job_element.get_attribute('href')
                job_urls.append(job_url)
            except Exception as e:
                print(f"Erreur lors de la récupération du lien pour l'élément {i} sur la page {page_num} : {e}")

    driver.quit()
    return job_urls


def srape_job_data(job_urls):
    job_paths = [url.split('/companies')[1] for url in job_urls]
    api_base_url = "https://api.welcometothejungle.com/api/v1/organizations"

    job_data = []
    entreprise_data = []

    for path in job_paths:
        api_url = f"{api_base_url}{path}"
        response = requests.get(api_url)
        if response.status_code == 200:
            job_json = response.json()
            job_info = {
                'id': job_json.get("job", {}).get("reference", ""),
                "job_title": job_json.get("job", {}).get("name", ""),
                "company_name": job_json.get("job", {}).get("organization", {}).get("name", ""),
                "city": job_json.get("job", {}).get("office", {}).get("district", ""),
                "zip_code": job_json.get("job", {}).get("office", {}).get("zip_code", ""),
                "contract_type": job_json.get("job", {}).get("contract_type", ""),
                "salary": f"{job_json.get('salary_min', '')} - {job_json.get('salary_max', '')} {job_json.get('salary_currency', '')}",
                "salary_min": job_json.get("job", {}).get("salary_min", ""),
                "salary_max": job_json.get("job", {}).get("salary_max", ""),
                "salary_currency": job_json.get("job", {}).get("salary_currency", ""),
                "job_description": job_json.get("job", {}).get("description", ""),
                "profile_description": job_json.get("job", {}).get("profile", ""),
                "date_creation": job_json.get("job", {}).get("published_at", "").split('T')[0] if job_json.get("job",
                                                                                                               {}).get(
                    "published_at") else "",
                "skills": [item['name']['fr'] for item in job_json.get("job", {}).get("skills", [])],
                "link": job_json.get("job", {}).get("urls", [{}])[0].get("href", "")
            }
            entreprise_info = {
                'company_name': job_json.get("job", {}).get("organization", {}).get('name', ''),
                "company_description": job_json.get("job", {}).get("organization", {}).get("website_organization",
                                                                                           {}).get("i18n_descriptions",
                                                                                                   {}).get("fr", ""),
                'logo': job_json.get("job", {}).get("organization", {}).get('logo', {}).get("url", ""),
                'company_link': job_json.get("job", {}).get("organization", {}).get('website', '')
            }

            entreprise_data.append(entreprise_info)

            # Gérer le salaire manquant
            if not job_info["salary"]:
                job_info["salary"] = np.nan

            job_data.append(job_info)
        else:
            print(f"Erreur lors de la requête de l'URL : {api_url}")

    return job_data, entreprise_data


def process_data(job_data, entreprise_data):
    # Convertir les dictionnaires en chaînes de caractères pour les rendre hachables
    for entreprise in entreprise_data:
        for key, value in entreprise.items():
            if isinstance(value, dict):
                entreprise[key] = str(value)

    # Conversion en DataFrame
    df_jobs = pd.DataFrame(job_data)
    df_entreprises = pd.DataFrame(entreprise_data).drop_duplicates()

    # Fonction pour nettoyer le HTML des descriptions
    def html_str(x):
        if x is None:
            return ""

        class HTMLFilter(HTMLParser):
            def __init__(self):
                super().__init__()
                self.text = ""

            def handle_data(self, data):
                self.text += data

        f = HTMLFilter()
        f.feed(x)
        return f.text

    # Nettoyage des descriptions
    df_jobs['job_description'] = df_jobs['job_description'].apply(html_str)
    df_jobs['profile_description'] = df_jobs['profile_description'].apply(html_str)
    df_entreprises['company_description'] = df_entreprises['company_description'].apply(html_str)

    # Remplacement des types de contrat
    contract_replacements = {
        'full_time': 'CDI',
        'apprenticeship': 'Apprentissage',
        'internship': 'Stage',
        'temporary': 'CDD'
    }
    df_jobs['contract_type'] = df_jobs['contract_type'].replace(contract_replacements)

    # Mise à jour de la colonne salaire
    df_jobs['salary'] = df_jobs.apply(
        lambda row: f"{row['salary_min']} - {row['salary_max']} {row['salary_currency']}"
        if pd.notnull(row['salary_min']) and pd.notnull(row['salary_max']) and pd.notnull(row['salary_currency'])
        else None, axis=1)

    # Suppression des colonnes inutiles
    df_jobs = df_jobs.drop(columns=['salary_min', 'salary_max', 'salary_currency'])



    #Verification des doublons
    df_jobs.drop_duplicates(subset='id', inplace=True)

    df_jobs['hard_skills'] = df_jobs['job_description'].apply(hard_sk)
    df_jobs['hard_skills'] = df_jobs['hard_skills'].apply(lambda x: ", ".join(x))

    #Pour soft skills
    df_jobs.rename(columns={'skills': 'soft_skills'}, inplace=True)


    #Changer le zip code

    df_jobs['zip_code'] = df_jobs['zip_code'].apply(lambda x: str(x))
    df_jobs['zip_code'] = df_jobs['zip_code'].apply(lambda x: "".join(re.findall(r'^\d{2}', x)))
    df_jobs['zip_code'][df_jobs['zip_code'].isna()] = 0
    # Creation de colonne update
    df_jobs['update_date'] = datetime.now().strftime('%d/%m/%Y')

    # mise en forme de soft skills
    df_jobs['soft_skills'] = df_jobs['soft_skills'].apply(lambda x: ", ".join(x))

    # Sauvegarde en CSV
    df_jobs.to_csv('jungle_jobs.csv', index=False)
    df_entreprises.to_csv('jungle_companies.csv', index=False)

    return df_jobs, df_entreprises


def scrape_wttj():
    job_urls = scrap_job_urls()
    job_data, entreprise_data = srape_job_data(job_urls)
    df_jobs, df_entreprises = process_data(job_data, entreprise_data)

    return df_jobs, df_entreprises


# Utilisation de la fonction principale
# df_jobs, df_entreprises = scrape_wttj()

# scrape_wttj()



#____________________________________LINKEDIN__________________________________

###################################################################################################################

###################################################################################################################
# PROJET 3 - Application pour rcherche offre d'emploi dans la DATA - 06/2024
# Team DATA TRACKs - Aurélien - Anna-Gael - Margaryta - Samia
#
#  LINKEDIN - OFFRE D EMPLOI
###################################################################################################################


# ------------------------------------------------------------------------------------------------------------
# FONCTION POUR LE SCRAPPING POUR LES DIFFERENTS JOBS DATA
# ------------------------------------------------------------------------------------------------------------

def scrapping_linkedin(job_to_scrap):
    print(f"--------------------------------------------------------------------------------")
    print(f"Lancement du scrapping sur LINKEDIN pour {job_to_scrap}")
    print(f"--------------------------------------------------------------------------------")

    ###########################################################################################################
    # Import des librairies
    import requests
    from bs4 import BeautifulSoup
    import math
    import pandas as pd
    import time

    # Déclaration de variables (listes)
    l = []  # liste des jobid
    d = []  # liste des dates de création des jobs car uniquement dispo sur une autre page

    o = {}  # dictionnaire pour les colonnes du futur dataframe
    offre = []  # liste des dictionnaires pour les colonnes du futur dataframe

    c = {}  # dictionnaire pour les colonnes du futur dataframe "entreprise"
    company = []  # liste des dictionnaires pour les colonnes du futur dataframe "entreprise"

    # Pour faciliter le scrapping

    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"}

    # SCRAPPING  # job_to_scrap
    ## Filtre sur les offres
    ### *Nombre d'offres*
    link_debut = "https://www.linkedin.com/jobs/search?keywords="
    link_fin = "&location=France&geoId=105015875&f_TPR=r2592000&position=1&pageNum=0"
    link = link_debut + job_to_scrap + link_fin

    res = requests.get(link, headers=header)
    # reponse ok de pour le scrapping
    if res.status_code != 200:

        print("NIV1 - Réponse négative du site : ", res)

    else:
        # temporisation
        time.sleep(5)
        soup_niv1 = BeautifulSoup(res.text, 'html.parser')

        ################################################################################################"
        # Forcé à 500 - car format à bougé entre temps
        alljobs = 500
        ################################################################################################"
        print(f"Nombre d'offre(s) à scrapper : {alljobs}")

        # Récupération du 1er id des offres
        first_job = soup_niv1.find("ul",
                                   {"class": "jobs-search__results-list"}
                                   ).find("div").get("data-entity-urn").split(":")[3]

        # print(f"id_first_job : {first_job}")

        ### *Récupération de tous les id sur l'API cachée*
        target_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=" + job_to_scrap + "&location=France&geoId=105015875&currentJobId=" + first_job + "&start={}"
        # print(target_url)

        # Vidange de la liste l des n° id_job pour ne pas cumuler les données à chaque relance et # liste des dates de création des jobs
        l.clear()
        d.clear()

        # Dans chaque page i, 10 offres sont affichées

        for i in range(0, math.ceil(int(alljobs) / 10)):

            if i == 0:
                j = 0
            else:
                j = i * 10

            res = requests.get(target_url.format(j), headers=header)
            if res.status_code != 200:
                print("NIV2 - Réponse négative du site : ", res)
                # print(target_url.format(j))
            else:
                time.sleep(0.7)
                soup_niv2 = BeautifulSoup(res.text, 'html.parser')
                alljobs_on_this_page = soup_niv2.find_all("li")

                # print(f"Nombre de job dans la page {len(alljobs_on_this_page)}, {alljobs_on_this_page}")
                # récupération des id des jobs
                for x in range(0, len(alljobs_on_this_page)):
                    try:
                        jobid = \
                        alljobs_on_this_page[x].find("div", {"class": "base-card"}).get('data-entity-urn').split(":")[3]
                    except:
                        jobid = alljobs_on_this_page[x].find("a", {
                            "class": "base-card relative w-full hover:no-underline focus:no-underline base-card--link base-search-card base-search-card--link job-search-card"}).get(
                            'data-entity-urn').split(":")[3]
                        # print(jobid)
                    l.append(jobid)
                    # balise avec date parution <time class="job-search-card__listdate--new" datetime="2024-06-07">
                    jobdate = alljobs_on_this_page[0].find("div", {"class": "base-search-card__metadata"}).find(
                        "time").get('datetime').strip()
                    d.append(jobdate)

        ## Avec les n° id des jobs => Scrapping infos sur Page individuelle offre sur API
        print(f"Lancement du scrapping sur les Pages individuelles offres LINKEDIN pour les {alljobs} offres")

        target_url = 'https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{}'

        offre.clear()
        # company.clear()

        # id//job_title//company_name//city//zip_code//contract_type//salary//job_description//profile_description//
        # date_creation//soft_skills//hard_skills//link

        for j in range(0, len(l)):
            # print(target_url.format(l[j]))
            resp = requests.get(target_url.format(l[j]), headers=header)
            time.sleep(0.5)
            if res.status_code != 200:
                print("NIV3 - Réponse négative du site : ", res)

            else:
                soup_niv3 = BeautifulSoup(resp.text, 'html.parser')

                o["id"] = l[j] + "_linkedin"

                try:
                    o["job_title"] = soup_niv3.find("div", {"class": "top-card-layout__entity-info"}).find(
                        "a").text.strip()
                except:
                    o["job_title"] = None

                try:
                    o["company_name"] = soup_niv3.find("div", {"class": "top-card-layout__card"}).find("a").find(
                        "img").get('alt')
                except:
                    o["company_name"] = None

                try:
                    o["city"] = soup_niv3.find("span",
                                               {"class": "topcard__flavor topcard__flavor--bullet"}).text.strip()
                except:
                    o["city"] = None

                try:
                    o["zip_code"] = soup_niv3.find("span",
                                                   {"class": "topcard__flavor topcard__flavor--bullet"}).text.strip()
                except:
                    o["zip_code"] = None

                try:
                    o["contract_type"] = \
                    (soup_niv3.find("ul", {"class": "description__job-criteria-list"}).text).replace('Seniority level',
                                                                                                     '').replace(
                        'Employment type', '|').replace('Job function', '|').replace('Industries', '|').replace('\n',
                                                                                                                '').split(
                        "|")[1].strip()
                except:
                    o["contract_type"] = None

                o["salary"] = None

                try:
                    o["job_description"] = (
                        soup_niv3.find("div", {"description__text description__text--rich"}).text.strip()).replace(
                        "Show more", "").replace("Show less", "").replace("\n", "").strip()
                except:
                    o["job_description"] = None

                try:
                    o["profile_description"] = (
                        soup_niv3.find("div", {"description__text description__text--rich"}).text.strip()).replace(
                        "Show more", "").replace("Show less", "").replace("\n", "").strip()
                except:
                    o["profile_description"] = None

                # profile_description		date_creation	soft_skills	hard_skills	link
                o["date_creation"] = d[j]

                try:
                    o["soft_skills"] = (
                        soup_niv3.find("div", {"description__text description__text--rich"}).text.strip()).replace(
                        "Show more", "").replace("Show less", "").replace("\n", "").strip()
                except:
                    o["soft_skills"] = None

                try:
                    o["hard_skills"] = (
                        soup_niv3.find("div", {"description__text description__text--rich"}).text.strip()).replace(
                        "Show more", "").replace("Show less", "").replace("\n", "").strip()
                except:
                    o["hard_skills"] = None

                try:
                    o["link"] = soup_niv3.find("a", {"class": "topcard__link"}).get("href")
                    # print (o["link"])
                except:
                    o["link"] = None

                # Fin des colonnes obligatoires pour les offres

                try:
                    o["niveau_hierarchique"] = \
                    (soup_niv3.find("ul", {"class": "description__job-criteria-list"}).text).replace('Seniority level',
                                                                                                     '').replace(
                        'Employment type', '|').replace('Job function', '|').replace('Industries', '|').replace('\n',
                                                                                                                '').split(
                        "|")[0].strip()
                except:
                    o["niveau_hierarchique"] = None

                try:
                    o["Fonction"] = \
                    (soup_niv3.find("ul", {"class": "description__job-criteria-list"}).text).replace('Seniority level',
                                                                                                     '').replace(
                        'Employment type', '|').replace('Job function', '|').replace('Industries', '|').replace('\n',
                                                                                                                '').split(
                        "|")[2].strip()
                except:
                    o["Fonction"] = None
                # Fin des colonnes facultatives pour les offres

                # ENTREPRISES Colonnes
                # company_name (plus haut) 	company_description 	logo 	company_link	company_note	company_sector
                try:
                    o["company_description"] = (
                        soup_niv3.find("div", {"description__text description__text--rich"}).text.strip()).replace(
                        "Show more", "").replace("Show less", "").replace("\n", "").strip()
                except:
                    o["company_description"] = None

                try:
                    o["logo"] = soup_niv3.find("section", {
                        "class": "top-card-layout container-lined overflow-hidden babybear:rounded-[0px]"}).find(
                        "img").get('data-delayed-url')
                except:
                    o["logo"] = None

                try:
                    o["company_link"] = soup_niv3.find("a", {"topcard__org-name-link topcard__flavor--black-link"}).get(
                        'href').strip()
                except:
                    o["company_link"] = None

                try:
                    o["company_note"] = None
                except:
                    o["company_note"] = None

                try:
                    o["company_sector"] = \
                    (soup_niv3.find("ul", {"class": "description__job-criteria-list"}).text).replace('Seniority level',
                                                                                                     '').replace(
                        'Employment type', '|').replace('Job function', '|').replace('Industries', '|').replace('\n',
                                                                                                                '').split(
                        "|")[3].strip()
                except:
                    o["company_sector"] = None

                offre.append(o)
                # company.append(c)

                o = {}
                # c = {}

            # CREATION DU DATAFRAME avec la liste des dictionnaires
            df_offre_linkedin = pd.DataFrame(offre)

            ### *"date_creation" str --> datetime*
            from datetime import datetime
            from datetime import date
            formatting = "%Y-%m-%d"
            df_offre_linkedin["date_creation"] = df_offre_linkedin["date_creation"].apply(
                lambda x: datetime.strptime(x, formatting))
            df_offre_linkedin["update"] = date.today()

            # suppression des doublons
            df_offre_linkedin.drop_duplicates(keep='first', inplace=True)

    return df_offre_linkedin


# ------------------------------------------------------------------------------------------------------------
# FONCTION POUR LE NETTOYAGE ET MISE EN FORME DES DONNEES LINKEDIN
# ------------------------------------------------------------------------------------------------------------
def fn_mise_en_forme(df_jobs_final):
    print(f"--------------------------------------------------------------------------------")
    print(f"Lancement de la Mise en Forme des DATA LINKEDIN")
    print(f"--------------------------------------------------------------------------------")

    # Suppression liste maudite des companies (à remplir si necessaire)
    liste_cie_maudite = ['LesJeudis']

    for cie in liste_cie_maudite:
        df_jobs_final = df_jobs_final[df_jobs_final['company_name'] != cie]

    # Suppression des enregistrements avec job_title vide en récupérant les id
    liste_linkedin_vide = list(df_jobs_final['id'][df_jobs_final['job_description'].isna()])
    for id_linkedin in liste_linkedin_vide:
        df_jobs_final = df_jobs_final.loc[df_jobs_final["id"] != id_linkedin]

    # Suppression des lignes en double en gardant la plus récente
    # Tri par date_creation descendant
    df_jobs_final = df_jobs_final.sort_values(by='date_creation', ascending=False).copy()
    df_jobs_final = df_jobs_final.drop_duplicates(subset='id', keep='first').copy()

    ## Transformation city
    # exemple : city [Clermont-Ferrand, Auvergne-Rhône-Alpes, France] et zip code
    df_jobs_final['city'] = df_jobs_final['city'].apply(lambda x: (str(x).split(','))[0])
    # Chercher avec les autres df de la team
    df_jobs_final['zip_code'] = df_jobs_final['zip_code'].apply(lambda x: None)

    ## Transformation Contract_type
    def contrat(wholedf):
        if 'CDI' in (wholedf['job_title']) or 'CDI' in (wholedf['job_description']):
            return 'CDI'
        elif 'CDD' in (wholedf['job_title']) or 'CDD' in (wholedf['job_description']):
            return 'CDD'
        elif 'Alternan' in (wholedf['job_title']) or 'Alternan' in (wholedf['job_description']) or 'Intern' in (
        wholedf['job_title']) or 'Intern' in (wholedf['job_description']):
            return 'Alternance'
        elif 'ALTERNAN' in (wholedf['job_title']) or 'ALTERNAN' in (wholedf['job_description']) or 'INTERN' in (
        wholedf['job_title']) or 'INTERN' in (wholedf['job_description']):
            return 'Alternance'
        elif 'alternan' in (wholedf['job_title']) or 'alternan' in (wholedf['job_description']) or 'intern' in (
        wholedf['job_title']) or 'intern' in (wholedf['job_description']):
            return 'Alternance'
        elif 'STAGE' in (wholedf['job_title']) or 'STAGE' in (wholedf['job_description']):
            return 'Stage'
        elif 'Stage' in (wholedf['job_title']) or 'Stage' in (wholedf['job_description']):
            return 'Stage'
        elif 'stage' in (wholedf['job_title']) or 'stage' in (wholedf['job_description']):
            return 'Stage'
        else:
            return 'NC'

    # print(df_jobs_final)

    df_jobs_final['contract_type'] = df_jobs_final.apply(contrat, axis=1)

    ## Récupération soft et hard skills
    # listes des skills via chatGPT
    hard_skills = ['Jira', 'CNN', 'RNN', 'Régression', 'classification', 'clustering', 'réduction de dimensionnalité',
                   'Tableau',
                   'Power BI', 'PowerBI', 'Matplotlib', 'Seaborn', 'Plotly', 'MongoDB', 'Cassandra', 'Couchbase',
                   'Hive', 'Pig', 'NoSQL',
                   'Hadoop', 'Spark', 'Bash', 'PowerShell', 'MySQL', 'PostgreSQL', 'Oracle', 'SQL', 'R', 'Pandas',
                   'NumPy', 'SciPy', 'Scikit-learn',
                   'TensorFlow', 'Keras', 'PyTorch', 'Python', 'Agile', 'Scrum', 'AWS', 'Google Cloud Platform',
                   'Microsoft Azure', 'Azure',
                   'AWS', 'S3', 'Redshift', 'Google BigQuery']

    soft_skills = ["Compétences en communication", "Esprit analytique","Travail en équipe", "Gestion du temps",
                   "Adaptabilité",
                   "Curiosité et apprentissage continu", "Attention aux détails", "Ethique et confidentialité",
                   "Résolution de problèmes",
                   "Esprit critique", "Capacité de synthèse", "Gestion des parties prenantes", "Vision stratégique",
                   "Compétences en leadership",
                   "Créativité", "Empathie", "Autonomie", "Négociation", "Résilience", "Compétences interpersonnelles",
                   "Gestion de projet",
                   "Pensée systémique", "Esprit d'initiative", "Capacité à gérer l'incertitude", "Gestion des conflits",
                   "Influence",
                   "Gestion des risques", "Pensée orientée vers les résultats", "Innovation", "Gestion des relations",
                   "Conscience culturelle",
                   "Transparence", "Gestion du changement", "Orientation client", "Collaboration interfonctionnelle",
                   "Optimisation des processus",
                   "Capacité à faire face à la pression", "Prise de décision éclairée", "Esprit d'entreprise",
                   "Communication skills", "Analytical skills", "Teamwork skills", "Time management", "Adaptability",
                   "Curiosity and continuous learning",
                   "Attention to detail", "Ethics and confidentiality", "Problem solving", "Critical thinking",
                   "Ability to synthesize",
                   "Stakeholder management", "Strategic vision", "Leadership skills", "Creativity", "Empathy",
                   "Autonomy", "Negotiation skills", "Resilience",
                   "Interpersonal skills", "Project Management", "Systems thinking", "Initiative",
                   "Ability to manage uncertainty", "Conflict management",
                   "Influence", "Risk management", "Results-oriented thinking", "Innovation", "Relationship Management",
                   "Cultural awareness",
                   "Transparency", "Change management", "Customer orientation", "Cross-functional collaboration",
                   "Process optimization",
                   "Ability to cope with pressure", "Informed decision-making", "Entrepreneurial spirit"]

    # fonction recherche dans le texte du job les skills
    def skills_soft(texte):
        # print(skills_list)
        liste_skills = []
        for skill in soft_skills:
            if skill.lower() in texte.lower():
                liste_skills.append(skill)
        # return liste_skills
        return ",".join(liste_skills)

    def skills_hard(texte):
        # print(skills_list)
        liste_skills = []
        for skill in hard_skills:
            if skill.lower() in texte.lower():
                liste_skills.append(skill)
        # return liste_skills
        return ",".join(liste_skills)

    df_jobs_final['soft_skills'] = df_jobs_final['job_description'].apply(skills_soft)
    df_jobs_final['hard_skills'] = df_jobs_final['job_description'].apply(skills_hard)

    # supression des colonnes inutiles
    df_jobs_final.drop(columns=['niveau_hierarchique', 'Fonction'], inplace=True)

    print(f"--------------------------------------------------------------------------------")
    print(f"Fin de la Mise en Forme des DATA LINKEDIN")
    print(f"--------------------------------------------------------------------------------")

    return df_jobs_final


# ------------------------------------------------------------------------------------------------------------
# PROGRAMME PRINCIPAL
# ------------------------------------------------------------------------------------------------------------
def linkedin():
    import pandas as pd

    print(f"--------------------------------------------------------------------------------")
    print(f"Lancement L'extraction des DATA LINKEDIN")
    print(f"--------------------------------------------------------------------------------")

    liste_jobs = ["Data+Analyste", "Business+Analyst", "Data+Scientist", "Data+Engineer"]

    # 1 - SCRAPPING
    # Boucle sur la liste des jobs recherchés

    ind = 0
    for job in liste_jobs:
        if ind == 0:
            df_linkedin_total = scrapping_linkedin(job)
            ind += 1
            # print(type(df_linkedin_total))
        else:
            df_linkedin_1 = scrapping_linkedin(job)
            df_linkedin_total = pd.concat([df_linkedin_total,
                                           df_linkedin_1],
                                          axis=0,
                                          ignore_index=True)
    # print(df_linkedin_total)
    # test sur le contenu du dataframe :
    if df_linkedin_total.empty:
        print('DataFrame is empty!')

    else:
        # print(df_linkedin_total)
        # 2 - MISE EN FORME
        df_linkedin_total = fn_mise_en_forme(df_linkedin_total)
        df_linkedin_total.sort_index(axis=0, inplace=True)

        df_linkedin_jobs = df_linkedin_total[['id', 'job_title', 'company_name', 'city', 'zip_code', 'contract_type',
                                              'salary', 'job_description', 'profile_description', 'date_creation',
                                              'soft_skills', 'hard_skills', 'link', 'update']]
        df_linkedin_cies = df_linkedin_total[['company_name','company_description', 'logo',
                                              'company_link', 'company_note', 'company_sector']]

        # suppression des doublons
        df_linkedin_cies.drop_duplicates(subset='company_name',keep='first', inplace=True)
        df_linkedin_cies.dropna(subset='company_name', inplace=True)

        # print(df_linkedin_jobs)

        # 3 - CREATION DES CSV
        df_linkedin_jobs.to_csv('linkedin_jobs.csv', index=False, encoding='utf-8')
        df_linkedin_cies.to_csv('linkedin_companies.csv', index=False, encoding='utf-8')

    print(f"--------------------------------------------------------------------------------")
    print(f"Fin L'extraction des DATA LINKEDIN")
    print(f"--------------------------------------------------------------------------------")

    return



#_________________________ALL THE MINI FUNC FOR SCRAP HELLO WORK ____________________


hard_skills=['Jira','CNN','RNN','Régression','POWER BI', 'BI' 'classification', 'clustering', 'réduction de dimensionnalité', 'Tableau', 'Power BI', 'Matplotlib', 'Seaborn', 'Plotly', 'MongoDB', 'Cassandra', 'Couchbase', 'Hive', 'Pig', 'NoSQL', 'Hadoop', 'Spark', 'Bash', 'PowerShell', 'MySQL', 'PostgreSQL', 'Oracle', 'SQL', 'R', 'Pandas', 'NumPy', 'SciPy', 'Scikit-learn', 'TensorFlow', 'Keras', 'PyTorch', 'Python', 'Agile', 'Scrum', 'AWS', 'Google Cloud Platform', 'Microsoft Azure', 'AWS', 'S3', 'Redshift', 'Google BigQuery',"Azure Data Lake","AWS Glue",
"Azure Synapse Analytics", "GDPR Compliance", "Data Encryption",
"IAM (Identity and Access Management)", "PyTest", "Unit Testing",
"Data Validation Tools (e.g., Great Expectations)","Trello","Asana","Confluence",
"MuleSoft","Apigee","MicroStrategy","SAP BusinessObjects","Collibra","Alation","Talend Data Quality","Informatica Data Quality","SPSS","SAS","Minitab","D3.js","QlikView","Looker","Julia","Scala","Java","C++","C#","Docker",
"Kubernetes","Jenkins","Git","GitLab CI/CD","Ansible","Terraform","Snowflake","Teradata","Apache NiFi",
"Talend","Informatica","Alteryx","XGBoost","LightGBM","CatBoost","OpenCV","Reinforcement Learning",
"GANs (Generative Adversarial Networks)","Kafka","Flink","Druid",
"Presto","Airflow"]

#__________FIND HARD SKILLS____________

def hard_sk(x):
    l = []
    for skill in hard_skills:
        if skill in x:
            l.append(skill)
    return l


soft_skills = [ "Compétences en communication", "Esprit analytique", "Travail en équipe",
    "Gestion du temps","Adaptabilité","Curiosité et apprentissage continu", "Attention aux détails","Ethique et confidentialité","Résolution de problèmes","Esprit critique","Capacité de synthèse","Gestion des parties prenantes","Vision stratégique", "Compétences en leadership", "Créativité","Empathie","Négociation","Résilience","Compétences interpersonnelles","Gestion de projet","Pensée systémique","Esprit d'initiative",
    "Capacité à gérer l'incertitude",
    "Gestion des conflits", "Influence","Gestion des risques","Pensée orientée vers les résultats","Innovation","Gestion des relations",
    "Conscience culturelle", "Transparence", "Gestion du changement", "Orientation client", "Collaboration interfonctionnelle",
    "Optimisation des processus", "Capacité à faire face à la pression", "Prise de décision éclairée",
    "Esprit d'entreprise", "Capacité de vulgarisation", "Capacité d'écoute active", "Gestion des priorités",
    "Compétences en mentorat","Capacité à donner et recevoir des feedbacks",
    "Confiance en soi","Établissement de rapports", "Persévérance","Gestion de l'ambiguïté","Intelligence émotionnelle",  "Diplomatie",  "Patience", "Proactivité","Vision à long terme","Capacité à motiver les autres","Capacité à inspirer","Flexibilité cognitive","Pensée critique","Sens de l'humour","Gestion du stress","Capacité à déléguer","Sens de l'organisation","Fiabilité","Capacité à travailler dans des environnements multiculturels","Capacité à mener des entretiens","Capacité à évaluer des performances","Capacité à travailler en autonomie", "Capacité à formuler des objectifs clairs","Capacité à construire des alliances","Capacité à apprendre des erreurs", "Sens de l'éthique professionnelle", "Capacité à gérer les attentes", "Capacité à maintenir des relations positives",  "Orientation vers la qualité","Capacité à travailler sous des délais serrés", "Capacité à intégrer des retours critiques","Capacité à prioriser les tâches", "Sens des affaires","Capacité à travailler à distance", "Gestion des imprévus", "Gestion de l'information",
    "Capacité à travailler avec des parties prenantes multiples",
    "Capacité à influencer sans autorité directe",
    "Capacité à concevoir des solutions créatives", "Capacité à travailler dans un environnement changeant", "Capacité à traiter des informations complexes","Orientation vers la performance","Capacité à comprendre les besoins des clients",
    "Capacité à développer des relations de confiance", "Capacité à coacher et former les autres", "Capacité à évaluer l'impact des décisions", "Capacité à communiquer des idées complexes","Capacité à gérer des projets multiples","Capacité à adapter le style de communication", "Capacité à intégrer des perspectives diversifiées", "Capacité à créer une culture de collaboration","Capacité à développer et gérer un réseau professionnel","Capacité à favoriser l'innovation","Capacité à anticiper les tendances futures","Capacité à naviguer dans des structures organisationnelles complexes", "Capacité à comprendre et utiliser les technologies émergentes","Capacité à équilibrer les priorités concurrentes","Capacité à élaborer des stratégies à long terme","Capacité à promouvoir une culture de l'apprentissage","Capacité à démontrer de l'intégrité","Capacité à renforcer la résilience de l'équipe","Capacité à communiquer avec assurance","Capacité à promouvoir la diversité et l'inclusion","Capacité à gérer les performances",
    "Capacité à comprendre les implications économiques",
    "Capacité à améliorer les processus existants","Capacité à soutenir le développement personnel", "Capacité à influencer le changement organisationnel", "Capacité à penser de manière anticipative",  "Capacité à mener des audits et des évaluations",
    "Capacité à définir des KPI pertinents", "Capacité à assurer la conformité réglementaire", "Capacité à promouvoir le bien-être au travail", "Capacité à développer des plans de continuité","Capacité à faciliter des workshops",
    "Capacité à créer des présentations percutantes","Capacité à analyser les dynamiques d'équipe",
    "Capacité à résoudre des conflits interpersonnels","Capacité à développer des politiques de données","Capacité à gérer les ressources humaines","Capacité à négocier avec les fournisseurs","Capacité à comprendre les besoins de formation", "Capacité à évaluer les compétences des équipes","Capacité à influencer la prise de décision","Capacité à identifier et à gérer les interdépendances",
    "Capacité à promouvoir la responsabilité individuelle et collective",
    "Capacité à travailler efficacement dans des environnements agiles",
    "Capacité à développer des solutions centrées sur l'utilisateur",
    "Capacité à intégrer la durabilité dans les pratiques professionnelles",
    "Capacité à gérer les coûts et les budgets",
    "Capacité à articuler une vision claire",
    "Capacité à évaluer et à intégrer les technologies de pointe",
    "Capacité à développer une culture de responsabilité",
    "Capacité à inspirer la confiance",
    "Capacité à gérer des équipes interdisciplinaires",
    "Capacité à comprendre les enjeux géopolitiques",
    "Capacité à créer et à gérer des feuilles de route",
    "Capacité à mener des études de marché",
    "Capacité à élaborer des stratégies de mise en œuvre",
    "Capacité à gérer des projets de transformation numérique",
    "Capacité à gérer la continuité des activités",
    "Capacité à évaluer les modèles économiques",
    "Capacité à favoriser la co-création",
    "Capacité à promouvoir l'engagement des employés",
    "Capacité à mettre en place des processus de gouvernance",
    "Capacité à conduire des évaluations d'impact",
    "Capacité à gérer la croissance de l'entreprise",
    "Capacité à élaborer des politiques de diversité et d'inclusion",
    "Capacité à coordonner des initiatives transversales",
    "Capacité à développer des programmes de reconnaissance",
    "Capacité à établir des partenariats stratégiques",
    "Capacité à piloter des projets internationaux",
    "Capacité à identifier des opportunités de marché",
    "Capacité à formuler des propositions de valeur",
    "Capacité à promouvoir une culture d'innovation",
    "Capacité à optimiser les performances opérationnelles",
    "Capacité à anticiper les besoins futurs","Capacité à gérer des portefeuilles de projets","Capacité à identifier et à atténuer les risques",
    "Capacité à conduire des transformations organisationnelles","Capacité à promouvoir l'agilité organisationnelle","Capacité à aligner les objectifs stratégiques et opérationnels","Capacité à développer des indicateurs de performance","Capacité à renforcer l'engagement des parties prenantes","Capacité à mettre en œuvre des changements culturels","Capacité à favoriser le développement des talents","Capacité à promouvoir la collaboration ouverte","Capacité à gérer la complexité","Capacité à conduire des analyses de rentabilité","Capacité à identifier des synergies","Capacité à promouvoir la responsabilité environnementale","Capacité à développer des écosystèmes d'innovation","Capacité à adapter les stratégies en fonction des feedbacks","Capacité à promouvoir une culture de l'amélioration continue",'Curiosité','Autonomie','Écoute active','Communication orale','Respect','Flexibilité et adaptabilité','Attitude positive','Faire confiance','Responsabilité','Intégrité','Ouverture à la nouveauté',
]

#___________SOFT SKILLS ADD________________

def soft_sk(x):
    l = []
    for skill in soft_skills:
        if skill in x:
            l.append(skill)
    return l

#____________CHANGE HTML TO TEXT _______________

def strip_text(x):
    y = x.strip()
    return y


#_____________ COMPANY DATASET CLEANING________________

sectors = ['Services aux Personnes • Particuliers',
           'Secteur informatique • ESN',
           'Santé • Social • Association',
           'Industrie Pétrolière • Pétrochimie',
           'Service public hospitalier',
           'Service public des collectivités territoriales',
           'Industrie Pharmaceutique • Biotechn. • Chimie',
           'Transport • Logistique','Industrie Agro-alimentaire',
           'Industrie Aéronautique • Aérospatial', 'Industrie Auto • Meca • Navale',
           'Média • Internet • Communication',
           'Industrie high-tech • Telecom','BTP', 'Enseignement • Formation',
           'Industrie Manufacturière', 'Secteur Energie • Environnement',
           'Distribution • Commerce de gros',
           'Banque • Assurance • Finance', 'Services aux Entreprises','Secteur informatique • ESN',
           'Industrie Manufacturière','Tourisme • Hôtellerie • Loisirs','Immobilier',
           'Agriculture • Pêche',
           'Santé • Social • Association']

def sector_search(x):
    if x in sectors:
        return x
    else :
        return "non renseigné"








#____________________________________HELLO WORK __________________________________

def hellowork1():
    data_jobs_id = []
    metiers = ['Data', "Analyst", "Analyste"]
    for i in range(1, 70):
    # for i in range(1, 2):  # pour test intermedaire
        api = 'https://www.hellowork.com/searchoffers/getsearchfacets?k=Data&k_autocomplete=Data+analyst&l=france&ray=all&cod=all&d=all&p=' + str(
            i) + '&mode=scroll&alert=%20&timestamp=1701361414591'
        r = requests.get(api, headers={
            'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"})
        data = json.loads(r.text)
        for j in range(0, 31):
        # for j in range(0, 4):  # pour test intermedaire
            for metier in metiers:
                if metier in data['Results'][1]['OfferTitle']:
                    try:
                        data_jobs_id.append(data['Results'][j]['Id'])
                    except IndexError:
                        pass
                else:
                    pass

    list_data_jobs = []
    list_data_companies = []

    for ele in data_jobs_id:
        url = 'https://www.hellowork.com/fr-fr/emplois/' + str(ele) + '.html'
        link = requests.get(url, headers={
            'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"})
        company_link = 'https://www.hellowork.com/fr-fr/emplois/' + ele + '.html'

        if link.status_code == 200:
            try:
                soup = BeautifulSoup(link.text, 'html.parser')

                t = soup.find('h1', class_='tw-inline').text
                r = ''.join(t.split('\n'))
                job_title = r.split('H/F')[0]
                company_name = r.split('H/F')[1]

                contract = soup.find_all('span', class_='tw-inline-flex tw-typo-m tw-text-grey')
                location = contract[0].get_text()



                contract_type = contract[1].get_text()

                # link1 = soup.find('a', {'class' : 'tw-text-base tw-mr-2 tw-link-text tw-mb-4'})
                # link = link1['href']

                date = soup.find('span', {'class': 'tw-block tw-typo-xs tw-text-grey tw-mt-3 tw-break-words'})
                t = date.get_text()
                date = re.findall('\d+/\d+/\d+', t)
                date = ''.join(date)

                description = soup.find_all('p', class_='tw-typo-long-m')
                profile_description = description[1].get_text()
                job_description = description[0].get_text()

                info = soup.find_all(class_='tw-readonly')
                s = info[2].text
                s = s.replace("\u202f", "")
                s = re.findall("\S+", s)
                salary = ' '.join(s)

                # _______________COMPANIES_____________________
                company_sector = info[4].text
                sector2 = info[5].text

                t = soup.find('h1', class_='tw-inline').text
                r = ''.join(t.split('\n'))
                company_name = r.split('H/F')[1]

                com = soup.find_all('p', class_='tw-typo-long-m tw-mb-12 sm:tw-mb-14 tw-break-words')
                com = com[2].get_text()
                company_description = com

                image = soup.find_all('img', class_='tw-h-7 sm:tw-h-11')
                logo = image[0].get('src')

                url = soup.find('a', class_='tw-text-base tw-mr-2 tw-link-text tw-mb-4')
                link = url.get('href')



            except AttributeError:
                pass
            except IndexError:
                pass

            update_date = datetime.now().strftime('%d/%m/%Y')

            d_jobs = {'id': ele,
                      'job_title': job_title,
                      'company_name': company_name,
                      'location' : location,
                      'contract_type': contract_type,
                      'salary': salary,
                      'job_description': job_description,
                      'profile_description': profile_description,
                      'date_creation': date,
                      'link': company_link,
                      'update_date': update_date
                      }

            list_data_jobs.append(d_jobs)

            d_companies = {'id': ele,
                           'company_name': company_name,
                           'company_description': company_description,
                           'logo': logo,
                           'company_link': url,
                           'company_sector': company_sector,
                           'sector2': sector2,
                           'update_date': update_date
                           }

            list_data_companies.append(d_companies)

    df_hello_companies = pd.DataFrame(list_data_companies)

    df_hello = pd.DataFrame(list_data_jobs)

    # _____________________CLEANING JOBS______________________________________


    df_hello['zip_code'] = df_hello['location'].apply(lambda x : "- ".join(re.findall('- \d{2}', x)).replace("- " ,""))
    df_hello['zip_code'][df_hello['zip_code'].isna()] = 0
    # df_hello['zip_code'] = df_hello['zip_code'].apply(lambda x: int(x))

    df_hello['city'] = df_hello['location'].apply(lambda x: re.sub('- \d{2}', '', x))

    df_hello['salary'] = df_hello['salary'].apply(
        lambda x: "".join(re.findall('\d+ - \d+', x)).replace('07 - 1766', '477,07 - 1766,92'))
    df_hello = df_hello[(df_hello['contract_type'] == 'CDI') | (df_hello['contract_type'] == 'CDD') | (
            df_hello['contract_type'] == 'Stage') | (df_hello['contract_type'] == 'Alternance')]

    df_hello['job_description'] = df_hello['job_description'].apply(strip_text)
    df_hello['profile_description'] = df_hello['profile_description'].apply(strip_text)

    df_hello['soft_skills'] = df_hello['profile_description'].apply(soft_sk)
    df_hello['hard_skills'] = df_hello['profile_description'].apply(hard_sk)
    df_hello.drop(columns=['location'], inplace=True)

    df_hello['soft_skills'] = df_hello['soft_skills'].apply(lambda x: ', '.join(x))

    df_hello['hard_skills'] = df_hello['hard_skills'].apply(lambda x: ', '.join(x))

    df_hello.drop_duplicates(subset='id', inplace=True)

    # _____________________CLEANING COMPANIES______________________________________

    df_hello_companies['company_description'] = df_hello_companies['company_description'].apply(strip_text)

    df_hello_companies['company_sector'] = df_hello_companies['company_sector'].apply(strip_text)
    df_hello_companies['company_sector'] = df_hello_companies['company_sector'].apply(sector_search)

    df_hello_companies['sector2'] = df_hello_companies['sector2'].apply(strip_text)
    df_hello_companies['sector2'] = df_hello_companies['sector2'].apply(sector_search)

    df_hello_companies['company_sector'].fillna(df_hello_companies['sector2'], inplace=True)
    df_hello_companies.drop(columns=['sector2'], inplace=True)

    df_hello_companies.drop_duplicates(subset='company_name',keep='first', inplace=True)

    df_hello.to_csv('hello_jobs.csv', index=False)
    df_hello_companies.to_csv('hello_companies.csv', index=False)
    return

