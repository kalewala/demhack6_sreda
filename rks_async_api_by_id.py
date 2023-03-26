import aiohttp
import asyncio
import pandas as pd
from datetime import datetime as dt

async def get_records(record_ids):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for record_id in record_ids:
            tasks.append(asyncio.ensure_future(get_record(record_id, session)))
        results = await asyncio.gather(*tasks)
        return pd.concat(results)

async def get_record(record_id, session):
    try:
        async with session.get(f"https://reestr.rublacklist.net/api/v3/record/{record_id}/") as response:
            json_record = await response.json()
            print(f"{dt.now()} Request successful for record {record_id}")
            return pd.DataFrame.from_dict(json_record, orient='index').T
    except:
        print(f"{dt.now()} Request failed for record {record_id}")
        return pd.DataFrame()

async def main():
    df_total = pd.DataFrame()
    batch_size = 10_000
    start_id = 10_000
    end_id = 5_600_000
    record_ids = range(start_id, end_id)
    for i in range(0, len(record_ids), batch_size):
        batch_ids = record_ids[i:i+batch_size]
        batch_df = await get_records(batch_ids)
        df_total = pd.concat([df_total, batch_df])
        print(f"{dt.now()} Processed records {i+1}-{i+len(batch_df)}")
    df_total.to_csv('test_output.csv', index=False)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())