USE MedicineDB;
GO

SET NOCOUNT ON;
PRINT '========================================='
PRINT 'ANALYTICAL SQL QUERIES'
PRINT '========================================='

-- 1. Number of medicines
PRINT '1. Total Medicines:';
SELECT COUNT(*) AS total_medicines FROM dbo.medicines;

-- 2. Number of unique generics
PRINT '2. Total Generics:';
SELECT COUNT(*) AS total_generics FROM dbo.generics;

-- 3. Number of manufacturers
PRINT '3. Total Manufacturers:';
SELECT COUNT(*) AS total_manufacturers FROM dbo.manufacturers;

-- 4. Average medicine price
PRINT '4. Average Medicine Price:';
SELECT ROUND(AVG(price), 2) AS avg_price FROM dbo.medicines WHERE price IS NOT NULL;

-- 5. Minimum and maximum medicine price
PRINT '5. Min and Max Medicine Price:';
SELECT 
    MIN(price) AS min_price, 
    MAX(price) AS max_price 
FROM dbo.medicines 
WHERE price IS NOT NULL;

-- 6. Number of brands per generic
PRINT '6. Number of Brands per Generic (Top 10):';
SELECT TOP 10
    g.generic_name,
    COUNT(m.brand_id) AS total_brands
FROM dbo.generics g
JOIN dbo.medicines m ON g.generic_id = m.generic_id
GROUP BY g.generic_name
ORDER BY total_brands DESC;

-- 7. Cheapest medicine for each generic (sample top 5 by generic id for readability)
PRINT '7. Cheapest medicine for each generic (Sample):';
WITH RankedPrices AS (
    SELECT 
        g.generic_name,
        m.brand_name,
        m.price,
        ROW_NUMBER() OVER(PARTITION BY g.generic_id ORDER BY m.price ASC) AS rnk
    FROM dbo.generics g
    JOIN dbo.medicines m ON g.generic_id = m.generic_id
    WHERE m.price IS NOT NULL
)
SELECT TOP 5 generic_name, brand_name AS cheapest_brand, price
FROM RankedPrices 
WHERE rnk = 1
ORDER BY generic_name;

-- 8. Most expensive medicine for each generic
PRINT '8. Most expensive medicine for each generic (Sample):';
WITH RankedPrices AS (
    SELECT 
        g.generic_name,
        m.brand_name,
        m.price,
        ROW_NUMBER() OVER(PARTITION BY g.generic_id ORDER BY m.price DESC) AS rnk
    FROM dbo.generics g
    JOIN dbo.medicines m ON g.generic_id = m.generic_id
    WHERE m.price IS NOT NULL
)
SELECT TOP 5 generic_name, brand_name AS most_expensive_brand, price
FROM RankedPrices 
WHERE rnk = 1
ORDER BY generic_name;

-- 9. Price difference between cheapest and most expensive brand within each generic
PRINT '9. Price difference within each generic (Top 5 largest differences):';
SELECT TOP 5
    g.generic_name,
    MIN(m.price) AS min_price,
    MAX(m.price) AS max_price,
    (MAX(m.price) - MIN(m.price)) AS price_difference
FROM dbo.generics g
JOIN dbo.medicines m ON g.generic_id = m.generic_id
WHERE m.price IS NOT NULL
GROUP BY g.generic_name
HAVING COUNT(m.brand_id) > 1
ORDER BY price_difference DESC;

-- 10. Potential savings percentage
PRINT '10. Potential savings percentage (Top 5 largest potential savings):';
SELECT TOP 5
    g.generic_name,
    MIN(m.price) AS min_price,
    MAX(m.price) AS max_price,
    CAST(ROUND(((MAX(m.price) - MIN(m.price)) / MAX(m.price)) * 100, 2) AS DECIMAL(5,2)) AS max_savings_percentage
FROM dbo.generics g
JOIN dbo.medicines m ON g.generic_id = m.generic_id
WHERE m.price IS NOT NULL AND m.price > 0
GROUP BY g.generic_name
HAVING COUNT(m.brand_id) > 1 AND MAX(m.price) > 0
ORDER BY max_savings_percentage DESC;

GO

-- SQL VIEWS (As requested: vw_medicine_details, vw_generic_price_comparison, vw_generic_brand_counts)
CREATE OR ALTER VIEW dbo.vw_medicine_details AS
SELECT 
    m.brand_id,
    m.brand_name,
    m.type,
    g.generic_name,
    mf.manufacturer_name,
    df.dosage_form_name,
    dc.drug_class_name,
    m.strength,
    m.price,
    m.currency
FROM dbo.medicines m
LEFT JOIN dbo.generics g ON m.generic_id = g.generic_id
LEFT JOIN dbo.manufacturers mf ON m.manufacturer_id = mf.manufacturer_id
LEFT JOIN dbo.dosage_forms df ON m.dosage_form_id = df.dosage_form_id
LEFT JOIN dbo.drug_classes dc ON g.drug_class_id = dc.drug_class_id;
GO

CREATE OR ALTER VIEW dbo.vw_generic_price_comparison AS
SELECT 
    g.generic_id,
    g.generic_name,
    COUNT(m.brand_id) AS total_brands,
    MIN(m.price) AS min_price,
    MAX(m.price) AS max_price,
    AVG(m.price) AS avg_price,
    (MAX(m.price) - MIN(m.price)) AS price_spread
FROM dbo.generics g
JOIN dbo.medicines m ON g.generic_id = m.generic_id
WHERE m.price IS NOT NULL
GROUP BY g.generic_id, g.generic_name;
GO

CREATE OR ALTER VIEW dbo.vw_generic_brand_counts AS
SELECT 
    g.generic_id,
    g.generic_name,
    COUNT(m.brand_id) AS brand_count
FROM dbo.generics g
LEFT JOIN dbo.medicines m ON g.generic_id = m.generic_id
GROUP BY g.generic_id, g.generic_name;
GO
