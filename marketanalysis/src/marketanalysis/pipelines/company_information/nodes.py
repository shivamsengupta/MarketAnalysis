"""
This is a boilerplate pipeline 'company_information'
generated using Kedro 0.19.3
"""

import json
import pandas as pd
import google.generativeai as genai
import pymongo
GOOGLE_API_KEY = "YOUR_API_KEY"
genai.configure(api_key=GOOGLE_API_KEY)
gemini = genai.GenerativeModel('gemini-pro')
generation_config = genai.GenerationConfig(
  temperature=0.9
)

def final_results(cleaned_markdown, keywords):
    prompt="""
You have a Markdown document containing information about a company. 
Your task is to first very carefully analyze all the content from the Markdown document completely and then 
extract the following details anyhow from the Markdown content:
- Company Name
- One-liner description about the company.
- Founding date of the company.
- Use cases for the company (comma-separated list).
- Fundings amount details of the company (comma-separated list).
- Target user persona for the tool (e.g., Product Manager, Sales, Engineer, CEO, etc.) (comma-separated list).
- Features offered by the company (comma-separated list).
- Integrations available for the company (comma-separated list).
- Pricing packages offered for the product (comma-separated list).
- List of investors by VC name (comma-separated list).
- List of investors by lead investor name (comma-separated list).
- Relevant URLs for further research (comma-separated list).

##Instruction:
1. Don't mention the content in the bracket for the above details like (comma-separated list) or 
(e.g., Product Manager, Sales, Engineer, CEO, etc.)
2. Don't give results in pipe-format (e.g., | Company Name | Company Description | Founding Date | Use Cases | Fundings Amount | Target User Persona | Features | Integrations | Pricing Packages | Investors by VC Name | Investors by Lead Investor Name | Relevant URLs |)
3. Give results like this:
 *Company Name:* Amazon

*One-liner description:* A global e-commerce giant.

*Founding date:* July 5, 1994

*Use cases:*
- Online shopping
- Cloud computing
- Digital streaming
- AI and machine learning
- E-commerce fulfillment
and so on...
4. Try your best to fill all the details. Don't leave any section empty. If possible try searching
on web for that section for that particular company and then fill the details. But don't leave any 
section empty. 
"""

    prompt2="""
    Please provide me the following details.
- Company Name
- One-liner description about the company.
- Founding date of the company.
- Use cases for the company (comma-separated list).
- Fundings amount details of the company (comma-separated list).
- Target user persona for the tool (e.g., Product Manager, Sales, Engineer, CEO, etc.) (comma-separated list).
- Features offered by the company (comma-separated list).
- Integrations available for the company (comma-separated list).
- Pricing packages offered for the product (comma-separated list).
- List of investors by VC name (comma-separated list).
- List of investors by lead investor name (comma-separated list).
- Relevant URLs for further research (comma-separated list).

##Instruction:
Please follow all the below instructions properly:-
- Try using the internet for getting results. I need all the above mentioned details anyhow.
- Take time to search the above details on the internet, do whatever it takes to fetch me the 
  details anyhow.
- Search the official websites, use the above points as keywords for web search, do web scraping
  for fetching the results like "jasper.ai List of investors by VC name". In the similar way go
  to google search bar and search using above points one by one along with the company name to 
  fetch results.
- Keep trying again and again till you get results, I know you will get when you keep on trying again and again
- I need Fundings amount details of the company, List of investors by VC name, List of investors 
  by lead investor name anyhow. Try searching multiple websites and whole internet but fetch me 
  all the details no matter what.
- If any of the above points is not publicly disclosed go to other websites but keep on searching 
  till you get the results
- Please provide me the details in a neat and clean format.
- Try to get as much detail as you can for every point.
- Don't leave any point empty
- Don't mention the content in the bracket for the above details like (comma-separated list) or 
(e.g., Product Manager, Sales, Engineer, CEO, etc.)
- Don't give results in pipe-format (e.g., | Company Name | Company Description | Founding Date | Use Cases | Fundings Amount | Target User Persona | Features | Integrations | Pricing Packages | Investors by VC Name | Investors by Lead Investor Name | Relevant URLs |)
- Give results like this:
 *Company Name:* Amazon

*One-liner description:* A global e-commerce giant.

*Founding date:* July 5, 1994

*Use cases:*
- Online shopping
- Cloud computing
- Digital streaming
- AI and machine learning
- E-commerce fulfillment
In a similar way provide all the details.
- Try your best to fill all the details. Don't leave any section empty.
"""
    #json_string = json.dumps(cleaned_markdown)
    trial_message=cleaned_markdown
    message="The Company name is "+trial_message+" And the keywords are "+keywords+" "+prompt2
    full_message = gemini.generate_content(contents = message,
                                            generation_config=generation_config,
                                            stream=False)
    
    # message=json_string+"\n"+"""Use this prompt to generate desired results 
    # for the above markdown content as directed in the prompt"""+prompt
    # full_message = gemini.generate_content(contents = message,
    #                                         generation_config=generation_config,
    #                                         stream=False)
    #print(full_message.text)
    return full_message.text

