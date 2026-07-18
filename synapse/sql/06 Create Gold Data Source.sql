CREATE EXTERNAL DATA SOURCE source_gold
WITH (
    LOCATION = 'https://awstoragedatalakezain.dfs.core.windows.net/gold',
    CREDENTIAL = cred_zain
)