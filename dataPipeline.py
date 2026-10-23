#data pipeline - cleaning, tranformation, EDA
import logging
import pandas as pd

#logger
logging.basicConfig(level=logging.INFO,format = "%(levelname)s:%(message)s")
logger = logging.getLogger(__name__)

#Load
def importData(rawFile):
    df = pd.read_excel(rawFile)
    logger.info("Importing %s",rawFile)
    return df

# Inspect
def inspData(df):
    logger.info("\nFirst few rows of the dataframe:\n %s",df.head())
    logger.info("\nSize of the data:\n %s",df.shape)
    logger.info("\nData types of each column:\n %s",df.dtypes)
    logger.info("\nNumber of missing values in each column:\n%s",df.isna().sum())
    logger.info("\nDuplicate rows in the data:\n%s", df.duplicated().sum())
    return df
#clean
def clnHeader(df):       
    #renaming columns appropriately
    df.columns = (df.columns
                .str.strip()
                .str.lower()
                .str.replace(r'[^a-z0-9]+', '_', regex=True))
    logger.info("\nColumn names after cleaning:\n%s",df.columns)
        #required column chcek
    req_cols =['uniqueid','disbursed_amount']
    miss_cols = [col for col in req_cols if col not in df.columns]
    if miss_cols:
        raise KeyError(f"Data set is missing required columns:{miss_cols}")

    return df

#transform
def trnsfrmData(df):
    #dropping duplicate rows
    duplicate_count = df.duplicated().sum()
    if duplicate_count > 0:
        logger.info("\nNumber of duplicate rows found:%s", duplicate_count)
        df.drop_duplicates(inplace=True)
    else:
        logger.info("\n No duplicates found %s", )
    
    #filling missing values in the 'employment_type' column with 'Unknown'
    print(f"\nNumber of missing values in 'employment_type' column before filling: {df['employment_type'].isnull().sum()}.")
    df['employment_type'] = df['employment_type'].fillna('Unknown')
    missing_after_filling = df['employment_type'].isnull().sum()
    if missing_after_filling == 0:
        print(f"Missing values in 'employment_type' column after filling: {missing_after_filling}.")
    else:
        print(f"There are still {missing_after_filling} missing values in 'employment_type' column after filling.")
    #date col
    df['disbursaldate'] = pd.to_datetime(df['disbursaldate'],errors='coerce')
    df['date_of_birth'] = pd.to_datetime(df['date_of_birth'],errors='coerce')
    #numeric col
    num_col =['disbursed_amount','asset_cost','ltv']
    for col in num_col:
        df[col] = pd.to_numeric(df[col],errors='coerce')
    #invalid check
    invalid_mask = (df['disbursaldate'] < df['date_of_birth'])|(df['date_of_birth']>pd.Timestamp.today().normalize())|(df['disbursed_amount']<0)|(df['asset_cost']<0) |(df['ltv'] < 0)
    if invalid_mask.sum()>0:
        print(f'Quarantine records#: {invalid_mask.sum()}')
        df[invalid_mask].to_excel("quarantine.xlsx",index = False)
    else:
        print(f'No invalid disbursaldate found.')
    
    df_clean = df[~invalid_mask].reset_index(drop=True)
    return df_clean   
        
# Save: as a new Excel file
def saveCleandata(df_clean,cleanFile):
    print("First few rows of the clean dataframe:")
    print(df_clean.head())
    if df_clean is not None:
        df_clean.to_excel(cleanFile, index=False)
    else:
        logger.error("Clean data is missing.")
        return
#main
def main():
    rawFile="rawLoanData.xlsx"
    cleanFile="cleanLoanData.xlsx"
    

    df = importData(rawFile)
    if df is  None:
        logger.error("Data has not been imported.")
        return
    else:
        df = inspData(df)
        df = clnHeader(df)
        df_clean = trnsfrmData(df)

    saveCleandata(df_clean,cleanFile)


#calling main
if __name__ == "__main__":
    main()