def assemble(
       scraped_df=pd.DataFrame
)-> pd.DataFrame:
    information=[]
    found_record=[]
    dict1=[]
    company_profiles=""
    company_names=[]

    # for index, row in scraped_df.iterrows():
    #     cleaned_markdown = row['CLEANED_MARKDOWN']
    #     company=row["Company"]
    #     comp_info=final_results(cleaned_markdown)
    #     information.append({'Company': company,
    #                      'COMPANY_PROFILE': "".join(comp_info)
    #                      })
    print("Enter the company urls (preferred) or names one line at a time:")
    names = []
    while True:
        name = input()
        if name == "":
            break
        names.append(name.lower())

    guidance_keywords = input(
        "Enter any guidance keywords to improve search (comma separated, press Enter if none): "
    ).split(",")
    guidance_keywords = [keyword.strip().lower() for keyword in guidance_keywords if keyword.strip()]
    
    #             MONGO DB CLIENT CREATION.....................
    client= pymongo.MongoClient("mongodb://localhost:27017")
    db = client["COMPANY_NAME_KEYWORD_RESULTS_DATABASE"]
    collection = db["initial_collection"]

    sorted_names=sorted(names)
    sorted_keywords=sorted(guidance_keywords)
    #             DATABASE SEARCHING STARTED........................
    record=collection.find_one({"companynames":", ".join(sorted_names),
                                "keywords":", ".join(sorted_keywords)})
    if record:
        print("SEARCHING MATCHED WITH A DOCUMENT...........................................")
        found_record.append({"CompetitiveAnalysis":record["results"]})
        df=pd.DataFrame(found_record)

    else: 
        print("NO DOCUMENTS FOUND. INITIATING CREATION OF A NEW DOCUMENT....................................")
        keywords=""
        for k in sorted_keywords:
            keywords=keywords+" "+k
        print("INFORMATION FETCHING STARTED..............................................")
        for company in sorted_names:
            comp_info=final_results(company, keywords)
            information.append({'Company': company,
                         'COMPANY_PROFILE': "".join(comp_info)
                         })
        print("INFORMATION FETCHING DONE................................................")   
        print("PREPARING FOR DATABASE INSERTION.........................................")   
        company_names = [item['Company'] for item in information]
        sorted_company_names=sorted(company_names)
        company_profiles = '\n\n'.join(f"{item['COMPANY_PROFILE']}\n{'='*100}" for item in information)
        df = pd.DataFrame(information)
        dict1 = {"companynames": ", ".join(sorted_company_names),
                  "keywords": ", ".join(sorted_keywords), 
                  "results": company_profiles}
        
        print("INSERTING INTO DATABASE.................................................")
        collection.insert_one(dict1)
        
    return df