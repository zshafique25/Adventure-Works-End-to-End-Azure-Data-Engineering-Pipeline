CREATE EXTERNAL DATA SOURCE source_silver
WITH (
    LOCATION = 'https://awstoragedatalakezain.dfs.core.windows.net/silver',
    CREDENTIAL = cred_zain
)