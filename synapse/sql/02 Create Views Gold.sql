-------------------------
-- CREATE VIEW CALENDER 
---------------------------
CREATE VIEW gold.calender
AS
SELECT *
FROM OPENROWSET(
    BULK 'https://awstoragedatalakezain.dfs.core.windows.net/silver/AdventureWorks_Calendar/',
    FORMAT = 'DELTA'
) AS QUERY1
GO

------------------------
-- CREATE VIEW CUSTOMERS
------------------------
CREATE VIEW gold.customers
AS
SELECT 
    * 
FROM 
    OPENROWSET
        (
            BULK 'https://awstoragedatalakezain.dfs.core.windows.net/silver/AdventureWorks_Customers/',
            FORMAT = 'DELTA'
        ) as QUERY1
GO


------------------------
-- CREATE VIEW PRODUCTS
------------------------
CREATE VIEW gold.products
AS
SELECT 
    * 
FROM 
    OPENROWSET
        (
            BULK 'https://awstoragedatalakezain.dfs.core.windows.net/silver/AdventureWorks_Products/',
            FORMAT = 'DELTA'
        ) as QUERY1
GO

------------------------
-- CREATE VIEW RETURNS
------------------------
CREATE VIEW gold.returns
AS
SELECT 
    * 
FROM 
    OPENROWSET
        (
            BULK 'https://awstoragedatalakezain.dfs.core.windows.net/silver/AdventureWorks_Returns/',
            FORMAT = 'DELTA'
        ) as QUERY1
GO       

------------------------
-- CREATE VIEW CATEGORIES
------------------------
CREATE VIEW gold.cat
AS
SELECT 
    * 
FROM 
    OPENROWSET
        (
            BULK 'https://awstoragedatalakezain.dfs.core.windows.net/silver/AdventureWorks_Product_Categories/',
            FORMAT = 'DELTA'
        ) as QUERY1
GO

    ------------------------
-- CREATE VIEW SALES
------------------------
CREATE VIEW gold.sales
AS
SELECT 
    * 
FROM 
    OPENROWSET
        (
            BULK 'https://awstoragedatalakezain.dfs.core.windows.net/silver/AdventureWorks_Sales/',
            FORMAT = 'DELTA'
        ) as QUERY1
GO

------------------------
-- CREATE VIEW SUBCAT
------------------------
CREATE VIEW gold.subcat
AS
SELECT 
    * 
FROM 
    OPENROWSET
        (
            BULK 'https://awstoragedatalakezain.dfs.core.windows.net/silver/AdventureWorks_Product_Subcategories/',
            FORMAT = 'DELTA'
        ) as QUERY1
GO

------------------------
-- CREATE VIEW TERRITORIES
------------------------
CREATE VIEW gold.territories
AS
SELECT 
    * 
FROM 
    OPENROWSET
        (
            BULK 'https://awstoragedatalakezain.dfs.core.windows.net/silver/AdventureWorks_Territories/',
            FORMAT = 'DELTA'
        ) as QUERY1
GO