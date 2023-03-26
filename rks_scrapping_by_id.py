from bs4 import BeautifulSoup
from collections import defaultdict
from datetime import datetime as dt
import pandas as pd
import asyncio
import aiohttp

def get_id_list(relpath) -> list:
    return (pd.read_csv(relpath).record_id.to_list())

def make_ans_dict() -> defaultdict:
    ans_dict = defaultdict(list)
    return ans_dict

async def get_decision_text(session, record_id) -> str:
    url = f'https://reestr.rublacklist.net/ru/record/{record_id}/'
    async with session.get(url) as response:
        print(f'{record_id}: page has status {response.status}')
        rks_soup = BeautifulSoup(await response.text(), 'html.parser')
        decision_title_row = rks_soup.find('div', class_='td_title', text='Номер решения')
        if decision_title_row is None:
            print(f'{record_id}: has failed')
            return None
        decision_text = decision_title_row.findNext(class_='td_content')
        if decision_text is None:
            print(f'{record_id}: has failed')
            return None
        print(f'{record_id}: has worked successfully!')
        return decision_text.text

async def process_batch(id_list, scrapping_dict, session):
    batch_tasks = []
    for record_id in id_list:
        print(f'{dt.now()} started scrapping {record_id}')
        task = asyncio.ensure_future(get_decision_text(session, record_id))
        batch_tasks.append(task)
    results = await asyncio.gather(*batch_tasks)
    for record_id, text in zip(id_list, results):
        scrapping_dict['record_id'].append(record_id)
        scrapping_dict['decisionNumber'].append(text)
        print(f'{dt.now()} finished scrapping {record_id}')
        await asyncio.sleep(0.25)
    print(f'{dt.now()} finished processing {len(id_list)} records!')

async def main(id_list, scrapping_dict, initial_df_relpath, save_path):
    async with aiohttp.ClientSession() as session:
        batch_size = 10
        num_batches = len(id_list) // batch_size + (1 if len(id_list) % batch_size != 0 else 0)
        for i in range(num_batches):
            batch_start = i * batch_size
            batch_end = min((i + 1) * batch_size, len(id_list))
            batch_id_list = id_list[batch_start:batch_end]
            print(f'Processing batch {i + 1} of {num_batches} with {len(batch_id_list)} records...')
            await process_batch(batch_id_list, scrapping_dict, session)
        df_scrapping = pd.DataFrame(scrapping_dict)
        df_initial = pd.read_csv(initial_df_relpath)
        # merge and select the necessary columns
        df_target = (df_scrapping
                     .merge(df_initial, how='inner', on='record_id')
                     .loc[:, ['record_id', 'decisionNumber', 'decisionDate', 
                              'authority_id', 'authority_name', 'status',
                              'domains', 'urls']]
        )
        # save output to csv 
        df_target.to_csv(save_path, index=False)

if __name__ == '__main__':
    df_relpath = 'roskomsvoboda_regions_of_interest_2022.csv'
    rks_id_list = get_id_list(df_relpath)
    rks_dict = make_ans_dict()
    df_save_path = 'roskomvsoboda_regions_scrapping_2022.csv'
    asyncio.run(main(rks_id_list, rks_dict, df_relpath, df_save_path))
